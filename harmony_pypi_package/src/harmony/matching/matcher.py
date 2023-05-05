import types
from collections import Counter
from typing import List

import numpy as np
from numpy import dot, mat, matmul, ndarray
from numpy.linalg import norm

from harmony.schemas.requests.text import Instrument


def cosine_similarity(vec1: ndarray, vec2: ndarray) -> ndarray:
    dp = dot(vec1, vec2.T)
    m1 = mat(norm(vec1, axis=1))
    m2 = mat(norm(vec2.T, axis=0))
    return np.asarray(dp / matmul(m1.T, m2))


def match_instruments_with_function(instruments: List[Instrument], query: str,
                                    vectorisation_function: types.FunctionType, mhc_questions=[], mhc_all_metadatas=[],
                                    mhc_embeddings=np.zeros((0, 0))) -> tuple:
    texts = []
    negated_texts = []
    instrument_ids = []
    question_indices = []
    all_questions = []
    for instrument in instruments:
        for question_idx, question in enumerate(instrument.questions):
            question.instrument_id = instrument.instrument_id
            all_questions.append(question)
            texts.append(question.question_text)
            # negated = negate(question.question_text, instrument.language) # TODO
            negated = question.question_text
            negated_texts.append(negated)
            instrument_ids.append(instrument.instrument_id)
            question_indices.append(question_idx)

    all_texts = texts + negated_texts
    if query:
        all_texts.append(query)

    all_vectors = vectorisation_function(all_texts)

    vectors_pos = all_vectors[:len(texts), :]
    vectors_neg = all_vectors[len(texts):len(texts) * 2, :]
    if query:
        vector_query = all_vectors[-1:, :]
        query_similarity = cosine_similarity(vectors_pos, vector_query)[:, 0]
    else:
        query_similarity = None

    pairwise_similarity = cosine_similarity(vectors_pos, vectors_pos)
    pairwise_similarity_neg1 = cosine_similarity(vectors_neg, vectors_pos)
    pairwise_similarity_neg2 = cosine_similarity(vectors_pos, vectors_neg)
    pairwise_similarity_neg_mean = np.mean([pairwise_similarity_neg1, pairwise_similarity_neg2], axis=0)

    similarity_polarity = np.sign(pairwise_similarity - pairwise_similarity_neg_mean)
    # Make sure that any 0's in polarity are converted to 1's
    where_0 = np.where(similarity_polarity == 0)
    similarity_polarity[where_0] = 1

    similarity_max = np.max([pairwise_similarity, pairwise_similarity_neg_mean], axis=0)
    similarity_with_polarity = similarity_max * similarity_polarity

    # Work out similarity with MHC
    if len(mhc_embeddings) > 0:
        similarities_mhc = cosine_similarity(vectors_pos, mhc_embeddings)

        ctrs = {}
        for idx, a in enumerate(np.argmax(similarities_mhc, axis=1)):
            if all_questions[idx].instrument_id not in ctrs:
                ctrs[all_questions[idx].instrument_id] = Counter()
            for topic in mhc_all_metadatas[a]["topics"]:
                ctrs[all_questions[idx].instrument_id][topic] += 1
            all_questions[idx].nearest_match_from_mhc_auto = mhc_questions[a].dict()

        instrument_to_category = {}
        for instrument_id, counts in ctrs.items():
            instrument_to_category[instrument_id] = []
            max_count = max(counts.values())
            for topic, topic_count in counts.items():
                if topic_count > max_count / 2:
                    instrument_to_category[instrument_id].append(topic)

        for question in all_questions:
            question.topics_auto = instrument_to_category[question.instrument_id]

    return all_questions, similarity_with_polarity, query_similarity

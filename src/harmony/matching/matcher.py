from collections import Counter
from typing import List, Callable

import numpy as np
from numpy import dot, mat, matmul, ndarray
from numpy.linalg import norm

from harmony.matching.negator import negate
from harmony.schemas.requests.text import Instrument


def cosine_similarity(vec1: ndarray, vec2: ndarray) -> ndarray:
    dp = dot(vec1, vec2.T)
    m1 = mat(norm(vec1, axis=1))
    m2 = mat(norm(vec2.T, axis=0))

    return np.asarray(dp / matmul(m1.T, m2))


def match_instruments_with_function(
    instruments: List[Instrument],
    query: str,
    vectorisation_function: Callable,
    mhc_questions: List = [],
    mhc_all_metadatas: List = [],
    mhc_embeddings: np.ndarray = np.zeros((0, 0)),
    texts_cached_vectors: dict[str, List[float]] = {},
) -> tuple:
    """
    Match instruments

    :param instruments: The instruments
    :param query: The query
    :param vectorisation_function: A function to vectorize a text
    :param mhc_questions
    :param mhc_all_metadatas
    :param mhc_embeddings
    :param texts_cached_vectors: A dictionary of already cached vectors from texts (key is the text and value is the vector)
    """

    # Vectors of texts that are already cached
    vectors_pos_cached = []
    vectors_neg_cached = []

    texts = []
    negated_texts = []
    all_questions = []
    for instrument in instruments:
        for question_idx, question in enumerate(instrument.questions):
            question.instrument_id = instrument.instrument_id
            all_questions.append(question)

            # Text
            question_text = question.question_text
            if question_text not in texts_cached_vectors.keys():
                texts.append(question_text)
            else:
                vectors_pos_cached.append(texts_cached_vectors[question_text])

            # Negated text
            negated_text = negate(question_text, instrument.language)
            if negated_text not in texts_cached_vectors.keys():
                negated_texts.append(negated_text)
            else:
                vectors_neg_cached.append(texts_cached_vectors[negated_text])

    # Add all texts together including query
    all_texts = texts + negated_texts
    if query:
        all_texts.append(query)

    # Get vectors for all texts
    all_vectors = vectorisation_function(all_texts)

    # Create a dictionary with new vectors
    new_vectors = {}
    for vector, text in zip(all_vectors, all_texts):
        new_vectors[text] = vector

    # Create numpy array of texts vectors
    tmp_vectors_pos = all_vectors[: len(texts), :]
    if vectors_pos_cached:
        # Concatenate the new vectors and the cached vectors
        vectors_pos = np.concatenate([tmp_vectors_pos, vectors_pos_cached], axis=0)
    else:
        # New vectors only
        vectors_pos = tmp_vectors_pos

    # Create numpy array of negated texts vectors
    tmp_vectors_neg = all_vectors[len(texts) : len(texts) * 2, :]
    if vectors_neg_cached:
        # Concatenate the new vectors and the cached vectors
        vectors_neg = np.concatenate([tmp_vectors_neg, vectors_neg_cached], axis=0)
    else:
        # New vectors only
        vectors_neg = tmp_vectors_neg

    # Get query similarity
    if query:
        vector_query = all_vectors[-1:, :]
        query_similarity = cosine_similarity(vectors_pos, vector_query)[:, 0]
    else:
        query_similarity = None

    pairwise_similarity = cosine_similarity(vectors_pos, vectors_pos)
    pairwise_similarity_neg1 = cosine_similarity(vectors_neg, vectors_pos)
    pairwise_similarity_neg2 = cosine_similarity(vectors_pos, vectors_neg)
    pairwise_similarity_neg_mean = np.mean(
        [pairwise_similarity_neg1, pairwise_similarity_neg2], axis=0
    )

    similarity_difference = pairwise_similarity - pairwise_similarity_neg_mean
    similarity_polarity = np.sign(similarity_difference)

    # Make sure that any 0's in polarity are converted to 1's
    where_0 = np.where(np.abs(similarity_difference) < 0.001)
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

    return all_questions, similarity_with_polarity, query_similarity, new_vectors

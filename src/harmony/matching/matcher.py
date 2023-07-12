from collections import Counter
from typing import List, Callable

import numpy as np
from harmony.matching.negator import negate
from harmony.schemas.requests.text import Instrument
from harmony.schemas.text_vector import TextVector
from numpy import dot, mat, matmul, ndarray
from numpy.linalg import norm


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

    # Create a list of text vectors
    all_questions = []
    text_vectors: List[TextVector] = []
    for instrument in instruments:
        for question in instrument.questions:
            question.instrument_id = instrument.instrument_id
            all_questions.append(question)

            # Text
            question_text = question.question_text
            if question_text not in texts_cached_vectors.keys():
                text_vectors.append(
                    TextVector(
                        text=question_text, vector=[], is_negated=False, is_query=False
                    )
                )
            else:
                vector = texts_cached_vectors[question_text]
                text_vectors.append(
                    TextVector(
                        text=question_text,
                        vector=vector,
                        is_negated=False,
                        is_query=False,
                    )
                )

            # Negated text
            negated_text = negate(question_text, instrument.language)
            if negated_text not in texts_cached_vectors.keys():
                text_vectors.append(
                    TextVector(
                        text=negated_text, vector=[], is_negated=True, is_query=False
                    )
                )
            else:
                vector = texts_cached_vectors[negated_text]
                text_vectors.append(
                    TextVector(
                        text=negated_text,
                        vector=vector,
                        is_negated=True,
                        is_query=False,
                    )
                )

    # Add query
    if query:
        if query not in texts_cached_vectors.keys():
            text_vectors.append(
                TextVector(text=query, vector=[], is_negated=False, is_query=True)
            )
        else:
            vector = texts_cached_vectors[query]
            text_vectors.append(
                TextVector(text=query, vector=vector, is_negated=False, is_query=True)
            )

    # Texts with no cached vector
    texts_not_cached = [x.text for x in text_vectors if not x.vector]

    # Get vectors for all texts not cached
    new_vectors_list: List = vectorisation_function(texts_not_cached).tolist()

    # Create a dictionary with new vectors
    new_vectors_dict = {}
    for vector, text in zip(new_vectors_list, texts_not_cached):
        new_vectors_dict[text] = vector

    # Add new vectors to all_texts
    for index, text_dict in enumerate(text_vectors):
        if not text_dict.vector:
            text_vectors[index].vector = new_vectors_list.pop(0)

    # Create numpy array of texts vectors
    vectors_pos = np.array(
        [
            x.vector
            for x in text_vectors
            if (x.is_negated is False and x.is_query is False)
        ]
    )

    # Create numpy array of negated texts vectors
    vectors_neg = np.array(
        [
            x.vector
            for x in text_vectors
            if (x.is_negated is True and x.is_query is False)
        ]
    )

    # Get query similarity
    if vectors_pos.any() and query:
        vector_query = np.array(
            [[x for x in text_vectors if x.is_query is True][0].vector]
        )
        query_similarity = cosine_similarity(vectors_pos, vector_query)[:, 0]
    else:
        query_similarity = np.array([])

    # Get similarity with polarity
    if vectors_pos.any():
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

        similarity_max = np.max(
            [pairwise_similarity, pairwise_similarity_neg_mean], axis=0
        )
        similarity_with_polarity = similarity_max * similarity_polarity
    else:
        similarity_with_polarity = np.array([])

    # Work out similarity with MHC
    if vectors_pos.any():
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

    return all_questions, similarity_with_polarity, query_similarity, new_vectors_dict

'''
MIT License

Copyright (c) 2023 Ulster University (https://www.ulster.ac.uk).
Project: Harmony (https://harmonydata.ac.uk)
Maintainer: Thomas Wood (https://fastdatascience.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
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


def add_text_to_vec(text, texts_cached_vectors, text_vectors, is_negated_, is_query_):
    if text not in texts_cached_vectors.keys():
        text_vectors.append(
            TextVector(
                text=text, vector=[], is_negated=is_negated_, is_query=is_query_
            )
        )
    else:
        vector = texts_cached_vectors[text]
        text_vectors.append(
            TextVector(
                text=text,
                vector=vector,
                is_negated=is_negated_,
                is_query=is_query_,
            )
        )
    return text_vectors


def process_questions(questions):
    texts_cached_vectors: dict[str, List[float]] = {}
    text_vectors: List[TextVector] = []
    for question_text in questions:
        text_vectors = add_text_to_vec(question_text, texts_cached_vectors, text_vectors, False, False)
        negated_text = negate(question_text, 'en')
        text_vectors = add_text_to_vec(negated_text, texts_cached_vectors, text_vectors, True, False)
    return text_vectors


def vectorise_texts(text_vectors, vectorisation_function):
    for index, text_dict in enumerate(text_vectors):
        if not text_dict.vector:
            text_vectors[index].vector = vectorisation_function([text_dict.text]).tolist()[0]
    return text_vectors


def vectors_pos_neg(text_vectors):
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
    return vectors_pos, vectors_neg


def create_full_text_vectors(all_questions, query, vectorisation_function, texts_cached_vectors):
    # Create a list of text vectors
    text_vectors = process_questions(all_questions)

    # Add query
    if query:
        text_vectors = add_text_to_vec(query, texts_cached_vectors, text_vectors, False, True)

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
    return text_vectors, new_vectors_dict


#
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
    all_questions = []
    for instrument in instruments:
        all_questions.extend(instrument.questions)
    # all_questions: List[Question] = all_questions
    all_questions_str: List[str] = [q.question_text for q in all_questions]
    #    all_questions = [instrument["question_text"] for instrument in instruments]

    text_vectors, new_vectors_dict = create_full_text_vectors(all_questions_str, query, vectorisation_function,
                                                              texts_cached_vectors)
    vectors_pos, vectors_neg = vectors_pos_neg(text_vectors)

    # Get similarity between the query (only one query?) and the questions
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
            top_mhc_match_ids = np.argmax(similarities_mhc, axis=1)
            for idx, mhc_item_idx in enumerate(top_mhc_match_ids):
                question_text = mhc_questions[mhc_item_idx].question_text
                if question_text is None or len(question_text) < 3:  # Ignore empty entries in MHC questionnaires
                    continue
                if all_questions[idx].instrument_id not in ctrs:
                    ctrs[all_questions[idx].instrument_id] = Counter()
                for topic in mhc_all_metadatas[mhc_item_idx]["topics"]:
                    ctrs[all_questions[idx].instrument_id][topic] += 1
                all_questions[idx].nearest_match_from_mhc_auto = mhc_questions[mhc_item_idx].dict()
                strength_of_match = similarities_mhc[idx, mhc_item_idx]
                all_questions[idx].topics_strengths = {topic: float(strength_of_match)}

            instrument_to_category = {}
            for instrument_id, counts in ctrs.items():
                instrument_to_category[instrument_id] = []
                max_count = max(counts.values())
                for topic, topic_count in counts.items():
                    if topic_count > max_count / 2:
                        instrument_to_category[instrument_id].append(topic)

            for question in all_questions:
                question.topics_auto = instrument_to_category[question.instrument_id]
        else:
            for question in all_questions:
                question.topics_auto = []

    return all_questions, similarity_with_polarity, query_similarity, new_vectors_dict

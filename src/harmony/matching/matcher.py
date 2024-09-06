"""
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
"""

import statistics
import heapq
from collections import Counter, OrderedDict
from typing import List, Callable

import numpy as np
from numpy import dot, matmul, ndarray, matrix
from numpy.linalg import norm

from harmony.matching.negator import negate
from harmony.schemas.catalogue_instrument import CatalogueInstrument
from harmony.schemas.catalogue_question import CatalogueQuestion
from harmony.schemas.requests.text import (
    Instrument,
    Question,
)
from harmony.schemas.text_vector import TextVector


def cosine_similarity(vec1: ndarray, vec2: ndarray) -> ndarray:
    dp = dot(vec1, vec2.T)
    m1 = matrix(norm(vec1, axis=1))
    m2 = matrix(norm(vec2.T, axis=0))

    return np.asarray(dp / matmul(m1.T, m2))


def add_text_to_vec(text, texts_cached_vectors, text_vectors, is_negated_, is_query_):
    if text not in texts_cached_vectors:
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


def process_questions(questions, texts_cached_vectors):
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


def create_full_text_vectors(
        all_questions: List[str],
        query: str | None,
        vectorisation_function: Callable,
        texts_cached_vectors: dict[str, list[float]],
) -> tuple[List[TextVector], dict]:
    """
    Create full text vectors.
    """

    # Create a list of text vectors
    text_vectors = process_questions(all_questions, texts_cached_vectors)

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


def match_instruments_with_catalogue_instruments(
        instruments: List[Instrument],
        catalogue_data: dict,
        vectorisation_function: Callable,
        texts_cached_vectors: dict[str, List[float]],
) -> tuple[List[Instrument], List[CatalogueInstrument]]:
    """
    Match instruments with catalogue instruments.

    :param instruments: The instruments.
    :param catalogue_data: The catalogue data.
    :param vectorisation_function: A function to vectorize a text.
    :param texts_cached_vectors: A dictionary of already cached vectors from texts (key is the text and value is the vector).
    :return: Index 0 in the tuple contains the list of instruments that now each contain the best instrument matches from the catalog.
        Index 1 in the tuple contains a list of closest instrument matches from the catalog for all the instruments.
    """

    # Gather all questions
    all_questions: List[str] = []
    for instrument in instruments:
        all_questions.extend([q.question_text for q in instrument.questions])
    all_questions = list(set(all_questions))

    # Create text vectors for all questions in all the uploaded instruments
    all_instruments_text_vectors, _ = create_full_text_vectors(
        all_questions=all_questions,
        query=None,
        vectorisation_function=vectorisation_function,
        texts_cached_vectors=texts_cached_vectors,
    )

    # For each instrument, find the best instrument matches for it in the catalogue
    for instrument in instruments:
        instrument.closest_catalogue_instrument_matches = (
            match_questions_with_catalogue_instruments(
                questions=instrument.questions,
                catalogue_data=catalogue_data,
                all_instruments_text_vectors=all_instruments_text_vectors,
                questions_are_from_one_instrument=True,
            )
        )

    # Gather all questions from all instruments and find the best instrument matches in the catalogue
    all_instrument_questions: List[Question] = []
    for instrument in instruments:
        all_instrument_questions.extend(instrument.questions)
    closest_catalogue_instrument_matches = match_questions_with_catalogue_instruments(
        questions=all_instrument_questions,
        catalogue_data=catalogue_data,
        all_instruments_text_vectors=all_instruments_text_vectors,
        questions_are_from_one_instrument=False,
    )

    return instruments, closest_catalogue_instrument_matches


def match_questions_with_catalogue_instruments(
        questions: List[Question],
        catalogue_data: dict,
        all_instruments_text_vectors: List[TextVector],
        questions_are_from_one_instrument: bool,
) -> List[CatalogueInstrument]:
    """
    Match questions with catalogue instruments.
    Each question from the list will receive the closest instrument match for it.
    The closest instrument match for all questions is returned as a result of this function.

    :param questions: The questions.
    :param catalogue_data: The catalogue data.
    :param all_instruments_text_vectors: A list of text vectors of all questions found in all the instruments uploaded.
    :param questions_are_from_one_instrument: If the questions provided are coming from one instrument only.

    :return: A list of closest instrument matches for the questions provided.
    """

    # Catalogue data
    catalogue_instrument_idx_to_catalogue_questions_idx: List[List[int]] = catalogue_data[
        "instrument_idx_to_question_idx"
    ]
    all_catalogue_questions_embeddings_concatenated: np.ndarray = catalogue_data[
        "all_embeddings_concatenated"
    ]
    all_catalogue_instruments: List[dict] = catalogue_data["all_instruments"]
    all_catalogue_questions: List[str] = catalogue_data["all_questions"]

    # No embeddings = nothing to find
    if len(all_catalogue_questions_embeddings_concatenated) == 0:
        return []

    # All instruments text vectors to dict
    all_instruments_text_vectors_dict = {
        text_vector.text: text_vector.vector for text_vector in all_instruments_text_vectors
    }

    # The total number of questions we received as input.
    num_input_questions = len(questions)

    # Get an array of dimensions.
    # (number of input questions) x (number of dimensions of LLM - typically 768, 384, 500, 512, etc.)
    vectors = np.array(
        [all_instruments_text_vectors_dict[question.question_text] for question in questions]
    )

    # Get a 2D array of (number of input questions) x (number of questions in catalogue).
    # E.g. index 0 (matches for the first input question) will contain a list of matches for each question in the
    # catalogue. So the best match for the first input question is the highest similarity found in index 0.
    catalogue_similarities = cosine_similarity(
        vectors, all_catalogue_questions_embeddings_concatenated
    )

    # Get a 1D array of length (number of input questions).
    # For each input question, this is the index of the single closest matching question text in our catalogues.
    # Note that each question text in the catalogue (vector index) is unique, and we must later do a further mapping to
    # find out which instrument(s) it occurs in.
    idxs_of_top_questions_matched_in_catalogue = np.argmax(catalogue_similarities, axis=1)

    # Get a set of all the top matching question text indices in our catalogue.
    # idxs_of_top_questions_matched_in_catalogue_set = set(idxs_of_top_questions_matched_in_catalogue)

    # This keeps track of each instrument matches how many question items in the query
    # e.g. if the first instrument in our catalogue (instrument 0) matches 4 items, then this dictionary will
    # contain {0: 4}.
    # instrument_idx_to_num_matching_items_with_query = {}

    # This dictionary will contain the index of the instrument and the cosine similarities to the top matched questions
    # in that instrument e.g. {50: [ ... ]}
    instrument_idx_to_cosine_similarities_top_match: dict[int, [float]] = {}

    # This keeps track of how many question items in total are contained in each instrument, irrespective of the
    # number of matches.
    # This is needed for stats such as precision and recall.
    instrument_idx_to_total_num_question_items_present = {}

    # Find any instruments matching
    input_question_idx_to_matching_instruments: List[List[dict]] = []
    for input_question_idx in range(len(questions)):
        input_question_idx_to_matching_instruments.append([])
    for input_question_idx in range(len(questions)):
        top_match_catalogue_question_idx = idxs_of_top_questions_matched_in_catalogue[
            input_question_idx
        ]
        for instrument_idx, question_idxs_in_this_instrument in enumerate(
                catalogue_instrument_idx_to_catalogue_questions_idx
        ):
            if top_match_catalogue_question_idx in question_idxs_in_this_instrument:
                instrument_from_catalogue = all_catalogue_instruments[instrument_idx]
                if not any(
                        x["instrument_name"] == instrument_from_catalogue["instrument_name"]
                        for x in input_question_idx_to_matching_instruments[input_question_idx]
                ):
                    input_question_idx_to_matching_instruments[
                        input_question_idx
                    ].append(instrument_from_catalogue)

    # For each catalogue instrument get the total number of question matches in the query
    # For each catalogue instrument get the total number of questions
    for instrument_idx, question_idxs_in_this_instrument in enumerate(
            catalogue_instrument_idx_to_catalogue_questions_idx
    ):
        catalogue_question_idxs_in_this_instrument_set = set(
            question_idxs_in_this_instrument
        )
        # instrument_idx_to_num_matching_items_with_query[instrument_idx] = len(
        #     catalogue_question_idxs_in_this_instrument_set.intersection(
        #         idxs_of_top_questions_matched_in_catalogue_set
        #     )
        # )
        instrument_idx_to_total_num_question_items_present[instrument_idx] = len(
            catalogue_question_idxs_in_this_instrument_set
        )

    # Question similarity with catalogue questions
    for idx, question in enumerate(questions):
        seen_in_instruments: List[CatalogueInstrument] = []
        for instrument in input_question_idx_to_matching_instruments[idx]:
            instrument_name = instrument["instrument_name"]
            instrument_url = instrument["metadata"].get("url", "")
            source = instrument["metadata"]["source"].upper()
            sweep = instrument["metadata"].get("sweep_id", "")
            seen_in_instruments.append(
                CatalogueInstrument(
                    instrument_name=instrument_name,
                    instrument_url=instrument_url,
                    source=source,
                    sweep=sweep,
                )
            )

        question.closest_catalogue_question_match = CatalogueQuestion(
            question=all_catalogue_questions[idxs_of_top_questions_matched_in_catalogue[idx]],
            seen_in_instruments=seen_in_instruments,
        )

    # Instrument index to list of cosine similarities top question match
    for input_question_idx, idx_top_input_question_match_in_catalogue in enumerate(
            idxs_of_top_questions_matched_in_catalogue
    ):
        for (
                catalogue_instrument_idx,
                catalogue_question_idxs_in_this_instrument,
        ) in enumerate(catalogue_instrument_idx_to_catalogue_questions_idx):
            catalogue_question_idxs_set = set(
                catalogue_question_idxs_in_this_instrument
            )
            if idx_top_input_question_match_in_catalogue in catalogue_question_idxs_set:
                # Create the list if it doesn't exist yet
                if not instrument_idx_to_cosine_similarities_top_match.get(
                        catalogue_instrument_idx
                ):
                    instrument_idx_to_cosine_similarities_top_match[
                        catalogue_instrument_idx
                    ] = []

                # Add the cosine similarity
                instrument_idx_to_cosine_similarities_top_match[
                    catalogue_instrument_idx
                ].append(
                    catalogue_similarities[input_question_idx][
                        idx_top_input_question_match_in_catalogue
                    ]
                )

    # Keep track of the instrument id and the count of top question matches that belong to it
    instrument_idx_to_top_matches_ct = {
        k: len(v) for k, v in instrument_idx_to_cosine_similarities_top_match.items()
    }

    # Calculate the average for each list of cosine similarities from instruments
    instrument_idx_to_cosine_similarities_average: dict[int, float] = {}
    for (
            instrument_idx,
            cosine_similarities,
    ) in instrument_idx_to_cosine_similarities_top_match.items():
        instrument_idx_to_cosine_similarities_average[instrument_idx] = (
            statistics.mean(cosine_similarities)
        )

    instrument_idx_to_score = {}
    for instrument_idx, average_sim in instrument_idx_to_cosine_similarities_average.items():
        score = average_sim * (0.1+instrument_idx_to_top_matches_ct.get(instrument_idx, 0))
        instrument_idx_to_score[instrument_idx] = score

    # Find the top 10 best instrument idx matches, index 0 containing the best match etc.
    top_n_catalogue_instrument_idxs = sorted(
        instrument_idx_to_score,
        key=instrument_idx_to_score.get,
        reverse=True
    )[:200]

    # Create a list of CatalogueInstrument for each top instrument
    top_instruments: List[CatalogueInstrument] = []
    for top_catalogue_instrument_idx in top_n_catalogue_instrument_idxs:
        top_catalogue_instrument = all_catalogue_instruments[top_catalogue_instrument_idx]
        num_questions_in_ref_instrument = (
            instrument_idx_to_total_num_question_items_present[
                top_catalogue_instrument_idx
            ]
        )
        num_top_match_questions = instrument_idx_to_top_matches_ct[
            top_catalogue_instrument_idx
        ]

        instrument_name = top_catalogue_instrument["instrument_name"]
        instrument_url = top_catalogue_instrument["metadata"].get("url", "")
        source = top_catalogue_instrument["metadata"]["source"].upper()
        sweep = top_catalogue_instrument["metadata"].get("sweep_id", "")

        if questions_are_from_one_instrument:
            info = (
                f"{instrument_name} Sweep {sweep if sweep else 'UNKNOWN'} matched {num_top_match_questions} "
                f"question(s) in your instrument, your instrument contains {num_input_questions} question(s). "
                f"The reference instrument contains {num_questions_in_ref_instrument} question(s)."
            )
        else:
            info = (
                f"{instrument_name} Sweep {sweep if sweep else 'UNKNOWN'} matched {num_top_match_questions} "
                f"question(s) in all of your instruments, your instruments contains {num_input_questions} "
                f"question(s). The reference instrument contains {num_questions_in_ref_instrument} question(s)."
            )

        top_instruments.append(CatalogueInstrument(
            instrument_name=instrument_name,
            instrument_url=instrument_url,
            source=source,
            sweep=sweep,
            metadata={
                "info": info,
                "num_matched_questions": num_top_match_questions,
                "num_ref_instrument_questions": num_questions_in_ref_instrument,
                "mean_cosine_similarity":  instrument_idx_to_cosine_similarities_average.get(top_catalogue_instrument_idx)
            },
        ))

    return top_instruments


def match_query_with_catalogue_instruments(
        query: str,
        catalogue_data: dict,
        vectorisation_function: Callable,
        texts_cached_vectors: dict[str, List[float]],
        max_results: int = 100,
) -> dict[str, list | dict]:
    """
    Match query with catalogue instruments.

    :param query: The query.
    :param catalogue_data: The catalogue data.
    :param vectorisation_function: A function to vectorize a text.
    :param texts_cached_vectors: A dictionary of already cached text vectors (text to vector).
    :param max_results: The max amount of instruments to return.
    :return: A dict containing the list of instruments (up to 100) and the new text vectors.
        E.g. {"instruments": [...], "new_text_vectors": {...}}.
    """

    response = {"instruments": [], "new_text_vectors": {}}

    # Catalogue data
    catalogue_instrument_idx_to_catalogue_questions_idx: List[List[int]] = (
        catalogue_data["instrument_idx_to_question_idx"]
    )
    all_catalogue_questions_embeddings_concatenated: np.ndarray = catalogue_data[
        "all_embeddings_concatenated"
    ]
    all_catalogue_instruments: List[dict] = catalogue_data["all_instruments"]

    # No embeddings = nothing to find
    if len(all_catalogue_questions_embeddings_concatenated) == 0:
        return response

    # Text vectors
    text_vectors, new_text_vectors = create_full_text_vectors(
        all_questions=[],
        query=query,
        vectorisation_function=vectorisation_function,
        texts_cached_vectors=texts_cached_vectors,
    )

    # Get an array of dimensions
    vectors = np.array([text_vectors[0].vector])

    # Get a 2D array of 1 x (number of questions in catalogue)
    catalogue_similarities = cosine_similarity(
        vectors, all_catalogue_questions_embeddings_concatenated
    )

    # Get the catalogue questions similarities for the query
    catalogue_questions_similarities_for_query = catalogue_similarities[0].tolist()

    # Get indexes of top matching questions in the catalogue
    # The first index contains the best match
    top_catalogue_questions_matches_idxs = [
        catalogue_questions_similarities_for_query.index(i)
        for i in heapq.nlargest(max_results, catalogue_questions_similarities_for_query)
    ]

    # A dict of matching instruments
    # The key is the name of the instrument and the value is the instrument
    instrument_matches: OrderedDict[str, Instrument] = OrderedDict()

    # Find the matching instruments by looking for the instrument of the top catalogue questions matches indexes
    # Loop through indexes of top matched catalogue question
    for top_catalogue_question_match_idx in top_catalogue_questions_matches_idxs:
        # Loop through instrument index with its question indexes
        for catalogue_instrument_idx, catalogue_instrument_questions_idxs in enumerate(
                catalogue_instrument_idx_to_catalogue_questions_idx
        ):
            # Check if the index of the top matched catalogue question is in the catalogue instrument's question indexes
            if top_catalogue_question_match_idx in catalogue_instrument_questions_idxs:
                catalogue_instrument = all_catalogue_instruments[
                    catalogue_instrument_idx
                ]

                # Add the instrument to the dict if it wasn't already added
                instrument_name = catalogue_instrument["instrument_name"]
                if instrument_name not in instrument_matches:
                    instrument_matches[instrument_name] = Instrument.model_validate(
                        catalogue_instrument
                    )

    response["instruments"] = [x for x in instrument_matches.values()]
    response["new_text_vectors"] = new_text_vectors

    return response


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
    Match instruments.

    :param instruments: The instruments
    :param query: The query
    :param vectorisation_function: A function to vectorize a text
    :param mhc_questions: MHC questions.
    :param mhc_all_metadatas: MHC metadatas.
    :param mhc_embeddings: MHC embeddings.
    :param texts_cached_vectors: A dictionary of already cached vectors from texts (key is the text and value is the vector).
    """

    all_questions: List[Question] = []
    for instrument in instruments:
        all_questions.extend(instrument.questions)

    text_vectors, new_vectors_dict = create_full_text_vectors(
        all_questions=[q.question_text for q in all_questions],
        query=query,
        vectorisation_function=vectorisation_function,
        texts_cached_vectors=texts_cached_vectors
    )

    # get vectors for all original texts and vectors for negated texts
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
    if vectors_pos.any():  # NOTE: Should an error be thrown if vectors_pos is empty?
        pairwise_similarity = cosine_similarity(vectors_pos, vectors_pos)
        # NOTE: Similarity of (vectors_neg, vectors_pos) & (vectors_pos, vectors_neg) should be the same
        pairwise_similarity_neg1 = cosine_similarity(vectors_neg, vectors_pos)
        pairwise_similarity_neg2 = cosine_similarity(vectors_pos, vectors_neg)
        pairwise_similarity_neg_mean = np.mean(
            [pairwise_similarity_neg1, pairwise_similarity_neg2], axis=0
        )

        # Polarity of 1 means the sentence shouldn't be negated, -1 means it should
        similarity_difference = pairwise_similarity - pairwise_similarity_neg_mean
        similarity_polarity = np.sign(similarity_difference)

        # Make sure that any 0's in polarity are converted to 1's
        where_0 = np.where(np.abs(similarity_difference) < 0.001)
        similarity_polarity[where_0] = 1

        similarity_max = np.max(
            [pairwise_similarity, pairwise_similarity_neg_mean], axis=0
        )
        # NOTE: A value of -1 and +1 both mean sentences are similar, 0 means not similar
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
                all_questions[idx].nearest_match_from_mhc_auto = mhc_questions[mhc_item_idx].model_dump()
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

    return (
        all_questions,
        similarity_with_polarity,
        query_similarity,
        new_vectors_dict
    )

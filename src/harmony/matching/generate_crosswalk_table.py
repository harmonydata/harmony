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

import operator
from typing import List

import numpy as np
import pandas as pd

from harmony.schemas.requests.text import Instrument


def generate_crosswalk_table(instruments: List[Instrument], item_to_item_similarity_matrix: np.ndarray,
                             threshold: float = None, is_allow_within_instrument_matches=False,
                             is_enforce_one_to_one: bool = False) -> pd.DataFrame:
    """
    Generate a crosswalk table for a list of instruments, given the similarity matrix that came out of the match function. A crosswalk is a list of pairs of variables from different studies that can be harmonised.
    @param instruments: The original list of instruments, each containing a question. The sum of the number of questions in all instruments is the total number of questions which should equal both the width and height of the similarity matrix.
    @param item_to_item_similarity_matrix: The cosine similarity matrix from Harmony
    @param threshold: The minimum threshold that we consider a match. This is applied to the absolute match value. So if a question pair has similarity 0.2 and threshold = 0.5, then that question pair will be excluded. Leave as None if you don't want to apply any thresholding.
    @param is_allow_within_instrument_matches: Defaults to False. If this is set to True, we include crosswalk items that originate from the same instrument, which would otherwise be excluded by default.
    @param is_enforce_one_to_one: Defaults to False.  If this is set to True, we force all variables in the crosswalk table to be matched with exactly one other variable.
    @return: A crosswalk table as a DataFrame.
    """

    # assert that the similarity matrix is square
    assert item_to_item_similarity_matrix.shape[0] == item_to_item_similarity_matrix.shape[1]

    # assert that the similarity matrix is symmetric
    assert np.allclose(item_to_item_similarity_matrix, item_to_item_similarity_matrix.T)

    # assert that the similarity matrix is -1 <= x <= 1
    assert np.all(np.round(item_to_item_similarity_matrix, 3) >= -1.)
    assert np.all(np.round(item_to_item_similarity_matrix, 3) <= 1.)

    # assert that the similarity matrix has 1s on its diagonals
    assert np.allclose(np.diag(item_to_item_similarity_matrix), 1.)

    # ensure that the entries of the similarity matrix are floats
    if item_to_item_similarity_matrix.dtype != np.float64:
        item_to_item_similarity_matrix = item_to_item_similarity_matrix.astype(np.float64)


    matching_pairs = []

    all_questions = []
    for instrument_idx, instrument in enumerate(instruments):
        for question in instrument.questions:
            all_questions.append((instrument_idx, question))

    abs_similarities_between_instruments = np.abs(item_to_item_similarity_matrix)

    coord_to_sim = {}
    for question_2_idx in range(abs_similarities_between_instruments.shape[0]):
        for question_1_idx in range(abs_similarities_between_instruments.shape[1]):
            if question_2_idx > question_1_idx:
                coord_to_sim[(question_2_idx, question_1_idx)] = abs_similarities_between_instruments[
                    question_2_idx, question_1_idx]

    is_used_x = set()
    is_used_y = set()
    for (question_2_idx, question_1_idx), sim in sorted(coord_to_sim.items(), key=operator.itemgetter(1), reverse=True):
        if question_1_idx not in is_used_x and question_2_idx not in is_used_y and (
                threshold is None or abs_similarities_between_instruments[
            (question_2_idx, question_1_idx)] >= threshold):

            instrument_1_idx, question_1 = all_questions[question_1_idx]
            instrument_2_idx, question_2 = all_questions[question_2_idx]

            instrument_1 = instruments[instrument_1_idx]
            instrument_2 = instruments[instrument_2_idx]

            if not is_allow_within_instrument_matches and instrument_1_idx == instrument_2_idx:
                continue

            question_1_identifier = f"{instrument_1.instrument_name}_{question_1.question_no}"
            question_2_identifier = f"{instrument_2.instrument_name}_{question_2.question_no}"

            matching_pairs.append({
                'pair_name': f"{question_1_identifier}_{question_2_identifier}",
                'question1_id': question_1_identifier,
                'question1_text': question_1.question_text,
                'question2_id': question_2_identifier,
                'question2_text': question_2.question_text,
                'match_score': item_to_item_similarity_matrix[question_1_idx, question_2_idx]
            })

            # best_matches.add((question_1_idx,question_2_idx))
            if is_enforce_one_to_one:
                is_used_x.add(question_1_idx)
                is_used_y.add(question_2_idx)

    # convert list to dataframe
    return pd.DataFrame(matching_pairs)

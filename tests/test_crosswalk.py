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

import sys
import unittest

import numpy as np
import pandas as pd

sys.path.append("../src")

from harmony.matching.generate_crosswalk_table import generate_crosswalk_table
from harmony import create_instrument_from_list
from harmony import match_instruments


class TestGenerateCrosswalkTable(unittest.TestCase):
    def setUp(self):
        # Sample data
        self.instruments_dummy = [create_instrument_from_list(["potato", "tomato", "radish"], instrument_name="veg")]

        self.similarity = np.array([
            [1.0, 0.7, 0.9],
            [0.7, 1.0, 0.8],
            [0.9, 0.8, 1.0]
        ])

        self.instruments = [create_instrument_from_list(
            ["Feeling nervous, anxious, or on edge", "Not being able to stop or control worrying"],
            instrument_name="GAD-7")]

        self.threshold = 0.6

    def test_generate_crosswalk_table_dummy_data(self):
        result = generate_crosswalk_table(self.instruments_dummy, self.similarity, self.threshold,
                                          is_allow_within_instrument_matches=True)

        expected_matches = [
            {'match_score': 0.9, 'pair_name': 'veg_1_veg_3', 'question1_id': 'veg_1', 'question1_text': 'potato',
             'question2_id': 'veg_3', 'question2_text': 'radish'},
            {'match_score': 0.8, 'pair_name': 'veg_2_veg_3', 'question1_id': 'veg_2', 'question1_text': 'tomato',
             'question2_id': 'veg_3', 'question2_text': 'radish'},
            {'match_score': 0.7, 'pair_name': 'veg_1_veg_2', 'question1_id': 'veg_1', 'question1_text': 'potato',
             'question2_id': 'veg_2', 'question2_text': 'tomato'}]

        self.assertEqual(len(result), len(expected_matches))

        for row_idx, expected_row in enumerate(expected_matches):
            self.assertEqual(expected_row["match_score"], result["match_score"].iloc[row_idx])
            self.assertEqual(expected_row["pair_name"], result["pair_name"].iloc[row_idx])
            self.assertEqual(expected_row["question1_id"], result["question1_id"].iloc[row_idx])
            self.assertEqual(expected_row["question2_id"], result["question2_id"].iloc[row_idx])
            self.assertEqual(expected_row["question1_text"], result["question1_text"].iloc[row_idx])
            self.assertEqual(expected_row["question2_text"], result["question2_text"].iloc[row_idx])

    def test_generate_crosswalk_table_empty(self):
        empty_similarity = np.eye(3)  # Identity matrix, no matches above threshold
        result = generate_crosswalk_table(self.instruments_dummy, empty_similarity, self.threshold)
        self.assertTrue(result.empty)

    def test_generate_crosswalk_table_real(self):
        match_response = match_instruments(self.instruments)
        result = generate_crosswalk_table(self.instruments, match_response.similarity_with_polarity, self.threshold,
                                          is_allow_within_instrument_matches=True)
        expected_matches = []

        for _, row in pd.DataFrame(expected_matches).iterrows():
            self.assertTrue(any(row.equals(result_row) for _, result_row in result.iterrows()))

        self.assertEqual(len(result), len(expected_matches))

        lower_threshold = 0.5
        result = generate_crosswalk_table(self.instruments, match_response.similarity_with_polarity, lower_threshold,
                                          is_allow_within_instrument_matches=True)

        self.assertEqual(len(result), 1)

    def test_crosswalk_two_instruments_allow_many_to_one_matches(self):

        instrument_1 = create_instrument_from_list(["I felt fearful."])
        instrument_2 = create_instrument_from_list(
            ["Feeling afraid, as if something awful might happen", "Feeling nervous, anxious, or on edge"])
        instruments = [instrument_1, instrument_2]

        match_response = match_instruments(instruments)
        result = generate_crosswalk_table(instruments, match_response.similarity_with_polarity, 0,
                                          is_enforce_one_to_one=False)

        self.assertEqual(2, len(result))

    def test_crosswalk_two_instruments_enforce_one_to_one_matches(self):

        instrument_1 = create_instrument_from_list(["I felt fearful."])
        instrument_2 = create_instrument_from_list(
            ["Feeling afraid, as if something awful might happen", "Feeling nervous, anxious, or on edge"])
        instruments = [instrument_1, instrument_2]

        match_response = match_instruments(instruments)
        result = generate_crosswalk_table(instruments, match_response.similarity_with_polarity, 0,
                                          is_enforce_one_to_one=True)

        self.assertEqual(1, len(result))


if __name__ == '__main__':
    unittest.main()

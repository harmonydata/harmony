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
import pandas as pd
import numpy as np

sys.path.append("../src")

from harmony.matching.generate_crosswalk_table import generate_crosswalk_table
from harmony import match_instruments
from harmony.schemas.requests.text import Instrument, Question

class TestGenerateCrosswalkTable(unittest.TestCase):
    def setUp(self):
        # Sample data
        self.all_questions_dummy = [
            Question(question_no="1", question_text="potato"),
            Question(question_no="2", question_text="tomato"),
            Question(question_no="3", question_text="radish"),
        ]

        self.instruments_dummy = Instrument(questions=self.all_questions_dummy)

        self.similarity = np.array([
            [1.0, 0.7, 0.9],
            [0.7, 1.0, 0.8],
            [0.9, 0.8, 1.0]
        ])
        self.all_questions_real = [Question(question_no="1", question_text="Feeling nervous, anxious, or on edge"),
                        Question(question_no="2", question_text="Not being able to stop or control worrying")]
        self.instruments = Instrument(questions=self.all_questions_real)

        self.threshold = 0.6


    def test_generate_crosswalk_table_dummy_data(self):
        result = generate_crosswalk_table(self.instruments_dummy.questions, self.similarity, self.threshold)

        expected_matches = [
            {"pair_name": "0_1", "question1_no": "1", "question1_text": "potato",
             "question2_no": "2", "question2_text": "tomato", "match_score": 0.7},
            {"pair_name": "0_2", "question1_no": "1", "question1_text": "potato",
             "question2_no": "3", "question2_text": "radish", "match_score": 0.9},
            {"pair_name": "1_2", "question1_no": "2", "question1_text": "tomato",
             "question2_no": "3", "question2_text": "radish", "match_score": 0.8},
        ]

        for _, row in pd.DataFrame(expected_matches).iterrows():
            self.assertTrue(any(row.equals(result_row) for _, result_row in result.iterrows()))

        self.assertEqual(len(result), len(expected_matches))

    def test_generate_crosswalk_table_empty(self):
        empty_similarity = np.eye(3)  # Identity matrix, no matches above threshold
        result = generate_crosswalk_table(self.all_questions_dummy, empty_similarity, self.threshold)
        self.assertTrue(result.empty)

    def test_generate_crosswalk_table_real(self):
        all_questions, similarity_with_polarity, _, _ = match_instruments([self.instruments])
        result = generate_crosswalk_table(all_questions, similarity_with_polarity, self.threshold)
        expected_matches = []

        for _, row in pd.DataFrame(expected_matches).iterrows():
            self.assertTrue(any(row.equals(result_row) for _, result_row in result.iterrows()))

        self.assertEqual(len(result), len(expected_matches))

        lower_threshold = 0.5
        result = generate_crosswalk_table(all_questions, similarity_with_polarity, lower_threshold)

        self.assertEqual(len(result), 1)


if __name__ == '__main__':
    unittest.main()

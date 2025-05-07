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

import sys
import unittest

sys.path.append("../src")

from harmony import match_instruments, create_instrument_from_list, find_clusters_deterministic
from harmony.schemas.requests.text import Instrument, Question
import numpy as np


if __name__ == '__main__':
    unittest.main()


class TestDeterministicClustering(unittest.TestCase):

    def test_two_questions_one_cluster(self):
        questions = create_instrument_from_list(
            ["Feeling nervous, anxious, or on edge", "Not being able to stop or control worrying"]).questions
        item_to_item_similarity_matrix = np.eye(2) / 2 + np.ones((2, 2)) / 2
        clusters = find_clusters_deterministic(questions, item_to_item_similarity_matrix)
        self.assertEqual(1, len(clusters))

    def test_three_questions_one_cluster(self):
        questions = create_instrument_from_list(
            ["Feeling nervous, anxious, or on edge", "Not being able to stop or control worrying", "Worrying too much about different things"]).questions
        item_to_item_similarity_matrix = np.eye(3) / 2 + np.ones((3, 3)) / 2
        clusters = find_clusters_deterministic(questions, item_to_item_similarity_matrix)
        self.assertEqual(1, len(clusters))

if __name__ == '__main__':
    unittest.main()

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

import numpy as np

sys.path.append("../src")

from harmony.matching.affinity_propagation_clustering import cluster_questions_affinity_propagation
from harmony.schemas.requests.text import Question


class TestAffinityPropagationClustering(unittest.TestCase):
    def setUp(self):
        self.questions = [
            Question(question_text="What is the capital of France?"),
            Question(question_text="What is the capital of Germany?"),
            Question(question_text="What is the capital of Spain?"),
            Question(question_text="What is the capital of Italy?")
        ]

    def test_1_cluster(self):
        clusters = cluster_questions_affinity_propagation(
            self.questions,
            item_to_item_similarity_matrix=np.array([
                [1., 1., 1., 1.],
                [1., 1., 1., 1.],
                [1., 1., 1., 1.],
                [1., 1., 1., 1.]
            ]))
        self.assertEqual(len(clusters), 1)

    def test_3_clusters(self):
        clusters = cluster_questions_affinity_propagation(
            self.questions,
            item_to_item_similarity_matrix=np.array([
                [1., 1., 1., 0.],
                [1., 1., 1., 0.],
                [1., 1., 1., 0.],
                [0., 0., 0., 1.]
            ]))
        self.assertEqual(len(clusters), 3)

    def test_cluster_identity(self):
        clusters = cluster_questions_affinity_propagation(
            self.questions,
            item_to_item_similarity_matrix=np.eye(4))
        self.assertEqual(len(clusters), 1)


if __name__ == '__main__':
    unittest.main()

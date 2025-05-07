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
from harmony.matching.cluster import cluster_questions, perform_kmeans
from harmony.schemas.requests.text import Question

sys.path.append("../src")


class TestCluster(unittest.TestCase):
    """Test class for the cluster.py module."""

    def setUp(self):
        self.all_questions_real = [Question(question_no="1",
                                            question_text="Feeling nervous, anxious, or on edge"),
                                   Question(question_no="2",
                                            question_text="Not being able to stop or control "
                                                          "worrying"),
                                   Question(question_no="3",
                                            question_text="Little interest or pleasure in doing "
                                                          "things"),
                                   Question(question_no="4", question_text="Feeling down, "
                                                                           "depressed or hopeless"),
                                   Question(question_no="5",
                                            question_text="Trouble falling/staying asleep, "
                                                          "sleeping too much"), ]

    def test_cluster(self):
        """Test the entire cluster module."""
        clusters_out, score_out = cluster_questions(self.all_questions_real, 2, False)
        assert len(clusters_out) == 5
        assert score_out

    @unittest.mock.patch("harmony.matching.cluster.KMeans")
    def test_perform_kmeans(self, mock_kmeans: unittest.mock.MagicMock):
        """Test the perform_kmeans function in the cluster module."""
        mock_kmeans_instance = unittest.mock.Mock()
        mock_kmeans.return_value = mock_kmeans_instance
        mock_kmeans_instance.fit_predict.return_value = np.array([0, 1, 0, 2, 1])
        test_embeddings = np.array([[1, 2], [3, 4], [1, 3], [7, 8], [4, 5]])

        result = perform_kmeans(test_embeddings, num_clusters=3)

        mock_kmeans.assert_called_once_with(n_clusters=3)
        mock_kmeans_instance.fit_predict.assert_called_once_with(test_embeddings)
        np.testing.assert_array_equal(result, np.array([0, 1, 0, 2, 1]))


if __name__ == '__main__':
    unittest.main()

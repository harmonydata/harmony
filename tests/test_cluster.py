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

from harmony.matching.cluster import (
    cluster_questions,
    perform_kmeans,
    visualize_clusters,
    kmeans_cluster_questions,
    deterministic_cluster_questions,
)
from harmony.schemas.requests.text import Question
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

sys.path.append("../src")


class TestCluster(unittest.TestCase):
    """Test class for the cluster.py module."""

    def setUp(self):
        self.all_questions_real = [
            Question(
                question_no="1", question_text="Feeling nervous, anxious, or on edge"
            ),
            Question(
                question_no="2",
                question_text="Not being able to stop or control worrying",
            ),
            Question(
                question_no="3",
                question_text="Little interest or pleasure in doing things",
            ),
            Question(
                question_no="4", question_text="Feeling down, depressed or hopeless"
            ),
            Question(
                question_no="5",
                question_text="Trouble falling/staying asleep, sleeping too much",
            ),
        ]

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

    @unittest.mock.patch("matplotlib.pyplot")
    @unittest.mock.patch("harmony.matching.cluster.PCA")
    def test_visualize_clusters(
        self, mock_pca: unittest.mock.MagicMock, mock_plt: unittest.mock.MagicMock
    ):
        """Test the visualization function for clustering."""
        mock_pca_instance = unittest.mock.Mock()
        mock_pca.return_value = mock_pca_instance
        test_embeddings = np.array([[1, 2], [3, 4], [1, 3], [7, 8], [4, 5]])
        test_labels = np.array([0, 1, 0, 2, 1])
        mock_reduced_embeddings = np.array(
            [[0.1, 0.2], [0.3, 0.4], [0.1, 0.3], [0.7, 0.8], [0.4, 0.5]]
        )
        mock_pca_instance.fit_transform.return_value = mock_reduced_embeddings

        visualize_clusters(test_embeddings, test_labels)

        mock_pca.assert_called_once()
        mock_pca_instance.fit_transform.assert_called_once_with(test_embeddings)
        mock_plt.scatter.assert_called_once()
        mock_plt.colorbar.assert_called_once()
        mock_plt.title.assert_called_once_with("Question Clusters")
        assert mock_plt.annotate.call_count == len(test_embeddings)
        mock_plt.show.assert_called_once()

    @unittest.mock.patch("harmony.matching.cluster.silhouette_score")
    @unittest.mock.patch("harmony.matching.cluster.visualize_clusters")
    @unittest.mock.patch("harmony.matching.cluster.perform_kmeans")
    def test_kmeans_cluster_questions(self, mock_perform_kmeans, mock_visualize, mock_silhouette):
        """Test the kmeans clustering function with multiple clusters."""
        # Setup test data
        test_embeddings = np.array([[1,2], [3,4], [1,3], [7,8], [4,5]])
        test_questions = [
            Question(question_no="1", question_text="First question"),
            Question(question_no="2", question_text="Second question"),
            Question(question_no="3", question_text="Third question"),
            Question(question_no="4", question_text="Fourth question"),
            Question(question_no="5", question_text="Fifth question"),
        ]
        test_questions_list = [q.question_text for q in test_questions]
        
        # Mock return values
        mock_perform_kmeans.return_value = np.array([0, 1, 0, 2, 1])
        mock_silhouette.return_value = 0.75
        
        # Test with visualization enabled
        df, score = kmeans_cluster_questions(
            test_embeddings,
            test_questions,
            test_questions_list,
            num_clusters=3,
            is_show_graph=True
        )
        
        # Verify kmeans was called correctly
        mock_perform_kmeans.assert_called_once_with(test_embeddings, 3)
        
        # Verify silhouette score was calculated
        mock_silhouette.assert_called_once_with(test_embeddings, mock_perform_kmeans.return_value)
        
        # Verify visualization was called
        mock_visualize.assert_called_once_with(test_embeddings, mock_perform_kmeans.return_value)
        
        # Check DataFrame structure and content
        self.assertEqual(len(df), 5)
        self.assertTrue(all(col in df.columns for col in ['question_text', 'cluster_number']))
        self.assertTrue(all(q in df['question_text'].values for q in test_questions_list))
        np.testing.assert_array_equal(df['cluster_number'].values, [0, 1, 0, 2, 1])
        
        # Check silhouette score
        self.assertEqual(score, 0.75)

    @unittest.mock.patch("harmony.matching.cluster.silhouette_score")
    @unittest.mock.patch("harmony.matching.cluster.visualize_clusters")
    @unittest.mock.patch("harmony.matching.cluster.perform_kmeans")
    def test_kmeans_cluster_questions_single_cluster(self, mock_perform_kmeans, mock_visualize, mock_silhouette):
        """Test the kmeans clustering function with a single cluster."""
        # Setup test data
        test_embeddings = np.array([[1,2], [3,4], [1,3]])
        test_questions = [
            Question(question_no="1", question_text="First question"),
            Question(question_no="2", question_text="Second question"),
            Question(question_no="3", question_text="Third question"),
        ]
        test_questions_list = [q.question_text for q in test_questions]
        
        # Mock return values
        mock_perform_kmeans.return_value = np.array([0, 0, 0])
        
        # Test with single cluster and visualization disabled
        df, score = kmeans_cluster_questions(
            test_embeddings,
            test_questions,
            test_questions_list,
            num_clusters=1,
            is_show_graph=False
        )
        
        # Verify kmeans was called correctly
        mock_perform_kmeans.assert_called_once_with(test_embeddings, 1)
        
        # Verify silhouette score wasn't calculated
        mock_silhouette.assert_not_called()
        
        # Verify visualization wasn't called
        mock_visualize.assert_not_called()
        
        # Check DataFrame structure and content
        self.assertEqual(len(df), 3)
        self.assertTrue(all(col in df.columns for col in ['question_text', 'cluster_number']))
        self.assertTrue(all(q in df['question_text'].values for q in test_questions_list))
        np.testing.assert_array_equal(df['cluster_number'].values, [0, 0, 0])
        
        # Check silhouette score is None for single cluster
        self.assertIsNone(score)

    def test_kmeans_cluster_questions_input_validation(self):
        """Test input validation for the kmeans clustering function."""
        # Test with mismatched lengths
        test_embeddings = np.array([[1,2], [3,4]])  # 2 embeddings
        test_questions = [
            Question(question_no="1", question_text="First question"),
            Question(question_no="2", question_text="Second question"),
            Question(question_no="3", question_text="Third question"),  # 3 questions
        ]
        test_questions_list = [q.question_text for q in test_questions]
        
        with self.assertRaises(ValueError):
            kmeans_cluster_questions(
                test_embeddings,
                test_questions,
                test_questions_list,
                num_clusters=2,
                is_show_graph=False
            )

    @unittest.mock.patch("harmony.matching.cluster.cosine_similarity")
    @unittest.mock.patch("harmony.matching.cluster.find_clusters_deterministic")
    def test_deterministic_cluster_questions(self, mock_find_clusters, mock_cosine_similarity):
        """Test the deterministic clustering function with multiple clusters."""
        # Setup test data
        test_embeddings = np.array([[1,2], [3,4], [1,3], [7,8], [4,5]])
        test_questions = [
            Question(question_no="1", question_text="First question"),
            Question(question_no="2", question_text="Second question"),
            Question(question_no="3", question_text="Third question"),
            Question(question_no="4", question_text="Fourth question"),
            Question(question_no="5", question_text="Fifth question"),
        ]
        test_questions_list = [q.question_text for q in test_questions]
        
        # Mock cosine similarity matrix
        mock_similarity_matrix = np.array([
            [1.0, 0.2, 0.8, 0.1, 0.3],
            [0.2, 1.0, 0.3, 0.2, 0.7],
            [0.8, 0.3, 1.0, 0.2, 0.4],
            [0.1, 0.2, 0.2, 1.0, 0.3],
            [0.3, 0.7, 0.4, 0.3, 1.0]
        ])
        mock_cosine_similarity.return_value = mock_similarity_matrix
        
        # Create mock clusters
        class MockCluster:
            def __init__(self, cluster_id, item_ids):
                self.cluster_id = cluster_id
                self.item_ids = item_ids
        
        mock_clusters = [
            MockCluster(0, {0, 2}),      # Questions 1 and 3
            MockCluster(1, {1, 4}),      # Questions 2 and 5
            MockCluster(2, {3}),         # Question 4
        ]
        mock_find_clusters.return_value = mock_clusters
        
        # Call function
        df, score = deterministic_cluster_questions(
            test_embeddings,
            test_questions,
            test_questions_list
        )
        
        # Verify cosine similarity was called
        mock_cosine_similarity.assert_called_once_with(test_embeddings)
        
        # Verify find_clusters_deterministic was called
        mock_find_clusters.assert_called_once_with(test_questions, mock_similarity_matrix)
        
        # Check DataFrame structure and content
        self.assertEqual(len(df), 5)
        self.assertTrue(all(col in df.columns for col in ['question_text', 'cluster_number']))
        self.assertTrue(all(q in df['question_text'].values for q in test_questions_list))
        
        # Verify cluster assignments
        expected_clusters = [0, 1, 0, 2, 1]  # Based on our mock clusters
        np.testing.assert_array_equal(df['cluster_number'].values, expected_clusters)
        
        # Verify silhouette score is None (as specified in the function)
        self.assertIsNone(score)

    def test_deterministic_cluster_questions_empty(self):
        """Test the deterministic clustering function with empty input."""
        test_embeddings = np.array([])
        test_questions = []
        test_questions_list = []
        
        df, score = deterministic_cluster_questions(
            test_embeddings,
            test_questions,
            test_questions_list
        )
        
        # Check that we get an empty DataFrame with the correct columns
        self.assertEqual(len(df), 0)
        self.assertTrue(all(col in df.columns for col in ['question_text', 'cluster_number']))
        self.assertIsNone(score)

    def test_deterministic_cluster_questions_single_item(self):
        """Test the deterministic clustering function with a single item."""
        test_embeddings = np.array([[1, 2]])
        test_questions = [
            Question(question_no="1", question_text="Single question"),
        ]
        test_questions_list = [q.question_text for q in test_questions]
        
        df, score = deterministic_cluster_questions(
            test_embeddings,
            test_questions,
            test_questions_list
        )
        
        # Check DataFrame structure and content
        self.assertEqual(len(df), 1)
        self.assertTrue(all(col in df.columns for col in ['question_text', 'cluster_number']))
        self.assertEqual(df['question_text'].iloc[0], "Single question")
        self.assertIsNone(score)

    def test_deterministic_cluster_questions_input_validation(self):
        """Test input validation for the deterministic clustering function."""
        # Test with mismatched lengths
        test_embeddings = np.array([[1,2], [3,4]])  # 2 embeddings
        test_questions = [
            Question(question_no="1", question_text="First question"),
            Question(question_no="2", question_text="Second question"),
            Question(question_no="3", question_text="Third question"),  # 3 questions
        ]
        test_questions_list = [q.question_text for q in test_questions]
        
        with self.assertRaises(ValueError):
            deterministic_cluster_questions(
                test_embeddings,
                test_questions,
                test_questions_list
            )

if __name__ == "__main__":
    unittest.main()

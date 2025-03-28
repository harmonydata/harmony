import sys
import unittest

from sklearn.datasets import make_blobs

sys.path.append("../src")

from harmony.matching.hdbscan_clustering import cluster_questions_hdbscan_from_embeddings
from harmony import create_instrument_from_list


class TestHDBSCANClustering(unittest.TestCase):
    def test_two_questions_one_cluster(self):
        embedding_dim = 384

        questions = create_instrument_from_list(
            ["Feeling nervous, anxious, or on edge", "Not being able to stop or control worrying"]).questions

        # Create fake dataset of embeddings with 2 samples, and 1 cluster
        question_embeddings, _ = make_blobs(n_samples=2, centers=1, random_state=42, n_features=embedding_dim)

        clusters = cluster_questions_hdbscan_from_embeddings(questions, question_embeddings)

        self.assertEqual(1, len(clusters))

    def test_three_questions_one_cluster(self):
        embedding_dim = 384

        questions = create_instrument_from_list(
            ["Feeling nervous, anxious, or on edge", "Not being able to stop or control worrying",
             "Worrying too much about different things"]).questions

        # Create fake dataset of embeddings with 3 samples, and 1 cluster
        question_embeddings, _ = make_blobs(n_samples=3, centers=1, random_state=42, n_features=embedding_dim)

        clusters = cluster_questions_hdbscan_from_embeddings(questions, question_embeddings)

        self.assertEqual(1, len(clusters))


if __name__ == '__main__':
    unittest.main()

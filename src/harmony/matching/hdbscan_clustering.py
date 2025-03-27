import sys
from typing import List


from sklearn.cluster import HDBSCAN
import numpy as np

from harmony.matching.generate_cluster_topics import generate_cluster_topics
from harmony.schemas.requests.text import Question
from harmony.schemas.responses.text import HarmonyCluster

def perform_hdbscan(embeddings_in: np.ndarray, min_cluster_size=2):
    """
       Cluster data using HDBScan.

       See an explanation of HDBScan here:
        - https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html

       Parameters
       ----------
       embeddings_in : np.ndarray
           Text embeddings.
       min_cluster_size : int
           The minimum amount of points in a cluster.
           Lower values can include noise in clusters.
           Defaulted at 2.
       Returns
       -------
       HDBSCAN : hdbscan.HDBSCAN
           A fitted HDBSCAN model.
       """
    hdbscan = HDBSCAN(min_cluster_size=min_cluster_size)
    hdbscan_model = hdbscan.fit(embeddings_in)

    return hdbscan_model

def cluster_questions_hdbscan_from_embeddings(questions: List[Question], embedding_matrix, min_cluster_size):
    """
    Cluster questions with HDBSCAN

    Parameters
    ----------
    questions : List[Question]
        The set of questions to cluster.

    item_to_item_similarity_matrix : np.ndarray
        The cosine similarity matrix for the questions.

    min_cluster_size : int
        Minimum similarity score required to cluster two items together.

    Returns
    -------
    List[HarmonyCluster]
        A list of HarmonyCluster objects representing the clusters.
    """

    hdbscan = perform_hdbscan(embedding_matrix, min_cluster_size)
    cluster_labels = hdbscan.labels_
    clusters = np.array([1, 2, 3, 2, 1, 3])  # Cluster assignments
    probabilities = np.array(hdbscan.probabilities_)  # Probability/confidence for each datapoint

    # Find the highest probability index for each cluster. For HDBSCAN, these are the "centroids".
    cluster_centroids = {
        cluster: np.argmax(probabilities[clusters == cluster])
        for cluster in cluster_labels
    }

    centroid_questions = [questions[i] for i in cluster_centroids.values()]

    for centroid in cluster_centroids:
        # Create HarmonyCluster object
        # Confused about what to put here currently

    return clusters_to_return

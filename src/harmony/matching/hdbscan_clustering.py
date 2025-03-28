from typing import List

import numpy as np
from sklearn.cluster import HDBSCAN

from harmony.matching.generate_cluster_topics import generate_cluster_topics
from harmony.schemas.requests.text import Question
from harmony.schemas.responses.text import HarmonyCluster


def perform_hdbscan(embeddings_in: np.ndarray, min_cluster_size=5):
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
           Defaults to 5.
       Returns
       -------
       HDBSCAN : hdbscan.HDBSCAN
           A fitted HDBSCAN model.
       """

    # Ensure min_cluster_size is not greater than the dataset length
    min_cluster_size = min([embeddings_in.shape[0], min_cluster_size])

    hdbscan = HDBSCAN(min_cluster_size=min_cluster_size)
    hdbscan_model = hdbscan.fit(embeddings_in)

    return hdbscan_model


def cluster_questions_hdbscan_from_embeddings(questions: List[Question], embedding_matrix: np.ndarray,
                                              min_cluster_size=5):
    """
    Cluster questions with HDBSCAN

    Parameters
    ----------
    questions : List[Question]
        The set of questions to cluster.

    embedding_matrix : np.ndarray
        Array of text embedding of each question.

    min_cluster_size : int
        The minimum amount of points in a cluster.
        Defaults to 5.

    Returns
    -------
    List[HarmonyCluster]
        A list of HarmonyCluster objects representing the clusters.
    """

    hdbscan = perform_hdbscan(embedding_matrix, min_cluster_size)
    cluster_labels = hdbscan.labels_
    probabilities = np.array(hdbscan.probabilities_)  # Probability/confidence for each datapoint.

    # Create dict with a key for each cluster, with each key storing a list of datapoint's
    # index in the labels list, its corresponding probability, and Question
    cluster_indices = {}
    for i, val in enumerate(cluster_labels):
        if val not in cluster_indices:
            cluster_indices[val] = []
        cluster_indices[val].append((i, probabilities[i], questions[i]))

    # Find the index of the highest probability datapoint for each cluster. For HDBSCAN, these are the "centroids".
    cluster_centroids = {
        cluster: max(cluster_indices[cluster], key=lambda x: x[1])[0]
        for cluster in cluster_indices.keys()
    }

    # Build HarmonyClusters, extract relevant data
    clusters_to_return = []
    for cluster_id, cluster_data in cluster_indices.items():
        centroid_id = cluster_centroids[cluster_id]

        # Retrieve centroid question
        centroid_question = None
        for ind, _, question in cluster_data:
            if ind == centroid_id:
                centroid_question = question
                break

        cluster = HarmonyCluster(
            cluster_id=cluster_id,
            centroid_id=centroid_id,
            centroid=centroid_question,
            item_ids=[ind for ind, _, _ in cluster_data],
            items=[question for _, _, question in cluster_data],
            text_description=centroid_question.question_text,
            keywords=[],
        )

        clusters_to_return.append(cluster)

        # generate cluster topics
        cluster_topics = generate_cluster_topics(clusters_to_return, top_k_topics=5)
        for cluster, topics in zip(clusters_to_return, cluster_topics):
            cluster.keywords = topics

    return clusters_to_return

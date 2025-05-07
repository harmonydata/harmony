import sys
from typing import List

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from harmony.matching.generate_cluster_topics import generate_cluster_topics
from harmony.schemas.requests.text import Question
from harmony.schemas.responses.text import HarmonyCluster

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def perform_kmeans(embeddings_in, num_clusters=5):
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans_labels = kmeans.fit_predict(embeddings_in)
    return kmeans_labels



def cluster_questions_kmeans_from_embeddings(questions: List[Question], embedding_matrix, num_clusters):
    kmeans_labels = perform_kmeans(embedding_matrix, num_clusters)
    # TODO: find out what this was for and do we need it?
    # sil_score = silhouette_score(embedding_matrix, kmeans_labels) if num_clusters > 1 else None

    clusters_to_return = []

    num_clusters_output = max(kmeans_labels) + 1

    cluster_idx_to_question_idxs = {}
    for question_idx, question in enumerate(questions):
        cluster_idx = kmeans_labels[question_idx]
        if cluster_idx not in cluster_idx_to_question_idxs:
            cluster_idx_to_question_idxs[cluster_idx] = []
        cluster_idx_to_question_idxs[cluster_idx].append(question_idx)



    for cluster_id, question_indices_in_cluster in cluster_idx_to_question_idxs.items():
        questions_in_cluster = [questions[i] for i in question_indices_in_cluster]
        # TODO: fix this - get better values for best_question_idx and text_description - need to identify centroid
        best_question_idx = question_indices_in_cluster[0]
        text_description = questions_in_cluster[0].question_text
        cluster = HarmonyCluster(
            cluster_id=cluster_id,
            centroid_id=best_question_idx,
            centroid=questions[best_question_idx],
            items=questions_in_cluster,
            item_ids=question_indices_in_cluster,
            text_description=text_description,
            keywords=[],
        )
        clusters_to_return.append(cluster)


    cluster_topics = generate_cluster_topics(clusters_to_return, top_k_topics=5)
    for cluster, topics in zip(clusters_to_return, cluster_topics):
        cluster.keywords = topics

    return clusters_to_return
import sys
from typing import List

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from harmony.matching.default_matcher import convert_texts_to_vector
from harmony.schemas.requests.text import Question


def perform_kmeans(embeddings_in, num_clusters=5):
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans_labels = kmeans.fit_predict(embeddings_in)
    return kmeans_labels


def visualize_clusters(embeddings_in, kmeans_labels):
    try:
        import matplotlib.pyplot as plt
        pca = PCA(n_components=2)
        reduced_embeddings = pca.fit_transform(embeddings_in)
        plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=kmeans_labels, cmap='viridis', s=50)
        plt.colorbar()
        plt.title("Question Clusters")

        for i, point in enumerate(reduced_embeddings):
            plt.annotate(
                str(i),  # Label each point with its question number
                (point[0], point[1]),  # Coordinates from reduced_embeddings
                fontsize=8,
                ha="center"
            )

        plt.show()
    except ImportError as e:
        print(
            "Matplotlib is not installed. Please install it using:\n"
            "pip install matplotlib==3.7.0"
        )
        sys.exit(1)


def cluster_questions(questions: List[Question], num_clusters: int, is_show_graph: bool):
    questions_list = [question.question_text for question in questions]
    embedding_matrix = convert_texts_to_vector(questions_list)
    kmeans_labels = perform_kmeans(embedding_matrix, num_clusters)
    df = pd.DataFrame({
        "question_text": questions_list,
        "cluster_number": kmeans_labels
    })

    # silhouette score requires at least 2 clusters
    if num_clusters > 1:
        sil_score = silhouette_score(embedding_matrix, kmeans_labels)
    else:
        sil_score = None

    if is_show_graph:
        visualize_clusters(embedding_matrix, kmeans_labels)

    return df, sil_score

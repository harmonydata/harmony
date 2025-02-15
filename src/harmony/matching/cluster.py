import sys
from typing import Callable, Protocol

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from harmony.matching.default_matcher import convert_texts_to_vector
from harmony.schemas.requests.text import Question
from harmony.schemas.enums.cluster_algorithms import ClusterAlgorithm

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from harmony.matching.deterministic_clustering import find_clusters_deterministic

REDUCED_EMBEDDINGS_DIMENSION = 2


class ClusteringFunction(Protocol):
    def __call__(
        self,
        embedding_matrix: np.ndarray,
        questions: list[Question],
        questions_list: list[str],
        num_clusters: int = 0,
        is_show_graph: bool = False,
    ) -> tuple[pd.DataFrame, float | None]: ...


def perform_kmeans(embeddings_in: np.ndarray, num_clusters: int = 5) -> np.ndarray:
    """Perform kmeans on the embeddings.

    Parameters
    ----------
    embeddings_in: np.ndarray
        Array of the embeddings.
    num_clusters: int, optional
        Number of clusters to perform the k-means on. Defaults to 5.

    Returns
    -------
    kmeans_labels: np.ndarray
        Cluster labels
    """

    kmeans = KMeans(n_clusters=num_clusters)
    kmeans_labels = kmeans.fit_predict(embeddings_in)
    return kmeans_labels


def visualize_clusters(embeddings_in: np.ndarray, kmeans_labels: np.ndarray) -> None:
    """Visualize the clusters from the kmeans algorithm.

    Uses principal components analysis to map the embeddings dimensions to
    REDUCED_EMBEDDINGS_DIMENSION and then displays them with matplotlib.

    Parameters
    ----------
    embeddings_in: np.ndarray
        Array of the embeddings
    kmeans_labels: np.ndarray
        Cluster labels

    Raises
    ----------
    ImportError if Matplotlib is not installed
    """

    try:
        import matplotlib.pyplot as plt

        pca = PCA(n_components=REDUCED_EMBEDDINGS_DIMENSION)
        reduced_embeddings = pca.fit_transform(embeddings_in)
        plt.scatter(
            reduced_embeddings[:, 0],
            reduced_embeddings[:, 1],
            c=kmeans_labels,
            cmap="viridis",
            s=50,
        )
        plt.colorbar()
        plt.title("Question Clusters")

        for i, point in enumerate(reduced_embeddings):
            plt.annotate(
                str(i),  # Label each point with its question number
                (point[0], point[1]),  # Coordinates from reduced_embeddings
                fontsize=8,
                ha="center",
            )

        plt.show()
    except ImportError:
        print(
            "Matplotlib is not installed. Please install it using:\n"
            "pip install matplotlib==3.7.0"
        )
        sys.exit(1)


def kmeans_cluster_questions(
    embedding_matrix: np.ndarray,
    questions: list[Question],
    questions_list: list[str],
    num_clusters: int,
    is_show_graph: bool,
) -> tuple[pd.DataFrame, float | None]:
    kmeans_labels = perform_kmeans(embedding_matrix, num_clusters)
    sil_score = (
        float(silhouette_score(embedding_matrix, kmeans_labels))
        if num_clusters > 1
        else None
    )

    if is_show_graph:
        visualize_clusters(embedding_matrix, kmeans_labels)

    df = pd.DataFrame(
        {"question_text": questions_list, "cluster_number": kmeans_labels}
    )
    return df, sil_score


def deterministic_cluster_questions(
    embedding_matrix: np.ndarray,
    questions: list[Question],
    questions_list: list[str],
    num_clusters: int = 0,
    is_show_graph: bool = False,
) -> tuple[pd.DataFrame, float | None]:
    similarity_matrix = cosine_similarity(embedding_matrix)

    clusters = find_clusters_deterministic(questions, similarity_matrix)

    cluster_labels = []
    for question_idx in range(len(questions)):
        for cluster in clusters:
            if question_idx in cluster.item_ids:
                cluster_labels.append(cluster.cluster_id)
                break

    sil_score = None
    df = pd.DataFrame(
        {"question_text": questions_list, "cluster_number": cluster_labels}
    )
    return df, sil_score


def get_cluster_questions_algorithm(
    algorithm: ClusterAlgorithm,
) -> Callable[
    [np.ndarray, list[Question], list[str], int, bool],
    tuple[pd.DataFrame, float | None],
]:
    if algorithm == ClusterAlgorithm.KMEANS:
        return kmeans_cluster_questions
    return deterministic_cluster_questions


def cluster_questions(
    questions: list[Question],
    num_clusters: int,
    is_show_graph: bool,
    algorithm: ClusterAlgorithm = ClusterAlgorithm.KMEANS,
) -> tuple[pd.DataFrame, float | None]:
    """
    Cluster questions using the specified algorithm.

    Parameters
    ----------
    questions : list[Question]
        A list of Question objects to cluster.
    num_clusters : int
        The number of clusters to create (only applicable for kmeans).
    is_show_graph : bool
        Whether to visualize the clusters.
    algorithm : str
        The clustering algorithm to use. Options are "kmeans" (default) or "deterministic".

    Returns
    -------
    df : pd.DataFrame
        A DataFrame with the questions and their assigned cluster numbers.
    sil_score : float or None
        The silhouette score for the clustering (None if the algorithm does not calculate it).
    """
    questions_list = [question.question_text for question in questions]
    embedding_matrix = convert_texts_to_vector(questions_list)
    cluster_questions_algorithm = get_cluster_questions_algorithm(algorithm)
    df, sil_score = cluster_questions_algorithm(
        embedding_matrix, questions, questions_list, num_clusters, is_show_graph
    )

    return df, sil_score

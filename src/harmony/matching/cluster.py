import sys
from typing import List

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from harmony.matching.default_matcher import convert_texts_to_vector
from harmony.schemas.requests.text import Question

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from harmony.matching.deterministic_clustering import find_clusters_deterministic

from sentence_transformers import SentenceTransformer


# Initialize the semantic embedding model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


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
    except ImportError:
        print(
            "Matplotlib is not installed. Please install it using:\n"
            "pip install matplotlib"
        )
        sys.exit(1)


def calculate_response_similarity(options1: List[str], options2: List[str]) -> float:
    """
    Calculate the semantic similarity score between two lists of response options.

    Parameters
    ----------
    options1 : List[str]
        The first set of response options.
    options2 : List[str]
        The second set of response options.

    Returns
    -------
    float
        A similarity score between 0 and 1.
    """
    if not options1 or not options2:
        return 0.0  # No similarity if one of the options is empty.

    # 轉換選項為語義嵌入向量
    embeddings1 = model.encode(options1)
    embeddings2 = model.encode(options2)

    # 計算語義相似性矩陣
    similarity_matrix = cosine_similarity(embeddings1, embeddings2)

    # 對每個選項找出最相似的匹配並計算平均相似度
    max_similarities = similarity_matrix.max(axis=1)
    return max_similarities.mean()


def cluster_questions(questions: List[Question], num_clusters: int, is_show_graph: bool, 
                      algorithm: str = "kmeans", use_response_similarity: bool = False,
                      question_similarity_weight: float = 0.5, response_similarity_weight: float = 0.5):
    """
    Cluster questions using the specified algorithm and optionally include response options similarity.

    Parameters
    ----------
    questions : List[Question]
        A list of Question objects to cluster.
    num_clusters : int
        The number of clusters to create (only applicable for kmeans).
    is_show_graph : bool
        Whether to visualize the clusters.
    algorithm : str
        The clustering algorithm to use. Options are "kmeans" (default) or "deterministic".
    use_response_similarity : bool
        Whether to include response options similarity in the final similarity score.
    question_similarity_weight : float
        Weight for the question similarity score (default is 0.5).
    response_similarity_weight : float
        Weight for the response options similarity score (default is 0.5).

    Returns
    -------
    df : pd.DataFrame
        A DataFrame with the questions and their assigned cluster numbers.
    sil_score : float or None
        The silhouette score for the clustering (None if the algorithm does not calculate it).
    final_score : float or None
        The combined similarity score of questions and response options (if enabled).
    """
    # Validate weights
    if not (0 <= question_similarity_weight <= 1 and 0 <= response_similarity_weight <= 1):
        raise ValueError("Weights must be between 0 and 1.")
    if abs(question_similarity_weight + response_similarity_weight - 1.0) > 1e-6:
        raise ValueError("The sum of question_similarity_weight and response_similarity_weight must equal 1.")

    # Initialize variables
    final_score = None
    similarity_matrix = None

    questions_list = [question.question_text for question in questions]
    embedding_matrix = convert_texts_to_vector(questions_list)

    # Perform clustering based on the selected algorithm
    if algorithm == "kmeans":
        kmeans_labels = perform_kmeans(embedding_matrix, num_clusters)
        sil_score = silhouette_score(embedding_matrix, kmeans_labels) if num_clusters > 1 else None

        if is_show_graph:
            visualize_clusters(embedding_matrix, kmeans_labels)

        df = pd.DataFrame({
            "question_text": questions_list,
            "cluster_number": kmeans_labels
        })

    elif algorithm == "deterministic":
        similarity_matrix = cosine_similarity(embedding_matrix)

        clusters = find_clusters_deterministic(questions, similarity_matrix)

        cluster_labels = []
        for question_idx in range(len(questions)):
            for cluster in clusters:
                if question_idx in cluster.item_ids:
                    cluster_labels.append(cluster.cluster_id)
                    break

        sil_score = None
        df = pd.DataFrame({
            "question_text": questions_list,
            "cluster_number": cluster_labels
        })

    else:
        raise ValueError(f"Unsupported algorithm '{algorithm}'. Please use 'kmeans' or 'deterministic'.")

    # Calculate response options similarity if enabled
    if use_response_similarity:
        response_similarities = []
        for i, question1 in enumerate(questions):
            for j, question2 in enumerate(questions):
                if i < j:  # Avoid recalculating for symmetrical pairs
                    response_similarity = calculate_response_similarity(question1.options, question2.options)
                    response_similarities.append(response_similarity)

        # Combine question similarity and response similarity
        question_similarity_score = np.mean(similarity_matrix) if similarity_matrix is not None else 0.0
        response_similarity_score = np.mean(response_similarities) if response_similarities else 0.0

        # Use adjustable weights for final score calculation
        final_score = (question_similarity_weight * question_similarity_score +
                       response_similarity_weight * response_similarity_score)

    return df, sil_score, final_score if use_response_similarity else None

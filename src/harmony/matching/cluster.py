import os
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer

if (
    os.environ.get("HARMONY_SENTENCE_TRANSFORMER_PATH", None) is not None
    and os.environ.get("HARMONY_SENTENCE_TRANSFORMER_PATH", None) != ""
):
    sentence_transformer_path = os.environ["HARMONY_SENTENCE_TRANSFORMER_PATH"]
else:
    sentence_transformer_path = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

model = SentenceTransformer(sentence_transformer_path)

# questions_in should be a list of question strings
def get_embeddings(questions_in):
    # Generate embeddings using HuggingFace model
    embedding_result = model.encode(questions_in, show_progress_bar=True)
    questions_df = pd.DataFrame()

    # Add embeddings to df and convert the embeddings to numpy arrays
    questions_df["embedding"] = [embedding.tolist() for embedding in embedding_result]
    questions_df["embedding"] = questions_df["embedding"].apply(np.array)

    # Stack embeddings into a matrix
    matrix = np.vstack(questions_df.embedding.values)
    return matrix


def perform_kmeans(embeddings_in, num_clusters=5):
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans_labels = kmeans.fit_predict(embeddings_in)
    return kmeans_labels


def visualize_clusters(embeddings_in, kmeans_labels):
    import matplotlib.pyplot as plt
    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embeddings_in)
    plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=kmeans_labels, cmap='viridis', s=50)
    plt.colorbar()
    plt.title("Question Clusters")
    plt.show()

def cluster_questions(instrument_in, num_clusters: int, graph: bool):
    # convert instruments into a list of questions
    questions_list = []
    for question in instrument_in.questions:
        questions_list.append(question.question_text)
    embedding_matrix = get_embeddings(questions_list)
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

    if graph:
        visualize_clusters(embedding_matrix, kmeans_labels)

    return df, sil_score

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
from sentence_transformers import SentenceTransformer
from harmony.schemas.requests.text import Question
from typing import List
from sklearn.metrics.pairwise import cosine_similarity

# Initialize a Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2") 

def generate_semantic_keywords(cluster_items: List[Question], top_k: int = 5) -> List[str]:
    """
    Generate representative keywords for a cluster using Sentence Transformers embeddings.

    Parameters
    ----------
    cluster_items : List[Question]
        The list of questions in the cluster.
    top_k : int
        Number of top keywords to extract.

    Returns
    -------
    List[str]
        A list of top keywords representing the cluster.
    """
    texts = [item.question_text for item in cluster_items]
    if not texts:
        return []

    # Generate embeddings for all texts
    embeddings = model.encode(texts)

    # Compute average embedding for the cluster
    cluster_embedding = embeddings.mean(axis=0, keepdims=True)

    # Calculate cosine similarity of each text to the cluster embedding
    similarities = cosine_similarity(cluster_embedding, embeddings)[0]

    # Rank texts based on similarity and select top_k
    top_indices = similarities.argsort()[-top_k:][::-1]  # Sort in descending order
    keywords = [texts[idx] for idx in top_indices]

    return keywords
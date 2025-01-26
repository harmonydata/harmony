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
from collections import Counter
from typing import List

import numpy as np

from harmony.schemas.requests.text import Question
from harmony.schemas.responses.text import HarmonyCluster

from collections import Counter
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from harmony.schemas.requests.text import Question
from harmony.schemas.responses.text import HarmonyCluster

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


def find_clusters_deterministic(
    questions: List[Question], item_to_item_similarity_matrix: np.ndarray, threshold: float = 0.5
) -> List[HarmonyCluster]:
    """
    deterministic clustering using Sentence Transformers for cluster keywords.

    Parameters
    ----------
    questions : List[Question]
        The set of questions to cluster.
    item_to_item_similarity_matrix : np.ndarray
        The cosine similarity matrix for the questions.
    threshold : float
        Minimum similarity score required to cluster two items together.

    Returns
    -------
    List[HarmonyCluster]
        A list of HarmonyCluster objects representing the clusters.
    """
    abs_similarities = np.abs(item_to_item_similarity_matrix)

    coord_to_sim = {
        (y, x): abs_similarities[y, x]
        for y in range(abs_similarities.shape[0])
        for x in range(abs_similarities.shape[1])
    }

    total_score = Counter()
    edges = set()
    vertices = set()

    for (y, x), sim in sorted(coord_to_sim.items(), key=lambda x: x[1], reverse=True):
        if x < y and sim >= threshold:
            if x not in vertices or y not in vertices:
                edges.add((x, y))
                vertices.add(x)
                vertices.add(y)
                total_score[x] += sim
                total_score[y] += sim

    question_idx_to_group_idx = {}
    for x, y in edges:
        if x not in question_idx_to_group_idx and y not in question_idx_to_group_idx:
            group_idx = min(x, y)
            question_idx_to_group_idx[x] = group_idx
            question_idx_to_group_idx[y] = group_idx
        elif x in question_idx_to_group_idx and y not in question_idx_to_group_idx:
            group_idx = question_idx_to_group_idx[x]
            question_idx_to_group_idx[y] = group_idx
        elif y in question_idx_to_group_idx and x not in question_idx_to_group_idx:
            group_idx = question_idx_to_group_idx[y]
            question_idx_to_group_idx[x] = group_idx

    for idx in range(len(questions)):
        if idx not in question_idx_to_group_idx:
            question_idx_to_group_idx[idx] = idx

    clusters_to_return = []
    all_groups = set(question_idx_to_group_idx.values())
    for group_no, group_idx in enumerate(sorted(all_groups)):
        items = []
        item_ids = []
        candidate_scores = {}

        for question_idx in question_idx_to_group_idx:
            if question_idx_to_group_idx[question_idx] == group_idx:
                items.append(questions[question_idx])
                item_ids.append(question_idx)
                candidate_scores[question_idx] = total_score.get(question_idx, 0)

        # Determine centroid
        best_question_idx = max(candidate_scores, key=candidate_scores.get)
        text_description = questions[best_question_idx].question_text

        # Generate semantic-based keywords
        cluster_keywords = generate_semantic_keywords(items)

        # Create HarmonyCluster object
        cluster = HarmonyCluster(
            cluster_id=group_no,
            centroid_id=best_question_idx,
            centroid=questions[best_question_idx],
            items=items,
            item_ids=item_ids,
            text_description=text_description,
            keywords=cluster_keywords,
        )
        clusters_to_return.append(cluster)

    return clusters_to_return

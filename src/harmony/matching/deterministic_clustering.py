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
import numpy as np
from typing import List
from collections import Counter
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from harmony.schemas.requests.text import Question
from harmony.schemas.responses.text import HarmonyCluster

# Initialize transformer model for semantic similarity
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_semantic_keywords(cluster_items: List[Question], top_k: int = 5) -> List[str]:
    """
    Extract representative question texts for a cluster using semantic similarity.

    This function computes the mean embedding of all questions in the cluster (the "semantic centroid"),
    and selects the top_k most semantically similar questions to that centroid.

    Parameters
    ----------
    cluster_items : List[Question]
        The list of Question objects belonging to a single cluster.
    top_k : int, optional
        The number of top representative texts to return (default is 5).

    Returns
    -------
    List[str]
        A list of question texts most representative of the cluster's meaning.
    """
    texts = [item.question_text for item in cluster_items]
    if not texts:
        return []

    embeddings = model.encode(texts)
    centroid = embeddings.mean(axis=0, keepdims=True)
    similarities = cosine_similarity(centroid, embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    return [texts[i] for i in top_indices]


def find_clusters_deterministic(
    questions: List[Question],
    item_to_item_similarity_matrix: np.ndarray,
    threshold: float = 0.5
) -> List[HarmonyCluster]:
    """
    Perform deterministic clustering based on a pairwise cosine similarity matrix.

    This method builds clusters by linking questions that exceed a similarity threshold.
    It also generates semantic keywords for each cluster using top representative questions.

    Parameters
    ----------
    questions : List[Question]
        The full list of input questions to be clustered.
    item_to_item_similarity_matrix : np.ndarray
        The cosine similarity matrix between all question embeddings.
    threshold : float, optional
        Minimum similarity value to link two questions into the same cluster (default is 0.5).

    Returns
    -------
    List[HarmonyCluster]
        A list of HarmonyCluster objects, each containing the cluster's centroid,
        items, question IDs, and generated semantic keywords.
    """
    abs_sim = np.abs(item_to_item_similarity_matrix)
    coord_to_sim = {(y, x): abs_sim[y, x] for y in range(abs_sim.shape[0]) for x in range(abs_sim.shape[1])}

    edges = set()
    vertices = set()
    total_score = Counter()

    # Build edges above threshold
    for (y, x), sim in sorted(coord_to_sim.items(), key=lambda x: x[1], reverse=True):
        if x < y and sim >= threshold:
            if x not in vertices or y not in vertices:
                edges.add((x, y))
                vertices.update([x, y])
                total_score[x] += sim
                total_score[y] += sim

    question_idx_to_group_idx = {}

    # Assign group ids
    for x, y in edges:
        if x not in question_idx_to_group_idx and y not in question_idx_to_group_idx:
            group_id = min(x, y)
            question_idx_to_group_idx[x] = group_id
            question_idx_to_group_idx[y] = group_id
        elif x in question_idx_to_group_idx:
            question_idx_to_group_idx[y] = question_idx_to_group_idx[x]
        elif y in question_idx_to_group_idx:
            question_idx_to_group_idx[x] = question_idx_to_group_idx[y]

    # Assign standalone questions to own groups
    for idx in range(len(questions)):
        if idx not in question_idx_to_group_idx:
            question_idx_to_group_idx[idx] = idx

    clusters_to_return = []
    all_groups = sorted(set(question_idx_to_group_idx.values()))

    for group_no, group_id in enumerate(all_groups):
        item_ids = [i for i, g in question_idx_to_group_idx.items() if g == group_id]
        items = [questions[i] for i in item_ids]
        score_map = {i: total_score.get(i, 0) for i in item_ids}

        if not items:
            continue

        # Determine centroid index
        centroid_idx = max(score_map, key=score_map.get)

        # Use semantic keywords instead of just 1 centroid question
        keywords = generate_semantic_keywords(items)
        text_description = ", ".join(keywords)

        cluster = HarmonyCluster(
            cluster_id=group_no,
            centroid_id=centroid_idx,
            centroid=questions[centroid_idx],
            items=items,
            item_ids=item_ids,
            text_description=text_description,
            keywords=keywords
        )

        clusters_to_return.append(cluster)

    return clusters_to_return

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
from typing import List

import numpy as np
from harmony.matching.generate_cluster_topics import generate_cluster_topics
from harmony.schemas.requests.text import Question
from harmony.schemas.responses.text import HarmonyCluster
from sklearn.cluster import AffinityPropagation


def cluster_questions_affinity_propagation(
        questions: List[Question],
        item_to_item_similarity_matrix: np.ndarray
) -> List[HarmonyCluster]:
    """
    Affinity Propagation Clustering using the cosine similarity matrix.

    Parameters
    ----------
    questions : List[Question]
        The set of questions to cluster.

    item_to_item_similarity_matrix : np.ndarray
        The cosine similarity matrix for the questions.

    Returns
    -------
    List[HarmonyCluster]
        A list of HarmonyCluster objects representing the clusters.
    """

    # assert that the number of questions is greater than 0
    assert len(questions) > 0

    # assert that the similarity matrix is not empty
    assert item_to_item_similarity_matrix.size > 0

    # assert that the number of questions is equal to the number of rows in the similarity matrix
    assert len(questions) == item_to_item_similarity_matrix.shape[0]

    # assert that the number of questions is equal to the number of columns in the similarity matrix
    assert len(questions) == item_to_item_similarity_matrix.shape[1]

    # assert that the number of questions is equal to the number of rows and columns in the similarity matrix
    assert len(questions) == item_to_item_similarity_matrix.shape[0]
    assert len(questions) == item_to_item_similarity_matrix.shape[1]

    # assert that the similarity matrix is square
    assert item_to_item_similarity_matrix.shape[0] == item_to_item_similarity_matrix.shape[1]

    # assert that the similarity matrix is symmetric
    assert np.allclose(item_to_item_similarity_matrix, item_to_item_similarity_matrix.T)

    # assert that the similarity matrix is -1 <= x <= 1
    assert np.all(np.round(item_to_item_similarity_matrix, 3) >= -1.)
    assert np.all(np.round(item_to_item_similarity_matrix, 3) <= 1.)

    # assert that the similarity matrix has 1s on its diagonals
    assert np.allclose(np.diag(item_to_item_similarity_matrix), 1.)

    # ensure that the entries of the similarity matrix are floats
    if item_to_item_similarity_matrix.dtype != np.float64:
        item_to_item_similarity_matrix = item_to_item_similarity_matrix.astype(np.float64)

    affinity_propagation = AffinityPropagation(affinity='precomputed', random_state=1, max_iter=10, convergence_iter=5)
    affinity_propagation.fit(np.abs(item_to_item_similarity_matrix))

    exemplars = affinity_propagation.cluster_centers_indices_
    labels = affinity_propagation.labels_

    clusters = []

    for i, exemplar in enumerate(exemplars):
        clusters.append(
            HarmonyCluster(
                cluster_id=i,
                centroid_id=exemplar,
                centroid=questions[exemplar],
                items=[],
                item_ids=[],
                text_description=questions[exemplar].question_text,
                keywords=[]
            )
        )

    cluster_ids = set([cluster.cluster_id for cluster in clusters])
    for i, label in enumerate(labels):
        if label not in cluster_ids:
            clusters.append(
                HarmonyCluster(
                    cluster_id=label,
                    centroid_id=i,
                    centroid=questions[i],
                    items=[],
                    item_ids=[],
                    text_description=questions[i].question_text,
                    keywords=[]
                )
            )
            cluster_ids.add(label)

        clusters[label].items.append(questions[i])
        clusters[label].item_ids.append(i)

    cluster_topics = generate_cluster_topics(clusters, top_k_topics=5)
    for cluster, topics in zip(clusters, cluster_topics):
        cluster.keywords = topics

    return clusters

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
from sklearn.cluster import AffinityPropagation
from harmony.schemas.responses.text import HarmonyCluster
from harmony.schemas.requests.text import Question
from harmony.matching.generate_cluster_topics import generate_cluster_topics

import numpy as np


def cluster_questions_affinity_propagation(
        questions: List[Question],
        item_to_item_similarity_matrix: np.ndarray,
        top_k_topics: int = 5,
        languages: List[str] = ["english"],
        additional_stopwords: List[str] = None,
    ) -> List[HarmonyCluster]:
    """
    Affinity Propagation Clustering using the cosine similarity matrix.

    Parameters
    ----------
    questions : List[Question]
        The set of questions to cluster.

    item_to_item_similarity_matrix : np.ndarray
        The cosine similarity matrix for the questions.

    top_k_topics: int
        The number of topics to assign to each cluster.

    languages: List[str]
        The languages of the questions. Used for topic assignment.

    additional_stopwords: List[str]
        Words to exclude from the topic names.

    Returns
    -------
    List[HarmonyCluster]
        A list of HarmonyCluster objects representing the clusters.
    """
    
    affinity_propagation = AffinityPropagation(affinity='precomputed', random_state=1)
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

    for i, label in enumerate(labels):
        clusters[label].items.append(questions[i])
        clusters[label].item_ids.append(i)

    cluster_topics = generate_cluster_topics(clusters, top_k_topics, languages, additional_stopwords)
    for cluster, topics in zip(clusters, cluster_topics):
        cluster.keywords = topics

    return clusters
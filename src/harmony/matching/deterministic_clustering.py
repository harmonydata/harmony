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

import operator
from collections import Counter
from typing import List

import numpy as np

from harmony.schemas.requests.text import Question
from harmony.schemas.responses.text import HarmonyCluster


def find_clusters_deterministic(questions: List[Question], item_to_item_similarity_matrix: np.ndarray,
                                threshold: float = None) -> List[HarmonyCluster]:
    """
    Find all clusters in a set of n questions, given the n x n matrix of cosine similarities between them.

    This uses a deterministic clustering algorithm.
    @param questions: The set of questions, length n - they don't have to be from the same instrument
    @param item_to_item_similarity_matrix: The cosine similarity between the questions. The diagonal will be 1 and this matrix is symmetrical about the diagonal. You can have negative values in it, as we will work from the absolute values.
    @param threshold: Minimum threshold of cosine similarity used for making a cluster
    @return: A list of HarmonyCluster objects which each have a centroid, cluster members, and a description text.
    """
    abs_similarities = np.abs(item_to_item_similarity_matrix)

    coord_to_sim = {}
    for y in range(abs_similarities.shape[0]):
        for x in range(abs_similarities.shape[1]):
            coord_to_sim[(y, x)] = abs_similarities[y, x]

    # Start with the closest cosine match and pair up the items in clusters ordering the edges in the graph by strong to weak.
    # Each time a node is assigned to a cluster, we increment its score with its cosine similarity to its neighbours
    # This boosts its chance of being chosen as the centroid.
    total_score = Counter()
    edges = set()
    vertices = set()
    for (y, x), sim in sorted(coord_to_sim.items(), key=operator.itemgetter(1), reverse=True):
        if x < y:
            if threshold is None or sim >= threshold:
                if x not in vertices or y not in vertices:
                    edges.add((x, y))
                    vertices.add(x)
                    vertices.add(y)

                    total_score[x] += sim
                    total_score[y] += sim

    question_idx_to_group_idx = {}
    for x, y in edges:
        if x not in question_idx_to_group_idx and y not in question_idx_to_group_idx:
            group_idx = min([x, y])
            question_idx_to_group_idx[x] = group_idx
            question_idx_to_group_idx[y] = group_idx
        elif x in question_idx_to_group_idx and y not in question_idx_to_group_idx:
            group_idx = question_idx_to_group_idx[x]
            question_idx_to_group_idx[y] = group_idx
        elif y in question_idx_to_group_idx and x not in question_idx_to_group_idx:
            group_idx = question_idx_to_group_idx[y]
            question_idx_to_group_idx[x] = group_idx

    for x in range(len(questions)):
        if x not in question_idx_to_group_idx:
            question_idx_to_group_idx[x] = x

    clusters_to_return = []

    all_groups = set(question_idx_to_group_idx.values())
    for group_no, group_idx in enumerate(sorted(all_groups)):
        candidate_scores = {}

        items = []
        item_ids = []
        for question_idx in question_idx_to_group_idx:
            if question_idx_to_group_idx[question_idx] == group_idx:
                items.append(questions[question_idx])
                item_ids.append(question_idx)
                candidate_scores[question_idx] = total_score.get(question_idx, 0)

        best_question_idx = max(candidate_scores, key=candidate_scores.get)
        text_description = questions[best_question_idx].question_text

        this_cluster = HarmonyCluster(cluster_id=group_no, centroid_id=best_question_idx,
                                      centroid=questions[best_question_idx], items=items, item_ids=item_ids,
                                      text_description=text_description)
        clusters_to_return.append(this_cluster)

    return clusters_to_return

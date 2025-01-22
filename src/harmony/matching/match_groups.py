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
from typing import List

import numpy as np
import pandas as pd

from harmony.schemas.requests.text import Question


def find_groups(questions: List[Question], item_to_item_similarity_matrix: np.ndarray) -> pd.DataFrame:
    abs_similarities = np.abs(item_to_item_similarity_matrix)

    coord_to_sim = {}
    for y in range(abs_similarities.shape[0]):
        for x in range(abs_similarities.shape[1]):
            coord_to_sim[(y, x)] = abs_similarities[y, x]

    edges = set()
    vertices = set()
    for (y, x), sim in sorted(coord_to_sim.items(), key=operator.itemgetter(1), reverse=True):
        if x < y:
            if x not in vertices or y not in vertices:
                edges.add((x, y))
                vertices.add(x)
                vertices.add(y)

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

        this_cluster = {"group_no": group_no, "items": []}
        for q in question_idx_to_group_idx:
            if question_idx_to_group_idx[q] == group_idx:
                this_cluster["items"].append(questions[q])

        questions.append(this_cluster)

    return clusters_to_return

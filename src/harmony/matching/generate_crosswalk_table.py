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

import pandas as pd

def generate_crosswalk_table(all_questions, similarity, threshold):
    matching_pairs = []

    # iterate through all pairs of questions
    for i, q1 in enumerate(all_questions):
        for j, q2 in enumerate(all_questions):
            # check for non-dupe and similarity above inputted threshold
            if j > i and similarity[i, j] > threshold:
                # add to list of matches
                matching_pairs.append({
                    'pair_name': f"{i}_{j}",
                    'question1_no': q1.question_no,
                    'question1_text': q1.question_text,
                    'question2_no': q2.question_no,
                    'question2_text': q2.question_text,
                    'match_score': similarity[i, j]
                })

    # convert list to dataframe
    return pd.DataFrame(matching_pairs)

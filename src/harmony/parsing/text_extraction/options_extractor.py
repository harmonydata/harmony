'''
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

'''

import re


def get_candidate_options(doc):
    running_sequences = []
    for span in doc.spans['CANDIDATE_OPTION']:
        sequence_to_append_to = []
        for test_sequence in running_sequences:
            test_span = test_sequence[-1]
            if test_span.end < span.start and test_span.end + 10 > span.start:
                sequence_to_append_to = test_sequence
        if len(sequence_to_append_to) == 0:
            running_sequences.append(sequence_to_append_to)
        sequence_to_append_to.append(span)

    return [s for s in running_sequences if len(s) > 2]


def clean_options(text):
    return re.sub(r'\s+', ' ', re.sub(r'^\W+|\W+$', '', text))


def get_correctly_ordered_options_text(options_spans: list):
    """
    Gets a text of all the options, in the order they appear in the document.
    :param options_spans:
    :return:
    """
    texts = []
    found = set()
    for s in sorted(options_spans, key=lambda s: s.start):
        clean_text = clean_options(s.text)
        if clean_text not in found:
            texts.append(clean_text)
            found.add(clean_text)

    return texts


def add_candidate_options(df_questions, doc):
    sequences = get_candidate_options(doc)

    if len(sequences) > 0:
        fallback_options = sequences[0]
    else:
        fallback_options = []

    candidate_options_per_question = [[]] * len(df_questions)
    if len(sequences) == 1:
        for i in range(len(df_questions)):
            candidate_options_per_question[i] = fallback_options
    else:
        for row_idx in range(len(df_questions)):
            tok_idx = df_questions["span"].iloc[row_idx].start
            next_tok_idx = None
            if row_idx < len(df_questions) - 1:
                next_tok_idx = df_questions["span"].iloc[row_idx + 1].start
            for s in sequences:
                if tok_idx < s[0].start and (next_tok_idx is None or next_tok_idx > s[0].start):
                    candidate_options_per_question[row_idx] = s
            if candidate_options_per_question[row_idx] == []:
                candidate_options_per_question[row_idx] = fallback_options

    df_questions["options_spans"] = candidate_options_per_question
    df_questions["options"] = df_questions["options_spans"].apply(get_correctly_ordered_options_text)

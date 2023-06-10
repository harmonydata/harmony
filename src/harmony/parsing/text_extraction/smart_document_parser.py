import re

import numpy as np
import pandas as pd
from spacy.tokens import Span
from harmony.parsing.text_extraction.sequence_finder import find_longest_uninterrupted_sequence
from harmony.parsing.text_extraction.spacy_wrapper import nlp
from harmony.schemas.requests.text import Question
from harmony.parsing.text_extraction.options_extractor import add_candidate_options


def normalise(text):
    return re.sub(r'\W', '', text.lower())


def clean_question(text):
    return re.sub(r'^\s*(-|\))\s*|\s*(-|\()\s*$', '', re.sub(r'\s+', ' ', text)).strip()


def get_question_from_span(question_span):
    """
    Get the text of a question, excluding any of the leading or trailing Likert options
    :param question_span:
    :return:
    """
    doc = question_span.doc
    tokens_to_include = set(range(question_span.start, question_span.end))

    # Logic to delete Likert options from end of text
    tokens_to_exclude = set()
    for option_span in doc.spans['CANDIDATE_OPTION']:
        for i in range(option_span.start, option_span.end):
            tokens_to_exclude.add(i)

    for i in tokens_to_exclude:
        if i + 1 in tokens_to_exclude or i - 1 in tokens_to_exclude:
            if i in tokens_to_include:
                tokens_to_include.remove(i)

    if len(tokens_to_include) == 0:
        return ""
    start = question_span.start
    end = max(tokens_to_include) + 1
    if start < end:
        question_span = doc[start:end]

    return clean_question(question_span.text)


def convert_to_dataframe(doc, is_training=False):
    df = pd.DataFrame({"span": list(doc.spans['CANDIDATE_QUESTION'])})

    if is_training:
        df["ground_truth"] = df.question.apply(lambda span: span._.ground_truth)

    # df["question"] = df["span"].apply(lambda span: clean_question(span.text))
    df["question"] = df["span"].apply(lambda span: get_question_from_span(span))

    df["preceding_bullet_value"] = df["span"].apply(lambda span: span._.preceding_bullet_value)

    return df


def is_acceptable_span(span: Span) -> bool:
    if span.end - span.start < 2:
        return False
    question = get_question_from_span(span)
    non_whitespace_text = re.sub(r'\W', '', question)
    if len(non_whitespace_text) < 10:
        return False
    return True


def get_questions(df):
    preceding_bullet_values = list(df.preceding_bullet_value)
    longest_uninterrupted_sequence = find_longest_uninterrupted_sequence(preceding_bullet_values)

    if longest_uninterrupted_sequence is not None:
        is_question_to_include = np.zeros((len(df),), dtype=bool)
        for idx, seq_type, value in longest_uninterrupted_sequence:
            is_question_to_include[idx] = 1
        df["is_question_to_include"] = is_question_to_include
    else:
        # df["prediction"] = list(predictions)
        # df["is_question_to_include"] = df["prediction"] == 2
        df["is_question_to_include"] = df.span.apply(is_acceptable_span)

    df_pred = df[df["is_question_to_include"]]
    df_pred.rename(columns={"preceding_bullet_value": "question_no"}, inplace=True)

    return df_pred


def parse_document(text):
    doc = nlp(text)
    df = convert_to_dataframe(doc)

    df = get_questions(df)
    add_candidate_options(df, doc)

    questions = []
    for idx in range(len(df)):
        if df.is_question_to_include.iloc[idx]:
            options = df.options.iloc[idx]
            question = Question(question_no=df.question_no.iloc[idx], question_intro="", question_text=df.question.iloc[idx], options=list(options))
            questions.append(question)

    return questions

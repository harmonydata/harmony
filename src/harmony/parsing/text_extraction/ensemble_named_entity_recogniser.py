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

import numpy as np
import json
import os
import re

import numpy as np
import requests
import spacy
from harmony.parsing.text_extraction.smart_document_parser import nlp, convert_to_dataframe, \
    get_questions, add_candidate_options
from spacy.tokens import DocBin

from harmony.parsing.text_extraction.dictionary_options_matcher import options_matcher
from harmony.parsing.text_extraction.options_words import OPTIONS_WORDS
from harmony.parsing.text_extraction.smart_table_analyser import get_questions_from_tables
from harmony.parsing.text_extraction.spacy_wrapper import mark_is_all_letters, \
    get_candidate_questions_and_mark_as_spans, set_is_numbered_bullet, mark_candidate_options_as_spans
from harmony.schemas.requests.text import Question

nlp = spacy.blank("en")

spacy_models = {"ner":None, "classifier":None}

def load_spacy_models():
    if spacy_models["ner"]  is None:
        if os.environ.get("HARMONY_NER_ENDPOINT") is None or os.environ.get("HARMONY_NER_ENDPOINT") == "":
            path = os.getenv("HARMONY_SPACY_PATH", os.path.expanduser("~") + "/harmony") + '/harmony_spacy_models/11_ner_0_spacy/model-best'
            if not os.path.isdir(path):
                print(f"Could not find model at {path}")
                print("Please run:\nfrom harmony import download_models\ndownload_models()")
                raise Exception()
            spacy_models["ner"] = spacy.load(path)

    if spacy_models["classifier"] is None:
        if os.environ.get("HARMONY_CLASSIFIER_ENDPOINT") is None or os.environ.get("HARMONY_CLASSIFIER_ENDPOINT") == "":
            path = os.getenv("HARMONY_SPACY_PATH", os.path.expanduser("~") + "/harmony") + '/harmony_spacy_models/29_classifier_spacy/model-best'
            if not os.path.isdir(path):
                print(f"Could not find model at {path}")
                print ("Please run:\nfrom harmony import download_models\ndownload_models()")
                raise Exception()
            spacy_models["classifier"] = spacy.load(path)


def add_manual_features(doc):
    mark_is_all_letters(doc)
    get_candidate_questions_and_mark_as_spans(doc)
    set_is_numbered_bullet(doc)
    mark_candidate_options_as_spans(doc)


def annotate_document(page_text):
    load_spacy_models()

    if os.environ.get("HARMONY_NER_ENDPOINT") is not None and os.environ.get(
            "HARMONY_NER_ENDPOINT") != "":
        response = requests.get(
            os.environ.get("HARMONY_NER_ENDPOINT"), json={"text": json.dumps([page_text])})
        doc_bin = DocBin().from_bytes(response.content)
        doc = list(doc_bin.get_docs(nlp.vocab))[0]
    else:
        doc = spacy_models["ner"](page_text)

    add_manual_features(doc)

    df = convert_to_dataframe(doc)

    df = get_questions(df)

    add_candidate_options(df, doc)

    token_classes = np.zeros((2, len(doc, )))

    for span in doc.ents:
        for ctr, token in enumerate(span):
            token_classes[0, token.i] = min(2, ctr + 1)

    for idx in range(len(df)):
        if df.is_question_to_include.iloc[idx]:
            for ctr, token in enumerate(df.span.iloc[idx]):
                token_classes[1, token.i] = min(2, ctr + 1)

    # Override any tokens that could be part of an options sequence.
    matches = options_matcher(doc)
    for m in matches:
        for idx in range(m[1], m[2]):
            token_classes[0, idx] = 0
            token_classes[1, idx] = 0

    return token_classes, doc, df


def extract_questions(page_text, tables):
    all_annotations, doc, df = annotate_document(page_text)

    questions = []

    cur_question_text = None

    for token in doc:
        result = 0
        ctr = 0
        for i in range(all_annotations.shape[0]):
            if all_annotations[i, token.i] == 1:
                result = 1
                ctr += 1
            elif all_annotations[i, token.i] == 2:
                if result == 0:
                    result = 2
                ctr += 1
        if ctr > 0:
            ws = token.whitespace_
            if result == 1 or cur_question_text == None:
                cur_question_text = re.sub(r'\n', ' ', token.text + ws)
            elif result == 2:
                cur_question_text += re.sub(r'\n', ' ', token.text + ws)
        else:
            if cur_question_text is not None:
                cur_question_text = re.sub(r'^- +', '', re.sub(r'\s+', ' ', cur_question_text).strip())
                if cur_question_text.lower() not in OPTIONS_WORDS:
                    questions.append(Question(question_text=cur_question_text, question_intro="",
                                              question_no=f"{len(questions) + 1}", options=[]))
            cur_question_text = None
    if cur_question_text is not None:
        cur_question_text = re.sub(r'^- +', '', re.sub(r'\s+', ' ', cur_question_text).strip())
        if cur_question_text.lower() not in OPTIONS_WORDS:
            questions.append(
                Question(question_text=cur_question_text, question_intro="", question_no=f"{len(questions) + 1}",
                         options=[]))

    # If any tables were detected in the PDF, extract questions from tables.
    if len(tables) > 0:
        questions_from_tables = get_questions_from_tables(tables)

        if len(questions_from_tables) * 2 > len(questions):
            print("Using tables response")
            questions = questions_from_tables

    questions_triaged = []
    if os.environ.get("HARMONY_CLASSIFIER_ENDPOINT") is not None and os.environ.get("HARMONY_CLASSIFIER_ENDPOINT") != "":
        response = requests.get(
            os.environ.get("HARMONY_CLASSIFIER_ENDPOINT"), json={"text": json.dumps([q.question_text for q in questions])})
        doc_bin = DocBin().from_bytes(response.content)
        docs = doc_bin.get_docs(nlp.vocab)
    else:
        docs = list(spacy_models["classifier"].pipe([q.question_text for q in questions]))

    for question, question_as_doc in zip(questions, docs):
        if question_as_doc.cats["1"] > 0.5:
            questions_triaged.append(question)
        else:
            print("Excluding question", question.question_text)
    if len(questions_triaged) > len(questions) / 2 and len(questions_triaged) > 5:
        questions = questions_triaged

    return questions, all_annotations, df

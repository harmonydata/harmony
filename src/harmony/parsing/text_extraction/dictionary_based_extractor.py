import sys
import os, re
sys.path.append("../harmonyapi/harmony/src/")
from harmony.schemas.requests.text import RawFile, Instrument, MatchBody, Question
mhc_questions = list()
with open("/media/thomas/642d0db5-2c98-4156-b591-1a3572c5868c/projects_client/wellcome/harmonyapi/mhc_questions.json", "r", encoding="utf-8") as f:
    for l in f:
        mhc_question = Question.parse_raw(l)
        mhc_questions.append(mhc_question)

all_questions = set()
all_options = set()
import re
for q in mhc_questions:
    cleaned_question= q.question_text.strip()
    if len(cleaned_question.split(" ")) > 1:
        all_questions.add(re.sub(r'(?:\?|\.|:)$', '', cleaned_question))
        all_questions.add(re.sub(r'(?:\?|\.|:)$', '', cleaned_question.upper()))
        all_questions.add(re.sub(r'(?:\?|\.|:)$', '', cleaned_question.lower()))
    options_list = [re.sub(r'(?:\?|\.|:)$', '', o.strip()) for o in q.options]
    if len(options_list) > 1:
        all_options.add(", ".join(options_list))
        all_options.add(" ".join(options_list))
        all_options.add("/".join(options_list))
        all_options.add(", ".join(options_list).upper())
        all_options.add(" ".join(options_list).upper())
        all_options.add("/".join(options_list).upper())
        all_options.add(", ".join(options_list).lower())
        all_options.add(" ".join(options_list).lower())
        all_options.add("/".join(options_list).lower())

import spacy
nlp = spacy.blank("en")
from spacy.matcher import PhraseMatcher
phrase_matcher = PhraseMatcher(nlp.vocab)
phrase_matcher.add(f"question", None, *nlp.pipe(all_questions))
phrase_matcher.add(f"option", None, *nlp.pipe(all_options))
import numpy as np

def annotate_document(page_text):
    doc_orig = nlp(page_text)

    new_char_index_to_old_token_index = {}
    text_cleaned = ""

    for token in doc_orig:
        ws = token.whitespace_
        if len(ws) > 1:
            ws = 1
        if "\n" in token.text:
            t = " "
        else:
            t = token.text + ws
        if text_cleaned.endswith(" ") and t.strip() == "":
            t = ""
        old_char_ctr = len(text_cleaned)
        text_cleaned += t
        new_char_ctr = len(text_cleaned)
        for idx in range(old_char_ctr, new_char_ctr):
            new_char_index_to_old_token_index[idx] = token.i

    doc = nlp(text_cleaned)
    print ("cleaned", text_cleaned)
    new_token_index_to_old_token_index = {}
    for token in doc:
        new_token_index_to_old_token_index[token.i] = new_char_index_to_old_token_index[token.idx]

    print (new_token_index_to_old_token_index)

    token_classes = np.zeros((len(doc_orig, )))

    phrase_matches = phrase_matcher(doc)

    for phrase_type, preprocessed_start, preprocessed_end in sorted(phrase_matches, key=lambda t: t[2] - t[1], reverse=True):
        is_overlap = False
        start = new_token_index_to_old_token_index[preprocessed_start]
        end = new_token_index_to_old_token_index[preprocessed_end]
        for i in range(start, end + 1):
            if token_classes[i] != 0:
                is_overlap = True
                break
        if is_overlap:
            continue
        if nlp.vocab.strings[phrase_type] == "question":
            token_classes[start] = 1
            for i in range(start + 1, end + 1):
                token_classes[i] = 2
        elif nlp.vocab.strings[phrase_type] == "option":
            token_classes[start] = 3
            for i in range(start + 1, end + 1):
                token_classes[end] = 4

    return token_classes
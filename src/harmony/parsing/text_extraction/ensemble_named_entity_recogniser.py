import spacy
import numpy as np
import re

from harmony.parsing.text_extraction.spacy_wrapper import mark_is_all_letters, \
    get_candidate_questions_and_mark_as_spans, set_is_numbered_bullet, mark_candidate_options_as_spans
from harmony.parsing.text_extraction.smart_document_parser import parse_document, nlp, convert_to_dataframe, get_questions, add_candidate_options
from harmony.schemas.requests.text import RawFile, Instrument, Question


# The trained NER recogniser
nlp = spacy.load(
    f'/media/thomas/642d0db5-2c98-4156-b591-1a3572c5868c/projects_client/wellcome/pdf_extraction_experiments/11_ner_0_spacy/model-best')


def add_manual_features(doc):
    mark_is_all_letters(doc)
    get_candidate_questions_and_mark_as_spans(doc)
    set_is_numbered_bullet(doc)
    mark_candidate_options_as_spans(doc)


def annotate_document(page_text):
    doc = nlp(page_text)
    add_manual_features(doc)

    df = convert_to_dataframe(doc)

    df = get_questions(df)

    add_candidate_options(df, doc)

    token_classes = np.zeros((2,len(doc, )))

    for span in doc.ents:
        for ctr, token in enumerate(span):
            token_classes[0, token.i] = min(2, ctr + 1)

    for idx in range(len(df)):
        if df.is_question_to_include.iloc[idx]:
            for ctr, token in enumerate(df.span.iloc[idx]):
                token_classes[1, token.i] = min(2, ctr + 1)

    return token_classes, doc

def extract_questions(page_text):
    all_annotations, doc = annotate_document(page_text)

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
                questions.append(Question(question_text = cur_question_text))
            cur_question_text = None
    if cur_question_text is not None:
        questions.append(Question(question_text=cur_question_text, question_intro="", question_no=1, options=[]))

    return questions, all_annotations
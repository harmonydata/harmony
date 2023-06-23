import spacy
import numpy as np
import re
import operator
from harmony.parsing.text_extraction.spacy_wrapper import mark_is_all_letters, \
    get_candidate_questions_and_mark_as_spans, set_is_numbered_bullet, mark_candidate_options_as_spans
from harmony.parsing.text_extraction.smart_document_parser import parse_document, nlp, convert_to_dataframe, get_questions, add_candidate_options
from harmony.schemas.requests.text import RawFile, Instrument, Question
from harmony.parsing.text_extraction.options_words import OPTIONS_WORDS
from harmony.parsing.text_extraction.smart_table_analyser import get_questions_from_tables
import os

data_path = os.getenv("DATA_PATH")

# The trained NER recogniser
nlp = spacy.load(
    data_path + '/11_ner_0_spacy/model-best')


nlp_final_classifier = spacy.load(
    data_path + '/29_classifier_spacy/model-best')

# from transformers import AutoTokenizer
#
# from transformers import TFAutoModelForSequenceClassification
#
# nlp_final_classifier = TFAutoModelForSequenceClassification.from_pretrained(f'/media/thomas/642d0db5-2c98-4156-b591-1a3572c5868c/projects_client/wellcome/pdf_extraction_experiments/31_model_old.hf')
# nlp_final_classifier_tokeniser = AutoTokenizer.from_pretrained(f'/media/thomas/642d0db5-2c98-4156-b591-1a3572c5868c/projects_client/wellcome/pdf_extraction_experiments/31_tokenizer.hf')


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

    return token_classes, doc, df

def extract_questions(page_text, tables):
    all_annotations, doc,df = annotate_document(page_text)


    questions = []
    # call to rule-based only
    # for idx in range(len(df)):
    #     if df.is_question_to_include.iloc[idx]:
    #         questions.append(Question(question_text = re.sub(r'\n',  ' ', df.span.iloc[idx].text)))
    # if len(questions) > 0:
    #     return questions, all_annotations, df

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
                    questions.append(Question(question_text = cur_question_text, question_intro="", question_no=f"{len(questions)+1}", options=[]))
            cur_question_text = None
    if cur_question_text is not None:
        cur_question_text = re.sub(r'^- +', '', re.sub(r'\s+', ' ', cur_question_text).strip())
        if cur_question_text.lower() not in OPTIONS_WORDS:
            questions.append(Question(question_text=cur_question_text, question_intro="", question_no=f"{len(questions)+1}", options=[]))

    # If any tables were detected in the PDF, extract questions from tables.
    if len(tables) > 0:
        questions_from_tables = get_questions_from_tables(tables)

        if len(questions_from_tables) * 2 > len(questions):
            print("Using tables response")
            questions = questions_from_tables

    questions_triaged = []

    for question, question_as_doc in zip(questions, nlp_final_classifier.pipe([q.question_text for q in questions])):
        if question_as_doc.cats["1"] > 0.5:
            questions_triaged.append(question)
        else:
            print ("Excluding question", question.question_text)
    if len(questions_triaged) > len(questions) / 2 and len(questions_triaged) > 5:
        questions = questions_triaged

    # Remove common suffixes
    # from collections import Counter
    # suffixes = Counter()
    # for q in questions:
    #     toks = q.question_text.split(" ")
    #     for i in range(1, 4):
    #         if i < len(toks) - 2:
    #             suffix = " ".join(toks[-i:])
    #             suffixes[suffix] += 1
    # if len(suffixes) > 0:
    #     sorted_suffixes = sorted(suffixes.items(), key = operator.itemgetter(1))
    #     if sorted_suffixes[0][1] > len(questions) / 2 and sorted_suffixes[0][1] > 4:
    #         print ("Removing", sorted_suffixes[0][1])
    #         for q in questions:
    #             try:
    #                 q.question_text = re.sub(sorted_suffixes[0][1] + "$", "", q.question_text)
    #             except:
    #                 pass

    return questions, all_annotations, df
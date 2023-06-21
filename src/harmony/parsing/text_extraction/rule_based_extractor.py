from harmony.parsing.text_extraction.smart_document_parser import parse_document, nlp, convert_to_dataframe, get_questions, add_candidate_options
import numpy as np


def annotate_document(page_text):
    doc = nlp(page_text)

    df = convert_to_dataframe(doc)

    df = get_questions(df)

    add_candidate_options(df, doc)

    token_classes = np.zeros((len(doc, )))

    for idx in range(len(df)):
        if df.is_question_to_include.iloc[idx]:
            for ctr, token in enumerate(df.span.iloc[idx]):
                token_classes[token.i] = min(2, ctr + 1)

    return token_classes
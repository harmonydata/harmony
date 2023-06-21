import spacy

nlp = spacy.load(f'/media/thomas/642d0db5-2c98-4156-b591-1a3572c5868c/projects_client/wellcome/pdf_extraction_experiments/11_ner_0_spacy/model-best')

import numpy as np


def annotate_document(page_text):
    doc = nlp(page_text)

    token_classes = np.zeros((len(doc, )))

    for span in doc.ents:
        for ctr, token in enumerate(span):
            token_classes[token.i] = min(2, ctr + 1)

    return token_classes
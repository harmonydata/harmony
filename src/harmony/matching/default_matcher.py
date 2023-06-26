from typing import List

import numpy as np

from sentence_transformers import SentenceTransformer

from harmony import match_instruments_with_function
from harmony.schemas.requests.text import Instrument
import os

if os.environ.get("HARMONY_SENTENCE_TRANSFORMER_PATH", None) is not None and os.environ.get("HARMONY_SENTENCE_TRANSFORMER_PATH", None) != "":
    sentence_transformer_path = os.environ["HARMONY_SENTENCE_TRANSFORMER_PATH"]
else:
    sentence_transformer_path = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

model = SentenceTransformer(sentence_transformer_path)

def convert_texts_to_vector(texts: np.ndarray):
    embeddings = model.encode(texts)
    return embeddings


def match_instruments(instruments: List[Instrument], query: str = None, mhc_questions: List = [],
                      mhc_all_metadatas: List = [],
                      mhc_embeddings: np.ndarray = np.zeros((0, 0))) -> tuple:
    return match_instruments_with_function(instruments, query, convert_texts_to_vector, mhc_questions,
                                           mhc_all_metadatas, mhc_embeddings)

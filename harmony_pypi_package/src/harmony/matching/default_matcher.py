from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from harmony import match_instruments_with_function
from harmony.schemas.requests.text import Instrument

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')


def convert_texts_to_vector(texts: np.ndarray):
    embeddings = model.encode(texts)
    return embeddings


def match_instruments(instruments: List[Instrument], query: str, mhc_questions=[], mhc_all_metadatas=[],
                      mhc_embeddings=np.zeros((0, 0))) -> tuple:
    return match_instruments_with_function(instruments, query, convert_texts_to_vector, mhc_questions, mhc_all_metadatas, mhc_embeddings)
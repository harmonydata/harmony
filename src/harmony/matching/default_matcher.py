"""
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
"""

import os
from typing import List

import numpy as np
from harmony import match_instruments_with_function
from harmony.schemas.requests.text import Instrument
from numpy import ndarray
from sentence_transformers import SentenceTransformer

if (
        os.environ.get("HARMONY_SENTENCE_TRANSFORMER_PATH", None) is not None
        and os.environ.get("HARMONY_SENTENCE_TRANSFORMER_PATH", None) != ""
):
    sentence_transformer_path = os.environ["HARMONY_SENTENCE_TRANSFORMER_PATH"]
else:
    sentence_transformer_path = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

model = SentenceTransformer(sentence_transformer_path)


def convert_texts_to_vector(texts: List, batch_size=50, max_batches=2000) -> ndarray:
    if batch_size == 0:
        embeddings = model.encode(sentences=texts, convert_to_numpy=True)

        return embeddings

    embeddings = []
    batch_count = 0

    # Process texts in batches
    for i in range(0, len(texts), batch_size):
        if batch_count >= max_batches:
            break
        batch = texts[i:i + batch_size]
        batch_embeddings = model.encode(sentences=batch, convert_to_numpy=True)
        embeddings.append(batch_embeddings)
        batch_count += 1

    # Concatenate all batch embeddings into a single NumPy array
    return np.concatenate(embeddings, axis=0)


def match_instruments(
        instruments: List[Instrument],
        query: str = None,
        mhc_questions: List = [],
        mhc_all_metadatas: List = [],
        mhc_embeddings: np.ndarray = np.zeros((0, 0)),
        texts_cached_vectors: dict[str, List[float]] = {}, batch_size: int = 50, max_batches: int = 2000,

) -> tuple:
    return match_instruments_with_function(
        instruments=instruments,
        query=query,
        vectorisation_function=lambda texts: convert_texts_to_vector(texts, batch_size=batch_size,
                                                                     max_batches=max_batches),
        mhc_questions=mhc_questions,
        mhc_all_metadatas=mhc_all_metadatas,
        mhc_embeddings=mhc_embeddings,
        texts_cached_vectors=texts_cached_vectors,
    )

"""Verify the three catalogue-matching entry points emit DeprecationWarning.

The catalogue path was replaced by a Weaviate
index and these functions are slated for removal. They must emit a
DeprecationWarning whose message references Weaviate so library users can
discover the replacement.
"""
import sys
import warnings

import numpy as np

sys.path.append("../src")

from harmony.matching.matcher import (
    match_instruments_with_catalogue_instruments,
    match_query_with_catalogue_instruments,
    match_questions_with_catalogue_instruments,
)
from harmony.schemas.requests.text import Instrument, Question
from harmony.schemas.text_vector import TextVector


def _minimal_catalogue_data():
    return {
        "instrument_idx_to_question_idx": [[0]],
        "all_embeddings_concatenated": np.array([[1.0, 0.0]]),
        "all_instruments": [{"instrument_name": "X", "metadata": {"source": "ref"}}],
        "all_questions": ["q"],
    }


def _assert_deprecation_mentions_weaviate(records):
    dep = [r for r in records if issubclass(r.category, DeprecationWarning)]
    assert dep, "expected at least one DeprecationWarning"
    assert any("weaviate" in str(r.message).lower() for r in dep), (
        f"DeprecationWarning should mention Weaviate; got: "
        f"{[str(r.message) for r in dep]}"
    )


def test_match_questions_with_catalogue_instruments_is_deprecated():
    questions = [Question(question_text="q")]
    vectors = [TextVector(text="q", vector=[1.0, 0.0], is_negated=False, is_query=False)]
    with warnings.catch_warnings(record=True) as recs:
        warnings.simplefilter("always")
        try:
            match_questions_with_catalogue_instruments(
                questions=questions,
                catalogue_data=_minimal_catalogue_data(),
                all_instruments_text_vectors=vectors,
                questions_are_from_one_instrument=True,
            )
        except Exception:
            pass
    _assert_deprecation_mentions_weaviate(recs)


def test_match_query_with_catalogue_instruments_is_deprecated():
    with warnings.catch_warnings(record=True) as recs:
        warnings.simplefilter("always")
        try:
            match_query_with_catalogue_instruments(
                query="hello",
                catalogue_data=_minimal_catalogue_data(),
                vectorisation_function=lambda texts: np.array([[1.0, 0.0]] * len(texts)),
                texts_cached_vectors={},
            )
        except Exception:
            pass
    _assert_deprecation_mentions_weaviate(recs)


def test_match_instruments_with_catalogue_instruments_is_deprecated():
    instruments = [
        Instrument(
            file_id="f",
            instrument_id="i",
            instrument_name="I",
            file_name="f.pdf",
            file_type="pdf",
            file_section="s",
            language="en",
            questions=[Question(question_text="q")],
        )
    ]
    with warnings.catch_warnings(record=True) as recs:
        warnings.simplefilter("always")
        try:
            match_instruments_with_catalogue_instruments(
                instruments=instruments,
                catalogue_data=_minimal_catalogue_data(),
                vectorisation_function=lambda texts: np.array([[1.0, 0.0]] * len(texts)),
                texts_cached_vectors={},
                is_negate=False,
            )
        except Exception:
            pass
    _assert_deprecation_mentions_weaviate(recs)
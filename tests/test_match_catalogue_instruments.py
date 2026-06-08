"""Characterization tests for match_questions_with_catalogue_instruments.

These tests pin down the function's current observable behavior using a small,
deterministic synthetic catalogue. They are scoped to the catalogue deprecation
window (see PR #133) and will be removed alongside the catalogue functions.
"""
import numpy as np
import pytest

pytestmark = pytest.mark.filterwarnings(
    "ignore:The catalogue-matching code path is deprecated:DeprecationWarning"
)

from harmony.matching.matcher import match_questions_with_catalogue_instruments
from harmony.schemas.requests.text import Question
from harmony.schemas.text_vector import TextVector


def _catalogue_data():
    """Synthetic catalogue with 3 instruments sharing some questions.

    Catalogue question texts (and their indices):
        0: "anxious"
        1: "nervous"
        2: "sad"
        3: "tired"

    Embeddings are 2-D and chosen so cosine similarity is predictable:
        anxious -> [1, 0]
        nervous -> [0.9, 0.1]   (close to anxious)
        sad     -> [0, 1]
        tired   -> [0.1, 0.9]   (close to sad)

    Instrument membership:
        inst 0 ("GAD"):  questions [0, 1]            -> anxiety
        inst 1 ("PHQ"):  questions [2, 3]            -> depression
        inst 2 ("MIXED"): questions [1, 2]           -> shared
    """
    all_questions = ["anxious", "nervous", "sad", "tired"]
    all_embeddings = np.array(
        [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0], [0.1, 0.9]],
        dtype=np.float64,
    )
    instrument_idx_to_question_idx = [[0, 1], [2, 3], [1, 2]]
    all_instruments = [
        {"instrument_name": "GAD", "metadata": {"source": "ref", "url": "u0", "sweep_id": "s0"}},
        {"instrument_name": "PHQ", "metadata": {"source": "ref", "url": "u1", "sweep_id": "s1"}},
        {"instrument_name": "MIXED", "metadata": {"source": "ref", "url": "u2"}},
    ]
    return {
        "instrument_idx_to_question_idx": instrument_idx_to_question_idx,
        "all_embeddings_concatenated": all_embeddings,
        "all_instruments": all_instruments,
        "all_questions": all_questions,
    }


def _input_questions_and_vectors():
    """Two input questions; first matches 'anxious' best, second matches 'sad' best."""
    questions = [
        Question(question_text="I feel anxious"),
        Question(question_text="I feel sad"),
    ]
    text_vectors = [
        TextVector(text="I feel anxious", vector=[1.0, 0.0], is_negated=False, is_query=False),
        TextVector(text="I feel sad",     vector=[0.0, 1.0], is_negated=False, is_query=False),
    ]
    return questions, text_vectors


def test_empty_catalogue_returns_empty_list():
    catalogue = _catalogue_data()
    catalogue["all_embeddings_concatenated"] = np.zeros((0, 0))
    questions, vectors = _input_questions_and_vectors()
    result = match_questions_with_catalogue_instruments(
        questions=questions,
        catalogue_data=catalogue,
        all_instruments_text_vectors=vectors,
        questions_are_from_one_instrument=True,
    )
    assert result == []


def test_each_matched_instrument_has_required_metadata_fields():
    """First input top-matches 'anxious' (in GAD); second top-matches 'sad' (in PHQ and MIXED).
    All three catalogue instruments end up in the result; each result carries the full
    metadata bundle the downstream consumers depend on."""
    catalogue = _catalogue_data()
    questions, vectors = _input_questions_and_vectors()
    result = match_questions_with_catalogue_instruments(
        questions=questions,
        catalogue_data=catalogue,
        all_instruments_text_vectors=vectors,
        questions_are_from_one_instrument=True,
    )
    names = [r.instrument_name for r in result]
    assert set(names) == {"GAD", "PHQ", "MIXED"}
    for r in result:
        assert r.metadata["num_matched_questions"] >= 1
        assert r.metadata["num_ref_instrument_questions"] >= 1
        assert "info" in r.metadata
        assert r.metadata["mean_cosine_similarity"] is not None


def test_full_output_snapshot_for_synthetic_catalogue():
    """Pin the full structure of the result against a known input.

    Any field drift — info string format, url, sweep, counts, mean similarity —
    breaks this test. This is the byte-identical guarantee the refactor promises.
    """
    catalogue = _catalogue_data()
    questions, vectors = _input_questions_and_vectors()
    result = match_questions_with_catalogue_instruments(
        questions=questions,
        catalogue_data=catalogue,
        all_instruments_text_vectors=vectors,
        questions_are_from_one_instrument=True,
    )
    serialized = [r.model_dump() for r in result]
    expected = [
        {
            "instrument_name": "GAD",
            "instrument_url": "u0",
            "source": "REF",
            "sweep": "s0",
            "metadata": {
                "info": (
                    "GAD Sweep s0 matched 1 question(s) in your instrument, "
                    "your instrument contains 2 question(s). "
                    "The reference instrument contains 2 question(s)."
                ),
                "num_matched_questions": 1,
                "num_ref_instrument_questions": 2,
                "mean_cosine_similarity": pytest.approx(1.0),
            },
        },
        {
            "instrument_name": "PHQ",
            "instrument_url": "u1",
            "source": "REF",
            "sweep": "s1",
            "metadata": {
                "info": (
                    "PHQ Sweep s1 matched 1 question(s) in your instrument, "
                    "your instrument contains 2 question(s). "
                    "The reference instrument contains 2 question(s)."
                ),
                "num_matched_questions": 1,
                "num_ref_instrument_questions": 2,
                "mean_cosine_similarity": pytest.approx(1.0),
            },
        },
        {
            "instrument_name": "MIXED",
            "instrument_url": "u2",
            "source": "REF",
            "sweep": "",
            "metadata": {
                "info": (
                    "MIXED Sweep UNKNOWN matched 1 question(s) in your instrument, "
                    "your instrument contains 2 question(s). "
                    "The reference instrument contains 2 question(s)."
                ),
                "num_matched_questions": 1,
                "num_ref_instrument_questions": 2,
                "mean_cosine_similarity": pytest.approx(1.0),
            },
        },
    ]
    assert serialized == expected


def test_two_inputs_with_same_top_match_each_contribute_similarity_to_owning_instruments():
    """Both input questions top-match Q2 ('sad'), which is contained in PHQ and MIXED.

    The second nested loop in `match_questions_with_catalogue_instruments` appends
    similarity per input question (not per instrument), so each owning instrument
    receives TWO similarity entries here. This invariant is exactly what the
    reverse-index refactor of that loop must preserve. GAD contains neither top
    match and must not appear in the result.
    """
    catalogue = _catalogue_data()
    questions = [
        Question(question_text="I am sad"),
        Question(question_text="feeling down"),
    ]
    vectors = [
        TextVector(text="I am sad", vector=[0.0, 1.0], is_negated=False, is_query=False),
        TextVector(text="feeling down", vector=[0.0, 1.0], is_negated=False, is_query=False),
    ]
    result = match_questions_with_catalogue_instruments(
        questions=questions,
        catalogue_data=catalogue,
        all_instruments_text_vectors=vectors,
        questions_are_from_one_instrument=False,
    )
    by_name = {r.instrument_name: r for r in result}
    assert by_name["PHQ"].metadata["num_matched_questions"] == 2
    assert by_name["MIXED"].metadata["num_matched_questions"] == 2
    assert "GAD" not in by_name


def test_closest_question_attached_to_each_input_question():
    catalogue = _catalogue_data()
    questions, vectors = _input_questions_and_vectors()
    match_questions_with_catalogue_instruments(
        questions=questions,
        catalogue_data=catalogue,
        all_instruments_text_vectors=vectors,
        questions_are_from_one_instrument=True,
    )
    assert questions[0].closest_catalogue_question_match.question == "anxious"
    assert questions[1].closest_catalogue_question_match.question == "sad"
    # 'anxious' lives in GAD (idx 0) -> seen_in_instruments contains GAD
    assert any(
        si.instrument_name == "GAD"
        for si in questions[0].closest_catalogue_question_match.seen_in_instruments
    )
    # 'sad' lives in PHQ (idx 1) and MIXED (idx 2)
    seen_names_q1 = {
        si.instrument_name
        for si in questions[1].closest_catalogue_question_match.seen_in_instruments
    }
    assert seen_names_q1 == {"PHQ", "MIXED"}


def test_info_string_one_vs_many_instruments():
    catalogue = _catalogue_data()
    questions, vectors = _input_questions_and_vectors()

    res_single = match_questions_with_catalogue_instruments(
        questions=questions,
        catalogue_data=catalogue,
        all_instruments_text_vectors=vectors,
        questions_are_from_one_instrument=True,
    )
    res_multi = match_questions_with_catalogue_instruments(
        questions=questions,
        catalogue_data=catalogue,
        all_instruments_text_vectors=vectors,
        questions_are_from_one_instrument=False,
    )
    # The wording differs by branch — pin it down
    assert "in your instrument," in res_single[0].metadata["info"]
    assert "in all of your instruments," in res_multi[0].metadata["info"]


def test_orphan_top_match_yields_empty_seen_in_and_empty_result():
    """An isolated catalogue question (in no instrument) is a legal top-match target.
    `seen_in_instruments` must be `[]` and the top-instruments list must be `[]`
    rather than crashing on a missing key."""
    catalogue = _catalogue_data()
    # Add a 5th catalogue question that no instrument references
    catalogue["all_questions"] = catalogue["all_questions"] + ["orphan"]
    catalogue["all_embeddings_concatenated"] = np.vstack(
        [catalogue["all_embeddings_concatenated"], np.array([[0.5, 0.5]])]
    )
    # Input vector deliberately closest to the orphan
    questions = [Question(question_text="balanced")]
    vectors = [TextVector(text="balanced", vector=[0.5, 0.5], is_negated=False, is_query=False)]
    result = match_questions_with_catalogue_instruments(
        questions=questions,
        catalogue_data=catalogue,
        all_instruments_text_vectors=vectors,
        questions_are_from_one_instrument=True,
    )
    # No instrument contains the orphan, so closest_catalogue_question_match.seen_in_instruments is empty,
    # and the top-instruments list is also empty (no instrument got a match).
    assert questions[0].closest_catalogue_question_match.question == "orphan"
    assert questions[0].closest_catalogue_question_match.seen_in_instruments == []
    assert result == []

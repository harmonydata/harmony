'''
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

'''

import sys
import unittest

sys.path.append("../src")

import numpy as np
from sentence_transformers import SentenceTransformer

from harmony import match_instruments
from harmony.schemas.requests.text import Instrument, Question


model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')


def create_mhc_question_with_text(text):
    """Create a Question object, bypassing validation for empty text (simulates MHC data)"""
    q = Question.model_construct(question_text=text)
    return q


class TestMhcEmptyFiltering(unittest.TestCase):
    """Tests for Issue #7: Remove empty items from MHC"""

    def test_empty_mhc_questions_are_skipped(self):
        """Verify that empty MHC questions are not matched"""
        questions_en = [
            Question(question_text="I feel anxious and worried about things"),
            Question(question_text="I have trouble sleeping at night"),
        ]
        instrument_en = Instrument(questions=questions_en)

        # MHC data with empty questions (using model_construct to bypass validation)
        mhc_metadata = [
            {'topics': ['anxiety']},
            {'topics': ['empty_topic']},  # This has empty text
            {'topics': ['sleep disorders']},
        ]

        mhc_questions = [
            create_mhc_question_with_text("Do you feel nervous or anxious?"),
            create_mhc_question_with_text(""),  # Empty question - should be skipped
            create_mhc_question_with_text("Do you have difficulty sleeping?"),
        ]

        mhc_embeddings = model.encode(np.asarray([
            "Do you feel nervous or anxious?",
            "placeholder",  # Will be masked out
            "Do you have difficulty sleeping?",
        ]))

        match_response = match_instruments(
            [instrument_en],
            mhc_questions=mhc_questions,
            mhc_embeddings=mhc_embeddings,
            mhc_all_metadatas=mhc_metadata,
            mhc_min_similarity=0.3
        )

        self.assertEqual(2, len(match_response.questions))

        # Verify no question matched to the empty MHC item
        for q in match_response.questions:
            if q.nearest_match_from_mhc_auto:
                self.assertNotEqual("", q.nearest_match_from_mhc_auto.get("question_text", ""))

    def test_whitespace_only_mhc_questions_are_skipped(self):
        """Verify that whitespace-only MHC questions are not matched"""
        questions_en = [Question(question_text="I feel depressed")]
        instrument_en = Instrument(questions=questions_en)

        mhc_metadata = [
            {'topics': ['whitespace']},
            {'topics': ['depression']},
        ]

        mhc_questions = [
            create_mhc_question_with_text("   "),  # Whitespace only - should be skipped
            create_mhc_question_with_text("Do you feel depressed or sad?"),
        ]

        mhc_embeddings = model.encode(np.asarray([
            "placeholder",
            "Do you feel depressed or sad?",
        ]))

        match_response = match_instruments(
            [instrument_en],
            mhc_questions=mhc_questions,
            mhc_embeddings=mhc_embeddings,
            mhc_all_metadatas=mhc_metadata,
            mhc_min_similarity=0.3
        )

        # Should match to the valid depression question
        if match_response.questions[0].nearest_match_from_mhc_auto:
            matched_text = match_response.questions[0].nearest_match_from_mhc_auto.get("question_text", "")
            self.assertIn("depressed", matched_text.lower())


class TestMhcSimilarityThreshold(unittest.TestCase):
    """Tests for Issue #8: Don't match to MHC items if similarity is too low"""

    def test_low_similarity_no_match(self):
        """Verify that questions with low similarity to MHC are not matched"""
        # Unrelated question
        questions = [Question(question_text="I lost my car keys")]
        instrument = Instrument(questions=questions)

        mhc_metadata = [
            {'topics': ['eating disorders']},
            {'topics': ['anxiety']},
        ]

        mhc_questions_as_text = [
            "Do you worry about your weight?",
            "Do you feel anxious?",
        ]

        mhc_embeddings = model.encode(np.asarray(mhc_questions_as_text))
        mhc_questions = [Question(question_text=t) for t in mhc_questions_as_text]

        # Use high threshold to ensure no match
        match_response = match_instruments(
            [instrument],
            mhc_questions=mhc_questions,
            mhc_embeddings=mhc_embeddings,
            mhc_all_metadatas=mhc_metadata,
            mhc_min_similarity=0.8
        )

        # Should not have MHC match due to low similarity
        self.assertIsNone(match_response.questions[0].nearest_match_from_mhc_auto)

    def test_high_similarity_match(self):
        """Verify that questions with high similarity to MHC are matched"""
        questions = [Question(question_text="I feel nervous and anxious")]
        instrument = Instrument(questions=questions)

        mhc_metadata = [
            {'topics': ['anxiety']},
        ]

        mhc_questions_as_text = [
            "Do you feel nervous or anxious?",
        ]

        mhc_embeddings = model.encode(np.asarray(mhc_questions_as_text))
        mhc_questions = [Question(question_text=t) for t in mhc_questions_as_text]

        # Use low threshold to allow match
        match_response = match_instruments(
            [instrument],
            mhc_questions=mhc_questions,
            mhc_embeddings=mhc_embeddings,
            mhc_all_metadatas=mhc_metadata,
            mhc_min_similarity=0.3
        )

        # Should have MHC match
        self.assertIsNotNone(match_response.questions[0].nearest_match_from_mhc_auto)

    def test_threshold_filters_unrelated(self):
        """Verify that mhc_min_similarity threshold filters unrelated questions"""
        # Completely unrelated question about cooking
        questions = [Question(question_text="How do I make a chocolate cake?")]
        instrument = Instrument(questions=questions)

        mhc_metadata = [
            {'topics': ['depression']},
        ]

        mhc_questions_as_text = [
            "Have you felt hopeless about the future?",
        ]

        mhc_embeddings = model.encode(np.asarray(mhc_questions_as_text))
        mhc_questions = [Question(question_text=t) for t in mhc_questions_as_text]

        # Use explicit threshold of 0.5 to filter unrelated
        match_response = match_instruments(
            [instrument],
            mhc_questions=mhc_questions,
            mhc_embeddings=mhc_embeddings,
            mhc_all_metadatas=mhc_metadata,
            mhc_min_similarity=0.5
        )

        # Should not have MHC match - cooking and depression are unrelated
        self.assertIsNone(match_response.questions[0].nearest_match_from_mhc_auto)


if __name__ == '__main__':
    unittest.main()

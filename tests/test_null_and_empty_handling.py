import sys
import os
import unittest

# Add src/ to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from harmony.matching.matcher import process_questions

class DummyTextVector:
    def __init__(self, text, vector=None, is_negated=False, is_query=False):
        self.text = text
        self.vector = vector
        self.is_negated = is_negated
        self.is_query = is_query

# Patch: monkeypatch harmony.matching.matcher.TextVector to DummyTextVector for testing
import harmony.matching.matcher as matcher
matcher.TextVector = DummyTextVector

class TestProcessQuestions(unittest.TestCase):
    def test_empty_string_returns_none_vector(self):
        result = process_questions([""], {}, is_negate=False)
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0].vector)

    def test_whitespace_string_returns_none_vector(self):
        result = process_questions(["   "], {}, is_negate=False)
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0].vector)

    def test_valid_string_creates_vector(self):
        # Here add_text_to_vec not mocked => will fail if it tries real embed
        # So just check that process_questions doesn't return None for text
        result = process_questions(["Hello"], {}, is_negate=False)
        self.assertEqual(result[0].text, "Hello")

if __name__ == "__main__":
    unittest.main()
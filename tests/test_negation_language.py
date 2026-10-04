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

from harmony.matching.matcher import get_question_languages, process_questions
from harmony.schemas.requests.text import Instrument, Question


class TestNegationLanguage(unittest.TestCase):
    """Regression tests for issue #142: negation must use the instrument's language, not always English."""

    def setUp(self):
        self.instrument_en = Instrument(language="en", questions=[Question(question_text="I feel depressed")])
        self.instrument_pt = Instrument(language="pt", questions=[Question(question_text="eu me sinto deprimido")])

    def get_negated_texts(self, instruments):
        question_languages = get_question_languages(instruments)
        all_questions = [q.question_text for i in instruments for q in i.questions]
        text_vectors = process_questions(all_questions, {}, is_negate=True, question_languages=question_languages)
        return [tv.text for tv in text_vectors if tv.is_negated]

    def test_question_languages_follow_instrument(self):
        question_languages = get_question_languages([self.instrument_en, self.instrument_pt])
        self.assertEqual("en", question_languages["I feel depressed"])
        self.assertEqual("pt", question_languages["eu me sinto deprimido"])

    def test_portuguese_item_uses_portuguese_negation(self):
        negated = self.get_negated_texts([self.instrument_en, self.instrument_pt])
        self.assertIn("never I feel depressed", negated)
        self.assertIn("não eu me sinto deprimido", negated)
        self.assertNotIn("never eu me sinto deprimido", negated)

    def test_default_is_english(self):
        text_vectors = process_questions(["I feel depressed"], {}, is_negate=True)
        negated = [tv.text for tv in text_vectors if tv.is_negated]
        self.assertEqual(["never I feel depressed"], negated)


if __name__ == '__main__':
    unittest.main()

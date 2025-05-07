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

from harmony import convert_text_to_instruments
from harmony.schemas.requests.text import RawFile

txt_gad_7_2_questions = RawFile.model_validate({
    "file_id": "d39f31718513413fbfc620c6b6135d0c",
    "file_name": "GAD-7.txt",
    "file_type": "txt",
    "content": """I feel nervous, anxious and afraid
I feel scared"""
}
)

leading_digits_csv = RawFile.model_validate({
    "file_id": "b89800ob990a",
    "file_name": "leading.csv",
    "file_type": "csv",
    "content": """1 I feel nervous
2 I feel afraid"""
})

trailing_digits_csv = RawFile.model_validate({
    "file_id": "obas2333of",
    "file_name": "trailing.csv",
    "file_type": "csv",
    "content": """I feel sad 2
I feel hopeless 2"""
})

parentheses_digits_csv = RawFile.model_validate({
    "file_id": "parentheses_digits_csv",
    "file_name": "parentheses.csv",
    "file_type": "csv",
    "content": """(1) I feel tired
(2) I feel weak"""
})

period_digits_csv = RawFile.model_validate({
    "file_id": "period_digits_csv",
    "file_name": "period.csv",
    "file_type": "csv",
    "content": """1. I feel angry
2. I feel upset"""
})

mixed_format_digits_csv = RawFile.model_validate({
    "file_id": "mixed_format_digits_csv",
    "file_name": "mixed.csv",
    "file_type": "csv",
    "content": """1) How do you feel
(2) Are you okay"""
})

both_ends_digits_csv = RawFile.model_validate({
    "file_id": "both_ends_digits_csv",
    "file_name": "bothends.csv",
    "file_type": "csv",
    "content": """1. How are you today (2)
(1) Are you feeling better 2."""
})


class TestConvertTxt(unittest.TestCase):

    def test_single_instrument(self):
        self.assertEqual(1, len(convert_text_to_instruments(txt_gad_7_2_questions)))

    def test_two_questions(self):
        self.assertEqual(2, len(convert_text_to_instruments(txt_gad_7_2_questions)[0].questions))

    def test_remove_leading_digits_from_csv(self):
        instruments = convert_text_to_instruments(leading_digits_csv)
        questions = instruments[0].questions
        self.assertEqual("I feel nervous", questions[0].question_text)
        self.assertEqual("I feel afraid", questions[1].question_text)

    def test_remove_trailing_digits_from_csv(self):
        instruments = convert_text_to_instruments(trailing_digits_csv)
        questions = instruments[0].questions
        self.assertEqual("I feel sad", questions[0].question_text)
        self.assertEqual("I feel hopeless", questions[1].question_text)

    def test_remove_parentheses_digits_from_csv(self):
        instruments = convert_text_to_instruments(parentheses_digits_csv)
        questions = instruments[0].questions
        self.assertEqual("I feel tired", questions[0].question_text)
        self.assertEqual("I feel weak", questions[1].question_text)

    def test_remove_period_digits_from_csv(self):
        instruments = convert_text_to_instruments(period_digits_csv)
        questions = instruments[0].questions
        self.assertEqual("I feel angry", questions[0].question_text)
        self.assertEqual("I feel upset", questions[1].question_text)

    def test_remove_mixed_format_digits_from_csv(self):
        instruments = convert_text_to_instruments(mixed_format_digits_csv)
        questions = instruments[0].questions
        self.assertEqual("How do you feel", questions[0].question_text)
        self.assertEqual("Are you okay", questions[1].question_text)

    def test_remove_both_ends_digits_from_csv(self):
        instruments = convert_text_to_instruments(both_ends_digits_csv)
        questions = instruments[0].questions
        self.assertEqual("How are you today", questions[0].question_text)
        self.assertEqual("Are you feeling better", questions[1].question_text)


if __name__ == '__main__':
    unittest.main()

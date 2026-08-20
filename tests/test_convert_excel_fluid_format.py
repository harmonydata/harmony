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

import base64
import io
import sys
import unittest

import pandas as pd

sys.path.append("../src")

from harmony import convert_excel_to_instruments
from harmony.schemas.requests.text import RawFile


def make_excel(rows, file_name="questionnaires.xlsx"):
    """Turn a list of rows into a RawFile holding a real xlsx, as the web app would."""
    buffer = io.BytesIO()
    pd.DataFrame(rows).to_excel(buffer, index=False, header=False)
    buffer.seek(0)
    return RawFile.model_validate({
        "file_id": "0123456789abcdef0123456789abcdef",
        "file_name": file_name,
        "file_type": "xlsx",
        "content": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
                   + base64.b64encode(buffer.read()).decode(),
    })


# The layout from issue #136: named columns in an order Harmony did not expect, and
# blank rows separating one questionnaire from the next.
WELLBEING_SCALES = [
    ["Questionnaire", "Question #", "Question text", "Notes"],
    ["GAD 7", 1, "Feeling nervous, anxious, or on edge", "Multiple Choice (Not at all / Several days)"],
    ["GAD 7", 2, "Not being able to stop or control worrying", "Yes / No / Sometimes"],
    [None, None, None, None],
    ["PHQ-9", 1, "Little interest or pleasure in doing things?", "Multiple Choice (Not at all / Several days)"],
    ["PHQ-9", 2, "Feeling down, depressed, or hopeless?", "Yes / No / Sometimes"],
    ["PHQ-9", 3, "Trouble falling or staying asleep?", "Yes / No / Sometimes"],
]


class TestConvertExcelFluidFormat(unittest.TestCase):

    def test_blank_rows_between_questionnaires_are_ignored(self):
        # Blank rows used to reach the schema as questions with no text, which raised.
        instruments = convert_excel_to_instruments(make_excel(WELLBEING_SCALES))
        self.assertEqual(5, sum(len(instrument.questions) for instrument in instruments))

    def test_question_text_column_is_identified(self):
        instruments = convert_excel_to_instruments(make_excel(WELLBEING_SCALES))
        self.assertEqual("Feeling nervous, anxious, or on edge",
                         instruments[0].questions[0].question_text)

    def test_question_number_column_is_identified(self):
        instruments = convert_excel_to_instruments(make_excel(WELLBEING_SCALES))
        self.assertEqual(["1", "2"], [q.question_no for q in instruments[0].questions])

    def test_one_sheet_can_hold_several_instruments(self):
        instruments = convert_excel_to_instruments(make_excel(WELLBEING_SCALES))
        self.assertEqual(["GAD 7", "PHQ-9"], [i.instrument_name for i in instruments])

    def test_instrument_ids_are_unique(self):
        instruments = convert_excel_to_instruments(make_excel(WELLBEING_SCALES))
        self.assertEqual(len(instruments), len({i.instrument_id for i in instruments}))

    def test_instrument_name_reaches_the_questions(self):
        instruments = convert_excel_to_instruments(make_excel(WELLBEING_SCALES))
        self.assertEqual("PHQ-9", instruments[1].questions[0].instrument_name)

    def test_notes_column_is_kept(self):
        instruments = convert_excel_to_instruments(make_excel(WELLBEING_SCALES))
        self.assertEqual("Yes / No / Sometimes", instruments[0].questions[1].question_intro)

    def test_instrument_name_carries_down_the_block(self):
        # Some spreadsheets name the questionnaire once, on its first row only.
        instruments = convert_excel_to_instruments(make_excel([
            ["Questionnaire", "Question"],
            ["GAD 7", "Feeling nervous, anxious, or on edge"],
            [None, "Not being able to stop or control worrying"],
            ["PHQ-9", "Feeling down, depressed, or hopeless?"],
        ]))
        self.assertEqual(["GAD 7", "PHQ-9"], [i.instrument_name for i in instruments])
        self.assertEqual(2, len(instruments[0].questions))

    def test_alternative_column_names(self):
        instruments = convert_excel_to_instruments(make_excel([
            ["Item", "Response options"],
            ["Feeling nervous, anxious, or on edge", "Not at all / Several days"],
        ]))
        self.assertEqual("Feeling nervous, anxious, or on edge",
                         instruments[0].questions[0].question_text)
        self.assertEqual(["Not at all", "Several days"], instruments[0].questions[0].options)

    def test_rows_above_the_header_are_ignored(self):
        instruments = convert_excel_to_instruments(make_excel([
            ["Wellbeing scales, collected March 2026", None],
            [None, None],
            ["Question", "Options"],
            ["Feeling nervous, anxious, or on edge", "Not at all / Several days"],
        ]))
        self.assertEqual(1, len(instruments[0].questions))
        self.assertEqual("Feeling nervous, anxious, or on edge",
                         instruments[0].questions[0].question_text)

    def test_sheet_without_a_header_is_read_by_position(self):
        # No recognisable header, so fall back to question number, question, options.
        instruments = convert_excel_to_instruments(make_excel([
            [1, "Feeling nervous, anxious, or on edge", "Not at all / Several days"],
            [2, "Not being able to stop or control worrying", "Not at all / Several days"],
        ]))
        self.assertEqual(1, len(instruments))
        self.assertEqual("Feeling nervous, anxious, or on edge",
                         instruments[0].questions[0].question_text)
        self.assertEqual(["Not at all", "Several days"], instruments[0].questions[0].options)

    def test_empty_sheet_yields_no_instruments(self):
        self.assertEqual([], convert_excel_to_instruments(make_excel([[None, None], [None, None]])))

    def test_header_with_no_questions_yields_no_instruments(self):
        self.assertEqual([], convert_excel_to_instruments(make_excel([["Question", "Options"]])))


if __name__ == '__main__':
    unittest.main()

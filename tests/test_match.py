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

from harmony import match_instruments
from harmony.schemas.requests.text import Instrument, Question

questions_en = [Question(question_text="Feeling nervous, anxious, or on edge"),
                Question(question_text="Not being able to stop or control worrying")]
instrument_en = Instrument(questions=questions_en)

questions_pt = [Question(
    question_text="Durante as últimas 2 semanas, com que freqüência você foi incomodado/a pelos problemas abaixo?"),
    Question(
        question_text="Durante as últimas 2 semanas, com que freqüência você foi incomodado/a pelos problemas abaixo?")]
instrument_pt = Instrument(questions=questions_pt, language="pt")

instrument_1 = Instrument.model_validate({
    "file_id": "fd60a9a64b1b4078a68f4bc06f20253c",
    "instrument_id": "7829ba96f48e4848abd97884911b6795",
    "instrument_name": "GAD-7 English",
    "file_name": "GAD-7 EN.pdf",
    "file_type": "pdf",
    "file_section": "GAD-7 English",
    "language": "en",
    "questions": [
        {
            "question_no": "1",
            "question_intro": "Over the last two weeks, how often have you been bothered by the following problems?",
            "question_text": "Feeling nervous, anxious, or on edge",
            "options": [
                "Not at all",
                "Several days",
                "More than half the days",
                "Nearly every day"
            ],
            "source_page": 0
        },
        {
            "question_no": "2",
            "question_intro": "Over the last two weeks, how often have you been bothered by the following problems?",
            "question_text": "Not being able to stop or control worrying",
            "options": [
                "Not at all",
                "Several days",
                "More than half the days",
                "Nearly every day"
            ],
            "source_page": 0
        }
    ]
}
)

instrument_2 = Instrument.model_validate({
    "file_id": "fd60a9a64b1b4078a68f4bc06f20253c",
    "instrument_id": "7829ba96f48e4848abd97884911b6795",
    "instrument_name": "GAD-7 Portuguese",
    "file_name": "GAD-7 PT.pdf",
    "file_type": "pdf",
    "file_section": "GAD-7 Portuguese",
    "language": "en",
    "questions": [
        {
            "question_no": "1",
            "question_intro": "Durante as últimas 2 semanas, com que freqüência você foi incomodado/a pelos problemas abaixo?",
            "question_text": "Sentir-se nervoso/a, ansioso/a ou muito tenso/a",
            "options": [
                "Nenhuma vez",
                "Vários dias",
                "Mais da metade dos dias",
                "Quase todos os dias"
            ],
            "source_page": 0
        },
        {
            "question_no": "2",
            "question_intro": "Durante as últimas 2 semanas, com que freqüência você foi incomodado/a pelos problemas abaixo?",
            "question_text": " Não ser capaz de impedir ou de controlar as preocupações",
            "options": [
                "Nenhuma vez",
                "Vários dias",
                "Mais da metade dos dias",
                "Quase todos os dias"
            ],
            "source_page": 0
        }
    ]
}
)


class TestMatch(unittest.TestCase):

    def test_single_instrument_simple(self):
        all_questions, similarity_with_polarity, query_similarity, new_vectors_dict = match_instruments([instrument_en])
        self.assertEqual(2, len(all_questions))
        self.assertEqual(2, len(similarity_with_polarity))
        self.assertLess(0.99, similarity_with_polarity[0][0])
        self.assertGreater(0.95, similarity_with_polarity[0][1])
        self.assertLess(0.99, similarity_with_polarity[1][1])
        self.assertGreater(0.95, similarity_with_polarity[1][0])

    def test_two_instruments_simple(self):
        all_questions, similarity_with_polarity, query_similarity, new_vectors_dict = match_instruments(
            [instrument_en, instrument_pt])
        self.assertEqual(4, len(all_questions))
        self.assertEqual(4, len(similarity_with_polarity))
        self.assertLess(0.99, similarity_with_polarity[0][0])

    def test_single_instrument_full_metadata(self):
        all_questions, similarity_with_polarity, query_similarity, new_vectors_dict = match_instruments([instrument_1])
        self.assertEqual(2, len(all_questions))
        self.assertEqual(2, len(similarity_with_polarity))
        self.assertLess(0.99, similarity_with_polarity[0][0])
        self.assertGreater(0.95, similarity_with_polarity[0][1])
        self.assertLess(0.99, similarity_with_polarity[1][1])
        self.assertGreater(0.95, similarity_with_polarity[1][0])

    def test_two_instruments_full_metadata(self):
        all_questions, similarity_with_polarity, query_similarity, new_vectors_dict = match_instruments(
            [instrument_1, instrument_2])
        self.assertEqual(4, len(all_questions))
        self.assertEqual(4, len(similarity_with_polarity))
        self.assertLess(0.99, similarity_with_polarity[0][0])


if __name__ == '__main__':
    unittest.main()

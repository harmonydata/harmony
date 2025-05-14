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

from harmony import create_instrument_from_list, import_instrument_into_harmony_web


class TestCreateInstrument(unittest.TestCase):

    def test_single_instrument_simple(self):
        instrument = create_instrument_from_list(["question A", "question B"], [])
        self.assertEqual(2, len(instrument.questions))

    def test_single_instrument_simple_2(self):
        instrument = create_instrument_from_list(["question A", "question B", "question C"], [],
                                                 instrument_name="potato")
        self.assertEqual(3, len(instrument.questions))
        self.assertEqual("potato", instrument.instrument_name)

    def test_single_instrument_with_answers(self):
        instrument = create_instrument_from_list(["question A", "question B", "question C"], ["Never", "Rarely", "Less than 2 times a week", "Everyday"],
                                                 instrument_name="potato")
        self.assertEqual(3, len(instrument.questions))
        self.assertEqual(4, len(instrument.questions[0].options))
        self.assertEqual(4, len(instrument.questions[1].options))
        self.assertEqual(4, len(instrument.questions[2].options))
        self.assertEqual("potato", instrument.instrument_name)
    def test_single_instrument_send_to_web(self):
        instrument = create_instrument_from_list(["question A", "question B"], [])
        web_url = import_instrument_into_harmony_web(instrument)
        self.assertIn("harmonydata.ac.uk", web_url)

    def test_single_instrument_with_options(self):
        question_texts = ["How often do you feel anxious?", "Do you have trouble sleeping?"]
        options_map = {
            "How often do you feel anxious?": ["Never", "Sometimes", "Often", "Always"],
            "Do you have trouble sleeping?": ["Yes", "No"]
        }
        instrument = create_instrument_from_list(question_texts, options_map=options_map)

        self.assertEqual(len(instrument.questions), 2)
        self.assertEqual(instrument.questions[0].options, ["Never", "Sometimes", "Often", "Always"])
        self.assertEqual(instrument.questions[1].options, ["Yes", "No"])

if __name__ == '__main__':
    unittest.main()

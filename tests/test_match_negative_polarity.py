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

questions_en = [Question(question_text="I feel nervous"),
                Question(question_text="I don't feel nervous")]
instrument_en = Instrument(questions=questions_en)


class TestMatch(unittest.TestCase):

    def test_single_instrument_with_negation_on_as_default(self):
        match_response = match_instruments([instrument_en])
        self.assertEqual(2, len(match_response.questions))
        self.assertEqual(2, len(match_response.similarity_with_polarity))
        self.assertLess(0.99, match_response.similarity_with_polarity[0][0])
        self.assertGreater(0, match_response.similarity_with_polarity[0][1])
        self.assertLess(0.99, match_response.similarity_with_polarity[1][1])
        self.assertGreater(0, match_response.similarity_with_polarity[1][0])

    def test_single_instrument_without_negation(self):
        match_response = match_instruments([instrument_en],
                                           is_negate=False)
        self.assertEqual(2, len(match_response.questions))
        self.assertEqual(2, len(match_response.similarity_with_polarity))
        self.assertLess(0.99, match_response.similarity_with_polarity[0][0])
        self.assertLess(0, match_response.similarity_with_polarity[0][1])
        self.assertLess(0.99, match_response.similarity_with_polarity[1][1])
        self.assertLess(0, match_response.similarity_with_polarity[1][0])


if __name__ == '__main__':
    unittest.main()

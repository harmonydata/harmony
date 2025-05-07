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
from harmony import create_instrument_from_list


class TestInstrumentToInstrumentSimilarity(unittest.TestCase):

    def test_same_instrument_twice(self):
        gad_2 = create_instrument_from_list(
            ["Feeling nervous, anxious, or on edge", "Not being able to stop or control worrying"])
        instruments = [gad_2, gad_2]

        match_response = match_instruments(
            instruments)

        self.assertEqual(4, len(match_response.questions))
        self.assertEqual(4, len(match_response.similarity_with_polarity))
        self.assertEqual(1, len(match_response.instrument_to_instrument_similarities))
        self.assertEqual(1, match_response.instrument_to_instrument_similarities[0].precision)
        self.assertEqual(1, match_response.instrument_to_instrument_similarities[0].recall)
        self.assertEqual(1, match_response.instrument_to_instrument_similarities[0].f1)

    def test_two_instruments_one_a_subset_of_another(self):
        gad_2 = create_instrument_from_list(
            ["Feeling nervous, anxious, or on edge", "Not being able to stop or control worrying"])
        gad_1 = create_instrument_from_list(
            ["Feeling nervous, anxious, or on edge"])
        instruments = [gad_2, gad_1]

        match_response = match_instruments(
            instruments)
        self.assertEqual(3, len(match_response.questions))
        self.assertEqual(3, len(match_response.similarity_with_polarity))
        self.assertEqual(1, len(match_response.instrument_to_instrument_similarities))
        self.assertEqual(1, match_response.instrument_to_instrument_similarities[0].precision)
        self.assertEqual(0.5, match_response.instrument_to_instrument_similarities[0].recall)
        self.assertEqual(0.75, match_response.instrument_to_instrument_similarities[0].f1)


if __name__ == '__main__':
    unittest.main()

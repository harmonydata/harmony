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
import numpy as np

from harmony.util.instrument_helper import create_instrument_from_list

sys.path.append("../src")

from harmony import match_instruments, example_instruments


class ResponseOptionsSimilarity(unittest.TestCase):
    def setUp(self):
        self.ces_d_english = example_instruments["CES_D English"]
        self.gad_7_english = example_instruments["GAD-7 English"]

    def test_responses_ces_d(self):
        match = match_instruments([self.ces_d_english])
        sim = match.response_options_similarity

        # check dimensions
        n, m = sim.shape
        self.assertEqual(n, m)
        self.assertEqual(n, (len(self.ces_d_english.questions)))
        self.assertEqual(m, (len(self.ces_d_english.questions)))

        # check between 0 and 1
        self.assertTrue(np.all(0 <= sim))
        self.assertTrue(np.all(sim <= 1))

        # assert that the similarity matrix has 1s on its diagonals
        self.assertTrue(np.allclose(np.diag(sim), 1.))
        # assert that the similarity matrix is symmetric
        self.assertTrue(np.allclose(sim, sim.T))
        # assert that the similarity matrix is not empty
        self.assertTrue(sim.size > 0)

    def test_responses_gad_7(self):
        match = match_instruments([self.gad_7_english])
        sim = match.response_options_similarity

        # check dimensions
        n, m = sim.shape
        self.assertEqual(n, m)
        self.assertEqual(n, (len(self.gad_7_english.questions)))
        self.assertEqual(m, (len(self.gad_7_english.questions)))

        # check between 0 and 1
        self.assertTrue(np.all(0 <= sim))
        self.assertTrue(np.all(sim <= 1))

        # assert that the similarity matrix has 1s on its diagonals
        self.assertTrue(np.allclose(np.diag(sim), 1.))
        # assert that the similarity matrix is symmetric
        self.assertTrue(np.allclose(sim, sim.T))
        # assert that the similarity matrix is not empty
        self.assertTrue(sim.size > 0)

    def test_responses_both(self):
        match = match_instruments([self.ces_d_english, self.gad_7_english])
        sim = match.response_options_similarity

        # check dimensions
        n, m = sim.shape
        self.assertEqual(n, m)
        self.assertEqual(n, (len(self.ces_d_english.questions)) + len(self.gad_7_english.questions))
        self.assertEqual(m, (len(self.ces_d_english.questions)) + len(self.gad_7_english.questions))

        # check between 0 and 1
        self.assertTrue(np.all(0 <= sim))
        self.assertTrue(np.all(sim <= 1))

        # assert that the similarity matrix has 1s on its diagonals
        self.assertTrue(np.allclose(np.diag(sim), 1.))
        # assert that the similarity matrix is symmetric
        self.assertTrue(np.allclose(sim, sim.T))
        # assert that the similarity matrix is not empty
        self.assertTrue(sim.size > 0)

    def test_empty_responses(self):
        # when the responses are empty, match_instruments returns all 1s
        match = match_instruments([create_instrument_from_list(["potato", "tomato", "radish"], instrument_name="veg")])
        sim = match.response_options_similarity
        self.assertTrue(np.all(sim == 1))


if __name__ == '__main__':
    unittest.main()

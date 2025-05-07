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

sys.path.append("../src")

from harmony import match_instruments, example_instruments
from harmony.util.instrument_helper import create_instrument_from_list


class TestTopics(unittest.TestCase):
    def setUp(self):
        self.veg = create_instrument_from_list(
            ["I like potatoes", "I like tomatoes", "I do not like radish"], instrument_name="veg")

    def test_topic_in_question(self):
        match = match_instruments([self.veg], topics=["potato", "tomato", "radish"])
        self.assertEqual(match.questions[0].topics, ["potato"])
        self.assertEqual(match.questions[1].topics, ["tomato"])
        self.assertEqual(match.questions[2].topics, ["radish"])

    def test_unrelated_topic_to_question(self):
        match = match_instruments([self.veg], topics=["apple", "pear", "orange"])
        self.assertTrue(not match.questions[0].topics)
        self.assertTrue(not match.questions[1].topics)
        self.assertTrue(not match.questions[2].topics)

    def test_empty_topics(self):
        match = match_instruments([self.veg])
        for idx, question in enumerate(match.questions):
            self.assertTrue(not question.topics)


if __name__ == '__main__':
    unittest.main()

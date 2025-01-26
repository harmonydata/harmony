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

from harmony.matching.cluster import cluster_questions
from harmony.schemas.requests.text import Question


class TestCluster(unittest.TestCase):
    def setUp(self):
        self.all_questions_real = [Question(question_no="1", question_text="Feeling nervous, anxious, or on edge"),
                                   Question(question_no="2",
                                            question_text="Not being able to stop or control worrying"),
                                   Question(question_no="3",
                                            question_text="Little interest or pleasure in doing things"),
                                   Question(question_no="4", question_text="Feeling down, depressed, or hopeless"),
                                   Question(question_no="5",
                                            question_text="Trouble falling/staying asleep, sleeping too much"), ]

    def test_cluster(self):
        clusters_out, score_out = cluster_questions(self.all_questions_real, 2, False)
        assert (len(clusters_out) == 5)
        assert score_out


if __name__ == '__main__':
    unittest.main()

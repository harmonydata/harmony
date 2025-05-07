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

from harmony import match_instruments, example_instruments
from harmony.matching.generate_cluster_topics import generate_cluster_topics
from harmony.matching.affinity_propagation_clustering import cluster_questions_affinity_propagation

from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0


class TestGenerateClusterTopics(unittest.TestCase):
    def setUp(self):
        self.gad_en = example_instruments["GAD-7 English"]
        self.gad_pt = example_instruments["GAD-7 Portuguese"]

    def test_topics_english(self):
        match_response = match_instruments([self.gad_en])
        clusters = cluster_questions_affinity_propagation(match_response.questions,
                                                          match_response.similarity_with_polarity)

        self.assertLess(1, len(clusters[0].keywords))
        self.assertLess(1, len(clusters[1].keywords))
        self.assertLess(1, len(clusters[2].keywords))
        self.assertLess(1, len(clusters[3].keywords))

        self.assertGreater(6, len(clusters[0].keywords))
        self.assertGreater(6, len(clusters[1].keywords))
        self.assertGreater(6, len(clusters[2].keywords))
        self.assertGreater(6, len(clusters[3].keywords))
        #
        # self.assertEqual(set(clusters[0].keywords), set(['feeling', 'annoyed', 'easily', 'becoming', 'irritable']))
        # self.assertEqual(set(clusters[1].keywords), set(['worrying', 'much', 'different']))
        # self.assertEqual(set(clusters[2].keywords), set(['trouble', 'relaxing', 'hard', 'restless']))
        # self.assertEqual(set(clusters[3].keywords), set(['along', 'care', 'checked']))

    def test_topics_portuguese(self):
        match_response = match_instruments([self.gad_pt])
        clusters = cluster_questions_affinity_propagation(match_response.questions,
                                                          match_response.similarity_with_polarity)

        self.assertLess(1, len(clusters[0].keywords))
        self.assertLess(1, len(clusters[1].keywords))

        self.assertGreater(6, len(clusters[0].keywords))
        self.assertGreater(6, len(clusters[1].keywords))
        #
        # self.assertEqual(set(clusters[0].keywords), set(['preocupar', 'diversas', 'coisas']))
        # self.assertEqual(set(clusters[1].keywords), set(['ficar', 'relaxar', 'dificuldade', 'aborrecido']))

    def test_topics_english_portuguese(self):
        match_response = match_instruments([self.gad_en, self.gad_pt])
        clusters = cluster_questions_affinity_propagation(match_response.questions,
                                                          match_response.similarity_with_polarity)

        self.assertLess(1, len(clusters[0].keywords))
        self.assertLess(1, len(clusters[1].keywords))
        self.assertLess(1, len(clusters[2].keywords))
        self.assertLess(1, len(clusters[3].keywords))

        self.assertGreater(6, len(clusters[0].keywords))
        self.assertGreater(6, len(clusters[1].keywords))
        self.assertGreater(6, len(clusters[2].keywords))
        self.assertGreater(6, len(clusters[3].keywords))
        #
        # self.assertEqual(set(clusters[0].keywords), set(['anxious', 'nervous', 'edge', 'nervoso']))
        # self.assertEqual(set(clusters[1].keywords), set(['worrying', 'coisas', 'preocupar']))
        # self.assertEqual(set(clusters[2].keywords), set(['trouble', 'relaxing', 'dificuldade', 'relaxar']))
        # self.assertEqual(set(clusters[3].keywords), set(['aborrecido', 'facilmente', 'irritado', 'annoyed', 'becoming']))
        # self.assertEqual(set(clusters[4].keywords), set(['acontecer', 'algo', 'medo']))
        # self.assertEqual(set(clusters[5].keywords), set(['along', 'difficult']))

    def test_langdetect_english_portuguese(self):
        for question in self.gad_en.questions:
            try:
                lang = detect(question.question_text)
            except:
                pass

            self.assertEqual(lang, "en")

        for question in self.gad_pt.questions:
            try:
                lang = detect(question.question_text)
            except:
                pass

            self.assertEqual(lang, "pt")


if __name__ == '__main__':
    unittest.main()

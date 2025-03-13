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

        clusters = cluster_questions_affinity_propagation(
            match_response.questions,
            match_response.similarity_with_polarity
        )
        topics = generate_cluster_topics(clusters)

        self.assertEqual(
            topics, 
            [
                ['feeling', 'easily', 'annoyed', 'irritable', 'becoming'],
                ['worrying', 'much', 'different'],
                ['relaxing', 'trouble', 'restless', 'sit'],
                ['people', 'problems']
            ]    
        )
        self.assertEqual(len(topics), len(clusters))

    def test_topics_portuguese(self):
        match_response = match_instruments([self.gad_pt])

        clusters = cluster_questions_affinity_propagation(
            match_response.questions,
            match_response.similarity_with_polarity
        )
        topics = generate_cluster_topics(clusters)

        self.assertEqual(
            topics, 
            [
                ['preocupar', 'diversas', 'coisas'], 
                ['ficar', 'relaxar', 'dificuldade', 'aborrecido']
            ]    
        )
        self.assertEqual(len(topics), len(clusters))

    def test_topics_english_portuguese(self):
        match_response = match_instruments([self.gad_en, self.gad_pt])

        clusters = cluster_questions_affinity_propagation(
            match_response.questions,
            match_response.similarity_with_polarity
        )
        topics = generate_cluster_topics(clusters)

        self.assertEqual(
            topics, 
            [
                ['edge', 'anxious', 'nervous', 'nervoso'], 
                ['worrying', 'diversas', 'coisas', 'preocupar'], 
                ['trouble', 'relaxing', 'dificuldade', 'relaxar'], 
                ['irritado', 'aborrecido', 'facilmente', 'easily', 'annoyed'],
                ['medo', 'acontecer', 'algo'], 
                ['made', 'home']
            ]   
        )
        self.assertEqual(len(topics), len(clusters))

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

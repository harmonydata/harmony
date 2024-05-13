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

import numpy as np
from sentence_transformers import SentenceTransformer

from harmony import match_instruments
from harmony.schemas.requests.text import Instrument, Question

questions_en = [Question(question_text="Feeling nervous, anxious, or on edge"),
                Question(question_text="Not being able to stop or control worrying")]
instrument_en = Instrument(questions=questions_en)

mhc_metadata = [{'topics': ['alcohol use']},
                {'topics': ['mental illness',
                            'anxiety',
                            'depression',
                            'self-harm and suicide']}
                ]

mhc_questions_as_text = ["Have you ever felt annoyed by criticism of your drinking?", "Have you recently"]

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

mhc_embeddings = model.encode(np.asarray(mhc_questions_as_text))

mhc_questions = [Question(question_text=t) for t in mhc_questions_as_text]


class TestMatchMhc(unittest.TestCase):

    def test_single_instrument_simple(self):
        all_questions, similarity_with_polarity, query_similarity, new_vectors_dict = match_instruments([instrument_en],
                                                                                                        mhc_questions=mhc_questions,
                                                                                                        mhc_embeddings=mhc_embeddings,
                                                                                                        mhc_all_metadatas=mhc_metadata)
        self.assertEqual(2, len(all_questions))

        topics = all_questions[0].topics_strengths
        top_topic = list(topics)[0]
        self.assertEqual("alcohol use", top_topic)
        self.assertLess(0.1, topics[top_topic])


if __name__ == '__main__':
    unittest.main()

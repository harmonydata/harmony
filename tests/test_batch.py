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
import numpy

sys.path.append("../src")

from harmony.matching.default_matcher import convert_texts_to_vector

class createModel:
    def encode(self, sentences, convert_to_numpy=True):
        # Generate a dummy embedding with 768 dimensions for each sentence
        return numpy.array([[1] * 768] * len(sentences))



model = createModel()

class TestBatching(unittest.TestCase):
    def test_convert_texts_to_vector_with_batching(self):
        # Create a list of 10 dummy texts
        texts = ["text" + str(i) for i in range(10)]


        batch_size = 5
        max_batches = 2
        embeddings = convert_texts_to_vector(texts, batch_size=batch_size, max_batches=max_batches)


        self.assertEqual(embeddings.shape[0], 10)


        self.assertEqual(embeddings.shape[1], 384)


if __name__ == "__main__":
    unittest.main()

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
from harmony.matching.negator import negate


class TestNegation(unittest.TestCase):

    def test_simple_example(self):
        text = "I never feel depressed"
        print(negate(text, "en"))
        self.assertEqual("I feel depressed", negate(text, "en"))

    def test_simple_example_neg(self):
        text = "I feel depressed"
        print(negate(text, "en"))
        self.assertEqual("never I feel depressed", negate(text, "en"))

    def test_verb_can_negation_en(self):
        text = "I can't feel happy"
        self.assertEqual("I can feel happy", negate(text, "en"))

    def test_verb_will_negation_en(self):
        text = "I won't feel happy"
        self.assertEqual("I will feel happy", negate(text, "en"))

    def test_verb_shall_negation_en(self):
        text = "I shan't feel happy"
        self.assertEqual("I shall feel happy", negate(text, "en"))

    def test_simple_example_pt(self):
        text = "eu me sinto deprimido"
        self.assertEqual("não eu me sinto deprimido", negate(text, "pt"))

    def test_simple_example_pt_neg(self):
        text = "não eu me sinto deprimido"
        self.assertEqual(" eu me sinto deprimido", negate(text, "pt"))

    def test_simple_example_es(self):
        text = "mi siento deprimido"
        self.assertEqual("no mi siento deprimido", negate(text, "es"))

    def test_simple_example_de(self):
        text = "Ich fühle mich nicht deprimiert"
        self.assertEqual("Ich fühle mich deprimiert", negate(text, "de"))

    def test_simple_example_de_neg(self):
        text = "Ich fühle mich deprimiert"
        self.assertEqual("nicht Ich fühle mich deprimiert", negate(text, "de"))

    def test_simple_example_it(self):
        text = "mi sento depresso"
        self.assertEqual("non mi sento depresso", negate(text, "it"))
    #
    # def test_simple_example_fr(self):
    #     text = "je me sens deprimé"
    #     self.assertEqual("ne pas je me sens deprimé", negate(text, "fr"))
    #
    # def test_simple_example_fr(self):
    #     text = "Je suis content"
    #     self.assertEqual("Je ne suis pas content", negate(text, "fr"))


if __name__ == '__main__':
    unittest.main()

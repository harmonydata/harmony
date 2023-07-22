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

import spacy

nlp = spacy.blank("en")


def get_change_en(doc) -> dict:
    """
    Identify how to change an English sentence from positive to negative or vice versa.
    :param doc:
    :return:
    """
    for tok in doc:
        if tok.text.lower() in {"always", "rather", "really", "very", "totally", "utterly", "absolutely", "completely",
                                "frequently", "often", "sometimes", "generally", "usually"}:
            return {tok.i: ("replace", "never")}
        if tok.text.lower() in {"never", "not", "n't"}:
            return {tok.i: ("replace", "")}
        if tok.text.lower() in {"cannot"}:
            return {tok.i: ("replace", "can")}
    result = {}
    for tok in doc:
        if tok.text.lower() in {"is", "are", "am", "are", "was", "were", "has", "have", "had"}:
            result[tok.i] = "insert_after", "not"
    if len(result) > 0:
        return result
    #     print ("fallback", doc)
    return {0: ("insert_before", "never")}


def get_change_pt(doc) -> dict:
    """
    Identify how to change a Portuguese sentence from positive to negative or vice versa.
    :param doc:
    :return:
    """
    for tok in doc:
        if tok.text.lower() in {"sempre", "bastante", "realmente", "muito", "totalmente", "totalmente", "absolutamente",
                                "completamente",
                                "frequentemente", "frequentemente", "vezes", "geralmente", "geralmente"}:
            return {tok.i: ("replace", "nunca")}
        if tok.text.lower() in {"nunca", "jamais", "nem", "não"}:
            return {tok.i: ("replace", "")}
    result = {}
    if len(result) > 0:
        return result
    return {0: ("insert_before", "não")}


def negate(text: str, language: str) -> str:
    """
    Converts negative sentences to pos and vice versa.
    Not meant to generate 100% accurate natural language, it's to go into transformer model and is not shown to a human.
    :param text:
    :param language: "en" or "pt"
    :return: the sentence negated
    """
    doc = nlp(text)

    if language == "pt":
        changes = get_change_pt(doc)
    else:
        changes = get_change_en(doc)

    text = ""
    for tok in doc:
        this_token_text = tok.text
        if tok.i in changes:
            change_operation, change_text = changes[tok.i]
            if change_operation == "replace":
                this_token_text = change_text
            elif change_operation == "insert_after":
                this_token_text += " " + change_text
            elif change_operation == "insert_before":
                this_token_text = change_text + " " + this_token_text
        text += this_token_text + tok.whitespace_
    return text
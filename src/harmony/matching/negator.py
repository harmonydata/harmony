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

import re

re_word = re.compile(r'(?i)(\S+)')


def tokenise(text):
    tokens = list(re_word.finditer(text))

    return tokens


def get_change_en(token_texts_lower: list) -> dict:
    """
    Identify how to change an English sentence from positive to negative or vice versa.
    :param doc:
    :return:
    """
    for token_idx, token_text_lower in enumerate(token_texts_lower):
        if token_text_lower in {"always", "rather", "really", "very", "totally", "utterly", "absolutely", "completely",
                                "frequently", "often", "sometimes", "generally", "usually"}:
            return {token_idx: ("replace", "never")}
        # Team Cheemu: added these if statements to handle negative contractions (eg. can't, won't, shan't)
        if token_text_lower == "can't":
            return {token_idx: ("replace", "can")}
        if token_text_lower == "won't":
            return {token_idx: ("replace", "will")}
        if token_text_lower == "shan't":
            return {token_idx: ("replace", "shall")}
        if token_text_lower in {"never", "not", "don't"}:
            return {token_idx: ("replace", "")}
        if token_text_lower in {"cannot"}:
            return {token_idx: ("replace", "can")}
    result = {}
    for token_idx, token_text_lower in enumerate(token_texts_lower):
        if token_text_lower in {"is", "are", "am", "are", "was", "were", "has", "have", "had"}:
            result[token_idx] = "insert_after", "not"
    if len(result) > 0:
        return result
    #     print ("fallback", doc)
    return {0: ("insert_before", "never")}


def get_change_pt(token_texts_lower: list) -> dict:
    """
    Identify how to change a Portuguese sentence from positive to negative or vice versa.
    :param doc:
    :return:
    """
    for token_idx, token_text_lower in enumerate(token_texts_lower):
        if token_text_lower in {"sempre", "bastante", "realmente", "muito", "totalmente", "totalmente", "absolutamente",
                                "completamente",
                                "frequentemente", "frequentemente", "vezes", "geralmente", "geralmente"}:
            return {token_idx: ("replace", "nunca")}
        if token_text_lower in {"nunca", "jamais", "nem", "não"}:
            return {token_idx: ("replace", "")}
    result = {}
    if len(result) > 0:
        return result
    return {0: ("insert_before", "não")}


def get_change_es(token_texts_lower: list) -> dict:
    """
    # Team Cheemu: Identify how to change a Spanish sentence from positive to negative or vice versa.
    :param doc:
    :return:
    """
    for token_idx, token_text_lower in enumerate(token_texts_lower):
        if token_text_lower in {"siempre", "bastante", "realmente", "muy", "mucho", "totalmente", "totalmente",
                                "absolutamente",
                                "completamente",
                                "frecuentemente", "frequentemente", "veces"}:
            return {token_idx: ("replace", "nunca")}
        if token_text_lower in {"nunca", "jamás", "ni", "no"}:
            return {token_idx: ("replace", "")}
    result = {}
    if len(result) > 0:
        return result
    return {0: ("insert_before", "no")}


def get_change_it(token_texts_lower: list) -> dict:
    """
    # Team Cheemu: Identify how to change an Italian sentence from positive to negative or vice versa.
    :param doc:
    :return:
    """
    for token_idx, token_text_lower in enumerate(token_texts_lower):
        if token_text_lower in {"sempre", "abbastanza", "realmente", "davvero", "veramente", "molto", "molta", "molti",
                                "molte", "totalmente", "assolutamente",
                                "completamente",
                                "frequentemente", "qualche volta", "a volte", "ogni tanto"}:
            return {token_idx: ("replace", "mai")}
        if token_text_lower in {"mai", "né", "non", "nessuno", "nulla", "niente"}:
            return {token_idx: ("replace", "")}
    result = {}
    for token_idx, token_text_lower in enumerate(token_texts_lower):
        if token_text_lower in {"è", "sono", "ero", "erano", "avevano", "avevo", "ho avuto", "sono stato", "sono stata",
                                "sono stati", "siamo stati", "sono state"}:
            result[token_idx] = "insert_before", "non"
    if len(result) > 0:
        return result
    return {0: ("insert_before", "non")}


def get_change_de(token_texts_lower: list) -> dict:
    """
    # Team Cheemu: Identify how to change a German sentence from positive to negative or vice versa.
    :param doc:
    :return:
    """
    for token_idx, token_text_lower in enumerate(token_texts_lower):
        if token_text_lower in {"immer", "ziemlich", "wirklich", "sehr", "viel", "total", "absolut",
                                "vollständig",
                                "häufig", "manchmal"}:
            return {token_idx: ("replace", "nie")}
        if token_text_lower in {"nie", "niemals", "weder", "nicht"}:
            return {token_idx: ("replace", "")}
    result = {}
    if len(result) > 0:
        return result
    return {0: ("insert_before", "nicht")}


# if we had time: add functionality to handle german word order using Spacy


def get_change_fr(token_texts_lower: list) -> dict:
    """
    # Team Cheemu: Identify how to change a French sentence from positive to negative or vice versa.
    :param doc:
    :return:
    """
    for token_idx, token_text_lower in enumerate(token_texts_lower):
        if token_text_lower in {"toujours", "assez", "vraiment", "très", "beaucoup de", "totalement", "absolumment",
                                "complètement", "plus", "trop de", "plein de",
                                "souvent", "de temps en temps"}:
            return {token_idx: ("replace", "nie")}
        if token_text_lower in {"personne", "jamais", "ni", "rien", "pas", "non", "ne", "n'", "nulle", "aucun",
                                "aucune", "guère"}:
            return {token_idx: ("replace", "")}
    result = {}
    if len(result) > 0:
        return result
    return {0: ("insert_before", "ne pas")}


def negate(text: str, language: str) -> str:
    """
    Converts negative sentences to positive and vice versa.
    Not meant to generate 100% accurate natural language, it's to go into transformer model and is not shown to a human.
    :param text:
    :param language:
    "en" for English, "pt" for Portuguese, "es" for Spanish, "it" for Italian, "de" for German, "fr" for French.
    :return: the sentence negated
    """
    tokens = tokenise(text)
    token_texts = [token.group() for token in tokens]
    token_texts_lower = [token.group().lower() for token in tokens]

    if language == "pt":
        changes = get_change_pt(token_texts_lower)
    elif language == "es":
        changes = get_change_es(token_texts_lower)
    elif language == "it":
        changes = get_change_it(token_texts_lower)
    elif language == "fr":
        changes = get_change_fr(token_texts_lower)
    elif language == "de":
        changes = get_change_de(token_texts_lower)
    else:
        changes = get_change_en(token_texts_lower)

    for token_idx, match in reversed(list(enumerate(tokens))):
        if token_idx in changes:
            change_operation, change_text = changes[token_idx]
            if change_operation == "replace":
                prefix  = text[:match.start()]
                suffix = text[match.end():]
                if prefix.endswith(" ") and suffix.startswith(" ") and change_text  == "":
                    prefix = prefix[:-1]
                text = prefix + change_text + suffix
            elif change_operation == "insert_after":
                prefix = text[:match.end()]
                suffix = text[match.end():]
                if prefix != "" and not prefix.endswith(" "):
                    prefix += " "
                if suffix != "" and not suffix.startswith(" "):
                    suffix = " " + suffix
                text = prefix + change_text + suffix
            elif change_operation == "insert_before":
                prefix = text[:match.start()]
                suffix = text[match.start():]
                if prefix != "" and not prefix.endswith(" "):
                    prefix += " "
                if suffix != "" and not suffix.startswith(" "):
                    suffix = " " + suffix
                text = prefix + change_text + suffix
    return text


if __name__ == "__main__":
    text = "I never feel depressed"
    print(negate(text, "en"))

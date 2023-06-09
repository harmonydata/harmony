from spacy.matcher import Matcher

from harmony.parsing.text_extraction.options_words import OPTIONS_WORDS

def create_options_matcher(nlp):
    options_matcher = Matcher(nlp.vocab)
    patterns = []

    for doc in nlp.pipe(OPTIONS_WORDS):
        pattern = []
        for tok in doc:
            if len(pattern) > 0:
                pattern.append({"IS_SPACE": True, "OP": "*"})
            pattern.append({"LOWER": tok.text.lower()})
        patterns.append(pattern)

    options_matcher.add("MWE", patterns)

    return options_matcher

import re
import unicodedata

import spacy
from spacy.language import Language
from spacy.tokens import Span
from spacy.tokens import Token

from harmony.parsing.text_extraction.spacy_options_matcher import create_options_matcher

re_contains_num = re.compile(r'.*\d.*')
re_contains_number = re.compile(r'(?i)^[a-z]*\d*[0-9]\d*[a-z]*$|^[a-z]\)$')
re_single_letter = re.compile(r'^[a-z]$')

Token.set_extension("is_all_letters", default=False)
Token.set_extension("is_numbered_bullet", default=False)

# Ground truth: 0 = nothing, 1 = option, 2 = question
Span.set_extension("ground_truth", default=0)

EXTRA_CHARACTERS_ALLOWED = {"(", ")", ",", "-", "—", "'", "“", "”", "‘", "’", '"', ";"}
ALLOWED_NUMBER_EXCEPTIONS = {"day", "time", "hour", "week", "month", "year", "portion", "wks", "wk", "mths", "mth",
                             "days", "times", "hours", "weeks", "months", "years", "portions",
                             "yrs", "yr", "h", "hs", "d", "ds",
                             "dia", "vez", "hora", "semana", "mês", "ano", "porção",
                             "dias", "vezes", "horas", "semanas", "mêses", "anos", "porçãos"}

language_to_options_matcher = {}
language_to_model = {}


# Define getter function
def get_is_all_letters(token):
    is_all_letters = True
    for c in token.text:
        if unicodedata.category(c)[0:1] != "L" and c not in EXTRA_CHARACTERS_ALLOWED:
            is_all_letters = False

    # Exception for 5 vezes, 4 days, 2 times, etc...
    # 1-2 horas
    is_permissible_numeric_exception = False
    if not is_all_letters and token.i < len(token.doc) - 1 and re_contains_num.match(token.text):
        if token.doc[token.i + 1].text.lower() in ALLOWED_NUMBER_EXCEPTIONS:
            is_permissible_numeric_exception = True
        # exception for 1-2 horas
        if token.i < len(token.doc) - 3 and re_contains_num.match(token.text) and token.doc[token.i + 1].text == "-" \
                and re_contains_num.match(token.doc[
                                              token.i + 2].text) and token.doc[
            token.i + 3].text.lower() in ALLOWED_NUMBER_EXCEPTIONS:
            is_permissible_numeric_exception = True

    if is_all_letters or is_permissible_numeric_exception or token.text in EXTRA_CHARACTERS_ALLOWED or (
            token.is_space and not token.text.count("\n") > 1):
        return True
    return False


def get_is_numbered_bullet(token):
    if token.i > 1:
        if "\n" in token.doc[token.i - 1].text and re_contains_number.match(token.text):
            return True
    if token.i > 2:
        if "\n" in token.doc[token.i - 2].text and re_single_letter.match(token.doc[token.i - 1].text) \
                and token.text in (")", "."):
            return True

    return False


@Language.component("set_is_numbered_bullet")
def set_is_numbered_bullet(doc):
    for token in doc:
        token._.is_numbered_bullet = get_is_numbered_bullet(token)
    return doc


def get_is_question(span):
    if len(span) > 1:
        return span[-1].text == "?"
    return False


Span.set_extension("is_question_mark", getter=get_is_question)


def get_preceding_bullet_value(span):
    for i in range(span.start + 1, span.start - 3, -1):
        if i >= span.end:
            continue
        if i >= 0 and i < len(span.doc):
            if span.doc[i]._.is_numbered_bullet:
                if span.doc[i].text in (")", "."):
                    return span.doc[i - 1].text + span.doc[i].text
                return span.doc[i].text
    return None


Span.set_extension("preceding_bullet_value", getter=get_preceding_bullet_value)


@Language.component("mark_is_all_letters")
def mark_is_all_letters(doc):
    for token in doc:
        if get_is_all_letters(token):
            token._.is_all_letters = True
    return doc


@Language.component("get_candidate_questions_and_mark_as_spans")
def get_candidate_questions_and_mark_as_spans(doc):
    spans = []
    start_from = 0
    for tok in doc[1:]:
        if tok.i <= start_from:
            continue
        if tok._.is_all_letters and not doc[tok.i - 1]._.is_all_letters:
            for tok2 in doc[tok.i + 1:]:
                if not tok2._.is_all_letters:

                    # A question must have at least one alphabetic character
                    if any([token.is_alpha for token in doc[tok.i: tok2.i]]):

                        start_point = tok.i
                        end_point = tok2.i
                        # If there was a trailing full stop, include that in the question
                        if tok2.text in (".", "?"):
                            end_point = tok2.i + 1

                        if start_point > 0 and end_point < len(doc) and end_point > start_point:
                            spans.append(Span(doc, tok.i, end_point, label="CANDIDATE_QUESTION"))
                    start_from = tok2.i
                    break

    doc.spans["CANDIDATE_QUESTION"] = spans

    return doc


@Language.component("mark_candidate_options_as_spans")
def mark_candidate_options_as_spans(doc):
    options_matcher = language_to_options_matcher[doc.lang_]
    spans = []
    options_matches = options_matcher(doc)
    is_token_seen = set()
    for options_match_id, start, end in sorted(options_matches, key=lambda m: m[2] - m[1], reverse=True):
        if any([i in is_token_seen for i in range(start, end)]):
            continue
        spans.append(Span(doc, start, end, label="CANDIDATE_OPTION"))
        for i in range(start, end):
            is_token_seen.add(i)

    doc.spans["CANDIDATE_OPTION"] = sorted(spans, key=lambda s: s.start)

    return doc


nlp = spacy.blank("en")

options_matcher = create_options_matcher(nlp)

language_to_options_matcher[nlp.lang] = options_matcher

nlp.add_pipe("mark_is_all_letters")
nlp.add_pipe("get_candidate_questions_and_mark_as_spans")
nlp.add_pipe("set_is_numbered_bullet")
nlp.add_pipe("mark_candidate_options_as_spans")

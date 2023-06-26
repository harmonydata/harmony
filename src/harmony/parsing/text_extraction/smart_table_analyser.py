from harmony.schemas.requests.text import RawFile, Instrument, Question
from harmony.parsing.text_extraction.options_words import OPTIONS_WORDS
import operator
import re
import numpy as np

def get_questions_from_tables(tables):
    questions_from_tables = []

    lengths = {}
    for table in tables:
        for row in table:
            for col_id, cell in enumerate(row):
                if col_id not in lengths:
                    lengths[col_id] = []
                lengths[col_id].append(len(str(cell)))

    cols_sorted_by_length = sorted(lengths.items(), key=lambda x : np.median(x[1]), reverse=True)
    question_col = cols_sorted_by_length[0][0]
    number_col = None
    if question_col > 0:
        number_col = 0

    for table in tables:
        for row in table:
            if question_col < len(row):
                options = []
                if question_col < len(row) - 1:
                    options = re.split(r'[,/]', row[question_col + 1])
                question_no = None
                if number_col is not None:
                    question_no = row[number_col]
                question_text = re.sub(r'\s+', ' ', re.sub(r'\n', ' ', row[question_col])).strip()
                if len(question_text) > 1 and question_text.lower() not in OPTIONS_WORDS and re.findall('[a-zA-Z]',
                                                                                                        question_text):
                    LEADING_NUMBER_PATTERN = "^\d+\.?\s*"
                    numbers_match = re.findall(LEADING_NUMBER_PATTERN, question_text)
                    if numbers_match and question_no is None:
                        question_no = numbers_match[0]
                        question_text = re.sub(LEADING_NUMBER_PATTERN, "", question_text).strip()
                    questions_from_tables.append(
                        Question(question_no=question_no, question_text=question_text, options=options))

    # for q in questions_from_tables:
    #     print("\t", q.question_text)
    return questions_from_tables
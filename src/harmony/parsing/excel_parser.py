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
import traceback
from typing import List

import numpy as np
import pandas as pd
from langdetect import detect

from harmony.parsing.util.excel_to_pandas import parse_excel_to_pandas
from harmony.schemas.requests.text import Question
from harmony.schemas.requests.text import RawFile, Instrument

re_header_column = re.compile(r'(?i)(?:question|text|pergunta)')

# Headers we know how to read, and the role each one plays. These match the whole
# cell so that "Question #" is not mistaken for "Question text".
COLUMN_PATTERNS = {
    "question": re.compile(
        r"(?i)^\s*(?:question(?:\s*(?:text|wording))?|item(?:\s*text)?|text|wording|pergunta)\s*$"),
    "question_no": re.compile(
        r"(?i)^\s*(?:(?:question|item|q)\s*(?:no\.?|number|num|#)|no\.?|number|#)\s*$"),
    "options": re.compile(
        r"(?i)^\s*(?:(?:response|answer)s?\s*(?:options?|choices|scale|categories)?"
        r"|options?|choices|categories)\s*$"),
    "instrument": re.compile(
        r"(?i)^\s*(?:questionnaire|instrument|scale|measure|survey)(?:\s*name)?\s*$"),
    "notes": re.compile(r"(?i)^\s*(?:notes?|comments?|remarks?|description)\s*$"),
}

NORMALISED_COLUMNS = ["question_no", "question", "options", "instrument", "notes"]


def clean_option_no(option_could_be_int):
    if option_could_be_int is None \
            or pd.isna(option_could_be_int) or pd.isnull(option_could_be_int):
        return ""
    if type(option_could_be_int) is str:
        return option_could_be_int
    if (type(option_could_be_int) is float or type(option_could_be_int) is np.float64 or type(
            option_could_be_int) is np.float32) \
            and option_could_be_int.is_integer():
        return str(int(option_could_be_int))
    return str(option_could_be_int)


def find_header_row(df: pd.DataFrame, rows_to_scan: int = 5) -> tuple:
    """Find the row that names the columns, and work out which column holds what.

    Returns (row index, {role: column}). The question text column is what we anchor
    on: if no row names one, we return (None, {}) and the caller falls back to
    reading the columns by position.
    """
    for row_idx in range(min(rows_to_scan, len(df))):
        roles = {}
        for col in df.columns:
            cell = df[col].iloc[row_idx]
            if not isinstance(cell, str):
                continue
            for role, pattern in COLUMN_PATTERNS.items():
                if role not in roles and pattern.match(cell):
                    roles[role] = col
                    break
        if "question" in roles:
            return row_idx, roles
    return None, {}


def columns_by_name(df: pd.DataFrame, header_row: int, roles: dict) -> pd.DataFrame:
    """Pick out the named columns, dropping the header row and anything above it."""
    body = df.iloc[header_row + 1:]
    result = pd.DataFrame(index=body.index)
    for role in NORMALISED_COLUMNS:
        col = roles.get(role)
        result[role] = body[col] if col is not None else ""
    return result


def columns_by_position(df: pd.DataFrame) -> pd.DataFrame:
    """Read the columns by position: question number, question, options.

    This is the original behaviour, kept for sheets with no header we recognise.
    """
    df_questions = df.copy()

    # check we have 3 columns. If more or less, adjust it by deleting or inserting.
    if len(df_questions.columns) > 3:
        if str(df_questions[df_questions.columns[3]].iloc[0]).lower() == "filename":
            if len(df_questions.columns) > 4 and str(
                    df_questions[df_questions.columns[4]].iloc[0]).lower() == "language":
                df_questions.drop(columns=df_questions.columns[5:], inplace=True)
            else:
                df_questions.drop(columns=df_questions.columns[4:], inplace=True)
        else:
            df_questions.drop(columns=df_questions.columns[3:], inplace=True)
    elif len(df_questions.columns) < 3:
        col_avg_lengths = [0] * len(df_questions.columns)
        for col_idx, col_name in enumerate(df_questions.columns):
            col_avg_lengths[col_idx] = df_questions[col_name].apply(lambda s: len(str(s))).mean()
        biggest_col = int(np.argmax(col_avg_lengths))
        if biggest_col == 0:
            df_questions.insert(0, "question_no", [str(n) for n in range(len(df_questions))])
        if len(df_questions.columns) < 3:
            df_questions.insert(2, "options", [""] * len(df_questions))

    # standardise the column names
    if len(df_questions.columns) == 3:
        df_questions.columns = ["question_no", "question", "options"]
    elif len(df_questions.columns) == 4:
        df_questions.columns = ["question_no", "question", "options", "filename"]
    else:
        df_questions.columns = ["question_no", "question", "options", "filename", "language"]

    # Check if header row present, in which case remove it
    rows_to_delete = []
    for i in range(len(df_questions)):
        if df_questions.question.iloc[i] is None or type(df_questions.question.iloc[i]) is not str or \
                re_header_column.match(df_questions.question.iloc[i]):
            rows_to_delete.append(i)
            break

    if len(rows_to_delete) > 0:
        df_questions.drop(rows_to_delete, inplace=True)

    df_questions["instrument"] = ""
    df_questions["notes"] = ""

    return df_questions[NORMALISED_COLUMNS]


def convert_excel_to_instruments(file: RawFile) -> List[Instrument]:
    sheet_name_to_dataframe = parse_excel_to_pandas(file.content)

    instruments = []
    for sheet_name, df_sheet in sheet_name_to_dataframe.items():
        # Blank rows are used to space questionnaires apart. Drop them up front so
        # they can't be read as questions, and renumber so that the row positions
        # used further down still line up with the row labels.
        df_sheet = df_sheet.dropna(how="all").reset_index(drop=True)
        if len(df_sheet) == 0:
            continue

        header_row, roles = find_header_row(df_sheet)
        if header_row is None:
            df_questions = columns_by_position(df_sheet)
        else:
            df_questions = columns_by_name(df_sheet, header_row, roles)

        for column in NORMALISED_COLUMNS:
            df_questions[column] = df_questions[column].apply(clean_option_no)

        # A row with no question text can't become a Question, since the schema asks
        # for at least one character. Drop those rather than raising.
        df_questions = df_questions[df_questions["question"].str.strip() != ""]
        if len(df_questions) == 0:
            continue

        # A questionnaire column lets one sheet hold several instruments. Carry the
        # name downwards so that a name written once at the top of a block covers it.
        instrument_names = df_questions["instrument"].replace("", np.nan).ffill().fillna("")

        for group_name, df_group in df_questions.groupby(instrument_names, sort=False):
            instrument_name = str(group_name).strip() or f"{file.file_name} / {sheet_name}"
            instrument_id = f"{file.file_id}_{len(instruments)}"

            questions = []
            for position, row in enumerate(df_group.itertuples(), start=1):
                options = [o.strip() for o in row.options.split("/") if o.strip()]
                questions.append(Question(
                    question_no=row.question_no or str(position),
                    question_intro=row.notes or None,
                    question_text=row.question,
                    options=options,
                    source_page=0,
                    instrument_id=instrument_id,
                    instrument_name=instrument_name,
                ))

            language = "en"
            try:
                language = detect(" ".join(df_group["question"]))
            except Exception:
                print("Error identifying language in Excel file")
                traceback.print_exc()

            instruments.append(Instrument(
                file_id=file.file_id,
                instrument_id=instrument_id,
                file_name=file.file_name,
                instrument_name=instrument_name,
                file_type=file.file_type,
                file_section=sheet_name,
                language=language,
                questions=questions
            ))

    return instruments

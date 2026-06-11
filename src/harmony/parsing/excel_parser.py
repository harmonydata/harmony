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
QUESTION_COLUMN_HINTS = re.compile(
    r'(?i)(question|text|pergunta|item|description|scale|statement|content)'
)


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


def convert_excel_to_instruments(file: RawFile) -> List[Instrument]:
    sheet_name_to_dataframe = parse_excel_to_pandas(file.content)

    instruments = []
    for sheet_idx, (sheet_name, df_questions) in enumerate(sheet_name_to_dataframe.items()):

        # Strip blank rows before assignment
        df_questions.dropna(how='all', inplace=True)
        df_questions.reset_index(drop=True, inplace=True)

        if len(df_questions) == 0:
            continue

        # Find the question column semantically
        question_col = None
        for col in df_questions.columns:
            if QUESTION_COLUMN_HINTS.search(str(col)):
                question_col = col
                break
        
        if question_col is None and len(df_questions) > 0:
            for col in df_questions.columns:
                val = str(df_questions[col].iloc[0])
                if QUESTION_COLUMN_HINTS.search(val):
                    question_col = col
                    break
        
        if question_col is None:
            # Fall back: longest average string length column
            avg_lens = df_questions.apply(lambda c: c.astype(str).str.len().mean())
            question_col = avg_lens.idxmax()

        question_col_idx = df_questions.columns.get_loc(question_col)

        # Ensure we have question_no, question, options
        if question_col_idx > 0:
            question_no_col = df_questions.columns[0]
        else:
            df_questions.insert(0, "generated_question_no", [str(n) for n in range(len(df_questions))])
            question_no_col = "generated_question_no"
            question_col_idx += 1

        if question_col_idx < len(df_questions.columns) - 1:
            options_col = df_questions.columns[question_col_idx + 1]
        else:
            df_questions["generated_options"] = ""
            options_col = "generated_options"

        # standardise the column names
        df_questions = df_questions[[question_no_col, question_col, options_col]].copy()
        df_questions.columns = ["question_no", "question", "options"]

        # Check if header row present, in which case remove it
        rows_to_delete = []
        for i in range(len(df_questions)):
            val = df_questions.question.iloc[i]
            if val is None or type(val) is not str or QUESTION_COLUMN_HINTS.search(val):
                rows_to_delete.append(i)
                break

        if len(rows_to_delete) > 0:
            df_questions.drop(rows_to_delete, inplace=True)

        # Make sure the whole DF is of type string.
        df_questions["question_no"] = df_questions["question_no"].apply(clean_option_no)
        df_questions["question"] = df_questions["question"].apply(clean_option_no)
        df_questions["options"] = df_questions["options"].apply(clean_option_no)

        if len(df_questions) == 0:
            continue

        questions = []
        for idx in range(len(df_questions)):
            o = df_questions.options.iloc[idx]
            if type(o) is str:
                options = o.split("/")
            else:
                options = []
            question = Question(question_no=str(df_questions.question_no.iloc[idx]), question_intro="blah",
                                question_text=str(df_questions.question.iloc[idx]),
                                options=options, source_page=0)
            questions.append(question)

        language = "en"
        try:
            valid_questions = df_questions["question"].dropna()
            valid_questions = [q for q in valid_questions if isinstance(q, str) and q.strip()]
            if valid_questions:
                language = detect(" ".join(valid_questions))
        except:
            print("Error identifying language in Excel file")
            traceback.print_exc()
            traceback.print_stack()

        instrument = Instrument(
            file_id=file.file_id,
            instrument_id=file.file_id + "_" + str(sheet_idx),
            file_name=file.file_name,
            instrument_name=file.file_name + " / " + sheet_name,
            file_type=file.file_type,
            file_section=sheet_name,
            language=language,
            questions=questions
        )

        instruments.append(instrument)

    return instruments

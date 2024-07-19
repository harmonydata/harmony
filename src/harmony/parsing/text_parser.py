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
from io import StringIO
from typing import List

import pandas as pd
from langdetect import detect

from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile, Instrument, Question

re_question_text_column = re.compile(r'(?i)(?:question|text|pergunta)')
re_number_column = re.compile(r'(?i)(?:number|\bno)')


def convert_text_to_instruments(file: RawFile) -> List[Instrument]:
    if file.file_type == FileType.txt or file.file_type == FileType.csv:  # text files not binary
        page_text = file.content
    else:  # any binary format
        page_text = file.text_content

    if file.file_id is None:
        file.file_id = str(hash(page_text))

    try:
        language = detect(page_text)
    except:
        language = "en"
        print(f"Error identifying language in {file.file_type} file")
        traceback.print_exc()
        traceback.print_stack()

    csv_sep = None
    if file.file_type == FileType.csv:
        first_line, _ = page_text.split("\n", 1)
        if "\t" in first_line:
            csv_sep = "\t"
        elif "," in first_line:
            csv_sep = ","

        string_io = StringIO(page_text)
        df = pd.read_csv(string_io, sep=csv_sep)
        df.fillna("", inplace=True)

        # Pick the column with the longest text as the question column
        col_lengths = {}
        for col in df.columns:
            col_lengths[col] = df[col].apply(lambda x: len(x) if type(x) is str else 0).sum()
        question_column = max(col_lengths, key=col_lengths.get)

        for col in df.columns:
            if re_question_text_column.match(col) and not re_number_column.findall(col):
                question_column = col
                break
        options_column = None
        for col in df.columns:
            if "options" in col.lower():
                options_column = col
                break
        numbers_column = None
        if question_column != df.columns[0]:
            numbers_column = df.columns[0]

        questions = []
        for idx in range(len(df)):
            if numbers_column is not None:
                question_no = str(df[numbers_column].iloc[idx])
            else:
                question_no = "Q" + str(len(questions) + 1).zfill(3)

            question_text = df[question_column].iloc[idx].strip()
            if options_column is not None:
                options = df[options_column].iloc[idx].split("/")
            else:
                options = []
            if question_text == "":
                continue
            question = Question(question_no=question_no, question_intro="", question_text=question_text,
                                options=options)
            questions.append(question)

    if file.file_type == FileType.txt or (file.file_type == FileType.csv and csv_sep is None):
        # Either txt file, or CSV file where no separating character was found in the first line
        questions = []
        for line in page_text.split("\n"):
            if line.strip() == "":
                continue
            line = re.sub(r'\s+', ' ', line)
            question_no = "Q" + str(len(questions) + 1).zfill(3)
            question_text = line.strip()
            if question_text == "":
                continue
            question = Question(question_no=question_no, question_intro="", question_text=question_text,
                                options=[])
            questions.append(question)

    instrument = Instrument(
        file_id=file.file_id,
        instrument_id=file.file_id + "_0",
        instrument_name=file.file_name,
        file_name=file.file_name,
        file_type=file.file_type,
        file_section="",
        language=language,
        questions=questions
    )

    instruments = [instrument]

    return instruments

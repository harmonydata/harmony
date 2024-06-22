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
import pickle as pkl
import re

import numpy as np

import harmony
from harmony.parsing.util.tika_wrapper import parse_pdf_to_plain_text
# from harmony.parsing.util.tesseract_wrapper import parse_image_pdf_to_plain_text
# from harmony.parsing.util.camelot_wrapper import parse_pdf_to_tables
from harmony.schemas.requests.text import RawFile, Instrument

re_initial_num = re.compile(r'(^\d+)')
re_initial_num_dot = re.compile(r'(^\d+\.)')
re_word = re.compile(r'(?i)(\b[\w\']+\b)')
re_alpha = re.compile(r'(^[a-zA-Z]+)')
re_bracket = re.compile(r'(?:\(|\))')
import pathlib

model_containing_folder = pathlib.Path(__file__).parent.resolve()

with open(f"{model_containing_folder}/rf_table_model.pkl", "rb") as f:
    rf_table_model = pkl.load(f)

with open(f"{model_containing_folder}/crf_text_model.pkl", "rb") as f:
    crf_text_model = pkl.load(f)


def convert_pdf_to_instruments(file: RawFile) -> Instrument:
    # file is an object containing these properties:
    # content: str - The raw file contents so if it's a PDF this is a byte sequence in base 64 encoding
    # text_content: str - this is empty but we will use Tika to populate this in this method
    # tables: list - this is a list of all the tables in the document. The front end has populated this field.

    if not file.text_content:
        file.text_content = parse_pdf_to_plain_text(file.content)  # call Tika to convert the PDF to plain text

    # TODO: New PDF parsing algorithm should go here, together with return statement.

    table_cell_texts = []
    page_tables = file.tables
    questions_from_tables = []
    if len(page_tables) > 0:
        for page_table in page_tables:
            tables = page_table['tables']
            for row in tables:
                for item in row:
                    if len(item.strip()) > 0:
                        table_cell_texts.append(item)

        X = []
        for idx in range(len(table_cell_texts)):
            t = table_cell_texts[idx]
            features = [len(t),
                        len(re_initial_num.findall(t)),
                        len(re_initial_num_dot.findall(t))]
            X.append(features)

        if len(X) > 0:
            X = np.asarray(X)

            y_pred = rf_table_model.predict(X)

            questions_from_tables = []
            for idx in range(len(table_cell_texts)):
                if y_pred[idx] == 1:
                    questions_from_tables.append(table_cell_texts[idx])


    if True:  # text CRF model
        questions_from_text = []
        X = []

        token_texts = []
        token_properties = []

        text = file.text_content
        char_indices_of_newlines = set()
        for idx, c in enumerate(text):
            if c == "\n":
                char_indices_of_newlines.add(idx)

        char_indices_of_question_marks = set()
        for idx, c in enumerate(text):
            if c == "?":
                char_indices_of_question_marks.add(idx)

        tokens = list(re_word.finditer(text))

        last_token_properties = {}

        for token in tokens:
            is_number = len(re_initial_num.findall(token.group()))
            is_number_dot = len(re_initial_num_dot.findall(token.group()))
            is_alpha = len(re_alpha.findall(token.group()))

            dist_to_newline = token.start()
            for c in range(token.start(), 1, -1):
                if c in char_indices_of_newlines:
                    dist_to_newline = token.start() - c
                    break

            dist_to_question_mark = len(text) - token.start()
            for c in range(token.start(), len(text)):
                if c in char_indices_of_question_marks:
                    dist_to_question_mark = c - token.start()
                    break

            is_capital = int(token.group()[0] != token.group()[0].lower())

            this_token_properties = {"length": len(token.group()), "is_number": is_number,
                                     "is_alpha": is_alpha,
                                     "is_capital": is_capital,
                                     "is_number_dot": is_number_dot,
                                     "dist_to_newline": dist_to_newline, "dist_to_question_mark": dist_to_question_mark,
                                     "char_index": token.start()}

            this_token_properties["prev_length"] = last_token_properties.get("length", 0)
            this_token_properties["prev_is_alpha"] = last_token_properties.get("is_alpha", 0)
            this_token_properties["prev_is_number"] = last_token_properties.get("is_number", 0)
            this_token_properties["prev_is_number_dot"] = last_token_properties.get("is_number_dot", 0)
            this_token_properties["prev_is_capital"] = last_token_properties.get("is_capital", 0)

            this_token_properties["prev_prev_length"] = last_token_properties.get("prev_length", 0)
            this_token_properties["prev_prev_is_alpha"] = last_token_properties.get("prev_is_alpha", 0)
            this_token_properties["prev_prev_is_number"] = last_token_properties.get("prev_is_number", 0)
            this_token_properties["prev_prev_is_number_dot"] = last_token_properties.get("prev_is_number_dot", 0)
            this_token_properties["prev_prev_is_capital"] = last_token_properties.get("prev_is_capital", 0)

            token_texts.append(token.group())

            token_properties.append(this_token_properties)

            last_token_properties = this_token_properties

        X.append(token_properties)

        y_pred = crf_text_model.predict(X)

        last_token_category = "O"
        for idx in range(len(X[0])):

            if y_pred[0][idx] != "O":
                if last_token_category == "O" or y_pred[0][idx] == "B":
                    start_idx = tokens[idx].start()
                    end_idx = len(text)
                    for j in range(idx + 1, len(X[0])):
                        if y_pred[0][j] == "O" or y_pred[0][j] == "B":
                            end_idx = tokens[j - 1].end()
                            break

                    question_text = text[start_idx:end_idx]
                    question_text = re.sub(r'\s+', ' ', question_text)
                    question_text = question_text.strip()
                    questions_from_text.append(question_text)

            last_token_category = y_pred[0][idx]

    if len(questions_from_text) > len(questions_from_tables):
        print ("Source of parsing was text CRF")
        instrument = harmony.create_instrument_from_list(questions_from_text, instrument_name=file.file_name, file_name=file.file_name)
        print(instrument)
        return [instrument]
    elif len(questions_from_tables) > 0:
        instrument = harmony.create_instrument_from_list(questions_from_tables, instrument_name=file.file_name, file_name=file.file_name)
        return [instrument]
    else:
        return []

    # return convert_text_to_instruments(file)

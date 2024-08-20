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

import pathlib
import pickle as pkl
import re

import harmony
from harmony.parsing.util.feature_extraction import convert_text_to_features
from harmony.parsing.util.tika_wrapper import parse_pdf_to_plain_text
from harmony.schemas.requests.text import RawFile, Instrument

model_containing_folder = pathlib.Path(__file__).parent.resolve()

with open(f"{model_containing_folder}/20240719_pdf_question_extraction_sklearn_crf_model.pkl", "rb") as f:
    crf_text_model = pkl.load(f)

# Predict method is taken from the training repo. Use the training repo as the master copy of the predict method.
# All training code is in https://github.com/harmonydata/pdf-questionnaire-extraction
def predict(test_text):
    token_texts, token_start_char_indices, token_end_char_indices, token_properties = convert_text_to_features(
        test_text)

    X = []
    X.append(token_properties)

    y_pred = crf_text_model.predict(X)

    questions_from_text = []

    tokens_already_used = set()

    last_token_category = "O"

    for idx in range(len(X[0])):

        if y_pred[0][idx] != "O" and idx not in tokens_already_used:
            if last_token_category == "O" or y_pred[0][idx] == "B":
                start_idx = token_start_char_indices[idx]
                end_idx = len(test_text)
                for j in range(idx + 1, len(X[0])):
                    if y_pred[0][j] == "O" or y_pred[0][j] == "B":
                        end_idx = token_end_char_indices[j - 1]
                        break
                    tokens_already_used.add(j)

                question_text = test_text[start_idx:end_idx]
                question_text = re.sub(r'\s+', ' ', question_text)
                question_text = question_text.strip()
                questions_from_text.append(question_text)

        last_token_category = y_pred[0][idx]

    return questions_from_text


def convert_pdf_to_instruments(file: RawFile) -> Instrument:
    # file is an object containing these properties:
    # content: str - The raw file contents so if it's a PDF this is a byte sequence in base 64 encoding
    # text_content: str - this is empty but we will use Tika to populate this in this method
    # tables: list - this is a list of all the tables in the document. The front end has populated this field.

    if not file.text_content:
        file.text_content = parse_pdf_to_plain_text(file.content)  # call Tika to convert the PDF to plain text

    questions_from_text = predict(file.text_content)

    instrument = harmony.create_instrument_from_list(questions_from_text, instrument_name=file.file_name,
                                                     file_name=file.file_name)
    return [instrument]

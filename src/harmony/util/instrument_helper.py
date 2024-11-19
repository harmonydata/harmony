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

import base64
import json
import uuid

from harmony.schemas.requests.text import Instrument, Question


def create_instrument_from_list(question_texts: list, question_numbers: list = None,
                                instrument_name: str = "My instrument",
                                file_name="My file") -> Instrument:
    """
    Read a list of strings and create an Instrument object.
    :return: Single Instrument.
    """

    questions = []
    for ctr, question_text in enumerate(question_texts):
        if question_numbers is not None:
            question_no = question_numbers[ctr]
        else:
            question_no = str(ctr + 1)
        questions.append(Question(question_text=question_text, question_no=question_no))

    return Instrument(questions=questions, instrument_name=instrument_name, instrument_id=uuid.uuid4().hex,
                      file_name=file_name, file_id=uuid.uuid4().hex)


def import_instrument_into_harmony_web(instrument: Instrument, harmony_fe_base_url="https://harmonydata.ac.uk") -> str:
    """
    Import a single instrument into the Harmony web UI.
    @param instrument: An instrument object created by Harmony
    @param harmony_fe_base_url: The base URL of the React app front end, defaulting to the web Harmony front end at harmonydata.ac.uk
    @return: a URL which you can click which will take you to the browser.
    """
    instrument_serialised_as_json = json.dumps(instrument.model_dump())
    instrument_json_b64_encoded_bytes = base64.urlsafe_b64encode(instrument_serialised_as_json.encode('utf-8'))
    instrument_json_b64_encoded_str = instrument_json_b64_encoded_bytes.decode("utf-8")

    url = f"{harmony_fe_base_url}/app/#/import/{instrument_json_b64_encoded_str}"

    return url

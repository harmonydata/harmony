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

from langdetect import detect

from harmony.parsing.text_extraction.ensemble_named_entity_recogniser import extract_questions
from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile, Instrument, Question


def convert_text_to_instruments(file: RawFile) -> List[Instrument]:
    if file.file_type == FileType.txt:
        page_text = file.content
    else:
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

    # TODO: replace this with smarter logic
    if file.file_type == FileType.txt:
        questions = []
        for line in page_text.split("\n"):
            if line.strip() == "":
                continue
            line = re.sub(r'\s+', ' ', line)
            question = Question(question_no=len(questions) + 1, question_intro="", question_text=line.strip(),
                                options=[])
            questions.append(question)
    else:
        questions, _, _ = extract_questions(page_text, file.tables)

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

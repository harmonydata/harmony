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

from typing import List
from harmony.parsing.excel_parser import convert_excel_to_instruments
from harmony.parsing.pdf_parser import convert_pdf_to_instruments
from harmony.parsing.text_parser import convert_text_to_instruments
from harmony.parsing.html_parser import convert_html_to_instruments
from harmony.parsing.google_forms_parser import convert_google_forms_to_instruments
from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile, Instrument, Question
import os
import base64
import io

def _get_instruments_from_file(file):
    """
    Route files to appropriate parsers based on file type.
    
    Args:
        file: RawFile object containing file content and metadata
        
    Returns:
        List[Instrument]: Parsed instruments from the file
    """

    # Images: we can process directly in a single call

    from typing import List, Optional
    from openai import OpenAI
    from pydantic import BaseModel, Field

    class ExtractedQuestion(BaseModel):
        question_no: Optional[str] = Field(None, description="Number of the question")
        question_intro: Optional[str] = Field(None, description="Introductory text applying to the question")
        question_text: str = Field(description="Text of the question", min_length=1)
        response_options: List[str] = Field([], description="The possible answer options")

    class QuestionList(BaseModel):
        questions: List[ExtractedQuestion]

    client = OpenAI()

    if file.file_type == FileType.image and len(file.content) < 500000 and os.environ.get("OPENAI_API_KEY") is not None:
        response = client.responses.parse(
            model="gpt-5.4-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Extract all questions, including any introductions and response options, from this PDF.",
                        },
                        {
                            "type": "input_file",
                            "image_url": file.content,
                        },
                    ],
                }
            ],
            text_format=QuestionList
        )
        instruments_from_this_file = []

        instrument = Instrument()
        for question in response.output_parsed:
            instrument.questions.append(Question(question_no=question.question_no, question_intro=question.qustion_intro,
                                                 text=question.question_text, options=question.response_options))

        instruments_from_this_file.append(instrument)

    elif file.file_type == FileType.pdf or file.file_type == FileType.docx and len(file.content) < 500000 and os.environ.get("OPENAI_API_KEY") is not None:
        # Upload the PDF file using the Files API
        content_type, content_string = file.content.split(",")
        file_in_bytes = base64.b64decode(content_string)

        uploaded_file = client.files.create(
            file=("document.pdf", io.BytesIO(file_in_bytes), "application/pdf"),
            purpose="user_data",
            expires_after={
                "anchor": "created_at",
                "seconds": 3600
            }
        )

        response = client.responses.parse(
            model="gpt-5.4-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Extract all questions, including any introductions and response options, from this PDF.",
                        },
                        {
                            "type": "input_file",
                            "file_id": uploaded_file.id,
                        },
                    ],
                }
            ],
            text_format=QuestionList
        )

        instruments_from_this_file = []

        instrument = Instrument(questions=[])
        for question in response.output_parsed.questions:
            instrument.questions.append(
                Question(question_no=question.question_no, question_intro=question.question_intro,
                         question_text=question.question_text, options=question.response_options))

        instruments_from_this_file.append(instrument)
    elif file.file_type == FileType.pdf or file.file_type == FileType.docx:
        instruments_from_this_file = convert_pdf_to_instruments(file)
    elif file.file_type == FileType.txt or file.file_type == FileType.csv:
        instruments_from_this_file = convert_text_to_instruments(file)
    elif file.file_type == FileType.xlsx:
        instruments_from_this_file = convert_excel_to_instruments(file)
    elif file.file_type == FileType.html or file.file_type == FileType.htm:
        instruments_from_this_file = convert_html_to_instruments(file)
    elif file.file_type == FileType.google_forms:
        instruments_from_this_file = convert_google_forms_to_instruments(file)
    else:
        instruments_from_this_file = []
    return instruments_from_this_file


def convert_files_to_instruments(files: List[RawFile]) -> List[Instrument]:
    """Convert files to instruments"""
    instruments = []
    for file in files:
        instruments_from_this_file = _get_instruments_from_file(file)
        instruments.extend(instruments_from_this_file)
    return instruments

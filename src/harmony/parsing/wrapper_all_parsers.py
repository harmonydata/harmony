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
from harmony.schemas.enums.parsing_methods import ParsingMethod
from harmony.schemas.requests.text import RawFile, Instrument, Question
import os
import base64
import io
import logging
import uuid

logger = logging.getLogger(__name__)

# PDFs and images are sent to OpenAI when OPENAI_API_KEY is set and the base64 content is under this length,
# which is OpenAI's 50 MB per-file limit once base64 has added its third.
# Anything else, or any failure in the OpenAI call, goes to the standard parsers below.
OPENAI_MAX_CONTENT_LENGTH = 50 * 1024 * 1024 * 4 // 3
OPENAI_FILE_TYPES = (FileType.pdf, FileType.png, FileType.jpg, FileType.jpeg)


def _convert_with_openai(file: RawFile) -> List[Instrument]:
    """
    Extract the questions from a PDF or an image with OpenAI.
    openai is imported here, so harmony still works without it installed.
    """
    from typing import Optional
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

    if file.file_type == FileType.pdf:
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
        document_name = "PDF"
        document_input = {
            "type": "input_file",
            "file_id": uploaded_file.id,
        }
        parsing_method = ParsingMethod.gen_ai_pdf
    else:
        # Images: we can process directly in a single call
        document_name = "image"
        document_input = {
            "type": "input_image",
            "image_url": file.content,
        }
        parsing_method = ParsingMethod.gen_ai_image

    response = client.responses.parse(
        model="gpt-5.4-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Extract all questions, including any introductions and response options, from this {document_name}.",
                    },
                    document_input,
                ],
            }
        ],
        text_format=QuestionList
    )

    questions = []
    for question in response.output_parsed.questions:
        questions.append(
            Question(question_no=question.question_no, question_intro=question.question_intro,
                     question_text=question.question_text, options=question.response_options))

    # Named the same way as the PDF parser names its instrument
    return [Instrument(questions=questions, instrument_name=file.file_name, instrument_id=uuid.uuid4().hex,
                       file_name=file.file_name, file_id=uuid.uuid4().hex, parsing_method=parsing_method)]


def _get_instruments_from_file(file):
    """
    Route files to appropriate parsers based on file type.

    Args:
        file: RawFile object containing file content and metadata

    Returns:
        List[Instrument]: Parsed instruments from the file
    """

    if file.file_type in OPENAI_FILE_TYPES and len(file.content) < OPENAI_MAX_CONTENT_LENGTH \
            and os.environ.get("OPENAI_API_KEY"):
        try:
            return _convert_with_openai(file)
        except Exception:
            logger.exception("OpenAI extraction failed for %s, using the standard parser instead", file.file_name)

    if file.file_type == FileType.pdf or file.file_type == FileType.docx:
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

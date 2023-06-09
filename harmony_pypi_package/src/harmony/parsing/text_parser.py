import re
from typing import List

from langdetect import detect

from harmony.parsing.text_extraction.smart_document_parser import parse_document
from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile, Instrument, Question


def convert_text_to_instruments(file: RawFile) -> List[Instrument]:
    if file.file_type == FileType.txt:
        page_text = file.content
    else:
        page_text = file.text_content

    language = detect(page_text)

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
        questions = parse_document(page_text)

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

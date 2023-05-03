from typing import List

from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile, Instrument, Question
from langdetect import detect
import re
import uuid

def convert_text_to_instruments(file: RawFile) -> List[Instrument]:  

    page_text = file.text_content
    
    language = detect(page_text)

    # TODO: replace this with smarter logic
    questions = []
    for line in page_text.split("\n"):
        if line.strip() == "":
            continue
        line = re.sub(r'\s+', ' ', line)
        question = Question(question_no=len(questions) + 1, question_intro="", question_text=line.strip(), options=[])
        questions.append(question)
            
    instrument = Instrument(
        file_id=file.file_id,
        instrument_id=uuid.uuid4().hex,
        instrument_name=file.file_name,
        file_name=file.file_name,
        file_type=file.file_type,
        file_section="",
        language=language,
        questions=questions
    )
    
    instruments = [instrument]

    return instruments

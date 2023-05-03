import re
import uuid

from langdetect import detect

from schemas.requests.text import RawFile, Instrument, Question
from harmony.parsing.tika_wrapper import parse_pdf_to_plain_text


def pdf_to_instrument(file: RawFile) -> Instrument:
    plain_text_pages = parse_pdf_to_plain_text(file.content)

    language = detect(" ".join(plain_text_pages))

    # TODO: replace this with smarter logic
    questions = []
    for page_no, page_text in enumerate(plain_text_pages):
        for line in page_text.split("\n"):
            if line.strip() == "":
                continue
            line = re.sub(r'\s+', ' ', line)
            question = Question(question_no=len(questions) + 1, question_intro="", question_text=line.strip(),
                                options=[], source_page=page_no)
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

    return instrument

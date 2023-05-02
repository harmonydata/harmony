import re
import uuid

from langdetect import detect

from schemas.requests.text import RawFile, Instrument, Question

re_starts_with_number = re.compile(r'^\d+[a-z]?')


def txt_to_instrument(file: RawFile) -> Instrument:
    plain_text = file.content

    language = detect(plain_text)

    question_texts = plain_text.split("\n")
    question_texts = [q.strip() for q in question_texts if len(q.strip()) > 0]
    question_numbers = [str(i + 1) for i in range(len(question_texts))]
    question_options = [""] * len(question_texts)

    for idx, q in enumerate(question_texts):
        m = re_starts_with_number.match(q)
        if m:
            question_numbers[idx] = m.group()
            question_texts[idx] = re.sub(r'^' + m.group() + r'[\.\s\)]+', "", q)
        else:
            question_texts[idx] = q

        colon = re.split(":|\t", question_texts[idx])
        if len(colon) > 1:
            question_options[idx] = colon[1]
            question_texts[idx] = colon[0]

    questions = []
    for idx, question_text in enumerate(question_texts):
        question = Question(question_no=question_numbers[idx], question_intro="", question_text=question_text,
                            options=question_options[idx].split("/"), source_page=0)
        questions.append(question)

    instrument = Instrument(
        file_id=file.file_id,
        instrument_id=uuid.uuid4().hex,
        file_name=file.file_name,
        file_type=file.file_type,
        instrument_name=file.file_name,
        file_section="",
        language=language,
        questions=questions
    )

    return instrument

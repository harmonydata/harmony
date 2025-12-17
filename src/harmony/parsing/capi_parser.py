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
from langdetect.lang_detect_exception import LangDetectException
from harmony.schemas.requests.text import RawFile, Instrument, Question

re_capi_code = re.compile(r'^([A-Z]{2,8}[0-9]*)$')


def is_capi_format(text: str) -> bool:
    """Detect if text content is in CAPI format based on density of uppercase variable codes."""
    if not text or len(text) < 100:
        return False

    lines = text.split("\n")

    # count lines starting with CAPI-style codes (e.g. AHATEA, BHOWREL)
    capi_code_pattern = re.compile(r'^[A-Z][A-Z0-9][A-Z0-9]+\s')
    capi_line_count = 0

    for line in lines:
        if capi_code_pattern.match(line.strip()):
            capi_line_count += 1

    # consider it CAPI if more than 2% of lines have codes and at least 10 found
    ratio = capi_line_count / max(len(lines), 1)
    return capi_line_count >= 10 and ratio >= 0.02


def extract_capi_questions(text: str) -> List[dict]:
    """Extract questions from CAPI formatted text. Variable codes appear on their own line
    with question text on following lines. Routing shown with | characters."""
    lines = text.split("\n")
    questions = []

    for idx, line in enumerate(lines):
        line_stripped = line.strip()

        # skip empty lines and table of contents entries
        if not line_stripped or '...' in line_stripped or '___' in line_stripped:
            continue

        match = re_capi_code.match(line_stripped)
        if match:
            code = match.group(1)

            # skip common non-question codes
            skip_codes = ['CARD', 'NOTE', 'READ', 'CODE', 'TEXT', 'ENDIF', 'ELSE', 'AND', 'THE', 'FOR']
            if code in skip_codes or len(code) < 3:
                continue

            # look at next lines for question text
            question_text = ""
            for next_idx in range(idx + 1, min(idx + 10, len(lines))):
                next_line = lines[next_idx].strip()

                # remove routing indicators
                next_line = next_line.lstrip('|').strip()

                # stop if we hit another CAPI code
                if re_capi_code.match(next_line):
                    break

                # stop if empty line after we have some text
                if not next_line and question_text:
                    break

                # skip interviewer instructions (all caps)
                if next_line.isupper() and len(next_line) > 10:
                    continue

                # stop at answer options (lines starting with numbers)
                if re.match(r'^\d+\s', next_line):
                    break

                # skip header/footer lines
                if 'Module' in next_line and any(char.isdigit() for char in next_line):
                    continue
                if 'Millennium Cohort' in next_line:
                    continue

                if next_line:
                    question_text += " " + next_line

            question_text = re.sub(r'\s+', ' ', question_text).strip()

            # skip feed-forward metadata
            if '(from feed forward)' in question_text.lower():
                continue

            # only add if meaningful question text
            if len(question_text) > 15 and ('?' in question_text or len(question_text) > 30):
                questions.append({
                    'question_no': code,
                    'question_text': question_text,
                    'line_idx': idx
                })

    return questions


def convert_capi_to_instruments(file: RawFile, text_content: str) -> List[Instrument]:
    """Convert a CAPI formatted PDF to Harmony Instruments."""
    extracted_questions = extract_capi_questions(text_content)

    if len(extracted_questions) == 0:
        return []

    questions = []
    for q in extracted_questions:
        question = Question(
            question_no=q['question_no'],
            question_intro="",
            question_text=q['question_text'],
            options=[],
            source_page=0
        )
        questions.append(question)

    language = "en"
    try:
        all_question_texts = [q['question_text'] for q in extracted_questions]
        valid_texts = [t for t in all_question_texts if isinstance(t, str) and t.strip()]
        if valid_texts:
            language = detect(" ".join(valid_texts))
    except LangDetectException:
        print("Error identifying language in CAPI file")
        traceback.print_exc()

    instrument = Instrument(
        file_id=file.file_id,
        instrument_id=file.file_id + "_0",
        file_name=file.file_name,
        instrument_name=file.file_name,
        file_type=file.file_type,
        file_section="CAPI",
        language=language,
        questions=questions
    )

    return [instrument]
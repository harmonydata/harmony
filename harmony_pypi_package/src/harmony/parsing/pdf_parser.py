import re
import uuid

from langdetect import detect

from harmony.schemas.requests.text import RawFile, Instrument, Question
from harmony.parsing.util.tika_wrapper import parse_pdf_to_plain_text
from harmony.parsing.text_parser import convert_text_to_instruments

def convert_pdf_to_instruments(file: RawFile) -> Instrument:
    file.text_content = parse_pdf_to_plain_text(file.content)

    return convert_text_to_instruments(file)

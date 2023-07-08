from typing import List

from harmony.parsing.excel_parser import convert_excel_to_instruments
from harmony.parsing.pdf_parser import convert_pdf_to_instruments
from harmony.parsing.text_parser import convert_text_to_instruments
from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile, Instrument


def _get_instruments_from_file(file):
    if file.file_type == FileType.pdf or file.file_type == FileType.docx:
        instruments_from_this_file = convert_pdf_to_instruments(file)
    elif file.file_type == FileType.txt:
        instruments_from_this_file = convert_text_to_instruments(file)
    elif file.file_type == FileType.xlsx:
        instruments_from_this_file = convert_excel_to_instruments(file)
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

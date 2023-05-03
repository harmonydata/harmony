from typing import List

from harmony.parsing.excel_parser import convert_excel_to_instruments
from harmony.parsing.pdf_parser import convert_pdf_to_instruments
from harmony.parsing.text_parser import convert_text_to_instruments
from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile, Instrument


def convert_file_to_instruments(file: RawFile) -> List[Instrument]:
    instruments = []

    if file.file_type == FileType.pdf:
        instruments.append(convert_pdf_to_instruments(file))
    elif file.file_type == FileType.txt:
        instruments.append(convert_text_to_instruments(file))
    elif file.file_type == FileType.xlsx:
        instruments.extend(convert_excel_to_instruments(file))

    return instruments

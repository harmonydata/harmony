from typing import List

from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile, Instrument
from harmony.parsing.excel_instrument_extractor import xlsx_to_instruments
from harmony.parsing.pdf_instrument_extractor import pdf_to_instrument
from harmony.parsing.text_instrument_extractor import txt_to_instrument

def convert_files_to_instruments(files: List[RawFile]) -> List[Instrument]:
    instruments = []

    for file in files:
        if file.file_type == FileType.pdf:
            instruments.append(pdf_to_instrument(file))
        elif file.file_type == FileType.txt:
            instruments.append(txt_to_instrument(file))
        elif file.file_type == FileType.xlsx:
            instruments.extend(xlsx_to_instruments(file))

    return instruments


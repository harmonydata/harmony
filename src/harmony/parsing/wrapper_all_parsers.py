import os
from typing import List

import pyfscache
from harmony.parsing.excel_parser import convert_excel_to_instruments
from harmony.parsing.pdf_parser import convert_pdf_to_instruments
from harmony.parsing.text_parser import convert_text_to_instruments
from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile, Instrument
from flask_caching import Cache
from main import app

cache_path = os.getenv("HARMONY_DATA_PATH", ".") + "/parse_cache"
cache = Cache(app, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': cache_path,
    'CACHE_DEFAULT_TIMEOUT': 3600 * 24 * 30,
})


@cache.memoize()
def cached_parse_file(file):
    if file.file_type == FileType.pdf:
        instruments_from_this_file = convert_pdf_to_instruments(file)
    elif file.file_type == FileType.txt:
        instruments_from_this_file = convert_text_to_instruments(file)
    elif file.file_type == FileType.xlsx:
        instruments_from_this_file = convert_excel_to_instruments(file)
    else:
        instruments_from_this_file = []
    return instruments_from_this_file


def convert_files_to_instruments(files: List[RawFile]) -> List[Instrument]:
    instruments = []

    for file in files:
        instruments_from_this_file = cached_parse_file(file)
        instruments.extend(instruments_from_this_file)

    return instruments

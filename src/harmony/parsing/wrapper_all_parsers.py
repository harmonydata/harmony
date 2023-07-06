from typing import List

from harmony.parsing.excel_parser import convert_excel_to_instruments
from harmony.parsing.pdf_parser import convert_pdf_to_instruments
from harmony.parsing.text_parser import convert_text_to_instruments
from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile, Instrument
from harmony.services.instruments_cache import InstrumentsCache
from harmony.util import cache_heper


def _get_instruments_from_file(file):
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
    """Get cached instruments of files or convert files to instruments"""

    instruments_cache = InstrumentsCache()

    instruments: List[Instrument] = []

    # A list of files whose instruments are not cached
    files_with_no_cached_instruments = []

    for file in files:
        hash_value = cache_heper.get_hash_value(file.content)
        if instruments_cache.has(hash_value):
            # If instruments are cached
            instruments.extend(instruments_cache.get(hash_value))
        else:
            # If instruments are not cached
            files_with_no_cached_instruments.append(file)

    # Get instruments that aren't cached yet and cache them
    for file_with_no_cached_instruments in files_with_no_cached_instruments:
        new_instruments = _get_instruments_from_file(file_with_no_cached_instruments)
        hash_value = cache_heper.get_hash_value(file_with_no_cached_instruments.content)
        instruments_cache.set(hash_value, new_instruments)
        instruments.extend(new_instruments)

    return instruments

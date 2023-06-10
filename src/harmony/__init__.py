__version__ = "0.2.0"

# TODO: make these configurable at package level
import os
from .parsing.text_parser import convert_text_to_instruments
from .parsing.excel_parser import convert_excel_to_instruments
from .parsing.pdf_parser import convert_pdf_to_instruments
from .parsing.wrapper_all_parsers import convert_files_to_instruments
from .parsing import *
from .schemas import *
from .matching.matcher import match_instruments_with_function
try:
    from .matching.default_matcher import match_instruments
except:
    print ("Warning: transformers not available. To use transformers, run pip install sentence-transformers")

from .util.file_helper import load_instruments_from_local_file

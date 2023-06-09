__version__ = "0.1.0"

# TODO: make these configurable at package level
from .parsing.text_parser import convert_text_to_instruments
from .parsing.excel_parser import convert_excel_to_instruments
from .parsing.pdf_parser import convert_pdf_to_instruments
from .parsing.wrapper_all_parsers import convert_files_to_instruments
from .parsing import *
from .schemas import *
from .matching.matcher import match_instruments_with_function

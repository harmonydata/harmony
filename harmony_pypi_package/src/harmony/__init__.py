__version__ = "0.1.0"

# TODO: make these configurable at package level
try:
    from .parsing.text_parser import convert_text_to_instruments
except ImportError:
    print ("Could not import text parser")
try:
    from .parsing.excel_parser import convert_excel_to_instruments
except ImportError:
    print ("Could not import Excel parser")
try:
    from .parsing.pdf_parser import convert_pdf_to_instruments
except ImportError:
    print ("Could not import Excel parser")
try:
    from .parsing.wrapper_all_parsers import convert_file_to_instruments
except ImportError:
    print ("Could not import Excel parser")
try:
    from .parsing import *
except ImportError:
    print ("Could not import parsing functions")
try:
    from .schemas import *
except ImportError:
    print ("Could not import schemas")

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

__version__ = "1.0.1"

# TODO: make these configurable at package level
import os

from .examples import example_instruments
from .schemas import *
from .util.instrument_helper import create_instrument_from_list, import_instrument_into_harmony_web
from .util.model_downloader import download_models

if os.environ.get("HARMONY_NO_PARSING") is None or os.environ.get("HARMONY_NO_PARSING") == "":
    from .parsing.text_parser import convert_text_to_instruments
    from .parsing.excel_parser import convert_excel_to_instruments
    from .parsing.pdf_parser import convert_pdf_to_instruments
    from .parsing.wrapper_all_parsers import convert_files_to_instruments
    from .parsing import *
    from .util.file_helper import load_instruments_from_local_file

if os.environ.get("HARMONY_NO_MATCHING") is None or os.environ.get("HARMONY_NO_MATCHING") == "":
    from .matching.matcher import match_instruments_with_function

    try:
        from .matching.default_matcher import match_instruments
    except ModuleNotFoundError:
        print("Warning: transformers not available. To use transformers, run pip install sentence-transformers")

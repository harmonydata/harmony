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

import sys
import unittest

sys.path.append("../src")

from harmony import convert_pdf_to_instruments
from harmony.schemas.requests.text import RawFile
from harmony import download_models


pdf_empty_table = RawFile.model_validate({
    "file_id": "d39f31718513413fbfc620c6b6135d0c",
    "file_name": "GAD-7.pdf",
    "file_type": "pdf",
    "tables": [],
    "text_content":"aaa",
    "content":""
})

pdf_non_empty_table = RawFile.model_validate({
    "file_id": "d39f31718513413fbfc620c6b6135d0c",
    "file_name": "GAD-7.pdf",
    "file_type": "pdf",
   'tables': [["hello"]],
    "text_content":"aaa",
        "content":""
})

class TestConvertPdfTables(unittest.TestCase):

    pass

    # Not using tables at the moment
    #
    # def test_empty_pdf(self):
    #
    #     self.assertEqual(0, len(convert_pdf_to_instruments(pdf_empty_table)))
    #
    # def test_two_questions(self):
    #     self.assertEqual(2, len(convert_pdf_to_instruments(pdf_non_empty_table)[0].questions))


if __name__ == '__main__':
    unittest.main()

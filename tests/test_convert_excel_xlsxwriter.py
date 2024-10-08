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

from harmony import convert_excel_to_instruments
from harmony.schemas.requests.text import RawFile

sys.path.append("../src")

xlsx_gad_7_2_questions = RawFile.model_validate({
    "file_id": "1d66bce4b80c4b0eaefe33f00cddedef",
    "file_name": "GAD-7.xlsx",
    "file_type": "xlsx",
    "content": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,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"
})


class TestConvertExcelXlsxwriter(unittest.TestCase):

    def test_single_instrument(self):
        self.assertEqual(1, len(convert_excel_to_instruments(xlsx_gad_7_2_questions)))

    def test_two_questions(self):
        self.assertEqual(2, len(convert_excel_to_instruments(xlsx_gad_7_2_questions)[0].questions))


if __name__ == '__main__':
    unittest.main()

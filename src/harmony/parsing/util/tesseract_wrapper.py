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

import base64
import io
import pytesseract
from pdf2image import convert_from_bytes

def parse_image_pdf_to_plain_text(contents: str) -> str:
    """
    Call the Tesseract library. For PDFs containing images.

    :param contents: The base64 encoding of the PDF file
    :return: A str containing the content of the document.
    """
    print("Preparing data for Tika")
    content_type, content_string = contents.split(",")
    file_in_bytes = base64.b64decode(content_string)
    pages = convert_from_bytes(file_in_bytes, 500)

    page_contents = []
    for pageNum, imgBlob in enumerate(pages):
        text = pytesseract.image_to_string(imgBlob, lang='eng')
        page_contents.append(text)

    return "\n".join(page_contents)
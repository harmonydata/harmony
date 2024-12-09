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
import uuid
from typing import List
import pdfkit
from bs4 import BeautifulSoup


from harmony.parsing.wrapper_all_parsers import convert_files_to_instruments
from harmony.schemas.requests.text import Instrument
from harmony.schemas.requests.text import RawFile

def extract_html_title(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    return soup.title.string.strip() if soup.title else "Untitled"

def convert_html_to_pdf(file_name: str) -> RawFile:
    """
    Convert html to pdf,
    """
    try:
        # Convert HTML to PDF
        if file_name.startswith("http"):
            pdf_content = pdfkit.from_url(file_name, False) 
        else:
            pdf_content = pdfkit.from_file(file_name, False)

        file_as_base64 = base64.urlsafe_b64encode(pdf_content).decode("ascii")

        return RawFile(
            file_type="pdf",
            content="," + file_as_base64,
            file_id=uuid.uuid4().hex,
            file_name=file_name,
        )

    except Exception as e:
        print(f"Error during HTML conversion and parsing: {e}")
        
def load_instruments_from_local_file(file_name: str) -> List[Instrument]:
    """
    Open a local file (PDF, Excel, Word or TXT format) and parse it into a list of Instrument objects.
    :param file_name: Local file path, either absolute or relative.
    :return: List of Instruments.
    """
    if file_name.lower().endswith("pdf"):
        file_type = "pdf"
    elif file_name.lower().endswith("xlsx"):
        file_type = "xlsx"
    elif file_name.lower().endswith("docx"):
        file_type = "docx"
    elif file_name.lower().endswith("html"):
        file_type = "html"
    else:
        file_type = "txt"

    if file_type in ["pdf", "xlsx", "docx"]:
        with open(
                file_name,
                "rb") as f:
            file_as_bytes = f.read()

        file_as_base64 = base64.b64encode(file_as_bytes).decode('ascii')
        print(f"File as Base64 (first 100 characters): {file_as_base64[:100]}")

        harmony_file = RawFile(file_type=file_type, content= "," + file_as_base64, file_id=uuid.uuid4().hex,
                               file_name=file_name)
    elif file_type == "html":
        harmony_file = convert_html_to_pdf(file_name)
        title = extract_html_title(file_name)
        harmony_file.file_name = title
    else:
        with open(
                file_name,
                "r", encoding="utf-8") as f:
            file_as_string = f.read()
        harmony_file = RawFile(file_type="txt", content=file_as_string, file_id=uuid.uuid4().hex,
                               file_name=file_name)

    return convert_files_to_instruments([harmony_file])

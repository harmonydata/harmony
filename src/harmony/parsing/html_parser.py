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
import pdfkit
from harmony.schemas.requests.text import RawFile

# Convert an HTML file (local or URL) into a PDF and process it using the existing PDF parser.
def convert_html_to_instruments(file: RawFile) -> None:
    if file.file_type != "html":
        raise ValueError("Input file must have a file_type of 'html'.")

    try:
        # Convert HTML to PDF
        if file.content.startswith("http"):
            pdf_content = pdfkit.from_url(file.content, False)  # False returns byte stream
        else:
            # Decode base64 content if the HTML file is provided as base64
            html_content = base64.urlsafe_b64decode(file.content).decode("utf-8")
            pdf_content = pdfkit.from_string(html_content, False)

        # Encode PDF as base64 for the RawFile
        file_as_base64 = base64.urlsafe_b64encode(pdf_content).decode("ascii")

        # Update the file to represent the converted PDF
        file.file_type = "pdf"
        file.content = "," + file_as_base64
        file.file_name = file.file_name.replace(".html", ".pdf")

        # Call the existing PDF parser
        convert_pdf_to_instruments(file)

    except Exception as e:
        print(f"Error during HTML conversion and parsing: {e}")

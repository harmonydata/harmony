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

from lxml import html
from tika import parser


def parse_pdf_to_plain_text(contents: str) -> str:
    """
    Call the Tika library (Java, called via a server) to process a PDF file into a list of strings.

    You need to have Tika running locally or on a remote server for this function to work:

    <code>
    java -jar tika-server-standard-2.3.0.jar
    </code>

    :param contents: The base64 encoding of the PDF file
    :return: A str containing the content of the document.
    """
    print("Preparing data for Tika")
    content_type, content_string = contents.split(",")
    file_in_bytes = base64.b64decode(content_string)

    file = io.BytesIO(file_in_bytes)
    print("Calling Tika")
    parsed = parser.from_buffer(file, xmlContent=True, requestOptions={'timeout': 300})
    print("Got response from Tika")
    parsed_xml = parsed["content"]

    et = html.fromstring(parsed_xml)
    pages = et.getchildren()[1].getchildren()
    print("Parsed response from Tika")

    return "\n".join([str(page.text_content()) for page in pages])

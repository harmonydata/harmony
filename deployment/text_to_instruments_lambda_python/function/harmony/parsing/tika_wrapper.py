import base64
import io

from lxml import html
from tika import parser


def parse_pdf_to_plain_text(contents: str) -> list:
    """
    Call the Tika library (Java, called via a server) to process a PDF file into a list of strings.
    :param contents: The base64 encoding of the PDF file
    :return: A list of strings each containing the content of a single page
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

    return [str(page.text_content()) for page in pages]

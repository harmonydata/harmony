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

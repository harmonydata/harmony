import base64
import io
import uuid
import camelot


def parse_pdf_to_tables(contents: str) -> str:
    """
    Call the Tesseract library. For PDFs containing images.

    :param contents: The base64 encoding of the PDF file
    :return: A str containing the content of the document.
    """
    print("Preparing data for Tika")
    content_type, content_string = contents.split(",")
    file_in_bytes = base64.b64decode(content_string)

    tmpfile = "/tmp/" + uuid.uuid4().hex + ".pdf"
    with open(tmpfile, "wb") as f:
        f.write(file_in_bytes)

    tables = camelot.read_pdf(tmpfile)

    return [t.data for t in tables]



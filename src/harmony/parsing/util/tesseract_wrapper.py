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
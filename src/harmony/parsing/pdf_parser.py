from harmony.parsing.text_parser import convert_text_to_instruments
from harmony.parsing.util.tika_wrapper import parse_pdf_to_plain_text
# from harmony.parsing.util.tesseract_wrapper import parse_image_pdf_to_plain_text
from harmony.parsing.util.camelot_wrapper import parse_pdf_to_tables
from harmony.schemas.requests.text import RawFile, Instrument
import camelot

def convert_pdf_to_instruments(file: RawFile) -> Instrument:
    if not file.text_content:
        file.text_content = parse_pdf_to_plain_text(file.content)
    # Fallback to Tesseract
    # if file.text_content is None or len(file.text_content.strip()) < 10:
    #     file.text_content = parse_image_pdf_to_plain_text(file.content)

    file.tables = parse_pdf_to_tables(file.content)

    return convert_text_to_instruments(file)

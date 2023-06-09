import base64
import uuid
from typing import List

from harmony.parsing.wrapper_all_parsers import convert_files_to_instruments
from harmony.schemas.requests.text import Instrument
from harmony.schemas.requests.text import RawFile


def load_instruments_from_local_file(file_name: str) -> List[Instrument]:
    if file_name.lower().endswith("pdf"):
        file_type = "pdf"
    elif file_name.lower().endswith("xlsx"):
        file_type = "xlsx"
    else:
        file_type = "txt"

    if file_type == "pdf" or file_type == "xlsx":
        with open(
                file_name,
                "rb") as f:
            file_as_bytes = f.read()

        file_as_base64 = base64.b64encode(file_as_bytes).decode('ascii')

        harmony_file = RawFile(file_type=file_type, content="," + file_as_base64, file_id=uuid.uuid4().hex)
    else:
        with open(
                file_name,
                "r", encoding="utf-8") as f:
            file_as_string = f.read()
        harmony_file = RawFile(file_type="txt", content=file_as_string, file_id=uuid.uuid4().hex)

    return convert_files_to_instruments([harmony_file])

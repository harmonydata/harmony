import base64
from typing import List
import uuid

from harmony.schemas.requests.text import Instrument
from harmony.schemas.requests.text import RawFile
from harmony.parsing.wrapper_all_parsers import convert_files_to_instruments
def load_instruments_from_local_file(file_name: str) -> List[Instrument]:
    with open(
            file_name,
            "rb") as f:
        file_as_bytes = f.read()

    file_as_base64 = base64.b64encode(file_as_bytes).decode('ascii')

    harmony_file = RawFile(file_type="pdf", content="," + file_as_base64, file_id=uuid.uuid4().hex)

    return convert_files_to_instruments([harmony_file])


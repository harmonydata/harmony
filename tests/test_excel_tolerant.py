import base64
import io
import unittest
import uuid
from harmony.parsing.wrapper_all_parsers import convert_files_to_instruments
from harmony.schemas.requests.text import RawFile


class TestExcelTolerantFormat(unittest.TestCase):
    def test_excel_tolerant_format(self):
        with open("tests/wellbeing-scales-list.xlsx", "rb") as f:
            file_as_bytes = f.read()

        file_as_base64 = base64.b64encode(file_as_bytes).decode("ascii")

        harmony_file = RawFile(
            file_type="xlsx",
            content="," + file_as_base64,
            file_id=uuid.uuid4().hex,
            file_name="wellbeing-scales-list.xlsx"
        )

        instruments = convert_files_to_instruments([harmony_file])

        self.assertGreater(len(instruments), 0)
        self.assertGreater(len(instruments[0].questions), 0)

        for q in instruments[0].questions:
            self.assertTrue(len(q.question_text.strip()) > 0)
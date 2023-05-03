import unittest

from harmony import convert_text_to_instruments
from harmony.schemas.requests.text import RawFile

txt_gad_7_2_questions = RawFile.parse_obj({
    "file_id": "d39f31718513413fbfc620c6b6135d0c",
    "file_name": "GAD-7.txt",
    "file_type": "txt",
    "content": """I feel nervous, anxious and afraid
I feel scared"""
}
)


class TestConvertTxt(unittest.TestCase):

    def test_single_instrument(self):
        self.assertEqual(1, len(convert_text_to_instruments(txt_gad_7_2_questions)))

    def test_two_questions(self):
        self.assertEqual(2, len(convert_text_to_instruments(txt_gad_7_2_questions)[0].questions))


if __name__ == '__main__':
    unittest.main()

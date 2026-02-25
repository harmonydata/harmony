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

import sys
import unittest
import json

sys.path.append("../src")

from harmony.parsing.google_forms_parser import (
    extract_form_id_from_url,
    parse_question_item,
    parse_google_form_structure,
    convert_google_forms_to_instruments
)
from harmony.schemas.requests.text import RawFile
from harmony.schemas.enums.file_types import FileType


# Mock data for testing without API calls
MOCK_FORM_RESPONSE = {
    "formId": "test_form_12345",
    "info": {
        "title": "GAD-7 Anxiety Scale",
        "description": "Generalized Anxiety Disorder Assessment",
        "documentTitle": "GAD-7 Form"
    },
    "items": [
        {
            "title": "Feeling nervous, anxious or on edge",
            "description": "",
            "questionItem": {
                "question": {
                    "choiceQuestion": {
                        "type": "RADIO",
                        "options": [
                            {"value": "Not at all"},
                            {"value": "Several days"},
                            {"value": "More than half the days"},
                            {"value": "Nearly every day"}
                        ]
                    }
                }
            }
        },
        {
            "title": "Not being able to stop or control worrying",
            "description": "",
            "questionItem": {
                "question": {
                    "choiceQuestion": {
                        "type": "RADIO",
                        "options": [
                            {"value": "Not at all"},
                            {"value": "Several days"},
                            {"value": "More than half the days"},
                            {"value": "Nearly every day"}
                        ]
                    }
                }
            }
        },
        {
            "title": "Rate your overall anxiety level",
            "description": "On a scale from 1 to 5",
            "questionItem": {
                "question": {
                    "scaleQuestion": {
                        "low": 1,
                        "high": 5,
                        "lowLabel": "Not anxious",
                        "highLabel": "Extremely anxious"
                    }
                }
            }
        },
        {
            "title": "Please provide additional comments",
            "description": "",
            "questionItem": {
                "question": {
                    "textQuestion": {
                        "paragraph": True
                    }
                }
            }
        },
        {
            "title": "Section Header",
            "description": "This is just a section, not a question"
        }
    ]
}


class TestExtractFormId(unittest.TestCase):
    """Test form ID extraction from various URL formats."""

    def test_extract_from_viewform_url(self):
        """Test extraction from standard viewform URL."""
        url = "https://docs.google.com/forms/d/e/1FAIpQLSc_example_id_12345/viewform"
        form_id = extract_form_id_from_url(url)
        self.assertEqual(form_id, "1FAIpQLSc_example_id_12345")

    def test_extract_from_edit_url(self):
        """Test extraction from edit URL."""
        url = "https://docs.google.com/forms/d/1FAIpQLSc_another_id_67890/edit"
        form_id = extract_form_id_from_url(url)
        self.assertEqual(form_id, "1FAIpQLSc_another_id_67890")

    def test_extract_from_direct_id(self):
        """Test extraction when input is already a form ID."""
        direct_id = "1FAIpQLSc_direct_form_id_xyz"
        form_id = extract_form_id_from_url(direct_id)
        self.assertEqual(form_id, direct_id)

    def test_invalid_url(self):
        """Test extraction from invalid URL returns None."""
        invalid_url = "https://example.com/not-a-google-form"
        form_id = extract_form_id_from_url(invalid_url)
        self.assertIsNone(form_id)


class TestParseQuestionItem(unittest.TestCase):
    """Test parsing of individual question items."""

    def test_parse_multiple_choice(self):
        """Test parsing a multiple choice question."""
        item = MOCK_FORM_RESPONSE["items"][0]
        question = parse_question_item(item, 1)

        self.assertIsNotNone(question)
        self.assertEqual(question.question_no, "1")
        self.assertEqual(question.question_text, "Feeling nervous, anxious or on edge")
        self.assertEqual(len(question.options), 4)
        self.assertIn("Not at all", question.options)
        self.assertIn("Nearly every day", question.options)

    def test_parse_scale_question(self):
        """Test parsing a linear scale question."""
        item = MOCK_FORM_RESPONSE["items"][2]
        question = parse_question_item(item, 3)

        self.assertIsNotNone(question)
        self.assertEqual(question.question_no, "3")
        self.assertEqual(question.question_text, "Rate your overall anxiety level")
        self.assertEqual(question.options, ["1", "2", "3", "4", "5"])
        self.assertIn("Not anxious", question.question_intro)
        self.assertIn("Extremely anxious", question.question_intro)

    def test_parse_text_question(self):
        """Test parsing a text question (no options)."""
        item = MOCK_FORM_RESPONSE["items"][3]
        question = parse_question_item(item, 4)

        self.assertIsNotNone(question)
        self.assertEqual(question.question_no, "4")
        self.assertEqual(question.question_text, "Please provide additional comments")
        self.assertEqual(question.options, [])

    def test_skip_non_question_item(self):
        """Test that non-question items (sections, page breaks) are skipped."""
        item = MOCK_FORM_RESPONSE["items"][4]
        question = parse_question_item(item, 5)

        self.assertIsNone(question)


class TestParseGoogleFormStructure(unittest.TestCase):
    """Test parsing complete form structure."""

    def test_parse_complete_form(self):
        """Test parsing a complete form structure into Instrument."""
        instrument = parse_google_form_structure(MOCK_FORM_RESPONSE)

        # Verify basic metadata
        self.assertEqual(instrument.file_id, "test_form_12345")
        self.assertEqual(instrument.instrument_id, "test_form_12345")
        self.assertEqual(instrument.instrument_name, "GAD-7 Anxiety Scale")
        self.assertEqual(instrument.file_type, FileType.google_forms)

        # Verify questions (should be 4 questions, skipping the section)
        self.assertEqual(len(instrument.questions), 4)

        # Verify metadata dictionary
        self.assertIsNotNone(instrument.metadata)
        self.assertEqual(instrument.metadata["form_id"], "test_form_12345")
        self.assertEqual(instrument.metadata["title"], "GAD-7 Anxiety Scale")
        self.assertEqual(instrument.metadata["source"], "google_forms")

        # Verify language detection (should default to "en")
        self.assertIsNotNone(instrument.language)


class TestConvertGoogleFormsToInstruments(unittest.TestCase):
    """Test complete conversion workflow."""

    def test_convert_from_json_content(self):
        """Test conversion from pre-fetched JSON content (for testing)."""
        file = RawFile(
            file_name="GAD-7.google_forms",
            file_type=FileType.google_forms,
            content=json.dumps(MOCK_FORM_RESPONSE)
        )

        instruments = convert_google_forms_to_instruments(file)

        # Verify we get a list with one instrument
        self.assertEqual(len(instruments), 1)

        instrument = instruments[0]

        # Verify instrument properties
        self.assertEqual(instrument.instrument_name, "GAD-7 Anxiety Scale")
        self.assertEqual(instrument.file_type, FileType.google_forms)
        self.assertEqual(len(instrument.questions), 4)

        # Verify first question
        first_q = instrument.questions[0]
        self.assertEqual(first_q.question_text, "Feeling nervous, anxious or on edge")
        self.assertEqual(len(first_q.options), 4)


if __name__ == '__main__':
    unittest.main()

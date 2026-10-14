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

import os
import sys
import types
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.append("../src")

from harmony.parsing import wrapper_all_parsers
from harmony.parsing.wrapper_all_parsers import convert_files_to_instruments
from harmony.schemas.requests.text import RawFile, Instrument

pdf_file = RawFile.model_validate({
    "file_name": "GAD-7.pdf",
    "file_type": "pdf",
    "content": "data:application/pdf;base64,JVBERi0xLjQK"
})

png_file = RawFile.model_validate({
    "file_name": "GAD-7.png",
    "file_type": "png",
    "content": "data:image/png;base64,iVBORw0KGgo="
})

csv_file = RawFile.model_validate({
    "file_name": "GAD-7.csv",
    "file_type": "csv",
    "content": "I feel nervous\nI feel afraid"
})

pdf_parser_result = [Instrument(instrument_name="from the PDF parser", questions=[])]


def fake_openai_module(client):
    module = types.ModuleType("openai")
    module.OpenAI = mock.Mock(return_value=client)
    return module


def fake_openai_client():
    client = mock.Mock()
    client.files.create.return_value = SimpleNamespace(id="file-abc")
    client.responses.parse.return_value = SimpleNamespace(output_parsed=SimpleNamespace(questions=[
        SimpleNamespace(question_no="1", question_intro="Over the last two weeks",
                        question_text="Feeling nervous", response_options=["Not at all", "Several days"]),
    ]))
    return client


class TestOpenAIExtraction(unittest.TestCase):

    def test_csv_parses_without_key_or_openai_installed(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.dict(sys.modules, {"openai": None}):
            instruments = convert_files_to_instruments([csv_file])
        self.assertEqual(2, len(instruments[0].questions))

    @mock.patch.object(wrapper_all_parsers, "convert_pdf_to_instruments", return_value=pdf_parser_result)
    def test_pdf_without_key_uses_pdf_parser(self, convert_pdf):
        with mock.patch.dict(os.environ, {}, clear=True):
            instruments = convert_files_to_instruments([pdf_file])
        self.assertEqual("from the PDF parser", instruments[0].instrument_name)

    @mock.patch.object(wrapper_all_parsers, "convert_pdf_to_instruments", return_value=pdf_parser_result)
    def test_pdf_with_key_uses_openai(self, convert_pdf):
        client = fake_openai_client()
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test"}), \
                mock.patch.dict(sys.modules, {"openai": fake_openai_module(client)}):
            instruments = convert_files_to_instruments([pdf_file])
        convert_pdf.assert_not_called()
        client.files.create.assert_called_once()
        self.assertEqual("GAD-7.pdf", instruments[0].instrument_name)
        self.assertEqual("GAD-7.pdf", instruments[0].file_name)
        self.assertEqual("Feeling nervous", instruments[0].questions[0].question_text)
        self.assertEqual("Over the last two weeks", instruments[0].questions[0].question_intro)
        self.assertEqual(["Not at all", "Several days"], instruments[0].questions[0].options)
        self.assertEqual(instruments[0].instrument_id, instruments[0].questions[0].instrument_id)

    def test_image_with_key_uses_openai(self):
        client = fake_openai_client()
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test"}), \
                mock.patch.dict(sys.modules, {"openai": fake_openai_module(client)}):
            instruments = convert_files_to_instruments([png_file])
        client.files.create.assert_not_called()
        self.assertEqual("GAD-7.png", instruments[0].instrument_name)
        self.assertEqual(1, len(instruments[0].questions))

    @mock.patch.object(wrapper_all_parsers, "convert_pdf_to_instruments", return_value=pdf_parser_result)
    def test_pdf_falls_back_when_openai_fails(self, convert_pdf):
        client = fake_openai_client()
        client.responses.parse.side_effect = RuntimeError("rate limited")
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test"}), \
                mock.patch.dict(sys.modules, {"openai": fake_openai_module(client)}):
            instruments = convert_files_to_instruments([pdf_file])
        self.assertEqual("from the PDF parser", instruments[0].instrument_name)

    @mock.patch.object(wrapper_all_parsers, "convert_pdf_to_instruments", return_value=pdf_parser_result)
    def test_large_pdf_uses_pdf_parser(self, convert_pdf):
        large_pdf_file = pdf_file.model_copy(
            update={"content": "data:application/pdf;base64," + "A" * wrapper_all_parsers.OPENAI_MAX_CONTENT_LENGTH})
        client = fake_openai_client()
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test"}), \
                mock.patch.dict(sys.modules, {"openai": fake_openai_module(client)}):
            instruments = convert_files_to_instruments([large_pdf_file])
        client.responses.parse.assert_not_called()
        self.assertEqual("from the PDF parser", instruments[0].instrument_name)

    @mock.patch.object(wrapper_all_parsers, "convert_pdf_to_instruments", return_value=pdf_parser_result)
    def test_docx_with_key_uses_pdf_parser(self, convert_pdf):
        docx_file = pdf_file.model_copy(update={"file_name": "GAD-7.docx", "file_type": "docx"})
        client = fake_openai_client()
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test"}), \
                mock.patch.dict(sys.modules, {"openai": fake_openai_module(client)}):
            instruments = convert_files_to_instruments([docx_file])
        client.responses.parse.assert_not_called()
        self.assertEqual("from the PDF parser", instruments[0].instrument_name)


if __name__ == '__main__':
    unittest.main()

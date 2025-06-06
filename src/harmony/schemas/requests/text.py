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

import uuid
from typing import List, Optional

from pydantic import ConfigDict, BaseModel, Field

from harmony.schemas.catalogue_instrument import CatalogueInstrument
from harmony.schemas.catalogue_question import CatalogueQuestion
from harmony.schemas.enums.file_types import FileType
from harmony.schemas.enums.languages import Language

DEFAULT_FRAMEWORK = "huggingface"
DEFAULT_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'


class RawFile(BaseModel):
    file_id: Optional[str] = Field(None, description="Unique identifier for the file (UUID-4)")
    file_name: str = Field("Untitled file", description="The name of the input file")
    file_type: FileType = Field(description="The file type (pdf, xlsx, txt)")
    content: str = Field(description="The raw file contents")
    text_content: Optional[str] = Field(None, description="The plain text content")
    tables: list = Field([], description="The tables in the file")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_id": "d39f31718513413fbfc620c6b6135d0c",
                "file_name": "GAD-7.pdf",
                "file_type": "pdf",
                "content": "data:application/pdf;base64,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ZXJpZgovQ0lEU3lzdGVtSW5mbyA8PCAvUmVnaXN0cnkgKEFkb2JlKSAvT3JkZXJpbmcgKElkZW50aXR5KSAvU3VwcGxlbWVudCAwID4+Ci9Gb250RGVzY3JpcHRvciAxMiAwIFIKL0NJRFRvR0lETWFwIC9JZGVudGl0eQovVyBbMCBbNjAwIDYzNiAzMTggMzE4IDY5NCA1OTIgMzIwIDMyMCA2NDQgNjQwIDQ3OCA1NjUgNjAyIDY0NCA1MTMgMzE4IDU5NiA1NjQgNjQwIDYzNiA4NzUgNDAyIDY0MCA2NDAgNTYwIDg1NiA1NjUgXQpdCj4+CmVuZG9iagoxNSAwIG9iago8PCAvTGVuZ3RoIDU0NiA+PgpzdHJlYW0KL0NJREluaXQgL1Byb2NTZXQgZmluZHJlc291cmNlIGJlZ2luCjEyIGRpY3QgYmVnaW4KYmVnaW5jbWFwCi9DSURTeXN0ZW1JbmZvIDw8IC9SZWdpc3RyeSAoQWRvYmUpIC9PcmRlcmluZyAoVUNTKSAvU3VwcGxlbWVudCAwID4+IGRlZgovQ01hcE5hbWUgL0Fkb2JlLUlkZW50aXR5LVVDUyBkZWYKL0NNYXBUeXBlIDIgZGVmCjEgYmVnaW5jb2Rlc3BhY2VyYW5nZQo8MDAwMD4gPEZGRkY+CmVuZGNvZGVzcGFjZXJhbmdlCjIgYmVnaW5iZnJhbmdlCjwwMDAwPiA8MDAwMD4gPDAwMDA+CjwwMDAxPiA8MDAxQT4gWzwwMDMxPiA8MDAyRT4gPDAwMDk+IDwwMDQ2PiA8MDA2NT4gPDAwNkM+IDwwMDY5PiA8MDA2RT4gPDAwNjc+IDwwMDcyPiA8MDA3Nj4gPDAwNkY+IDwwMDc1PiA8MDA3Mz4gPDAwMkM+IDwwMDYxPiA8MDA3OD4gPDAwNjQ+IDwwMDMyPiA8MDA0RT4gPDAwNzQ+IDwwMDYyPiA8MDA3MD4gPDAwNjM+IDwwMDc3PiA8MDA3OT4gXQplbmRiZnJhbmdlCmVuZGNtYXAKQ01hcE5hbWUgY3VycmVudGRpY3QgL0NNYXAgZGVmaW5lcmVzb3VyY2UgcG9wCmVuZAplbmQKCmVuZHN0cmVhbQplbmRvYmoKNyAwIG9iago8PCAvVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTAKL0Jhc2VGb250IC9EZWphVnVTZXJpZgovRW5jb2RpbmcgL0lkZW50aXR5LUgKL0Rlc2NlbmRhbnRGb250cyBbMTQgMCBSXQovVG9Vbmljb2RlIDE1IDAgUj4+CmVuZG9iagoxNiAwIG9iago8PAovTGVuZ3RoIDQKPj4Kc3RyZWFtCv///+AKZW5kc3RyZWFtCmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyAKWwo2IDAgUgpdCi9Db3VudCAxCi9Qcm9jU2V0IFsvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQ10KPj4KZW5kb2JqCnhyZWYKMCAxOAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwMDE2OSAwMDAwMCBuIAowMDAwMDA4MjQzIDAwMDAwIG4gCjAwMDAwMDAyMTggMDAwMDAgbiAKMDAwMDAwMDMxMyAwMDAwMCBuIAowMDAwMDAwMzUwIDAwMDAwIG4gCjAwMDAwMDgwNTIgMDAwMDAgbiAKMDAwMDAwMDY3MCAwMDAwMCBuIAowMDAwMDAxMjQ0IDAwMDAwIG4gCjAwMDAwMDA0ODQgMDAwMDAgbiAKMDAwMDAwMDY1MCAwMDAwMCBuIAowMDAwMDAxMjYzIDAwMDAwIG4gCjAwMDAwMDE1MzkgMDAwMDAgbiAKMDAwMDAwNzEzNSAwMDAwMCBuIAowMDAwMDA3NDU0IDAwMDAwIG4gCjAwMDAwMDgxODkgMDAwMDAgbiAKMDAwMDAwNzExNCAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDE4IAovSW5mbyAxIDAgUgovUm9vdCAyIDAgUgo+PgpzdGFydHhyZWYKODM0MSAKJSVFT0YK"
            }
        })


class Question(BaseModel):
    question_no: Optional[str] = Field(None, description="Number of the question")
    question_intro: Optional[str] = Field(None, description="Introductory text applying to the question")
    question_text: str = Field(description="Text of the question")
    options: List[str] = Field([], description="The possible answer options")
    source_page: int = Field(0, description="The page of the PDF on which the question was located, zero-indexed")
    instrument_id: Optional[str] = Field(None, description="Unique identifier for the instrument (UUID-4)")
    instrument_name: Optional[str] = Field(None, description="Human readable name for the instrument")
    topics: Optional[list] = Field([], description="List of user-given topics with which to tag the questions")
    topics_auto: Optional[list] = Field(None, description="Automated list of topics identified by model")
    topics_strengths: Optional[dict] = Field(None,
                                             description="Automated list of topics identified by model with strength of topic")
    nearest_match_from_mhc_auto: Optional[dict] = Field(None, description="Automatically identified nearest MHC match")
    closest_catalogue_question_match: Optional[CatalogueQuestion] = Field(
        None, description="The closest question match in the catalogue for the question"
    )
    seen_in_catalogue_instruments: list[CatalogueInstrument] = Field(
        default=None, description="The instruments from the catalogue were the question was seen in"
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question_no": "1",
                "question_intro": "Over the last two weeks, how often have you been bothered by the following problems?",
                "question_text": "Feeling nervous, anxious, or on edge",
                "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"],
                "source_page": 0
            }
        })


class Instrument(BaseModel):
    file_id: Optional[str] = Field(None, description="Unique identifier for the file (UUID-4)")
    instrument_id: Optional[str] = Field(None, description="Unique identifier for the instrument (UUID-4)")
    instrument_name: str = Field("Untitled instrument", description="Human-readable name of the instrument")
    file_name: str = Field("Untitled file", description="The name of the input file")
    file_type: Optional[FileType] = Field(None, description="The file type (pdf, xlsx, txt)")
    file_section: Optional[str] = Field(None, description="The sub-section of the file, e.g. Excel tab")
    study: Optional[str] = Field(None, description="The study")
    sweep: Optional[str] = Field(None, description="The sweep")
    metadata: Optional[dict] = Field(None,
                                     description="Optional metadata about the instrument (URL, citation, DOI, copyright holder)")
    language: Language = Field(Language.English,
                               description="The ISO 639-2 (alpha-2) encoding of the instrument language")
    questions: List[Question] = Field(description="The items inside the instrument")
    closest_catalogue_instrument_matches: List[CatalogueInstrument] = Field(
        None,
        description="The closest instrument matches in the catalogue for the instrument, the first index "
                    "contains the best match etc"
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_id": "fd60a9a64b1b4078a68f4bc06f20253c",
                "instrument_id": "7829ba96f48e4848abd97884911b6795",
                "instrument_name": "GAD-7 English",
                "file_name": "GAD-7.pdf",
                "file_type": "pdf",
                "file_section": "GAD-7 English",
                "language": "en",
                "study": "MCS",
                "sweep": "Sweep 1",
                "questions": [{"question_no": "1",
                               "question_intro": "Over the last two weeks, how often have you been bothered by the following problems?",
                               "question_text": "Feeling nervous, anxious, or on edge",
                               "options": ["Not at all", "Several days", "More than half the days",
                                           "Nearly every day"],
                               "source_page": 0
                               }]
            }
        })

    def model_post_init(self, ctx) -> None:
        # Assign instrument ID if missing
        if not self.instrument_id:
            self.instrument_id = uuid.uuid4().hex

        # Assign instrument ID to questions
        for question in self.questions or []:
            question.instrument_id = self.instrument_id


class MatchParameters(BaseModel):
    framework: str = Field(DEFAULT_FRAMEWORK, description="The framework to use for matching")
    model: str = Field(DEFAULT_MODEL, description="Model")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "framework": DEFAULT_FRAMEWORK,
                "model": DEFAULT_MODEL
            }
        })


DEFAULT_MATCH_PARAMETERS = MatchParameters(framework=DEFAULT_FRAMEWORK, model=DEFAULT_MODEL)


class MatchBody(BaseModel):
    instruments: List[Instrument] = Field(description="Instruments to harmonise"),
    topics: Optional[list] = Field([], description="Topics with which to tag the questions")
    query: Optional[str] = Field(None, description="Search term")
    parameters: MatchParameters = Field(DEFAULT_MATCH_PARAMETERS, description="Parameters on how to match")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "instruments": [{
                    "file_id": "fd60a9a64b1b4078a68f4bc06f20253c",
                    "instrument_id": "7829ba96f48e4848abd97884911b6795",
                    "instrument_name": "GAD-7 English",
                    "file_name": "GAD-7 EN.pdf",
                    "file_type": "pdf",
                    "file_section": "GAD-7 English",
                    "language": "en",
                    "questions": [{"question_no": "1",
                                   "question_intro": "Over the last two weeks, how often have you been bothered by the following problems?",
                                   "question_text": "Feeling nervous, anxious, or on edge",
                                   "options": ["Not at all", "Several days", "More than half the days",
                                               "Nearly every day"],
                                   "source_page": 0
                                   },
                                  {"question_no": "2",
                                   "question_intro": "Over the last two weeks, how often have you been bothered by the following problems?",
                                   "question_text": "Not being able to stop or control worrying",
                                   "options": ["Not at all", "Several days", "More than half the days",
                                               "Nearly every day"],
                                   "source_page": 0
                                   }

                                  ]
                },
                    {
                        "file_id": "fd60a9a64b1b4078a68f4bc06f20253c",
                        "instrument_id": "7829ba96f48e4848abd97884911b6795",
                        "instrument_name": "GAD-7 Portuguese",
                        "file_name": "GAD-7 PT.pdf",
                        "file_type": "pdf",
                        "file_section": "GAD-7 Portuguese",
                        "language": "en",
                        "questions": [{"question_no": "1",
                                       "question_intro": "Durante as últimas 2 semanas, com que freqüência você foi incomodado/a pelos problemas abaixo?",
                                       "question_text": "Sentir-se nervoso/a, ansioso/a ou muito tenso/a",
                                       "options": ["Nenhuma vez", "Vários dias", "Mais da metade dos dias",
                                                   "Quase todos os dias"],
                                       "source_page": 0
                                       },
                                      {"question_no": "2",
                                       "question_intro": "Durante as últimas 2 semanas, com que freqüência você foi incomodado/a pelos problemas abaixo?",
                                       "question_text": " Não ser capaz de impedir ou de controlar as preocupações",
                                       "options": ["Nenhuma vez", "Vários dias", "Mais da metade dos dias",
                                                   "Quase todos os dias"],
                                       "source_page": 0
                                       }

                                      ]
                    }

                ],
                "topics": ["anxiety, depression, sleep"],
                "query": "anxiety",
                "parameters": {"framework": DEFAULT_FRAMEWORK,
                               "model": DEFAULT_MODEL}
            }
        })


class SearchInstrumentsBody(BaseModel):
    parameters: MatchParameters = Field(DEFAULT_MATCH_PARAMETERS, description="Parameters on how to search")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "parameters": {"framework": DEFAULT_FRAMEWORK,
                               "model": DEFAULT_MODEL}
            }
        })

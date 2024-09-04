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

from typing import List

from harmony.schemas.catalogue_instrument import CatalogueInstrument
from harmony.schemas.requests.text import Instrument
from harmony.schemas.requests.text import Question
from pydantic import BaseModel, Field, RootModel


class MatchResponse(BaseModel):
    instruments: List[Instrument] = Field(description="A list of instruments")
    questions: List[Question] = Field(
        description="The questions which were matched, in an order matching the order of the matrix"
    )
    matches: List[List] = Field(description="Matrix of cosine similarity matches")
    query_similarity: List = Field(
        None, description="Similarity metric between query string and items"
    )
    closest_catalogue_instrument_matches: List[CatalogueInstrument] = Field(
        default=[],
        description="The closest catalogue instrument matches in the catalogue for all the instruments, "
                    "the first index contains the best match etc."
    )


class SearchInstrumentsResponse(BaseModel):
    instruments: List[Instrument] = Field(description="A list of instruments")


class InstrumentList(RootModel):
    root: List[Instrument]


class CacheResponse(BaseModel):
    instruments: List[Instrument] = Field(description="A list of instruments")
    vectors: List[dict] = Field(description="A list of vectors")

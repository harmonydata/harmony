from typing import List

from harmony.schemas.requests.text import Instrument
from harmony.schemas.requests.text import Question
from pydantic import BaseModel, Field


class MatchResponse(BaseModel):
    questions: List[Question] = Field(
        description="The questions which were matched, in an order matching the order of the matrix"
    )
    matches: List[List] = Field(description="Matrix of cosine similarity matches")
    query_similarity: List = Field(
        None, description="Similarity metric between query string and items"
    )


class InstrumentList(BaseModel):
    __root__: List[Instrument]


class CacheResponse(BaseModel):
    instruments: List[Instrument] = Field(description="A list of instruments")
    vectors: List[dict] = Field(description="A list of vectors")

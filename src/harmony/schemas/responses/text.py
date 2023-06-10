from typing import List

from pydantic import BaseModel, Field

from harmony.schemas.requests.text import Question, Instrument


class MatchResponse(BaseModel):
    questions: List[Question] = Field(
        description='The questions which were matched, in an order matching the order of the matrix')
    matches: List[List] = Field(description='Matrix of cosine similarity matches')
    query_similarity: List = Field(None, description='Similarity metric between query string and items')
    
class InstrumentList(BaseModel):
    __root__: List[Instrument]

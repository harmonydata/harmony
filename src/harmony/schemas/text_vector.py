from typing import List

from pydantic import BaseModel, Field


class TextVector(BaseModel):
    text: str = Field()
    vector: List[float] = Field()
    is_negated: bool = Field()
    is_query: bool = Field()

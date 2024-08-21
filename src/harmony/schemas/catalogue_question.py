from pydantic import BaseModel, Field

from harmony.schemas.catalogue_instrument import CatalogueInstrument


class CatalogueQuestion(BaseModel):
    question: str = Field(description="The catalogue question")
    seen_in_instruments: list[CatalogueInstrument] = Field(
        description="The instruments from the catalogue were the question was seen in"
    )

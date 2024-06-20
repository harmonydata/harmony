from pydantic import BaseModel, Field


class CatalogueInstrument(BaseModel):
    instrument_name: str = Field(description="Instrument name")
    instrument_url: str = Field(description="Instrument URL")
    source: str = Field(description="Source")
    sweep: str = Field(description="Sweep")
    metadata: dict = Field(default=None, description="Metadata")

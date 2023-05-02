from typing import List

from pydantic import BaseModel, Field

class RawFile(BaseModel):
    file_id: str = Field(None, description="Unique identifier for the file (UUID-4)")
    file_name: str = Field("Untitled file", description="The name of the input file")
    file_type: str = Field(description="The file type (pdf, xlsx, txt)")
    content: str = Field(description="The raw file contents")

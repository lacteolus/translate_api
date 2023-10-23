"""
Basic models (schemas) used in API requests and responses
"""
from pydantic import BaseModel, Field


class WordResponse(BaseModel):
    word: str = Field(description="Word itself")
    definitions: list[str] = Field(default=[], description="List of word possible definitions")
    translations: dict = Field(default={}, description="Word possible translations")
    synonyms: list[str] = Field(default=[], description="List of word possible synonyms")
    examples: list[str] = Field(default=[], description="List of word possible examples")


class WordsResponse(BaseModel):
    words: list[WordResponse] = Field(default=[], description="List of words")
    page_size: int = Field(default=10, description="Number of items per page")
    page_num: int = Field(default=0, description="Number of the current page")
    offset: int = Field(default=0, description="Offset from the first item")


class About(BaseModel):
    title: str = Field(description="API title")
    summary: str = Field(description="API summary information")
    description: str = Field(description="API description")
    version: str = Field(description="API version")
    contact: dict = Field(default={}, description="Contact information")
    license_info: dict = Field(default={}, description="License information")
    debug: dict = Field(default={}, description="Debugging information")

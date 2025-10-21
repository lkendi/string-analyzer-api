"""String schema module"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class StringProperties(BaseModel):
    """
    Properties of a string
    """
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: dict

class StringFilters(BaseModel):
    """
    Filters for string requests
    """
    is_palindrome: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    word_count: Optional[int] = None
    contains_character: Optional[str] = None


class StringRequest(BaseModel):
    """
    Format of a string request
    """
    value: str


class StringResponse(BaseModel):
    """
    Format of a string response
    """
    id: str
    value: str
    properties: StringProperties
    created_at: datetime

class StringListResponse(BaseModel):
    """
    Format of a list of string responses
    """
    data: List[StringResponse]
    count: int
    filters_applied: StringFilters

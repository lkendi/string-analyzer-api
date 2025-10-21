"""String schema module"""
from pydantic import BaseModel
from datetime import datetime

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

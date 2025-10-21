"""API routes module"""
from hashlib import sha256
from datetime import datetime
from fastapi import FastAPI, HTTPException, status, Depends
from app.schemas.string import StringRequest, \
                                StringResponse, \
                                StringProperties, \
                                StringFilters, \
                                StringListResponse
from app.storage import strings_db


app = FastAPI()


@app.get("/")
def root():
    """
    Root endpoint

    Returns
    -------
    A message indicating that the API is running
    """
    return {"message": "Hello! String API is running."}


@app.get("/strings", response_model=StringListResponse)
def get_all_strings(filters: StringFilters = Depends()):

    """
    Get all strings with optional filters

    Returns
    -------
    A list of all strings that exist (in-memory)

    Raises
    ------
    HTTPException - if no strings exist or if the query parameters are invalid
    """

    try:
        if filters.contains_character and len(
                filters.contains_character) > 1:
            raise ValueError("contains_character must be a single character.")
        if filters.min_length is not None and filters.min_length < 0:
            raise ValueError("min_length must be a positive integer.")
        if filters.max_length is not None and filters.max_length < 0:
            raise ValueError("max_length must be a positive integer.")
        if filters.word_count is not None and filters.word_count < 0:
            raise ValueError("word_count must be a positive integer.")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid query parameter values or types: {str(e)}"
        ) from e

    if not strings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No strings found."
        )

    results = list(strings_db.values())

    if filters.is_palindrome is not None:
        results = list(filter(
            lambda x: x.properties.is_palindrome ==
            filters.is_palindrome, results))

    if filters.min_length is not None:
        results = list(filter(
            lambda x: x.properties.length >= filters.min_length, results))

    if filters.max_length is not None:
        results = list(filter(
            lambda x: x.properties.length <= filters.max_length, results))

    if filters.word_count is not None:
        results = list(filter(
            lambda x: x.properties.word_count == filters.word_count, results))

    if filters.contains_character:
        results = list(filter(
            lambda x: filters.contains_character in x.value, results))

    return {
        "data": results,
        "count": len(results),
        "filters_applied": {
            "is_palindrome": filters.is_palindrome,
            "min_length": filters.min_length,
            "max_length": filters.max_length,
            "word_count": filters.word_count,
            "contains_character": filters.contains_character
        }
    }


@app.get("/strings/{string_value}", response_model=StringResponse)
def get_string(string_value: str):

    """
    Get a specific string

    Parameters
    ----------
    string_value: str - the string to get

    Returns
    -------
    StringResponse - the properties of the string

    Raises
    ------
    HTTPException - if the string does not exist
    """
    if string_value not in strings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String not found."
        )
    return strings_db[string_value]


@app.post("/strings", response_model=StringResponse,
          status_code=status.HTTP_201_CREATED)
def analyze_string(request: StringRequest):
    """
    Analyze a string and return its properties

    Parameters
    ----------
    request: StringRequest - the string to analyze

    Returns
    -------
    StringResponse - the properties of the string

    Raises
    ------
    HTTPException - if the string is invalid or already exists
    """

    value = request.value

    if value is None or value.strip() == "" or not isinstance(value, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="String value is required."
        )

    if value in strings_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="String already exists. Please enter a different string."
        )

    properties = StringProperties(
        length=len(value),
        is_palindrome=value.lower() == value.lower()[::-1],
        unique_characters=len(set(value)),
        word_count=len(value.split()),
        sha256_hash=sha256(value.encode()).hexdigest(),
        character_frequency_map={char: value.count(char)
                                 for char in set(value)}
    )

    response = StringResponse(
        id=properties.sha256_hash,
        value=value,
        properties=properties,
        created_at=datetime.now()
    )

    strings_db[value] = response
    return response

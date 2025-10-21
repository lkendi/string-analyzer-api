"""API routes module"""
from hashlib import sha256
from datetime import datetime
from fastapi import FastAPI, HTTPException, status, Depends
from app.schemas.string import StringRequest, \
                                StringResponse, \
                                StringProperties, \
                                StringFilters, \
                                StringListResponse, \
                                NaturalLanguageFilterResponse
from app.storage import strings_db
from app.utils.filter_strings import filter_strings
from app.utils.natural_language_parser import parse_natural_language_query


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

    filters_dict = {
        "is_palindrome": filters.is_palindrome,
        "min_length": filters.min_length,
        "max_length": filters.max_length,
        "word_count": filters.word_count,
        "contains_character": filters.contains_character
    }

    if not strings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No strings found."
        )

    try:
        result = filter_strings(filters_dict)
    except HTTPException as e:
        raise e

    return result


@app.get("/strings/filter-by-natural-language",
         response_model=NaturalLanguageFilterResponse)
def filter_by_natural_language(query: str):
    """
    Filter strings by natural language query

    Parameters
    ----------
    query: str - the natural language query to filter by

    Returns
    -------
    NaturalLanguageFilterResponse - the filtered strings and their properties

    Raises
    ------
    HTTPException - if the query is invalid or no strings exist
    """

    if not query or not isinstance(query, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query is required and must be a string."
        )

    if not strings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No strings found."
        )
    try:
        filters = parse_natural_language_query(query)
        print("filters", filters)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid query parameter values or types: {str(e)}"
        ) from e

    return {
        **filter_strings(filters),
        "interpreted_query": {
            "original": query,
            "parsed_filters": filters
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


@app.delete("/strings/{string_value}", status_code=status.HTTP_204_NO_CONTENT)
def delete_string(string_value: str):
    """
    Delete a string

    Parameters
    ----------
    string_value: str - the string to delete

    Returns
    -------
    None

    Raises
    ------
    HTTPException - if the string does not exist
    """
    if string_value not in strings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String not found."
        )
    del strings_db[string_value]

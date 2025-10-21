"""API routes module"""
from hashlib import sha256
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from app.schemas.string import StringRequest, StringResponse, StringProperties
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


@app.get("/strings", response_model=list[StringResponse])
def get_strings():

    """
    Get all strings

    Returns
    -------
    A list of all strings that exist (in-memory)

    Raises
    ------
    HTTPException - if no strings exist
    """
    if not strings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No strings found."
        )
    return list(strings_db.values())


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

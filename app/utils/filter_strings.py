"""
Utility functions for filtering strings.
"""

from fastapi import HTTPException, status
from app.storage import strings_db


def filter_strings(filters: dict):
    """
    Apply filter criteria to the in-memory strings database.

    Parameters
    ----------
    filters : dict
        Dictionary of filters (e.g., {"is_palindrome": True, "min_length": 5})

    Returns
    -------
    dict
        A response dictionary containing the filtered data, count, and filters applied.

    Raises
    ------
    HTTPException
        If no strings match or the database is empty.
    """
    if not strings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No strings found."
        )

    results = list(strings_db.values())

    if filters.get("is_palindrome") is not None:
        results = [x for x in results if x.properties.is_palindrome == filters["is_palindrome"]]

    if filters.get("min_length") is not None:
        results = [x for x in results if x.properties.length >= filters["min_length"]]

    if filters.get("max_length") is not None:
        results = [x for x in results if x.properties.length <= filters["max_length"]]

    if filters.get("word_count") is not None:
        results = [x for x in results if x.properties.word_count == filters["word_count"]]

    if filters.get("contains_character"):
        results = [x for x in results if filters["contains_character"] in x.value]

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching strings found"
        )

    return {
        "data": results,
        "count": len(results),
        "filters_applied": filters
    }

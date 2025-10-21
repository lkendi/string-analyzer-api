"""
Utility function for parsing natural language
"""
import re

def parse_natural_language_query(query: str):
    """
    Parse a natural language query into structured filters.

    Supported examples:
    - "all single word palindromic strings"
    - "strings longer than 10 characters"
    - "strings containing the letter z"
    - "palindromic strings"
    """
    query = query.lower().strip()
    filters = {}

    try:
        if "single word" in query:
            filters["word_count"] = 1

        match = re.search(r"longer than (\d+)", query)
        if match:
            filters["min_length"] = int(match.group(1))

        match = re.search(r"shorter than (\d+)", query)
        if match:
            filters["max_length"] = int(match.group(1))

        match = re.search(r"containing (?:the letter )?([a-z])", query)
        if match:
            filters["contains_character"] = match.group(1)

        if "palindromic" in query or "palindrome" in query:
            filters["is_palindrome"] = True

    except Exception:
        raise ValueError(f"Unsupported or invalid query format: '{query}'")

    if not filters:
        raise ValueError(f"Unsupported query: '{query}'")

    return filters

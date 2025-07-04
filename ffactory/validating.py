import os
from datetime import datetime, date

def validate_date(date_str: str) -> date:
    """
    Validates that a string is a date in 'YYYY-MM-DD' format and converts it to a date object.

    Args:
        date_str (str): Date string to validate.

    Returns:
        date: Corresponding date object.

    Raises:
        TypeError: If `date_str` is not a string.
        ValueError: If the string is not in the 'YYYY-MM-DD' format or is an invalid date.
    """
    if not isinstance(date_str, str):
        raise TypeError('Date must be in string format (YYYY-MM-DD)')
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError('Invalid date or format (expected YYYY-MM-DD)')

def validate_path(path: str) -> None:
    """
    Validates that a given path is a non-empty string, that its directory exists, and that the filename
    contains no invalid characters.

    Args:
        path (str): File path to validate.

    Raises:
        TypeError: If `path` is not a string.
        ValueError: If `path` is empty or contains invalid characters.
        FileNotFoundError: If the directory part of the path does not exist.
    """
    if not isinstance(path, str):
        raise TypeError("path must be a string")

    if path.strip() == "":
        raise ValueError("path cannot be an empty string")

    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist")

    filename = os.path.basename(path)
    invalid_chars = r'<>:"/\\|?*'
    if any(char in filename for char in invalid_chars):
        raise ValueError(f"Filename '{filename}' contains invalid characters")

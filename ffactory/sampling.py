from .presenter import TablePresenter

class Sampling:
    """
    Represents a sampled subset of tabular data.
    Provides utilities to export or display the sampled rows in a formatted table or save to a file.
    """
    def __init__(self, columns: list[dict[str, str]], rows: list[dict[str, str | int | float]]):
        """
        Initializes a new Sampling object with column names and sampled data.
        """
        self.__cols = columns
        self.__rows = rows

    @property
    def rows(self) -> list[dict]:
        """
        Returns the current rows of the table.

        Returns:
            list[dict]: The list of row dictionaries.
        """
        return self.__rows

    @property
    def columns(self) -> list[str]:
        """
        Returns the current column names.

        Returns:
            list[str]: A list of column names.
        """
        return self.__cols


    def save(self, file_extension: str, path: str) -> None:
        """
        Saves the current data to a file using the specified format.

        Args:
            file_extension (str): File format ('csv', 'json', 'html').
            path (str): Full path (without extension) to save the file.

        Raises:
            TypeError: If `file_extension` is not a string.
            ValueError: If `file_extension` is not a supported format.
            ValueError: If the path is empty or has invalid characters.
            FileNotFoundError: If the directory in the path does not exist.
        """
        TablePresenter.save(self.__cols, self.__rows, file_extension, path)

    def as_table(self, return_string: bool = True) -> str | None:
        """
        Returns or prints a formatted table string from the current object's data.

        Args:
            return_string (bool, optional): 
                If True, returns the table as a string.  
                If False, prints the table to stdout and returns None. Defaults to True.

        Returns:
            str: The formatted table as a string.

        Raises:
            TypeError: If input data is invalid, as enforced by TablePresenter.as_table.
            ValueError: If column names or values are malformed.
        """
        return TablePresenter.as_table(self.__cols, self.__rows, return_string)

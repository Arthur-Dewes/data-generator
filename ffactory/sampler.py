import random
import numpy as np
from collections import Counter, defaultdict
from .sampling import Sampling
from .presenter import TablePresenter

class TableSampler:
    """
    Provides various sampling methods (random, stratified, systematic, and cluster)
    for tabular data, as well as tools to rename columns, view the table, or export it.
    """
    def __init__(self, columns: list[str], rows: list[dict[str, str | int | float]]):
        """
        Initializes a TableSampler with the given columns and rows.
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
    
    @columns.setter
    def columns(self, names: list[str] | dict[str, str]) -> None:
        """
        Renames the columns of the table.

        Accepts:
            - A list of strings: full renaming in order.
            - A dict[str, str]: partial renaming (old_name → new_name).

        Raises:
            TypeError: If input is not a list or dict of strings.
            ValueError: If renaming to an existing column name.
                        If old column names don't exist.
                        If list length doesn't match number of columns.
        """
        if isinstance(names, list):
            if not all(isinstance(name, str) for name in names):
                raise TypeError("All column names must be strings.")
            if len(names) != len(self.__cols):
                raise ValueError("New column list must have the same number of elements.")
            if any(name in self.__cols and name != old for name, old in zip(names, self.__cols)):
                raise ValueError("Cannot rename a column to an existing column name.")
            old_keys = self.__cols
            self.__cols = names
            for row in self.__rows:
                new_row = {}
                for old, new in zip(old_keys, names):
                    new_row[new] = row.pop(old)
                row.update(new_row)

        elif isinstance(names, dict):
            if not all(isinstance(k, str) and isinstance(v, str) for k, v in names.items()):
                raise TypeError("Both keys and values in the dictionary must be strings.")
            for old in names:
                if old not in self.__cols:
                    raise ValueError(f"Column '{old}' does not exist.")
            for old, new in names.items():
                if new in self.__cols and new != old:
                    raise ValueError(f"Cannot rename '{old}' to '{new}': name already exists.")

            self.__cols = [names.get(col, col) for col in self.__cols]
            for row in self.__rows:
                for old, new in names.items():
                    row[new] = row.pop(old)

        else:
            raise TypeError("Input must be a list or a dict of strings.")

    def random_sampling(self, n_samples: int, repo: bool = True) -> Sampling:
        """
        Performs simple random sampling.
        Selects rows at random from the dataset.

        Args:
            n_samples (int): Number of rows to sample.
            repo (bool, optional): Whether to sample with replacement. Defaults to True.

        Returns:
            Sampling: A new Sampling object with the sampled rows.

        Raises:
            TypeError: If `n_samples` is not an integer or `repo` is not a boolean.
            ValueError: If `n_samples` is not positive.
            ValueError: If `n_samples` exceeds dataset size when `repo=False`.
        """
        if not isinstance(n_samples, int) or n_samples <= 0:
            raise ValueError("n_samples must be a positive integer")
        if not isinstance(repo, bool):
            raise TypeError("repo must be a boolean value")

        if n_samples > len(self.__rows) and not repo:
            raise ValueError("Sample size exceeds population size without replacement")

        indices = (
            random.choices(range(len(self.__rows)), k=n_samples)
            if repo else
            random.sample(range(len(self.__rows)), k=n_samples)
        )

        return Sampling(columns=self.__cols, rows=[self.__rows[i] for i in indices])

    def stratified_sampling(self, n_samples: int, column: str) -> Sampling:
        """
        Performs stratified sampling based on a specified column.
        Samples proportionally from subgroups defined by a column.

        Args:
            n_samples (int): Total number of samples to draw.
            column (str): Column to use for stratification.

        Returns:
            Sampling: A new Sampling object with the stratified sample.

        Raises:
            TypeError: If `n_samples` is not an integer.
            ValueError: If `n_samples` is not positive.
            ValueError: If `n_samples` exceeds dataset size.
            ValueError: If the specified column does not exist.
        """
        if not isinstance(n_samples, int) or n_samples <= 0:
            raise ValueError("n_samples must be a positive integer")
        if column not in self.__cols:
            raise ValueError(f"Column '{column}' does not exist")
        if n_samples > len(self.__rows):
            raise ValueError("Sample size exceeds number of available rows")

        value_counts = Counter(row[column] for row in self.__rows)
        unique_values = list(value_counts.keys())
        counts = np.array(list(value_counts.values()), dtype=float)

        if n_samples < len(unique_values):
            print("Sample size is too small to follow the proportions of the column")

        proportions = counts / counts.sum()
        adjusted_counts = np.round(proportions * n_samples).astype(int)

        diff = n_samples - adjusted_counts.sum()
        if diff != 0:
            idx = np.argmax(adjusted_counts)
            adjusted_counts[idx] += diff

        grouped = defaultdict(list)
        for row in self.__rows:
            grouped[row[column]].append(row)

        result = []
        for val, count in zip(unique_values, adjusted_counts):
            group = grouped[val]
            if count > len(group):
                count = len(group)
            result.extend(random.sample(group, k=count))

        return Sampling(columns=self.__cols, rows=result)
    
    def systematic_sampling(self, interval: int, n_samples: int) -> Sampling:
        """
        Performs systematic sampling with a fixed interval.
        Selects rows at regular intervals through the dataset.

        Args:
            interval (int): Interval between selected rows.
            n_samples (int): Number of samples to draw.

        Returns:
            Sampling: A new Sampling object with systematically selected rows.

        Raises:
            TypeError: If `interval` or `n_samples` is not an integer.
            ValueError: If `interval` or `n_samples` is not positive.
            ValueError: If `n_samples` exceeds dataset size.
            ValueError: If `interval` is greater than or equal to dataset size.
        """
        if not isinstance(interval, int) or interval <= 0:
            raise ValueError("interval must be a positive integer")
        if not isinstance(n_samples, int) or n_samples <= 0:
            raise ValueError("n_samples must be a positive integer")
        if n_samples > len(self.__rows):
            raise ValueError("Sample size exceeds number of available rows")
        if interval >= len(self.__rows):
            raise ValueError("interval is too large for the dataset")

        table = []
        idx = 0
        for _ in range(n_samples):
            while self.__rows[idx % len(self.__rows)] in table:
                idx += 1
            table.append(self.__rows[idx % len(self.__rows)])
            idx += interval

        return Sampling(columns=self.__cols, rows=table)
        
    def cluster_sampling(self, group_by: str, n_samples: int) -> Sampling:
        """
        Performs cluster sampling by grouping rows using a specific column.
        Randomly selects groups (clusters) and includes all their rows.

        Args:
            group_by (str): Column to define clusters.
            n_samples (int): Number of clusters to sample.

        Returns:
            Sampling: A new Sampling object with rows from selected clusters.

        Raises:
            TypeError: If `n_samples` is not an integer.
            ValueError: If `n_samples` is not positive.
            ValueError: If the specified column does not exist.
            ValueError: If `n_samples` exceeds the number of available clusters.
        """
        if not isinstance(n_samples, int) or n_samples <= 0:
            raise ValueError("n_sample must be a positive integer")
        if group_by not in self.__cols:
            raise ValueError(f"Column '{group_by}' does not exist")

        clusters = defaultdict(list)
        for row in self.__rows:
            key = row[group_by]
            clusters[key].append(row)

        all_keys = list(clusters.keys())

        if n_samples > len(all_keys):
            raise ValueError(f"Number of clusters requested exceeds number of available groups ({len(all_keys)})")

        selected_keys = random.sample(all_keys, k=n_samples)

        result = []
        for key in selected_keys:
            result.extend(clusters[key])

        return Sampling(columns=self.__cols, rows=result)
    
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

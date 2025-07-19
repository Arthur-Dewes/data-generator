import re
import math
import random
from typing import Any
from faker import Faker
from datetime import date
from .sampler import TableSampler
from .presenter import TablePresenter
from .validating import validate_date
from .emailMaker import generate_email_from_name

class FakeDataGenerator:
    """
    Generates customizable synthetic data based on configurable columns and locale. 
    Useful for testing, prototyping, and simulations.
    """
    def __init__(self, num_rows: int, locale: str, seed: int = 20):
        """
        Initializes the generator with the desired number of rows, locale, and random seed.

        Raises:
            TypeError: If any argument is of an invalid type.
            ValueError: If the locale is unsupported or the number of rows is non-positive.
        """
        self._validateInputParameters(num_rows, locale, seed)

        Faker.seed(seed)
        self.__faker = Faker(locale)
        self.__rows: list[dict] = []
        self.__cols: list[dict] = []
        self.__num_rows: int = num_rows
        self.__faker_instances: dict[str, Any] = {}
        self.__base_seed: int = seed
    
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
        return [col['name'] for col in self.__cols]
    
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
        current_columns = [col["name"] for col in self.__cols]

        if isinstance(names, list):
            if not all(isinstance(name, str) for name in names):
                raise TypeError("All column names must be strings.")
            if len(names) != len(self.__cols):
                raise ValueError("New column list must have the same number of elements.")
            if any(new in current_columns and new != old for new, old in zip(names, current_columns)):
                raise ValueError("Cannot rename a column to an existing column name.")

            for col, new_name in zip(self.__cols, names):
                col["name"] = new_name

            for row in self.__rows:
                new_row = {}
                for old_name, new_name in zip(current_columns, names):
                    new_row[new_name] = row.pop(old_name)
                row.update(new_row)

        elif isinstance(names, dict):
            if not all(isinstance(k, str) and isinstance(v, str) for k, v in names.items()):
                raise TypeError("Both keys and values in the dictionary must be strings.")

            for old in names:
                if old not in current_columns:
                    raise ValueError(f"Column '{old}' does not exist.")

            for old, new in names.items():
                if new in current_columns and new != old:
                    raise ValueError(f"Cannot rename '{old}' to '{new}': name already exists.")

            for col in self.__cols:
                if col["name"] in names:
                    col["name"] = names[col["name"]]

            for row in self.__rows:
                for old, new in names.items():
                    row[new] = row.pop(old)

        else:
            raise TypeError("Input must be a list or a dict of strings.")

    __br_cols = ('index', 'name', 'email', 'age', 'cpf', 'cnpj', 'phoneNumber'
                'job', 'date', 'time',  'int', 'float', 'boolean')
    __us_cols = ('index', 'name', 'email', 'age', 'ssn', 'ein', 'phoneNumber'
                'job', 'date', 'time',  'int', 'float', 'boolean')
    __repetitive_cols = ('phoneNumber', 'date', 'time', 'int', 'float', 'boolean')
    
    @classmethod
    def _validateInputParameters(cls, num_rows, locale, seed) -> None:

        if not isinstance(locale, str):
            raise TypeError('Invalid locale type: is not a string')
        elif locale not in ('pt_BR', 'en_US'): 
            raise ValueError(f'Invalid locale: {locale}. Choose one of pt_BR or en_US')

        if not isinstance(num_rows, int) or num_rows <= 0:
            raise TypeError(f'Non-natural value: {num_rows}')

        if not isinstance(seed, (int, float)):
            raise TypeError(f'Seed value received is not numeric: {seed}')

    def add_column(self, name: str, **kwargs) -> None:
        """
        Adds a new column to the data schema.

        Accepted column names:
            For locale 'pt_BR':
                'index', 'name', 'email', 'age', 'cpf', 'cnpj', 'phoneNumber'
                'job', 'date', 'time',  'int', 'float', 'boolean'
            For locale 'en_US':
                'index', 'name', 'email', 'age', 'ssn', 'ein', 'phoneNumber'
                'job', 'date', 'time',  'int', 'float', 'boolean'

        Args:
            name (str): Name of the column to add.
            **kwargs: Optional parameters depending on the column type:
                - int: `min_int` (int), `max_int` (int)
                - float: `min_float` (int|float), `max_float` (int|float)
                - date: `min_date` (str, format 'YYYY-MM-DD'), `max_date` (str, format 'YYYY-MM-DD')
                - age: `min_age` (int), `max_age` (int)
                - boolean: `chance_of_true` (int|float, from 0 to 100)

        Raises:
            ValueError: If any argument is invalid or inconsistent with the column schema.
            TypeError: If any argument is of an invalid type.
        """

        repetitive_cols = FakeDataGenerator.__repetitive_cols

        available_cols = (
            self.__br_cols if self.__faker.locales[0] == 'pt_BR'
            else self.__us_cols
        )

        if name not in available_cols:
            raise ValueError(f'Column {name} is not available for locale {self.__faker.locales[0]}')

        if name == 'int':
            kwargs['min_int'] = kwargs.get('min_int', None)
            kwargs['max_int'] = kwargs.get('max_int', None)
        
            if kwargs['min_int'] is not None and not isinstance(kwargs['min_int'], int):
                raise TypeError('min_int must be int')
            if kwargs['max_int'] is not None and not isinstance(kwargs['max_int'], int):
                raise TypeError('max_int must be int')

        elif name == 'float':
            kwargs['min_float'] = kwargs.get('min_float', None)
            kwargs['max_float'] = kwargs.get('max_float', None)

            if kwargs['min_float'] is not None and not isinstance(kwargs['min_float'], (int, float)):
                raise TypeError('min_float must be int or float')
            if kwargs['max_float'] is not None and not isinstance(kwargs['max_float'], (int, float)):
                raise TypeError('max_float must be int or float')

        elif name == 'date':
            kwargs['min_date'] = kwargs.get('min_date', None)
            kwargs['max_date'] = kwargs.get('max_date', None)

            if kwargs['min_date'] is not None and not isinstance(kwargs['min_date'], str):
                raise TypeError('min_date must be str')
            if kwargs['max_date'] is not None and not isinstance(kwargs['max_date'], str):
                raise TypeError('max_date must be str')

        elif name == 'age':
            kwargs['min_age'] = kwargs.get('min_age', None)
            kwargs['max_age'] = kwargs.get('max_age', None)

            if kwargs['min_age'] is not None and not isinstance(kwargs['min_age'], int):
                raise TypeError('min_age must be int')
            if kwargs['max_age'] is not None and not isinstance(kwargs['max_age'], int):
                raise TypeError('max_age must be int')

        elif name == 'boolean':
            if 'chance_of_true' not in kwargs:
                kwargs['chance_of_true'] = 50
            if not isinstance(kwargs['chance_of_true'], (int, float)):
                raise TypeError('chance_of_true must be int or float')
            if not (0 <= kwargs['chance_of_true'] <= 100):
                raise ValueError('chance_of_true must be between 0 and 100')

        existing_names = [col['name'] for col in self.__cols]
        original_name = name

        if name in existing_names:
            if name in repetitive_cols:
                i = 2
                while name in existing_names:
                    name = f"{original_name}{i}"
                    i += 1
            else:
                raise ValueError(f"Column {original_name} already added and does not support repetition")

        faker_for_column = Faker(self.__faker.locales[0])
        derived_seed = self.__base_seed + len(self.__faker_instances)
        faker_for_column.seed_instance(derived_seed)
        self.__faker_instances[name] = faker_for_column

        self.__cols.append({'name': name, 'params': kwargs})
    
    def add_columns(self, columns: list[str | tuple[str, dict]]) -> None:
        """
        Adds multiple columns at once.

        Accepted column names:
            For locale 'pt_BR':
                'index', 'name', 'email', 'age', 'cpf', 'cnpj', 'phoneNumber'
                'job', 'date', 'time',  'int', 'float', 'boolean'
            For locale 'en_US':
                'index', 'name', 'email', 'age', 'ssn', 'ein', 'phoneNumber'
                'job', 'date', 'time',  'int', 'float', 'boolean'

        Args:
            columns (list[str | tuple[str, dict]]): A list where each element is either:
                - A string (e.g., 'name'), or
                - A tuple (column_name, parameters_dict)

        Raises:
            TypeError: If any item is not a string or a valid (str, dict) tuple.
            ValueError: If the format of any item is incorrect.
        """
        if not isinstance(columns, list):
            raise TypeError("Expected a list of column names or (name, kwargs) tuples.")

        for item in columns:
            if isinstance(item, str):
                self.add_column(item)
            elif isinstance(item, tuple) and len(item) == 2:
                name, kwargs = item
                if not isinstance(name, str) or not isinstance(kwargs, dict):
                    raise TypeError("Expected a tuple in the format: (str, dict)")
                self.add_column(name, **kwargs)
            else:
                raise ValueError("Each column must be a string or a (name, kwargs) tuple.")
            
    def remove_column(self, name: str) -> None:
        """
        Removes a column from the table by name.

        Args:
            name (str): The name of the column to remove.

        Raises:
            TypeError: If name is not a string.
            ValueError: If the column does not exist.
        """
        if not isinstance(name, str):
            raise TypeError("Column name must be a string.")

        col_index = next((i for i, col in enumerate(self.__cols) if col['name'] == name), None)

        if col_index is None:
            raise ValueError(f"Column '{name}' does not exist.")

        del self.__cols[col_index]

        for row in self.__rows:
            row.pop(name, None)
        
    def concatenate(self, table: "FakeDataGenerator") -> None:
        """
        Concatenates rows from another FakeDataGenerator instance, ensuring that 
        both the original column schemas and the current column orders match.

        Args:
            table (FakeDataGenerator): The other instance to concatenate data from.

        Raises:
            TypeError: If `table` is not a FakeDataGenerator instance.
            ValueError: If the original schemas or current column orders/names do not match.
        """
        current_columns = [col['name'] for col in self.__cols]

        if not isinstance(table, FakeDataGenerator):
            raise TypeError("Expected a FakeDataGenerator instance.")
        
        if self.columns != table.columns:
            raise ValueError("Cannot concatenate: column names or order do not match.")

        if 'index' in current_columns:
            for row in table.rows:
                row['index'] += len(self.__rows)

        self.__rows.extend(table.rows)

    def __eq__(self, other) -> bool:
        """
        Checks equality with another FakeDataGenerator instance based on the set of
        initial column names, regardless of their order.

        Args:
            other (FakeDataGenerator): The other instance to compare.

        Returns:
            bool: True if both have the same initial column names (regardless of order); False otherwise.
        """
        if not isinstance(other, FakeDataGenerator):
            return False
        return set(self.columns) == set(other.columns)

    def _generate_date(self, min_date: str | None, max_date: str | None) -> date:
        """
        Generates a random date between `min_date` and `max_date`.

        Args:
            min_date (str|None): Minimum date as 'YYYY-MM-DD'.
            max_date (str|None): Maximum date as 'YYYY-MM-DD'.

        Returns:
            date: Randomly generated date within the specified range.
        """
        default = min_date is None or max_date is None or min_date == max_date
        if default:
            return self.__faker.date_between(start_date="-10y")

        min_dt = validate_date(min_date)
        max_dt = validate_date(max_date)

        if min_dt > max_dt:
            min_dt, max_dt = max_dt, min_dt

        return self.__faker.date_between_dates(date_start=min_dt, date_end=max_dt)

    def _generate_age(self, min_age: int | None, max_age: int | None) -> int:
        """
        Generates a random age between `min_age` and `max_age`.

        Args:
            min_age (int|None): Minimum age.
            max_age (int|None): Maximum age.

        Returns:
            int: Randomly generated age within the specified range.
        """
        default = min_age is None or max_age is None or min_age == max_age
        if default:
            return self.__faker.random_int(min=18, max=90)

        if min_age > max_age:
            min_age, max_age = max_age, min_age

        return self.__faker.random_int(min=min_age, max=max_age)
    
    def _generate_int(self, min_int: int | None, max_int: int | None) -> int:
        """
        Generates a random integer between `min_int` and `max_int`.

        Args:
            min_int (int|None): Minimum integer.
            max_int (int|None): Maximum integer.

        Returns:
            int: Randomly generated integer within the specified range.
        """
        default = min_int is None or max_int is None or min_int == max_int
        if default:
            possible_bases = [0, 10, 100, 1000, 10000, 100000, 1000000]
            base_value = self.__faker.random_element(elements=possible_bases)

            if base_value == 0:
                max_int_value = 9
            else:
                max_int_value = 10 ** (math.floor(math.log10(base_value)) + 1) - 1

            return self.__faker.random_int(min=base_value, max=max_int_value)

        if min_int > max_int:
            min_int, max_int = max_int, min_int

        return self.__faker.random_int(min=min_int, max=max_int)

    def _generate_float(self, min_float: int | float | None, max_float: int | float | None) -> float:
        """
        Generates a random float between `min_float` and `max_float`.

        Args:
            min_float (int|float|None): Minimum float.
            max_float (int|float|None): Maximum float.

        Returns:
            float: Randomly generated float within the specified range.
        """
        default = min_float is None or max_float is None or min_float == max_float
        if default:
            return round(random.uniform(0.0, 1.0), 2)

        if min_float > max_float:
            min_float, max_float = max_float, min_float

        return round(random.uniform(min_float, max_float), 2)
    
    def _add_rows(self) -> None:
        """
        Generates a single row of synthetic data based on configured columns
        and appends it to the internal rows list.
        """
        row = {}

        for col in self.__cols:
            name = col['name']
            params = col.get('params', {})
            faker = self.__faker_instances[name]

            match name:
                case 'index':
                    row[name] = len(self.__rows)

                case 'email':
                    row[name] = generate_email_from_name(row['name'], faker) if 'name' in row else faker.email()

                case _ if re.fullmatch(r'age\d*', name):
                    row[name] = self._generate_age(**params)

                case _ if re.fullmatch(r'date\d*', name):
                    row[name] = self._generate_date(**params)

                case _ if re.fullmatch(r'int\d*', name):
                    row[name] = self._generate_int(**params)

                case _ if re.fullmatch(r'float\d*', name):
                    row[name] = self._generate_float(**params)

                case _ if re.fullmatch(r'phoneNumber\d*', name):
                    row[name] = faker.cellphone_number() if faker.locales[0] == 'pt_BR' else faker.phone_number()

                case _ if re.fullmatch(r'boolean\d*', name):
                    chance = params.get('chance_of_true', 50)
                    row[name] = int(faker.boolean(chance_of_getting_true=chance))

                case _:
                        row[name] = getattr(faker, name)()
                     
        self.__rows.append(row)

    def generate_data(self, clear_before: bool = True) -> None:
        """
        Generates data based on the configured schema.

        Args:
            clear_before (bool, optional): Whether to clear previously generated data before generating new data. 
                                           Defaults to True.
        """
        if clear_before:
            self.__rows = []

        for label in ['name', 'index']:
            for col in self.__cols:
                if col['name'] == label:
                    self.__cols.remove(col)
                    self.__cols.insert(0, col)
                    break

        for _ in range(self.__num_rows):
            self._add_rows()
    
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
        current_columns = [col['name'] for col in self.__cols]
        TablePresenter.save(current_columns, self.__rows, file_extension, path)

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
        col_names = [col['name'] for col in self.__cols]
        return TablePresenter.as_table(col_names, self.__rows, return_string)

    def to_sampler(self) -> TableSampler:
        """
        Converts the generated data to a TableSampler instance for sampling operations.

        Returns:
            TableSampler: A sampler object initialized with the generated data.
        """
        col_names = [col['name'] for col in self.__cols]
        return TableSampler(columns=col_names, rows=self.__rows)

    def info(self) -> None:
        """
        Prints a summary of the table schema, data size, and available functionalities.
        """
        print("FakeDataGenerator Summary")
        print("-" * 40)

        print(f"Locale: {self.__faker.locales[0]}")
        print(f"Number of rows: {len(self.__rows)}")
        print(f"Number of columns: {len(self.__cols)}")

        print("\nCurrent columns:")
        if not self.__cols:
            print("  (No columns added yet)")
        else:
            for col in self.__cols:
                print(f"  - {col['name']}")

        print("\nColumns that can be repeated:")
        print("  ", ", ".join(self.__repetitive_cols))

        print("\nMain functions:")
        print("  add_column(name, **kwargs)        → Add a single column")
        print("  add_columns([...])                → Add multiple columns")
        print("  remove_column(name)               → Remove a column")
        print("  generate_data()                   → Generate synthetic data")
        print("  as_table()                        → Print or return a formatted table")
        print("  save(ext, path)                   → Save data to file")
        print("  to_sampler()                      → Convert to sampler object")
        print("  info()                            → Show this summary")

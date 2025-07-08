import re
import math
import random
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
        self.__rows = []
        self.__cols = []
        self.__original_schema = []
        self.__num_rows = num_rows
        self.__faker_instances = {}
        self.__base_seed = seed
    
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

    __br_cols = ('id', 'name', 'email', 'age', 'cpf', 'cnpj', 'price', 'phoneNumber',
                'job', 'date', 'time', 'boolean')
    __us_cols = ('id', 'name', 'email', 'age', 'ssn', 'ein', 'price', 'phoneNumber',
                'job', 'date', 'time', 'boolean')
    __repetitive_cols = ('boolean', 'price', 'date', 'age', 'phoneNumber')
    
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
                'id', 'name', 'email', 'age', 'cpf', 'cnpj', 'price', 
                'phoneNumber', 'job', 'date', 'time', 'boolean'
            For locale 'en_US':
                'id', 'name', 'email', 'age', 'ssn', 'ein', 'price', 
                'phoneNumber', 'job', 'date', 'time', 'boolean'

        Args:
            name (str): Name of the column to add.
            **kwargs: Optional parameters depending on the column type:
                - price: `min_price` (int|float), `max_price` (int|float)
                - date: `min_date` (str, format 'YYYY-MM-DD'), `max_date` (str, format 'YYYY-MM-DD')
                - age: `min_age` (int), `max_age` (int)
                - boolean: `true_chance` (int|float, from 0 to 100)

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

        if name == 'price':
            kwargs['min_price'] = kwargs.get('min_price', None)
            kwargs['max_price'] = kwargs.get('max_price', None)

            if kwargs['min_price'] is not None and not isinstance(kwargs['min_price'], (int, float)):
                raise TypeError('min_price must be int or float')
            if kwargs['max_price'] is not None and not isinstance(kwargs['max_price'], (int, float)):
                raise TypeError('max_price must be int or float')

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
            if 'true_chance' not in kwargs:
                kwargs['true_chance'] = 50
            if not isinstance(kwargs['true_chance'], (int, float)):
                raise TypeError('true_chance must be int or float')
            if not (0 <= kwargs['true_chance'] <= 100):
                raise ValueError('true_chance must be between 0 and 100')

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
        self.__original_schema.append(name)
    
    def add_columns(self, columns: list[str | tuple[str, dict]]) -> None:
        """
        Adds multiple columns at once.

        Accepted column names:
            For locale 'pt_BR':
                'id', 'name', 'email', 'age', 'cpf', 'cnpj', 'price', 
                'phoneNumber', 'job', 'date', 'time', 'boolean'
            For locale 'en_US':
                'id', 'name', 'email', 'age', 'ssn', 'ein', 'price', 
                'phoneNumber', 'job', 'date', 'time', 'boolean'

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
        if not isinstance(table, FakeDataGenerator):
            raise TypeError("Expected a FakeDataGenerator instance.")

        if self.__original_schema != table.__original_schema:
            raise ValueError("Cannot concatenate: original column schemas do not match.")

        if self.columns != table.columns:
            raise ValueError("Cannot concatenate: current column names or order do not match.")

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

        return set(self.__original_schema) == set(other.__original_schema)

    def _generate_date(self, min_date: str, max_date: str) -> date:
        """
        Generates a random date between `min_date` and `max_date`.

        Args:
            min_date (str): Minimum date as 'YYYY-MM-DD'.
            max_date (str): Maximum date as 'YYYY-MM-DD'.

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

    def _generate_age(self, min_age: int, max_age: int) -> int:
        """
        Generates a random age between `min_age` and `max_age`.

        Args:
            min_age (int): Minimum age.
            max_age (int): Maximum age.

        Returns:
            int: Randomly generated age within the specified range.
        """
        default = min_age is None or max_age is None or min_age == max_age
        if default:
            return self.__faker.random_int(min=18, max=90)

        if min_age > max_age:
            min_age, max_age = max_age, min_age

        return self.__faker.random_int(min=min_age, max=max_age)

    def _generate_price(self, min_price: int, max_price: int) -> float:
        """
        Generates a random price between `min_price` and `max_price`.

        Args:
            min_price (int): Minimum price.
            max_price (int): Maximum price.

        Returns:
            float: Randomly generated price within the specified range.
        """
        default = min_price is None or max_price is None or min_price == max_price
        if default:
            possible_bases = [0, 10, 100, 1000, 10000, 100000, 1000000]
            base_value = self.__faker.random_element(elements=possible_bases)

            max_price_value = 9 if base_value == 0 else 10 ** (math.floor(math.log10(base_value)) + 1) - 1
            return round(random.uniform(base_value, max_price_value), 2)

        if min_price > max_price:
            min_price, max_price = max_price, min_price

        return round(random.uniform(min_price, max_price), 2)
    
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
                case 'id':
                    row[name] = len(self.__rows)

                case 'email':
                    row[name] = generate_email_from_name(row['name'], faker) if 'name' in row else faker.email()

                case _ if re.fullmatch(r'age\d*', name):
                    row[name] = self._generate_age(**params)

                case _ if re.fullmatch(r'date\d*', name):
                    row[name] = self._generate_date(**params)

                case _ if re.fullmatch(r'price\d*', name):
                    row[name] = self._generate_price(**params)

                case _ if re.fullmatch(r'phoneNumber\d*', name):
                    row[name] = faker.cellphone_number() if faker.locales[0] == 'pt_BR' else faker.phone_number()

                case _ if re.fullmatch(r'boolean\d*', name):
                    chance = params.get('true_chance', 50)
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

        for label in ['name', 'id']:
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
        TablePresenter.save(self.__rows, self.__cols, file_extension, path)

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

        print("\nColumns:")
        if not self.__cols:
            print("  (No columns added yet)")
        else:
            for col in self.__cols:
                name = col['name']
                params = col.get('params', {})
                if params:
                    param_str = ", ".join(f"{k}={v}" for k, v in params.items())
                    print(f"  - {name} ({param_str})")
                else:
                    print(f"  - {name}")

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


import csv
import json
from jinja2 import Template
from datetime import date
import textwrap
from .validating import validate_path

ALLOWED_FORMATS = ('csv', 'json', 'html')

class TablePresenter:
    """
    Provides utilities to display and export tabular data in different formats.

    This class supports:
        - Pretty-printing tables in fixed-width text format.
        - Exporting data to CSV, JSON, and HTML formats.
        - Automatic validation of inputs to ensure data integrity before formatting or saving.

    Methods:
        as_table(columns, rows, return_string=True):
            Formats a table using fixed-width text based on column names and row data.

        save(rows, columns, file_extension, path):
            Saves tabular data to a file in CSV, JSON, or HTML format.
    """

    @staticmethod
    def as_table(columns: list[str], rows: list[dict[str, str | int | float]], return_string: bool = True) -> str | None:
        """
        Returns or prints a formatted text table from the given columns and rows.

        Args:
            columns (list[str]): List of column names in the desired order.
            rows (list[dict[str, str | int | float]]): List of data rows, each represented as a dictionary.
            return_string (bool, optional): 
                If True, returns the formatted table as a string.
                If False, prints the table to stdout. Defaults to True.

        Returns:
            str: The formatted table as a string.

        Raises:
            TypeError: If `columns` is not a list of strings.
            TypeError: If `rows` is not a list of dictionaries.
            TypeError: If any dictionary key in `rows` is not a string.
            TypeError: If any dictionary value in `rows` is not a str, int, float, or None.
            TypeError: If `return_string` is not a boolean.
        """
        if not isinstance(columns, list) or not all(isinstance(col, str) for col in columns):
            raise TypeError("columns must be a list of strings.")
        
        if not isinstance(rows, list):
            raise TypeError("rows must be a list of dictionaries.")
        for i, row in enumerate(rows):
            if not isinstance(row, dict):
                raise TypeError(f"Row at index {i} is not a dictionary.")
            for key, value in row.items():
                if not isinstance(key, str):
                    raise TypeError(f"Key '{key}' in row {i} is not a string.")
                if not (isinstance(value, (str, int, float, date)) or value is None):
                    raise TypeError(f"Value '{value}' in row {i}, key '{key}' has invalid type {type(value)}.")
        
        if not isinstance(return_string, bool):
            raise TypeError("return_string must be a boolean.")
        
        def clean_cell(val):
            if val is None:
                return ''
            if isinstance(val, date):
                return val.isoformat()
            return str(val).replace('\r', '').replace('\n', ' ')

        col_widths = {}
        for col in columns:
            header_len = len(col)
            content_len = max((len(clean_cell(row.get(col, ''))) for row in rows), default=0)
            col_widths[col] = max(header_len, content_len)

        def wrap_cell(val, width):
            val = clean_cell(val)
            return textwrap.wrap(val, width=width) or ['']

        header = " | ".join(f"{col:<{col_widths[col]}}" for col in columns)
        separator = "-+-".join("-" * col_widths[col] for col in columns)

        lines = []
        for row in rows:
            wrapped_cells = [wrap_cell(row.get(col, ''), col_widths[col]) for col in columns]
            max_lines = max(len(cell) for cell in wrapped_cells)
            for i in range(max_lines):
                line_parts = []
                for cell_lines, col in zip(wrapped_cells, columns):
                    part = cell_lines[i] if i < len(cell_lines) else ''
                    line_parts.append(f"{part:<{col_widths[col]}}")
                lines.append(" | ".join(line_parts))

        table_string = "\n".join([header, separator] + lines)

        if return_string:
            return table_string
        else:
            print(table_string)

    @staticmethod
    def save(rows: list[dict], columns: list[dict], file_extension: str, path: str) -> None:
        """
        Saves data rows to a file in the specified format (CSV, JSON, or HTML).

        Args:
            rows (list[dict]): List of data rows to save.
            columns (list[dict]): List of column definitions (each a dict); only the column names are used for output.
            file_extension (str): File format/extension to save ('csv', 'json', or 'html').
            path (str): Full file path (without extension) where the file will be saved.

        Raises:
            TypeError: If `file_extension` or `path` is not a string.
            ValueError: If `file_extension` is not one of the allowed formats ('csv', 'json', 'html'), or if
                        the `path` is empty or contains invalid filename characters.
            FileNotFoundError: If the directory in `path` does not exist.
        """
        if not isinstance(file_extension, str):
            raise TypeError('Invalid file_extension type: it is not a string')
        if file_extension not in ALLOWED_FORMATS:
            raise ValueError(f'Invalid output format: {file_extension}')
        validate_path(path)
        
        col_names = columns

        if file_extension == 'csv':
            with open(f'{path}.csv', 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=col_names, delimiter=';')
                writer.writeheader()
                writer.writerows(rows)

        elif file_extension == 'json':
            def convert_dates(obj):
                if isinstance(obj, date):
                    return obj.isoformat()
                raise TypeError(f'Type {type(obj)} not serializable')

            with open(f'{path}.json', 'w', encoding='utf-8') as jsonfile:
                json.dump(rows, jsonfile, ensure_ascii=False, indent=4, default=convert_dates)

        elif file_extension == 'html':
            template_html = """
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    table {
                        font-family: "Courier New", Courier, monospace;
                        border-collapse: collapse;
                        width: 100%;
                    }
                    td, th {
                        border: 1px solid #dddddd;
                        text-align: left;
                        padding: 8px;
                    }
                    tr:nth-child(even) {
                        background-color: #dddddd;
                    }
                </style>
            </head>
            <body>
                <table>
                    <thead>
                        <tr>
                            {% for col in cols %}
                                <th>{{ col }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in data %}
                        <tr>
                            {% for col in cols %}
                                <td>{{ row.get(col, '') }}</td>
                            {% endfor %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </body>
            </html>
            """
            template = Template(template_html)
            html_content = template.render(cols=col_names, data=rows)

            with open(f'{path}.html', 'w', encoding='utf-8') as htmlfile:
                htmlfile.write(html_content)

from faker import Faker
import csv
import json
from jinja2 import Template
import math
import random
from .emailMaker import generate_email_from_name

class FakeDataGenerator:
    """
    A comprehensive utility for generating synthetic data with configurable properties.

    This class generates realistic fake data tailored to different locales, making it ideal for use cases such as
    software testing, backend/frontend development, machine learning prototyping, and demonstrations. It supports
    consistent relationships between fields (e.g., name-based emails), optional sequential ID columns, and
    export to CSV, JSON, or HTML formats.
    
    Supported Fields:
        For Brazilian locale (pt_BR):
            - name: Full name
            - email: Email address (can be based on name)
            - age: Random integer between 18-90
            - cpf: Brazilian individual taxpayer registry number
            - cnpj: Brazilian company registry number
            - price: Monetary value with realistic distribution
            - phoneNumber: Brazilian cell phone number format
            - address: Brazilian address format
            - job: Professional occupation
            - date: Date values
            - time: Time values
            
        For US locale (en_US):
            - name: Full name
            - email: Email address (can be based on name)
            - age: Random integer between 18-90
            - ssn: Social Security Number
            - ein: Employer Identification Number
            - price: Monetary value with realistic distribution
            - phoneNumber: US phone number format
            - address: US address format
            - job: Professional occupation
            - date: Date values
            - time: Time values

    Parameters:
        fields (list[str]): List of field names to generate. Must be from the supported fields list.
        num_rows (int): Number of data rows to generate. Must be a positive integer.
        locale (str): The locale for data generation. Currently supports 'pt_BR' and 'en_US'.
        seed (int, optional): Random seed for reproducible results. Defaults to 20.
        id (bool, optional): Whether to include a sequential ID column (0 to n-1). Defaults to False.
        output_format (str, optional): Output format for saved data. 
                                        Options: 'csv', 'json', 'html'. Defaults to 'csv'.
    
    Raises:
        ValueError: If any parameters are invalid or incompatible.
    
    Examples:
        # Generate 100 rows with name and email fields in US format
        generator = FakeDataGenerator(
            fields=['name', 'email'],
            num_rows=100,
            locale='en_US'
        )
        generator.save('./output', 'us_contacts')
        
        # Generate 50 rows with multiple fields, IDs, and output as JSON using Brazilian locale
        generator = FakeDataGenerator(
            fields=['name', 'email', 'cpf', 'phoneNumber', 'address'],
            num_rows=50,
            locale='pt_BR',
            seed=42,
            id=True,
            output_format='json'
        )
        generator.save('./output', 'br_contacts')
        
        # Generate HTML table with names, ages and jobs
        generator = FakeDataGenerator(
            fields=['name', 'age', 'job'],
            num_rows=25,
            locale='en_US',
            output_format='html'
        )
        generator.save('./output', 'employees')
    
    Notes:
        - The seed parameter ensures reproducibility across runs
        - When 'name' is in fields, it's automatically moved to be the first field (after ID if enabled)
        - The module requires the 'faker' package and 'jinja2'
        - For HTML output, a simple styled table is generated
        - Price values follow a realistic distribution with different magnitudes
    """
    def __init__(self, fields: list[str], num_rows: int, locale: str, seed: int = 20, id: bool = False, output_format: str ='csv'):
        
        self._validateInputParameters(fields, num_rows, locale, seed, id,output_format)

        Faker.seed(seed)
        self.faker = Faker(locale)
        self.fields = fields.copy()
        if 'name' in self.fields:
            self.fields.remove('name')
            self.fields.insert(0, 'name')
        self.num_rows = num_rows
        self.add_id = id
        self.output_format = output_format

    # implementar id
    _br_fields = ('name', 'email', 'age', 'cpf', 'cnpj', 'price', 'phoneNumber', 'address',
                            'job', 'date', 'time')
    _us_fields = ('name', 'email', 'age', 'ssn', 'ein', 'price', 'phoneNumber', 'address',
                            'job', 'date', 'time')
    
    @classmethod
    def _validateInputParameters(cls, fields, num_rows, locale, seed, id, output_format):
        global _br_fields
        global _us_fields

        if not isinstance(locale, str):
            raise ValueError('Invalid locale type: is not a string')
        elif locale not in ('pt_BR', 'en_US'): 
            raise ValueError(f'Invalid locale: {locale}. Choose one of pt_BR or en_US')

        allowed_fields = cls._br_fields if locale == 'pt_BR' else cls._us_fields


        if not fields:
            raise ValueError(f'No columns were given: {fields}')
        elif not isinstance(fields, list) or not all(isinstance(f, str) for f in fields):
            raise ValueError(f'Invalid fields type: is not a list of strings')

        for col in fields:
            if col not in allowed_fields:
                raise ValueError(f'Invalid field: {col}')

        if not isinstance(num_rows, int) or num_rows <= 0:
            raise ValueError(f'Non-natural value: {num_rows}')

        if not isinstance(seed, (int, float)):
            raise ValueError(f'Seed value received is not numeric: {seed}')

        if not isinstance(id, bool):
            raise ValueError(f'Not boolan: {id}')

        allowed_output_format = ('csv','json', 'html')

        if not isinstance(output_format, str):
            raise ValueError('Invalid output_format type: is not a string')
        if output_format not in allowed_output_format:
            raise ValueError(f'Invalid output format: {output_format}')


    def _generate_row(self, row_id=None):
        row = {}

        if self.add_id and row_id is not None:
            row['id'] = row_id
        
        for field in self.fields:
            if field == 'email':
                row[field] = generate_email_from_name(row['name'], self.faker) if 'name' in row else self.faker.email()
            elif field == 'age':
                row[field] = self.faker.random_int(min=18, max=90)
            elif field == 'price':
                possible_bases = [0, 10, 100, 1000, 10000, 100000, 1000000]
                base_value = self.faker.random_element(elements=possible_bases)

                if base_value == 0:
                    max_value = 9
                else:
                    max_value = 10 ** (math.floor(math.log10(base_value)) + 1) - 1
                
                integer_part = self.faker.random_int(min=base_value, max=max_value)
                decimal_part = round(random.uniform(0, 0.99), 2)
                final_price = round(integer_part + decimal_part, 2)

                row[field] = final_price
            elif field == 'phoneNumber':
                row[field] = self.faker.cellphone_number() if self.faker.locale == 'pt_BR' else self.faker.phone_number()
            else:
                row[field] = getattr(self.faker, field)()
        return row

    def _generate_data(self):
        return [self._generate_row(row_id=i if self.add_id else None) for i in range(self.num_rows)]

    def save(self, path, filename):
        data = self._generate_data()
        
        all_fields = ['id'] + self.fields if self.add_id else self.fields.copy()

        if self.output_format == 'csv':
            with open(f'{path}/{filename}.csv', 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=all_fields, delimiter=';')
                writer.writeheader()
                writer.writerows(data)
        
        if self.output_format == 'json':
            with open(f'{path}/{filename}.json', 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, ensure_ascii=False, indent=4)
        
        if self.output_format == 'html':
            template_html = """
            <html>
            <head>
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
                            {% for field in fields %}
                                <th>{{ field }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in data %}
                        <tr>
                            {% for field in fields %}
                                {% if row.get(field) is not none %}
                                    <td>{{ row[field] }}</td>
                                {% else %}
                                    <td></td>
                                {% endif %}
                            {% endfor %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </body>
            </html>
            """
            template = Template(template_html)
            html_content = template.render(title="Fake Data", fields=all_fields, data=data)

            with open(f'{path}/{filename}.html', 'w', encoding='utf-8') as htmlfile:
                htmlfile.write(html_content)
import unicodedata
import re
from faker import Faker

def generate_email_from_name(name: str, faker: Faker) -> str:
    """
    Gera um e-mail coerente com o nome fornecido, com variações realistas.
    """

    def slugify(text):
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        return re.sub(r'[^a-zA-Z ]', '', text)

    clean_name = slugify(name)
    parts = clean_name.lower().split()

    if not parts:
        return faker.email()

    first = parts[0]
    last = parts[-1]
    first_initial = first[0] if first else ''

    domain = faker.free_email_domain()

    patterns = [
        f"{first}.{last}",
        f"{first}_{last}",
        f"{first}{last}",
        f"{first_initial}{last}",
        f"{last}.{first}",
        f"{first}",
        f"{first}{faker.random_int(min=10, max=99)}",
        f"{first}.{last}{faker.random_int(min=10, max=99)}"
    ]

    username = faker.random_element(patterns)

    email = f"{username}@{domain}"

    return email

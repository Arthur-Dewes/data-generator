import unicodedata
import re
from faker import Faker

def generate_email_from_name(name: str, faker: Faker) -> str:
    """
    Gera um e-mail coerente com o nome fornecido, com variações realistas.
    Remove prefixos e sufixos.
    """

    PREFIXES = {'srta', 'sr', 'sra', 'dr', 'dra', 'misc', 'miss', 'mr', 'mx', 'ms', 'ind', 'mrs'}
    SUFFIXES = {'v', 'md', 'ii', 'iii', 'iv', 'phd', 'jr', 'dds', 'dvm'}

    def slugify(text: str) -> str:
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        return re.sub(r'[^a-zA-Z ]', '', text)

    words = name.strip().split()
    cleaned_words = []

    for i, word in enumerate(words):
        w = word.lower().strip('.,')
        if i == 0 and w in PREFIXES:
            continue
        elif i == len(words) - 1 and w in SUFFIXES:
            continue
        cleaned_words.append(word)

    clean_name = slugify(" ".join(cleaned_words))
    parts = clean_name.lower().split()

    if not parts:
        return faker.email()

    first = parts[0]
    last = parts[-1]
    first_initial = first[0] if first else ''
    last_initial = last[0] if last else ''
    middle = parts[1] if len(parts) > 2 else ''

    domain = faker.free_email_domain()

    patterns = [
        f"{first}.{last}",
        f"{first}_{last}",
        f"{first}{last}",
        f"{first_initial}{last}",
        f"{last}.{first}",
        f"{first}",
        f"{first}{faker.random_int(min=10, max=99)}",
        f"{first}.{last}{faker.random_int(min=10, max=99)}",
        f"{first_initial}.{last}",
        f"{first}{last_initial}",
        f"{first}.{middle}.{last}" if middle else f"{first}.{last}",
        f"{first}_{last_initial}",
        f"{last}_{first}",
        f"{last}{faker.random_int(min=100, max=999)}",
        f"{first}{last}{faker.random_int(min=1000, max=9999)}",
        f"{first[0]}{middle[0] if middle else ''}{last}".lower(),
        f"{first}.{last}_{faker.random_element(['dev', 'user', 'mail'])}",
        f"{first}{faker.random_element(['', '_'])}{faker.random_int(min=1, max=999)}"
    ]

    username = faker.random_element(patterns)
    email = f"{username}@{domain}"
    return email

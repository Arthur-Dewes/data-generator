# ffactory

**ffactory** is a Python library for generating, visualizing, and sampling synthetic tabular data. Ideal for testing, prototyping, exploratory analysis, and simulations — without relying on sensitive or real-world datasets.

---

## Features

* Customizable data generation with flexible schemas
* Support for multiple locales (`pt_BR`, `en_US`)
* Table visualization with configurable formatting
* Export to formats: `CSV`, `JSON`, `HTML`
* Table concatenation with schema validation
* Sampling methods: random, stratified, systematic, and cluster
* Partial or full column renaming with safety checks

---

## Installation

Clone this repository or add `ffactory` to your project manually.  
Install dependencies.

```bash
pip install faker numpy jinja2
```

or by uv

```bash
uv venv
uv sync
```

---

## Usage Example

```python
from ffactory import FakeDataGenerator

# Create a table with 100 rows
gen = FakeDataGenerator(num_rows=100, locale='pt_BR')

# Add columns
# Some columns can repeat (use gen.info() to see which columns support repetition)
gen.add_columns([
    'name',
    'email',
    ('age', {'min_age': 18, 'max_age': 65}),
    ('date', {'min_date': '2010-01-01', 'max_date': '2022-12-31'}),
    ('boolean', {'true_chance': 70}),
    ('price', {'min_price': 50, 'max_price': 200})
])

# Generate the data
gen.generate_data()

# Display as formatted table
gen.as_table(return_string=False)

# Save to CSV
gen.save('csv', 'dados_falsos')
```

---

## Sampling

Transform the generated data into a sampler and apply common sampling techniques:

```python
sampler = gen.to_sampler()

# Simple random sampling without replacement
sample1 = sampler.random_sampling(n_samples=5, repo=False)

# Stratified sampling based on 'boolean' column
sample2 = sampler.stratified_sampling(n_samples=1, column='boolean')

# Systematic sampling
sample3 = sampler.systematic_sampling(interval=10, n_samples=5)

# Cluster sampling using the 'age' column
sample4 = sampler.cluster_sampling(group_by='age', n_samples=3)

sample1.as_table(return_string=False)
```

---

## Package Structure

| Module              | Description                                  |
| ------------------- | -------------------------------------------- |
| `FakeDataGenerator` | Generates and manages synthetic tabular data |
| `TableSampler`      | Sampling methods for tabular data            |
| `Sampling`          | Represents sampled subsets of rows           |

---

## Supported Export Formats

* CSV (`;` as separator)
* JSON (pretty-printed, supports `date` objects)
* HTML (styled HTML table)


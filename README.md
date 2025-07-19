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

gen = FakeDataGenerator(100, 'pt_BR')

gen.add_columns([
    'index',
    'name',
    ('date', {'min_date': '2010-01-01', 'max_date': '2022-12-31'}),
    'boolean',
    ('boolean', {'true_chance': 25}),
    'float',
    ('int', {'min_int': 0, 'max_int': 4})
])
gen.generate_data()

gen.as_table(return_string=False)
gen.info()

gen.save('csv', 'data')

```

---

### Concatenation and Equality Between Generators

* concatenate merges two generators if their column names and order match.
* __eq__ checks if two generators have the same set of column names, ignoring order.

```python
# To generate multiple variations of a column (e.g., different parameter settings), create separate generators and concatenate them.
another_gen = FakeDataGenerator(100, 'pt_BR')

another_gen.add_columns([
    'index',
    'name',
    'date',
    'boolean',
    'boolean',
    'float',
    ('int', {'min_int': 5, 'max_int': 9})
])
another_gen.generate_data()

gen.concatenate(another_gen)

gen.as_table(return_string=False)

```

---

## Sampling

Transform the generated data into a sampler and apply common sampling techniques:

```python
sampler = gen.to_sampler()

# Rename 'int' to 'classes' for use in group-based sampling
sampler.columns = {'int': 'classes'}

# Simple random sampling without replacement
sample1 = sampler.random_sampling(n_samples=10, repo=False)

# Stratified sampling based on 'classes' column
sample2 = sampler.stratified_sampling(n_samples=10, column='classes')

# Systematic sampling
sample3 = sampler.systematic_sampling(interval=10, n_samples=10)

# Cluster sampling using the 'classes' column
sample4 = sampler.cluster_sampling(group_by='classes', n_samples=3)

for sampling in [sample1, sample2, sample3, sample4]:
    sampling.as_table(return_string=False)
    print()

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

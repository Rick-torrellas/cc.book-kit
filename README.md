# cc-book-kit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Rick-torrellas/CapsuleCore-book/badges/version.json)
[![CI CD](https://github.com/Rick-torrellas/CapsuleCore-book/actions/workflows/main.yaml/badge.svg)](https://github.com/Rick-torrellas/CapsuleCore-book/actions/workflows/main.yaml)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Download](https://img.shields.io/github/v/release/Rick-torrellas/CapsuleCore-book?label=Download&color=orange)](https://github.com/Rick-torrellas/CapsuleCore-book/releases)
[![docs](https://img.shields.io/badge/docs-read_now-blue?style=flat-square)](https://rick-torrellas.github.io/cc-book-kit/)
[![Ask DeepWiki](https://img.shields.io/badge/DeepWiki-Documentation-blue?logo=gitbook&logoColor=white)](https://deepwiki.com/Rick-torrellas/CapsuleCore-book)
[![PyPI](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/cc.book-kit/)

💊⚛️

---

## Installation

Ensure you have your environment ready (recommended to use uv or pip):

```bash
pip install capsulecore-book
```

---

## Usage

Here is a simple example using the standard JSONLexicon.

```python
from cc_book_kit.capsule import JSONLexicon, 
from cc_book_kit.core import Codex, CodexPolicy

# 1. Initialize the storage (Lexicon)
repository = JSONLexicon(storage_path="my_knowledge_base.json")

# 2. Define your business policies
policy = CodexPolicy(
    title_unique=True,
    tags_lowercase=True,
    category_required=True
)

# 3. Create the Codex engine
codex = Codex(repository=repository, policy=policy)

# 4. Create entries
entry_a = codex.create_entry(
    title="Python Programming",
    content="A high-level programming language.",
    tags=["coding", "backend"],
    category="Technology"
)

entry_b = codex.create_entry(
    title="Knowledge Graphs",
    content="A way to represent interconnected data.",
    tags=["data", "graph"],
    category="Science"
)

# 5. Create a relation between them
relation = codex.create_relation(
    from_id=entry_a.id,
    to_id=entry_b.id,
    connection_type="related_to"
)

print(f"Created entry: {entry_a.title} with ID: {entry_a.id}")
```

### Choosing a Lexicon

Depending on your performance needs, you can swap the storage engine easily:

| Lexicon | Best For... | 
| :-----: | :-----: |
| JSONLexicon | Portability and no extra dependencies. |
| UJSONLexicon | Faster serialization than standard json. |
| ORJSONLexicon | Maximum performance, native Datetime/UUID support. |
| PydanticLexicon | Strict data validation and schema integrity. |

---

### Customizing Policies

You can adjust how the Codex behaves by modifying the CodexPolicy:

```python
custom_policy = CodexPolicy(
    title_max_length=50,
    category_default="Uncategorized",
    tags_sort=True
)
codex = Codex(repository=repository, policy=custom_policy)
```

## Key Features

* Hexagonal Architecture: Decouples core logic from storage implementation.
* Graph Structure: Manage data as a network of entries and connections.
* Multiple Lexicons: Out-of-the-box support for standard JSON, ujson, orjson, and Pydantic validation.
* Policy-Driven: Configurable rules for title uniqueness, tag formatting, and category management.

# Capsule Core book

## Installation

Ensure you have your environment ready (recommended to use uv or pip):

```bash
pip install capsulecore-book
```

## usage

```python
from CapsuleCore_book import JSONLexicon, Codex

lexicon = JSONLexicon(storage_path="./my_knowledge_base.json")
codex = Codex(lexicon)

entry1 = codex.create_entry(
    title="Atomic Habits 3",
    content="Small changes lead to remarkable results.",
    tags=["productivity", "books"]
)

entry2 = codex.create_entry(
    title="The Power of Habit 3",
    content="Habits are the compound interest of self-improvement.",
    tags=["productivity", "books"]
)

codex.create_relation(entry1.id, entry2.id, relation_type="related_to")
```
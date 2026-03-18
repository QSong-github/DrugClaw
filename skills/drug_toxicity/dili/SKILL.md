# 61_DILI — Drug-Induced Liver Injury (DILIrank 2.0 & DILIst)

## Overview

| Field | Value |
|---|---|
| Category | Drug-centric |
| Subcategory | Drug Toxicity |
| Source | FDA Liver Toxicity Knowledge Base (LTKB) |
| Datasets | **DILIrank 2.0** – severity classification; **DILIst** – extended annotations |
| URL | <https://www.fda.gov/science-research/liver-toxicity-knowledge-base-ltkb/drug-induced-liver-injury-rank-dilirank-20-dataset> |

**DILIrank** classifies drugs into four DILI concern levels:

- **Most-DILI-Concern** — strong evidence of causing liver injury
- **Less-DILI-Concern** — weaker or limited evidence
- **No-DILI-Concern** — no significant DILI evidence
- **Ambiguous** — conflicting or insufficient data

## File Layout

```
DATA_DIR/
  ├── DILIrank*.xlsx   # DILIrank dataset (one or more sheets)
  └── DILIst*.xlsx     # DILIst dataset (one or more sheets)
```

Default `DATA_DIR`:
```
/blue/qsong1/wang.qing/AgentLLM/DrugClaw/resources_metadata/drug_toxicity/DILI
```

Override via environment variable: `export DILI_DATA_DIR=/your/path`

## Dependencies

```bash
conda install openpyxl   # or: pip install openpyxl
# pandas is also required (usually already installed)
```

## Usage

### CLI

```bash
# Run default examples (acetaminophen, isoniazid, troglitazone)
python 61_DILI.py
```

### Python API

```python
from importlib.machinery import SourceFileLoader
mod = SourceFileLoader("dili", "61_DILI.py").load_module()

# Single entity
results = mod.query_dili("acetaminophen")

# Multiple entities
results = mod.query_dili(["isoniazid", "troglitazone"])
```

### Return Format

```json
[
  {
    "source": "DILIrank_2.0.xlsx",
    "match_count": 1,
    "matches": [
      {
        "Compound Name": "Acetaminophen",
        "DILI Concern": "Most-DILI-Concern",
        "...": "..."
      }
    ]
  }
]
```

- Returns an empty list when no matches are found.
- Returns `{"error": "..."}` if the data directory is missing or empty.

### LLM Integration Example

```text
User:  "Is troglitazone associated with liver injury?"
Agent: calls query_dili("troglitazone")
       → source: DILIrank_2.0.xlsx, DILI Concern: Most-DILI-Concern
       → "Yes — troglitazone is classified as Most-DILI-Concern in the FDA DILIrank dataset."
```

## CLI Usage (Fallback)

When vibe coding fails, run the skill script directly from the command line:

```bash
python skills/drug_toxicity/dili/dili_skill.py <entity1> [entity2] ...
```

**Example:**
```bash
python skills/drug_toxicity/dili/dili_skill.py aspirin
```

The script imports functions from the sibling `example.py`, executes the query, and prints LLM-readable results to stdout.

# DrugEHRQA

> **Subcategory**: `drug_nlp` &nbsp;|&nbsp; **Access mode**: `Dataset`

**Purpose**: Drug QA over EHR  

**Coverage**: Question-answering dataset over structured/unstructured EHRs  

## Setup

1. Download the dataset from: <https://github.com/jayachaturvedi/DrugEHRQA>
2. Set `csv_path` (or `tsv_path` / `json_path`) in config (see below).

## Configuration

| Key | Type / Description |
|-----|--------------------|
| `json_path` | path to DrugEHRQA JSON file (questions, answers, drug entities) |
| `csv_path` | alternative: path to CSV version |
| `delimiter` | CSV delimiter (default: ",") |

## Usage

```python
from drugclaw.skills.drug_nlp.drugehrqa import DrugEHRQASkill

skill = DrugEHRQASkill(config={
    "json_path": "...",  # path to DrugEHRQA JSON file (questions, answers, drug entities)
    "csv_path": "...",  # alternative: path to CSV version
    "delimiter": "...",  # CSV delimiter (default: ",")
})

if skill.is_available():
    results = skill.retrieve(
        entities={"drug": ["imatinib"]},
        query="mechanism",
        max_results=20,
    )
    for r in results:
        print(r.source_entity, r.relationship, r.target_entity)
```

## Output (`RetrievalResult`)

| Field | Description |
|-------|-------------|
| `source_entity` | Drug name |
| `target_entity` | Target / disease / ADE / partner |
| `relationship` | Relation type |
| `weight` | Confidence / score (0–1 or raw) |
| `evidence_text` | Human-readable summary |
| `sources` | Source IDs (PMID, DOI, etc.) |
| `metadata` | Extra fields specific to this skill |

## Data Source

- Homepage: <https://github.com/jayachaturvedi/DrugEHRQA>

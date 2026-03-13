# n2c2 2018 Track 2

> **Subcategory**: `drug_nlp` &nbsp;|&nbsp; **Access mode**: `Dataset`

**Purpose**: Clinical NLP ADE corpus  

**Coverage**: n2c2 2018 adverse drug event extraction from EHRs  

## Setup

1. Download the dataset from: <https://n2c2.dbmi.hms.harvard.edu/>
2. Set `csv_path` (or `tsv_path` / `json_path`) in config (see below).

## Configuration

| Key | Type / Description |
|-----|--------------------|
| `tsv_path` | path to pre-parsed TSV/CSV (drug, adverse_event, sentence, label) |
| `csv_path` | alternative CSV path |
| `delimiter` | column delimiter (default: "   ") |

## Usage

```python
from drugclaw.skills.drug_nlp.n2c2_2018 import N2C22018Skill

skill = N2C22018Skill(config={
    "tsv_path": "...",  # path to pre-parsed TSV/CSV (drug, adverse_event, sentence, label)
    "csv_path": "...",  # alternative CSV path
    "delimiter": "...",  # column delimiter (default: "   ")
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

- Homepage: <https://n2c2.dbmi.hms.harvard.edu/>

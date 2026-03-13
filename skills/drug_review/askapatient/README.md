# askapatient

> **Subcategory**: `drug_review` &nbsp;|&nbsp; **Access mode**: `Dataset`

**Purpose**: Patient experience reports  

**Coverage**: Patient-reported drug experiences from AskAPatient.com  

## Setup

1. Download the dataset from: <https://www.askapatient.com / Kaggle mirror>
2. Set `csv_path` (or `tsv_path` / `json_path`) in config (see below).

## Configuration

| Key | Type / Description |
|-----|--------------------|
| `csv_path` | path to askapatient CSV file |
| `delimiter` | column delimiter (default: ",") |

## Usage

```python
from drugclaw.skills.drug_review.askapatient import AskAPatientSkill

skill = AskAPatientSkill(config={
    "csv_path": "...",  # path to askapatient CSV file
    "delimiter": "...",  # column delimiter (default: ",")
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

- Homepage: <https://www.askapatient.com / Kaggle mirror>

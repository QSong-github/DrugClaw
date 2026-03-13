# DILI

> **Subcategory**: `drug_toxicity` &nbsp;|&nbsp; **Access mode**: `Local File`

**Purpose**: DILI benchmark dataset  

**Coverage**: Drug-induced liver injury benchmark dataset (Xu et al.)  

## Setup

## Configuration

| Key | Type / Description |
|-----|--------------------|
| `csv_path` | path to DILI CSV (columns: drug/Drug/compound_name, |
| `delimiter` | column delimiter (default: auto-detect from extension) |

## Usage

```python
from drugclaw.skills.drug_toxicity.dili import DILISkill

skill = DILISkill(config={
    "csv_path": "...",  # path to DILI CSV (columns: drug/Drug/compound_name,
    "delimiter": "...",  # column delimiter (default: auto-detect from extension)
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

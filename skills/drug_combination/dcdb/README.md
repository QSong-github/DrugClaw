# DCDB

> **Subcategory**: `drug_combination` &nbsp;|&nbsp; **Access mode**: `Local File`

**Purpose**: Drug combination reference  

**Coverage**: Drug Combination Database with efficacy information  

## Setup

1. Download the dataset from: <http://www.cls.zju.edu.cn/dcdb/>
2. Set `csv_path` (or `tsv_path` / `json_path`) in config (see below).

## Configuration

| Key | Type / Description |
|-----|--------------------|
| `csv_path` | path to DCDB CSV/TSV file |
| `delimiter` | column delimiter (default: auto-detect from extension) |

## Usage

```python
from drugclaw.skills.drug_combination.dcdb import DCDBSkill

skill = DCDBSkill(config={
    "csv_path": "...",  # path to DCDB CSV/TSV file
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

## Data Source

- Homepage: <http://www.cls.zju.edu.cn/dcdb/>

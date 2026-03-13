# CancerDR

> **Subcategory**: `drug_repurposing` &nbsp;|&nbsp; **Access mode**: `Local File`

**Purpose**: Cancer drug resistance  

**Coverage**: Drug resistance mutations and cancer drug sensitivity  

## Setup

1. Download the dataset from: <http://crdd.osdd.net/raghava/cancerdr/>
2. Set `csv_path` (or `tsv_path` / `json_path`) in config (see below).

## Configuration

| Key | Type / Description |
|-----|--------------------|
| `csv_path` | path to CancerDR CSV/TSV download |
| `delimiter` | column delimiter (default: auto-detect from extension) |

## Usage

```python
from drugclaw.skills.drug_repurposing.cancerdr import CancerDRSkill

skill = CancerDRSkill(config={
    "csv_path": "...",  # path to CancerDR CSV/TSV download
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

- Homepage: <http://crdd.osdd.net/raghava/cancerdr/>

# PharmKG

> **Subcategory**: `drug_knowledgebase` &nbsp;|&nbsp; **Access mode**: `Local File`

**Purpose**: Pharmaceutical knowledge graph  

**Coverage**: Multi-relational drug KG (drug-gene-disease-pathway)  

## Setup

1. Download the dataset from: <https://github.com/MindRank-Biotech/PharmKG>
2. Set `csv_path` (or `tsv_path` / `json_path`) in config (see below).

## Configuration

| Key | Type / Description |
|-----|--------------------|
| `train_tsv` | path to PharmKG train.tsv |

## Usage

```python
from drugclaw.skills.drug_knowledgebase.pharmkg import PharmKGSkill

skill = PharmKGSkill(config={
    "train_tsv": "...",  # path to PharmKG train.tsv
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

- Homepage: <https://github.com/MindRank-Biotech/PharmKG>

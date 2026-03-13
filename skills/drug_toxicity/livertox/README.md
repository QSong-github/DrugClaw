# LiverTox

> **Subcategory**: `drug_toxicity` &nbsp;|&nbsp; **Access mode**: `REST API`

**Purpose**: Drug-induced liver injury  

**Coverage**: NCBI LiverTox clinical descriptions of DILI by drug  

## Usage

```python
from drugclaw.skills.drug_toxicity.livertox import LiverToxSkill

skill = LiverToxSkill(config={
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

- Homepage: <https://www.ncbi.nlm.nih.gov/books/NBK547852/>

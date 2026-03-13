# RxList Drug Descriptions

> **Subcategory**: `drug_labeling` &nbsp;|&nbsp; **Access mode**: `REST API`

**Purpose**: Drug monographs  

**Coverage**: Clinical drug descriptions including mechanism and dosing  

## Usage

```python
from drugclaw.skills.drug_labeling.rxlist import RxListSkill

skill = RxListSkill(config={
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

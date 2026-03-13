# VigiAccess

> **Subcategory**: `adr` &nbsp;|&nbsp; **Access mode**: `REST API`

**Purpose**: WHO pharmacovigilance  

**Coverage**: WHO global adverse reaction database (VigiBase summary)  

## Usage

```python
from drugclaw.skills.adr.vigiaccess import VigiAccessSkill

skill = VigiAccessSkill(config={
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

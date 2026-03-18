---
name: repodb-query
description: >
  Query the RepoDB drug repurposing database. Use whenever the user asks about
  drug-disease associations, drug repurposing candidates, or wants to look up
  any entity (drug name, indication, DrugBank ID, UMLS CUI, NCT ID) in RepoDB.
---

# RepoDB Query Skill

Search RepoDB records by any entity. Auto-detects type by prefix:

| Input Pattern | Detected As | Match Logic |
|---|---|---|
| `DB00584` | DrugBank ID | exact on `drugbank_id` |
| `C0020538` | UMLS CUI | exact on `ind_id` |
| `NCT00001234` | Trial ID | exact on `NCT` |
| anything else | free text | substring on `drug_name` OR `ind_name` |

## API

| Function | Input | Returns |
|---|---|---|
| `load_repodb(path)` | CSV path | DataFrame |
| `search(df, entity)` | single entity string | DataFrame |
| `search_batch(df, entities)` | list of entity strings | dict[str, DataFrame] |
| `summarize(hits, entity)` | DataFrame + label | compact text |
| `to_json(hits)` | DataFrame | list[dict] |

## Usage

See `if __name__ == "__main__"` block in `repodb_query.py` for runnable examples covering: drug name, DrugBank ID, UMLS CUI, indication name, batch search, and JSON output.

## Data

- **Source**: `full.csv` (comma or tab separated, auto-detected)
- **Columns**: `drug_name`, `drugbank_id`, `ind_name`, `ind_id`, `NCT`, `status`, `phase`, `DetailedStatus`
- **Path**: `DATA_PATH` variable in `repodb_query.py`

## CLI Usage (Fallback)

When vibe coding fails, run the skill script directly from the command line:

```bash
python skills/drug_repurposing/repodb/repodb_skill.py <entity1> [entity2] ...
```

**Example:**
```bash
python skills/drug_repurposing/repodb/repodb_skill.py metformin
```

The script imports functions from the sibling `example.py`, executes the query, and prints LLM-readable results to stdout.

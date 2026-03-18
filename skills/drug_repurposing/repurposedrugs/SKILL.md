---
name: RepurposeDrugs-query
description: >
  Query the RepurposeDrugs single-agent drug repurposing database. Use whenever
  the user asks about drug-disease repurposing associations, clinical trial phases
  for repurposed drugs, or wants to look up any entity (drug name, disease name,
  NCT ID) in RepurposeDrugs.
---

# RepurposeDrugs Query Skill

Search single-agent drug-disease repurposing associations. Auto-detects query type by pattern:

| Input Pattern | Detected As | Match Logic |
|---|---|---|
| `NCT01856868` | Trial NCT ID | exact match in parsed NCT_IDs |
| `1` – `4` | Phase number | exact on `Phase` |
| anything else | free text | substring on `Drug_name` OR `Disease_name` |

## API

| Function | Input | Returns |
|---|---|---|
| `load_data(path)` | xlsx path | DataFrame (adds `NCT_IDs` column) |
| `search(df, entity)` | single entity string | DataFrame |
| `search_batch(df, entities)` | list of entity strings | dict[str, DataFrame] |
| `summarize(hits, entity)` | DataFrame + label | compact LLM-readable text |
| `to_json(hits)` | DataFrame | list[dict] |

## Usage

See `if __name__ == "__main__"` block in `16_RepurposeDrugs.py` for runnable examples covering: drug name, disease name, NCT ID lookup, batch search, and JSON output.

## Data

- **Source**: RepurposeDrugs – Ianevski A et al., *Briefings in Bioinformatics*, 2024
- **URL**: <https://repurposedrugs.org/>
- **Local file**: `dataset_single.xlsx`
- **Columns**: `Drug_name`, `Disease_name`, `Phase`, `Merged_RefNew`
- **Derived**: `NCT_IDs` (list of NCT identifiers extracted from `Merged_RefNew` URL)
- **Scale**: 4 314 compounds × 1 756 indications, 28 148 drug-disease pairs
- **Path**: `DATA_PATH` variable in `16_RepurposeDrugs.py`

## CLI Usage (Fallback)

When vibe coding fails, run the skill script directly from the command line:

```bash
python skills/drug_repurposing/repurposedrugs/repurposedrugs_skill.py <entity1> [entity2] ...
```

**Example:**
```bash
python skills/drug_repurposing/repurposedrugs/repurposedrugs_skill.py metformin
```

The script imports functions from the sibling `example.py`, executes the query, and prints LLM-readable results to stdout.

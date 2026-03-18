---
name: GDKD-query
description: >
  Query the Gene-Drug Knowledge Database (GDKD) for variant-specific
  gene–drug associations in oncology. Use when the user asks about
  cancer genomic biomarkers, drug sensitivity/resistance by gene or
  variant, targetable mutations, or clinical evidence for cancer
  therapeutics.
---

# GDKD Query Skill

Search the Gene-Drug Knowledge Database (v20.0) by any entity.
Auto-detects input type by pattern:

| Input Pattern | Detected As | Match Logic |
|---|---|---|
| `BRAF`, `EGFR` | Gene symbol | exact on `Gene` (case-insensitive) |
| `V600E`, `T315I` | Variant | exact on `Variant` |
| `amplification` | Variant keyword | substring on `Description` |
| anything else | Free text | substring on `Disease`, `Gene`, `Description`, all `Therapeutic context` columns |

## API

| Function | Input | Returns |
|---|---|---|
| `load_gdkd(path)` | xlsx path | DataFrame |
| `search(df, entity)` | single entity string | DataFrame |
| `search_batch(df, entities)` | list of entity strings | dict[str, DataFrame] |
| `summarize(hits, entity)` | DataFrame + label | compact text |
| `to_json(hits)` | DataFrame | list[dict] |

## Usage

See `if __name__ == "__main__"` block in `16_GDKD.py` for runnable
examples covering: gene symbol, variant, disease name, drug name,
batch search, and JSON output.

## Data

- **Source**: GDKD Knowledge Database v20.0 (Synapse `syn2370773`)
- **Paper**: Dienstmann et al., *Cancer Discovery* 2015;5(2):118-123
- **Format**: xlsx, one row per disease–gene–variant triplet
- **Core columns**: `Disease`, `Gene`, `Variant`, `Description`, `Effect`
- **Association slots**: up to 8 per row, each with `Association_N`, `Therapeutic context_N`, `Status_N`, `Evidence_N`, `PMID_N`
- **Path**: `DATA_PATH` variable in `16_GDKD.py`

## CLI Usage (Fallback)

When vibe coding fails, run the skill script directly from the command line:

```bash
python skills/dti/gdkd/gdkd_skill.py <entity1> [entity2] ...
```

**Example:**
```bash
python skills/dti/gdkd/gdkd_skill.py imatinib
```

The script imports functions from the sibling `example.py`, executes the query, and prints LLM-readable results to stdout.

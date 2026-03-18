---
name: DrugComb
description: >
  Query the DrugComb drug combination database for cancer cell-line synergy
  and sensitivity data. Use whenever the user asks about drug combinations,
  synergy scores (ZIP/Bliss/Loewe/HSA), combination sensitivity (CSS),
  or wants to look up how two drugs interact in a specific cancer cell line.
---

# DrugComb Query Skill

Search DrugComb summary records by any entity. Auto-detects type by pattern:

| Input Pattern | Detected As | Match Logic |
|---|---|---|
| `5-FU` / `imatinib` | drug name | case-insensitive substring on `drug_row` OR `drug_col` |
| `A549` / `MCF-7` | cell line | case-insensitive substring on `cell_line_name` |
| `12345` (pure digits) | block_id | exact on `block_id` |
| `CID:2244` | PubChem CID | exact on `drug_row_cid` OR `drug_col_cid` |

## API

| Function | Input | Returns |
|---|---|---|
| `load_drugcomb(path)` | CSV path | `list[dict]` |
| `columns(data)` | loaded data | column name list |
| `search(data, entity)` | single entity string | `list[dict]` |
| `search_batch(data, entities)` | list of entity strings | `dict[str, list[dict]]` |
| `summarize(hits, entity)` | hit list + label | compact LLM-readable text |
| `to_json(hits)` | hit list | `list[dict]` |

## Usage

See `if __name__ == "__main__"` block in `50_DrugComb.py` for runnable examples covering: drug name search, cell-line search, batch search, and JSON output.

## Data

- **Source**: DrugComb v1.4 summary table (`summary_table_v1.4.csv`, 193 MB)
- **Download**: <https://zenodo.org/records/11102665>
- **Key columns**: `block_id`, `drug_row`, `drug_col`, `cell_line_name`, `synergy_zip`, `synergy_bliss`, `synergy_loewe`, `synergy_hsa`, `css_ri` / `css`, `study_name`
- **Path**: `DATA_PATH` variable in `50_DrugComb.py`

## Citation

Zagidullin B, Aldahdooh J, Zheng S, et al. DrugComb: an integrative cancer drug combination data portal. *Nucleic Acids Res.* 2019;47(W1):W43–W51. doi:10.1093/nar/gkz337

## CLI Usage (Fallback)

When vibe coding fails, run the skill script directly from the command line:

```bash
python skills/drug_combination/drugcomb/drugcomb_skill.py <entity1> [entity2] ...
```

**Example:**
```bash
python skills/drug_combination/drugcomb/drugcomb_skill.py doxorubicin
```

The script imports functions from the sibling `example.py`, executes the query, and prints LLM-readable results to stdout.

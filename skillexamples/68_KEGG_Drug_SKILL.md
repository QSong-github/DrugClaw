---
name: kegg-drug-query
description: >
  Query KEGG Drug through the KEGG REST API. Use whenever the user asks about
  approved drugs in KEGG, drug targets, pathways, KEGG Drug IDs, or
  drug-drug-interaction annotations for one drug or a small list of drugs.
---

# KEGG Drug Query Skill

Search KEGG Drug by name or direct KEGG Drug ID, then fetch the parsed flat
file entry, targets, or interaction annotations.

| Input Pattern | Detected As | Action |
|---|---|---|
| `D00109` / `dr:D00109` | KEGG Drug ID | direct `get_entry()` / `get_targets()` / `get_interactions()` |
| `aspirin` / `warfarin` | free-text drug name | `search()` then fetch first hit |
| `["metformin", "imatinib"]` | list of drugs | iterate `query()` per item |

## API

| Function | Input | Returns |
|---|---|---|
| `search(query, limit=10)` | drug name / keyword | `list[dict]` with `id`, `name` |
| `get_entry(drug_id)` | KEGG Drug ID | parsed entry `dict` |
| `get_targets(drug_id)` | KEGG Drug ID | `list[str]` |
| `get_interactions(drug_id)` | KEGG Drug ID | `list[str]` |
| `query(entities, fields="all")` | `str` or `list[str]` | one result dict per entity |

## Usage

See `if __name__ == "__main__"` in `68_KEGG_Drug.py` for runnable examples
covering: single-drug query, batch query, ID query, targets-only mode, and
interactions-only mode.

## Key Fields

Top-level parsed fields may include: `entry`, `name`, `formula`,
`exact_mass`, `mol_weight`, `efficacy`, `comment`, `remark`, `drug_id`.

Section lists may include: `targets`, `interactions`, `pathways`, `classes`.

On unresolved name search, `query()` returns `{"query": "...", "error":
"No match found"}`.

## Notes

- The script uses the first KEGG search hit for free-text names; ambiguous
  names may need manual review.
- Live validation on 2026-03-15 confirmed
  `https://rest.kegg.jp/find/drug/aspirin` returned KEGG Drug hits including
  `dr:D00109`.
- KEGG REST access is typically available for academic use; commercial access
  may require a license.

## Data Source

- **Homepage**: <https://www.genome.jp/kegg/>
- **API docs**: <https://www.kegg.jp/kegg/docs/keggapi.html>
- **REST base**: <https://rest.kegg.jp>
- **Paper**: <https://academic.oup.com/nar/article/38/suppl_1/D355/3112250>


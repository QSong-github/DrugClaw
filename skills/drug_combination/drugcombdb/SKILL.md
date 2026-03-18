---
name: drugcombdb-query
description: >
  Query DrugCombDB drug combination synergy data from local CSV files.
  Use whenever the user asks about drug combinations, synergy/antagonism
  scores, combination therapies in cancer cell lines, or wants to look up
  any entity (drug name, drug pair, PubChem CID, cell line, record ID)
  in DrugCombDB.
---

# DrugCombDB Query Skill

Search drug combination synergy records by entity. Auto-detects type:

| Input Pattern | Detected As | Match Logic |
|---|---|---|
| `12345` (pure integer) | Record ID | exact on `ID` in drugcombs_scored |
| `CIDs00065628` | PubChem CID | substring on `cIds` in drug_chemical_info |
| `A549`, `MCF7`, `A2058` … | Cell line | substring on `Cell line` in drugcombs_scored |
| anything else | Drug name | substring on `Drug1` OR `Drug2` |

## API

| Function | Input | Returns |
|---|---|---|
| `search(entity, limit)` | single entity string | `list[dict]` |
| `search_batch(entities, limit)` | list of entity strings | `dict[str, list[dict]]` |
| `search_drug(drug_name, limit)` | drug name | scored combinations |
| `search_drug_pair(drug1, drug2, limit)` | two drug names | combinations for that pair |
| `search_cell_line(name, limit)` | cell line name | combinations on that cell line |
| `get_by_id(record_id)` | numeric ID string | exact record(s) |
| `get_drug_info(drug_name)` | drug name | chemical info (MW, SMILES, CID) |
| `get_drug_info_by_cid(cid)` | PubChem CID string | chemical info |
| `list_cell_lines()` | — | all cell lines with COSMIC IDs |
| `get_classification(drug, model, limit)` | drug + model name | synergy/antagonism label |
| `search_three_drug(drug, limit)` | drug name | three-drug combination records |
| `summarize(results, entity)` | list + label | compact LLM-readable text |
| `to_json(results)` | list | `list[dict]` (passthrough) |

## Data Files

| File | Key Columns | Description |
|---|---|---|
| `drugcombs_scored.csv` | ID, Drug1, Drug2, Cell line, ZIP, Bliss, Loewe, HSA | Main synergy scores |
| `drug_chemical_info.csv` | drugName, cIds, drugNameOfficial, molecularWeight, smilesString | Drug chemical properties |
| `cell_Line.csv` | cellName, cosmicId, tag | Cancer cell line metadata |
| `Syner&Antag_{model}.csv` | ID, Drug1, Drug2, Cell line, score, classification | Binary synergy/antagonism labels (zip/bliss/loewe/hsa/voting) |
| `ThreeDrugCombs.csv` | Drug1, Drug2, Drug3, concentrations, viability, … | Three-drug combo experiments |
| `drugcombs_response.csv` | (dose-response matrices) | Raw experimental dose-response data |
| `SynDrugComb_*.xlsx` | (varies) | FDA-approved, external DB, and text-mined combinations |

## Usage

See `if __name__ == "__main__"` block in `21_DrugCombDB.py` for runnable
examples covering: drug name search, cell line search, drug pair lookup,
chemical info, synergy classification, three-drug combos, batch search,
and JSON output.

## Data Source

- **Source**: http://drugcombdb.denglab.org/ (downloaded files)
- **Path**: `DATA_DIR` variable in `21_DrugCombDB.py`
- **Coverage**: 448 555 drug combinations, 2 887 drugs, 124 cancer cell lines
- **Synergy models**: ZIP, Bliss, Loewe, HSA — positive = synergy, negative = antagonism
- **Citation**: Liu H et al. *Nucleic Acids Res.* 2020;48(D1):D871-D881

## CLI Usage (Fallback)

When vibe coding fails, run the skill script directly from the command line:

```bash
python skills/drug_combination/drugcombdb/drugcombdb_skill.py <entity1> [entity2] ...
```

**Example:**
```bash
python skills/drug_combination/drugcombdb/drugcombdb_skill.py doxorubicin
```

The script imports functions from the sibling `example.py`, executes the query, and prints LLM-readable results to stdout.

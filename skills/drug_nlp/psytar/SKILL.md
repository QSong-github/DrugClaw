---
name: psytar-query
description: >
  Query the PsyTAR psychiatric adverse-reaction corpus. Use when the user asks
  about patient-reported ADRs, withdrawal symptoms, drug indications, or
  effectiveness for Zoloft, Lexapro, Cymbalta, or Effexor XR.  Accepts drug
  names (brand or generic), symptom terms, or UMLS CUIs.
---

# PsyTAR Query Skill

891 patient reviews → 6 009 annotated sentences → extracted ADR / WD / SSI /
DI entities → mapped to 918 UMLS + 755 SNOMED CT concepts.

## Entity Detection & Routing

| Input Pattern | Detected As | Targets |
|---|---|---|
| `C0917801` | UMLS CUI | `*_Mapped` sheets only (UMLS1/UMLS2 cols) |
| `Zoloft` / `sertraline` | Drug name | `drug_id` or `drug` columns (alias-aware) |
| `nausea`, `insomnia` … | Free text | substring across all cell values |

Generic ↔ brand aliases: sertraline↔Zoloft, escitalopram↔Lexapro,
duloxetine↔Cymbalta, venlafaxine↔Effexor.

## API

| Function | Input | Returns |
|---|---|---|
| `search(entity, sheet?, label?)` | single string | `{sheet: [row_dict]}` |
| `search_batch(entities, sheet?, label?)` | list of strings | `{entity: {sheet: [row_dict]}}` |
| `summarize(results, entity)` | result dict + label | compact text |
| `to_json(results)` | result dict | `list[dict]` (flat, adds `_sheet`) |
| `describe()` | — | dataset overview text |

### Parameters

- **`sheet`** — restrict to one sheet (fuzzy-matched: `"ADR"` → `ADR_Identified`).
- **`label`** — when on `Sentence_Labeling`, keep only rows where the named
  label column (ADR / WD / EF / INF / SSI / DI) equals 1.

## Sheet Schema

| Sheet | Description | Key Columns |
|---|---|---|
| `Sample` | Original posts | drug_id, rating, indication, side-effect, comment, gender, age, duration |
| `Sentence_Labeling` | 6 009 sentences, binary labels | drug_id, sentence_index, sentences, ADR, WD, EF, INF, SSI, DI, Findings, others, rating, category |
| `ADR_Identified` | Extracted ADR mentions | drug_id, sentence_index, sentences, ADR1 … ADRn |
| `WD_Identified` | Extracted WD mentions | drug_id, sentence_index, sentences, WD1 … WDn |
| `SSI_Identified` | Extracted SSI mentions | drug_id, sentence_index, sentences, SSI1 … SSIn |
| `DI_Identified` | Extracted DI mentions | drug_id, sentence_index, sentences, DI1 … DIn |
| `ADR_Mapped` | ADR → UMLS/SNOMED | drug_id, sentence_index, ADR/ADRs, UMLS1, UMLS2, SNOMED-CT, mild, moderate, severe, persistent, not-persistent, body-site, rating, drug, class, type, entity_type |
| `WD_Mapped` | WD → UMLS/SNOMED | (same structure as ADR_Mapped) |
| `SSI_Mapped` | SSI → UMLS/SNOMED | (same structure) |
| `DI_Mapped` | DI → UMLS/SNOMED | (same structure) |

### Mapped-sheet qualifier columns

`mild`, `moderate`, `severe` — severity descriptors;
`persistent`, `not-persistent` — duration;  `body-site` — anatomical site;
`entity_type` — Cognitive / Physiological / Psychological / Functional.

## Usage

```python
from importlib.machinery import SourceFileLoader
m = SourceFileLoader("psytar", "36_PSYTAR.py").load_module()

# overview
print(m.describe())

# drug → ADR mappings
res = m.search("Zoloft", sheet="ADR_Mapped")
print(m.summarize(res, "Zoloft"))

# generic name works too
res = m.search("sertraline", sheet="ADR_Mapped")

# symptom in one Identified sheet
res = m.search("nausea", sheet="ADR_Identified")

# symptom across all sheets
res = m.search("insomnia")

# UMLS CUI (auto-scoped to Mapped sheets)
res = m.search("C0917801")

# withdrawal sentences for Effexor
res = m.search("Effexor", sheet="Sentence_Labeling", label="WD")

# batch
batch = m.search_batch(["Lexapro", "insomnia", "C0917801"])

# JSON for pipeline
flat = m.to_json(m.search("Cymbalta"))
```

## Data Source

- **Corpus**: PsyTAR v1.0 — CC BY 4.0
- **File**: `PsyTAR_dataset.xlsx` — set via `DATA_PATH` or env `PSYTAR_XLSX`
- **Paper**: Zolnoori et al., *Data in Brief* 24, 103838 (2019).
  https://doi.org/10.1016/j.dib.2019.103838
- **Stats**: 891 reviews, 6 009 sentences, 4 813 ADR + 590 WD + 1 219 SSI
  + 792 DI mentions, 918 UMLS / 755 SNOMED concepts

## CLI Usage (Fallback)

When vibe coding fails, run the skill script directly from the command line:

```bash
python skills/drug_nlp/psytar/psytar_skill.py <entity1> [entity2] ...
```

**Example:**
```bash
python skills/drug_nlp/psytar/psytar_skill.py sertraline
```

The script imports functions from the sibling `example.py`, executes the query, and prints LLM-readable results to stdout.

---
name: cpic-query
description: >
  Query the CPIC pharmacogenomics API. Use whenever the user asks about
  gene-based prescribing guidelines, drug-gene pairs, CPIC recommendations,
  PharmGKB-linked PGx evidence, or wants to query one drug, one gene, or a
  short list of entities through CPIC.
---

# CPIC Query Skill

Search CPIC by drug name or gene symbol. Drug names are resolved to `drugid`
first, then routed to the appropriate PostgREST tables.

| Input Pattern | Detected As | Action |
|---|---|---|
| `clopidogrel` / `warfarin` | drug name | resolve via `/v1/drug`, then query guidelines / pairs / recommendations |
| `CYP2D6` / `CYP2C19` | gene symbol | query `/v1/pair` by `genesymbol` |
| `["warfarin", "codeine"]` | list of drugs | iterate `query()` per item |

## API

| Function | Input | Returns |
|---|---|---|
| `get_drug_info(drug_name)` | single drug name | `list[dict]` from `/v1/drug` |
| `get_guidelines(drug_name=None)` | optional drug name | `list[dict]` from `/v1/guideline` |
| `get_gene_drug_pairs(drug_name=None, gene=None)` | optional drug or gene | `list[dict]` from `/v1/pair` |
| `get_recommendations(drug_name)` | single drug name | `list[dict]` from `/v1/recommendation` |
| `query(entities, fields="all")` | `str` or `list[str]` | one result dict per entity |

## Usage

See `if __name__ == "__main__"` in `67_CPIC.py` for runnable examples
covering: single-drug query, batch drug query, gene-only pair lookup, and
guideline-only retrieval.

## Key Fields

**drug_info**: `drugid`, `name`, `drugbankid`, `atcid`, `flowchart`.

**guidelines**: `name`, `url`, `version`.

**gene_drug_pairs**: `genesymbol`, `drugid`, `cpiclevel`, `clinpgxlevel`,
`pgxtesting`, `citations`.

**recommendations**: `drugid`, `phenotypes`, `implications`,
`drugrecommendation`, `classification`, `population`.

## Notes

- The API uses `drugid` in `pair` and `recommendation`; the script correctly
  resolves names through `/v1/drug` first.
- Live validation on 2026-03-15 confirmed the official CPIC endpoint
  `https://api.cpicpgx.org/v1/drug?name=ilike.*clopidogrel*` returned JSON with
  a `clopidogrel` record.
- Gene symbols are heuristically auto-detected in `query()`. Short uppercase
  strings may be treated as genes first.

## Data Source

- **Homepage**: <https://cpicpgx.org/>
- **API docs**: <https://cpicpgx.org/cpic-data/>
- **API base**: <https://api.cpicpgx.org/v1>
- **Paper**: <https://pubmed.ncbi.nlm.nih.gov/33479744/>


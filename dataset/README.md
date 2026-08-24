# DrugAudit data

Data accompanying *DrugClaw and DrugAudit: A Primary-Source-Grounded Agent and
Authority-Aware Benchmark for Drug-Information Question Answering*
(Findings of EMNLP 2026).

## Files

| File | Items | Description |
|---|---|---|
| `evidence.xlsx` | 3,961 | DrugAudit items in spreadsheet form: question, gold answer, gold evidence, and the source database each item was generated from. The `Verdict` and `Notes` columns are an empty template for anyone who wants to run their own manual review. |
| `medqa_drug.json` | 751 | Drug-related subset of MedQA-USMLE, five-way multiple choice. Filtered to stems mentioning at least one drug name from a 14,000-entry lexicon. |
| `pubmedqa_drug.json` | 512 | Drug-related subset of PubMedQA, three-way yes/no/maybe. Same lexical filter applied to abstracts. |

## Item counts

`evidence.xlsx` contains all **3,961** generated items. The benchmark reported in
the paper is the **3,772** items that pass the automated quality audit
(95.2%); the remaining 189 are retained here so the filtering step is
reproducible rather than hidden.

Per-source counts in this file (pre-filter):

| Source | Items |
|---|---|
| openFDA FAERS | 520 |
| FDA Orange Book | 512 |
| ChEMBL | 508 |
| DrugCentral | 501 |
| LiverTox | 409 |
| PharmGKB | 396 |
| Multi-source | 386 |
| openFDA Label | 381 |
| SIDER | 348 |

## How items were built

For each source database: candidate drugs are sampled by frequency in that
source's own index; a typed query is issued against the live skill and the
returned row is kept as the gold record; a per-source template prompts an LLM to
write a question whose answer is exactly that row; a structural validator checks
that every gold citation resolves to the right database, locator and snippet;
and an LLM auditor scores answer-citation consistency. Gold answers are
therefore machine-extracted from primary regulatory and peer-reviewed records
rather than written by the authors.

## Licence and provenance

Items are derived from public regulatory and peer-reviewed sources (openFDA,
ChEMBL, DrugCentral, PharmGKB/CPIC, SIDER, LiverTox, FDA Orange Book). MedQA
and PubMedQA subsets are filtered from their original public releases and
retain those datasets' original licences. Please cite the original sources
alongside this benchmark.

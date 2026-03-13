# DrugClaw RAG Skills

This document catalogues every RAG skill in DrugClaw, organised by category.
Skills expose 19 of the 171 drug resources in `DrugResource_Full_Survey.xlsx`
through a **unified `RetrievalResult` schema** that feeds directly into the
LangGraph agent pipeline.

---

## Architecture Overview

```
drugclaw/skills/
├── base.py          # RetrievalResult schema · RAGSkill · DatasetRAGSkill
├── registry.py      # SkillRegistry — dispatch hub, skill tree, LLM descriptions
├── skill_tree.py    # SkillTree — 6-domain hierarchy of all 171 resources
├── __init__.py      # build_default_registry() factory
│
├── kg/              # Knowledge Graph skills  (graph nodes + edges, local files)
├── database/        # Database skills         (REST APIs + local structured DBs)
└── dataset/         # Dataset skills          (labelled pairs for QA and eval)
```

### Unified Output Schema — `RetrievalResult`

| Field | Type | Required | Description |
|---|---|---|---|
| `source_entity` | str | ✓ | Source node name |
| `source_type` | str | ✓ | `drug` / `gene` / `disease` / `protein` / `pathway` / … |
| `target_entity` | str | ✓ | Target node name |
| `target_type` | str | ✓ | Same vocabulary as `source_type` |
| `relationship` | str | ✓ | Edge label, e.g. `"treats_disease"`, `"inhibits"` |
| `weight` | float | ✓ | **Always `1.0`** — a retrieved triplet either exists or it doesn't |
| `source` | str | ✓ | Skill name (provenance label) |
| `evidence_text` | str | — | Free-text explanation / abstract snippet |
| `sources` | List[str] | — | Provenance references — any mix of PMIDs (`"PMID:12345"`), URLs, or paper titles |
| `skill_category` | str | — | `KG` / `Database` / `Dataset` |
| `metadata` | dict | — | Any additional key-value pairs |

> **Note on `sources`**: not every resource provides citations. Leave the list
> empty when no provenance is available. Use the prefix `"PMID:"` for PubMed
> IDs, bare URLs for web links, and plain text for paper/dataset titles.

---

## Skill Tree

All **171 resources** from `DrugResource_Full_Survey.xlsx` are catalogued in
`skill_tree.py` as a navigable 6-domain hierarchy:

```
[1] Drug Mechanisms & Pharmacology
    [1a] Drug-Target Interactions   (BindingDB ✓, ChEMBL ✓, DTC ○, …)
    [1b] Drug Mechanisms            (DrugMechDB ✓, MecDDI ○, KEGG ○, …)
    [1c] Drug Classification        (ATC ○, RxNorm ○, UMLS ○, …)

[2] Drug-Disease & Repurposing
    [2a] Drug Indications           (DrugCentral ✓, OpenFDA ✓, DrugBank ○, …)
    [2b] Drug Repurposing           (RepoDB ✓, DrugRepoBank ○, ZINC ○, …)
    [2c] Cancer Pharmacology        (OncoKB ✓, OREGANO ○, CancerDR ○, …)

[3] Drug Safety
    [3a] Adverse Drug Reactions     (SIDER ✓, FAERS ✓, VigiAccess ○, …)
    [3b] Drug-Drug Interactions     (DDInter ○, DrugBank DDI ○, …)
    [3c] Toxicity                   (ToxCast ○, DILIrank ○, Tox21 ○, …)

[4] Genomics, Omics & Pharmacogenomics
    [4a] Pharmacogenomics           (PharmGKB ✓, ClinPGx ○, PharmKG ✓)
    [4b] Gene-Disease Associations  (DisGeNET ✓, CTD ✓, ROBOKOP ○, …)
    [4c] Omics Drug Response        (LINCS L1000 ○, CMap ○, GDSC ○, …)

[5] Clinical Evidence & Literature
    [5a] Clinical Trials            (ClinicalTrials ✓, TrialPanorama ○)
    [5b] Clinical EHR/NLP           (MIMIC ○, DrugEHRQA ○, n2c2 ○, …)
    [5c] Literature & Text Mining   (PubChem ✓, PubMed PMC ○, SemMedDB ○, …)

[6] Integrative Knowledge Graphs
    [6a] Heterogeneous KGs          (UniD3 ✓, Hetionet ✓, DRKG ✓, PrimeKG ✓)
    [6b] Domain-Specific KGs        (PharmKG ✓, STITCH ○, ROBOKOP ○, …)
    [6c] Biomedical Ontologies      (UMLS ○, SemMedDB ○, Monarch ○, …)
```

`✓` = implemented and registered   `○` = catalogued, not yet wired up

The `SkillRegistry` exposes the tree via:

```python
# Full tree for LLM system prompt (shows all 171 resources with ✓/○)
registry.skill_tree_prompt

# Compact one-liner per registered skill
registry.skill_tree_compact

# Keyword-match → relevant registered skills
registry.get_skills_for_query("adverse drug reaction side effects")
# → ['SIDER', 'FAERS', 'DisGeNET', ...]
```

The `RetrieverAgent` injects `skill_tree_prompt` into its system prompt and
uses `get_skills_for_query(query)` to give the LLM a pre-filtered suggestion
list before asking it to write the full `query_plan`.

`RetrievalResult.to_dict()` produces the exact format consumed by
`agent_retriever._build_subgraph()`.  The downstream `RerankerAgent` then
applies its own semantic + structural scoring on top of the retrieved edges.

---

## Category 1 — Knowledge Graph (KG)

Structured graph data with typed nodes and directed edges.
Most KG skills load local files; `DrugMechDB` can auto-fetch from GitHub.

| Skill | Source | Access | Covers |
|---|---|---|---|
| **UniD3** | UniD3 GraphML | Local files | DDI / Drug-Enzyme / Drug-Target (6 graphs: L1/L2 × DDM/DEA/DTA) |
| **DrugMechDB** | [SuLab/DrugMechDB](https://github.com/SuLab/DrugMechDB) | Auto-download or local JSON | Drug→Target→Pathway→Disease mechanism paths |
| **Hetionet** | [hetio/hetionet](https://github.com/hetio/hetionet) | Local TSV | Drug–Gene–Disease–Pathway–Anatomy (24 metaedge types) |
| **DRKG** | [gnn4dr/DRKG](https://github.com/gnn4dr/DRKG) | Local TSV | Multi-relational KG (DrugBank+Hetionet+STRING+GNBR+IntAct+DGIdb) |
| **PrimeKG** | [mims-harvard/PrimeKG](https://github.com/mims-harvard/PrimeKG) | Local CSV | Precision Medicine KG (10 entity types, 18 relation types) |
| **PharmKG** | [MindRank-Biotech/PharmKG](https://github.com/MindRank-Biotech/PharmKG) | Local TSV | Drug–Gene–Disease triplets (500k+) |

### Configuration

```python
# config.py → SKILL_CONFIGS
"DrugMechDB": {
    "local_path": "",        # leave empty to auto-fetch from GitHub
    "fetch_remote": True,
},
"Hetionet": {
    "node_tsv": "/data/hetionet/nodes.tsv",
    "edge_tsv": "/data/hetionet/edges.tsv",
},
"DRKG":    {"drkg_tsv":  "/data/drkg/drkg.tsv"},
"PrimeKG": {"edge_csv":  "/data/primekg/kg.csv"},
"PharmKG": {"train_tsv": "/data/pharmkg/train.tsv"},
```

UniD3 paths are inherited from `config.KG_ENDPOINTS['unid3']`.

---

## Category 2 — Database

Curated databases accessed via public REST APIs or local structured files.

### Public REST APIs — no key required

| Skill | Database | Covers |
|---|---|---|
| **ChEMBL** | [ChEMBL](https://www.ebi.ac.uk/chembl/) | Drug–target bioactivity (IC50, Ki, EC50, 14 k+ targets) |
| **ClinicalTrials** | [ClinicalTrials.gov](https://clinicaltrials.gov/) | Drug–disease clinical study records (phase, status, outcome) |
| **OpenFDA** | [openFDA](https://open.fda.gov/) | FDA drug labels: indications, ADRs, drug interactions |
| **CTD** | [CTD](https://ctdbase.org/) | Chemical–Gene–Disease interactions (curated + inferred) |
| **PharmGKB** | [PharmGKB](https://www.pharmgkb.org/) | Pharmacogenomics drug–gene–variant PGx relationships |
| **DrugCentral** | [DrugCentral](https://drugcentral.org/) | Approved drug indications and targets |
| **PubChem** | [PubChem](https://pubchem.ncbi.nlm.nih.gov/) | Bioassay activity, pathways |
| **BindingDB** | [BindingDB](https://www.bindingdb.org/) | Drug–protein binding affinities (Ki, Kd, IC50, EC50) |
| **DisGeNET** | [DisGeNET](https://www.disgenet.org/) | Gene–Disease associations with GDA evidence |

### Requires free API key

| Skill | Database | How to get key |
|---|---|---|
| **OncoKB** | [OncoKB](https://www.oncokb.org/) | [Register free](https://www.oncokb.org/account/register) — set `config['api_token']` |

### Local file — requires download

| Skill | Database | Download | Covers |
|---|---|---|---|
| **SIDER** | [SIDER 4.1](http://sideeffects.embl.de/) | [sideeffects.embl.de](http://sideeffects.embl.de/) | Drug–side effect pairs from approved drug labels |

### Configuration

```python
"ChEMBL":         {"timeout": 20},
"ClinicalTrials": {"timeout": 15, "max_per_call": 10},
"OpenFDA":        {"api_key": "", "timeout": 15},   # key optional
"CTD":            {"timeout": 20},
"DisGeNET":       {"api_key": "", "timeout": 20},   # free key → higher rate limit
"PharmGKB":       {"timeout": 20},
"DrugCentral":    {"timeout": 20},
"PubChem":        {"timeout": 20},
"BindingDB":      {"timeout": 20},
"OncoKB":         {"api_token": "<your_token>", "timeout": 20},
"SIDER": {
    "se_tsv":         "/data/sider/meddra_all_se.tsv",
    "name_to_stitch": {},   # optional {drug_name_lower: stitch_id} map
},
```

---

## Category 3 — Dataset

Labelled datasets of drug–disease (or drug–AE) pairs.  They act as RAG
evidence sources just like any other skill.

| Skill | Dataset | Download | Covers | Labels |
|---|---|---|---|---|
| **RepoDB** | [RepoDB](https://unmtid-shinyapps.net/shiny/repodb/) | unmtid-shinyapps.net | Drug–disease repositioning outcomes | Approved / Terminated / Suspended / Withdrawn |
| **FAERS** | [FDA FAERS](https://www.fda.gov/drugs/fda-adverse-event-reporting-system-faers) | fda.gov (quarterly) | Drug–adverse event spontaneous reports | positive (≥ min_reports) |

### Benchmark Evaluation Pattern

Dataset skills provide `get_all_pairs()` to enumerate labelled examples.
When benchmarking on a dataset, **simply exclude it from the registry** so
the pipeline cannot see its ground truth:

```python
from drugclaw.skills import (
    build_default_registry, RepoDBSkill, ChEMBLSkill,
    ClinicalTrialsSkill, DrugMechDBSkill
)

# Build registry WITHOUT RepoDB
registry = build_default_registry(config)
registry.unregister("RepoDB")

# Separately load RepoDB just to get the evaluation pairs
repodb = RepoDBSkill(config={"csv_path": "/data/repodb/repodb.csv"})
eval_pairs = repodb.get_approved_pairs()   # or get_all_pairs()

# Run pipeline on each pair
for pair in eval_pairs:
    result = system.query(
        f"Can {pair['drug']} treat {pair['disease']}?",
        omics_constraints=...
    )
    # compare result against pair['label']
```

The pipeline uses ChEMBL, ClinicalTrials, DrugMechDB, etc. as evidence,
but never sees the RepoDB labels — clean evaluation.

### Configuration

```python
"RepoDB": {
    "csv_path":       "/data/repodb/repodb.csv",
    "include_failed": False,   # True to also surface terminated/withdrawn pairs
},
"FAERS": {
    "csv_path":    "/data/faers/faers_processed.csv",
    "min_reports": 5,
},
```

---

## Adding a New Skill

1. Pick the correct base class:
   - `RAGSkill` → KG or Database skill
   - `DatasetRAGSkill` → labelled dataset (adds `get_all_pairs()`)

2. Create `drugclaw/skills/<category>/<name>_skill.py`:

```python
from ..base import RAGSkill, RetrievalResult
from typing import Any, Dict, List, Optional

class MySkill(RAGSkill):
    name = "MySkill"
    resource_type = "Database"   # or "KG" / "Dataset"
    aim = "Short purpose"
    data_range = "What it covers"

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 50,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        # ... fetch/look up data ...
        return [RetrievalResult(
            source_entity="drugA", source_type="drug",
            target_entity="diseaseB", target_type="disease",
            relationship="treats_disease",
            weight=1.0,              # always 1.0
            source="MySkill",
            skill_category="Database",
        )]
```

3. Export from `skills/<category>/__init__.py`.
4. Import + register in `skills/__init__.py` → `build_default_registry()`.
5. Add a `SKILL_CONFIGS` entry in `config.py`.

---

## SkillRegistry API

```python
registry = SkillRegistry()
registry.register(skill)                     # add a skill
registry.unregister("RepoDB")               # remove (e.g. for benchmark)
registry.list_skills()                       # all names
registry.list_skills(resource_type="KG")    # filter by category
registry.get_skill("ChEMBL")                # ChEMBLSkill instance or None

# Aggregate query → List[Dict] for _build_subgraph
registry.query(
    skill_names=["ChEMBL", "ClinicalTrials"],
    entities={"drug": ["imatinib"], "disease": ["CML"]},
    query="imatinib CML mechanism",
    max_results_per_skill=20,
)

# LLM prompt string (used by RetrieverAgent)
print(registry.kg_database_descriptions)
```

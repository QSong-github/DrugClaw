# DrugClaw — Drug-Specialized Agentic RAG System

A multi-agent agentic RAG system purpose-built for drug knowledge retrieval, reasoning, and synthesis. DrugClaw integrates **68 curated LLM-friendly drug resources** across **15 drug-specific subcategories**, distinguishing it from general-purpose biomedical RAG systems.

## Overview

DrugClaw implements an iterative, evidence-driven agentic pipeline powered by LangGraph. Five specialized agents collaborate to retrieve, rank, synthesize, and evaluate drug knowledge — covering drug-target interactions (DTI), adverse drug reactions (ADR), drug-drug interactions (DDI), drug mechanisms, pharmacogenomics, drug repurposing, and more.

### Why DrugClaw?

| | DrugClaw | General Biomedical RAG |
|---|---|---|
| Knowledge scope | 68 drug-specific resources | Generic biomedical KGs |
| Subcategory routing | 15 drug subcategories | Domain-level only |
| CLI support | ChEMBL, ChEBI, KEGG Drug | Rarely |
| Agent identity | Drug-aware prompts | Generic biomedical prompts |
| Evidence attribution | Distinguishes clinical vs. experimental vs. predicted | Often not differentiated |

### Key Features

- **Drug-Specialized Agents**: All 5 agents are prompted with drug domain awareness (pharmacological plausibility, CYP450, IC50, pharmacogenomics, etc.)
- **68-Resource Skill System**: Covers DTI, ADR, DDI, drug mechanism, drug labeling, drug ontology, drug repurposing, pharmacogenomics, drug toxicity, drug combinations, drug molecular properties, drug-disease associations, drug knowledge bases, drug reviews, and drug NLP datasets
- **CLI-First Access**: ChEMBL (`chembl_webresource_client`), ChEBI (`libchebipy`), KEGG Drug (`bioservices`) — Python package CLI with REST fallback
- **15-Subcategory Skill Tree**: LLM-navigable tree with `✓`/`○` availability markers and `[CLI]`/`[LOCAL_FILE]` access mode tags
- **Iterative Reasoning**: Evidence-driven iteration with reward-based convergence detection
- **Source Attribution**: Evidence explicitly tagged by drug knowledge source and evidence type

## Architecture

```
┌─────────────────────────────────────────┐
│            Drug Query / Question        │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│           Retriever Agent               │
│  - Navigates 15-subcategory Skill Tree  │
│  - Selects relevant drug resources      │
│  - Dispatches to SkillRegistry          │
│  - Builds drug evidence subgraph        │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│           Re-ranker Agent               │
│  - Scores paths by pharmacological      │
│    plausibility and evidence quality    │
│  - Ranks clinical > experimental >      │
│    computational evidence               │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│           Responder Agent               │
│  - Synthesizes drug knowledge paths     │
│  - Generates drug-centric answers       │
│  - Cites specific sources per claim     │
│  - Uses drug terminology (IC50, Ki, etc)│
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│           Reflector Agent               │
│  - Evaluates drug evidence sufficiency  │
│  - Detects gaps: missing ADR/DDI/target │
│  - Computes reward r_k, marginal gain   │
│  - Decides: iterate or finalize         │
└──────────────────┬──────────────────────┘
                   │
           ┌───────┴───────┐
           │               │
           ▼               ▼
      Continue?         Finalize
           │               │
           ▼               ▼
  ┌─────────────┐   ┌──────────────┐
  │ Web Search  │   │ Final Answer │
  │   Agent     │   │ (drug-centric│
  │ (drug-focus)│   │  with sources│
  └──────┬──────┘   └──────────────┘
         │
         └──> Loop back to Retriever
```

## 15 Drug Subcategories

| Subcategory Key | Description | Example Resources |
|---|---|---|
| `dti` | Drug-Target Interaction | ChEMBL, BindingDB, DGIdb, Open Targets |
| `adr` | Adverse Drug Reactions | FAERS, SIDER, nSIDES, ADReCS |
| `drug_knowledgebase` | Drug Encyclopedias & KGs | DrugBank, DrugCentral, IUPHAR, CPIC |
| `drug_mechanism` | Mechanism of Action | DRUGMECHDB |
| `drug_labeling` | FDA Labels & Prescribing Info | OpenFDA, DailyMed, MedlinePlus |
| `drug_ontology` | Drug Classification & Ontology | RxNorm, ATC/DDD, NDF-RT, ChEBI |
| `drug_repurposing` | Drug Repurposing KGs | RepoDB, DRKG, Oregano, RepurposingHub |
| `pharmacogenomics` | PGx Variants & Drug Response | PharmGKB |
| `ddi` | Drug-Drug Interactions | DDInter, KEGG Drug, MecDDI |
| `drug_toxicity` | Drug Toxicity & DILI | LiverTox, DILIrank, UniTox |
| `drug_combination` | Drug Combination Synergy | DrugComb, DrugCombDB, DCDB |
| `drug_molecular_property` | Molecular Properties | GDSC |
| `drug_disease` | Drug-Disease Associations | SemMedDB/SemTyp |
| `drug_review` | Patient Drug Reviews | Drugs.com, WebMD, AskAPatient |
| `drug_nlp` | Drug NLP Datasets | ADE Corpus, DDI Corpus, DrugProt |

## File Structure

```
drugclaw/
├── config.py                # System configuration
├── models.py                # Data models (Entity, Edge, AgentState, etc.)
├── llm_client.py            # LLM API wrapper
├── main_system.py           # LangGraph orchestration (DrugClawSystem)
├── agent_retriever.py       # Retriever agent
├── agent_reranker.py        # Re-ranker agent
├── agent_responder.py       # Responder agent
├── agent_reflector.py       # Reflector agent
├── agent_websearch.py       # Web search agent (drug-focused)
├── query_logger.py          # Query session logging
└── skills/
    ├── base.py              # RAGSkill, CLISkillMixin, AccessMode
    ├── registry.py          # SkillRegistry
    ├── skill_tree.py        # 15-subcategory Skill Tree
    ├── dti/                 # Drug-target interaction skills
    ├── adr/                 # Adverse drug reaction skills
    ├── drug_knowledgebase/  # Drug encyclopedia skills
    ├── drug_mechanism/      # Drug mechanism skills
    ├── drug_labeling/       # Drug labeling skills
    ├── drug_ontology/       # Drug ontology skills
    ├── drug_repurposing/    # Drug repurposing skills
    ├── pharmacogenomics/    # Pharmacogenomics skills
    ├── ddi/                 # Drug-drug interaction skills
    ├── drug_toxicity/       # Drug toxicity skills
    ├── drug_combination/    # Drug combination skills
    ├── drug_molecular_property/
    ├── drug_disease/
    ├── drug_review/
    └── drug_nlp/
```

## Installation

```bash
pip install langgraph openai

# Optional CLI packages (enable CLI-first access for 3 skills)
pip install chembl_webresource_client  # ChEMBL
pip install libchebipy                 # ChEBI
pip install bioservices                # KEGG Drug
```

## Configuration

Create an API key file:

```json
{
  "OPENAI_API_KEY": "your-api-key-here",
  "base_url": "https://your-navigator-endpoint.com/v1"
}
```

Update `config.py` to point to your key file and configure local file paths for `LOCAL_FILE` skills (DrugBank, SIDER, FAERS, etc.).

## Usage

### Basic Example

```python
from drugclaw.config import Config
from drugclaw.main_system import DrugClawSystem

config = Config()
system = DrugClawSystem(config)

result = system.query("What are the known drug targets and adverse effects of imatinib?")
print(result['answer'])
```

### With Biological Constraints

```python
from drugclaw.models import OmicsConstraints

constraints = OmicsConstraints(
    gene_sets=['BCR', 'ABL1', 'KIT'],
    pathway_sets=['Tyrosine kinase signaling'],
    disease_terms=['Chronic myeloid leukemia']
)

result = system.query(
    "Which drugs could be repurposed for CML with minimal DDI risk?",
    omics_constraints=constraints
)
```

### Programmatic Skill Access

```python
from drugclaw.skills import build_default_registry

registry = build_default_registry(config)

# Query specific subcategory
results = registry.query(
    skill_names=['ChEMBL', 'BindingDB', 'DGIdb'],
    entities={'drug': ['imatinib']},
    query='imatinib drug targets',
    max_results_per_skill=10
)

# List skills by subcategory
dti_skills = registry.list_by_subcategory('dti')
cli_skills  = registry.list_by_access_mode('CLI')
```

## Agent Details

### 1. Retriever Agent
- **Identity**: Drug knowledge navigator across 15 subcategories
- **Input**: Drug query + omics constraints
- **Output**: Drug evidence subgraph (drug–target, drug–disease, drug–gene edges)
- **Tools**: 68 drug resources via SkillRegistry with subcategory routing

### 2. Re-ranker Agent
- **Identity**: Pharmacological evidence evaluator
- **Input**: Drug evidence subgraph
- **Output**: Ranked paths prioritizing clinical > experimental > computational evidence
- **Scoring**: `α × semantic_relevance + β × structural_importance`

### 3. Responder Agent
- **Identity**: Drug knowledge synthesizer
- **Input**: Top-ranked drug evidence paths
- **Output**: Drug-centric answer with source attribution and pharmacological terminology
- **Format**: Adapts to query type — mechanism, repurposing, ADR lookup, DDI check, etc.

### 4. Reflector Agent
- **Identity**: Drug evidence sufficiency evaluator
- **Input**: Current answer, drug evidence subgraph, iteration history
- **Output**: Sufficiency score, reward `r_k`, marginal gain `Δr_k`, continuation decision
- **Drug-specific gaps**: Flags missing target affinity, absent ADR records, no DDI evidence
- **Stopping**: `E_s ≥ 0.7 AND Δr_k < ε`

### 5. Web Search Agent
- **Identity**: Drug literature supplementor
- **Trigger**: Insufficient structured evidence + low marginal gain
- **Scope**: Drug-focused — PubMed pharmacology, FDA updates, clinical trial drug arms
- **Output**: Recent drug research with evidence level classification

## Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_ITERATIONS` | 10 | Maximum reasoning iterations |
| `EVIDENCE_THRESHOLD_EPSILON` | 0.1 | Minimum marginal gain to continue |
| `MIN_EVIDENCE_SCORE` | 0.7 | Threshold for evidence sufficiency |
| `MAX_SUBGRAPH_SIZE` | 100 | Max entities in evidence graph |
| `SEMANTIC_WEIGHT` | 0.6 | Weight for semantic scoring |
| `STRUCTURAL_WEIGHT` | 0.4 | Weight for structural scoring |

## Adding a New Drug Skill

```python
# drugclaw/skills/<subcategory>/<name>_skill.py
from drugclaw.skills.base import RAGSkill, AccessMode, RetrievalResult

class MyDrugDBSkill(RAGSkill):
    name = "MyDrugDB"
    subcategory = "dti"           # one of the 15 subcategory keys
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    description = "My drug-target database"

    def is_available(self) -> bool:
        return True

    def retrieve(self, entities, query="", max_results=50):
        # call your API, return List[RetrievalResult]
        ...
```

Then register it in `drugclaw/skills/__init__.py` under the appropriate subcategory block.

## Theory

### Evidence Sufficiency
At iteration `k`, the Reflector evaluates:
```
E_s(q0, G_k, a_k) → [0, 1]
```
Where `q0` = original drug query, `G_k` = drug evidence subgraph at iteration k, `a_k` = intermediate answer.

### Convergence Criterion
```
Δr_k = r_k - r_{k-1} < ε
```
Iteration stops when evidence is sufficient (`E_s ≥ 0.7`) and marginal gain is below threshold.

### Minimal Sufficient Drug Evidence
The system extracts `G_q*`: the minimal drug knowledge subgraph that is sufficient, mechanistically interpretable, and pruned of redundant or low-confidence evidence.

## Troubleshooting

**Empty results from a skill**: Check `skill.is_available()` — `LOCAL_FILE` skills require local data paths configured in `config.py`.

**LLM not generating valid JSON**: Lower temperature to 0.1–0.3 for structured outputs; `llm_client.generate_json()` has fallback parsing.

**Iteration not converging**: Lower `EVIDENCE_THRESHOLD_EPSILON` or increase `MAX_ITERATIONS`; check Reflector agent prompts.

**CLI skill not using CLI path**: Install the optional package (`chembl_webresource_client`, `libchebipy`, or `bioservices`); `CLISkillMixin` auto-detects via `importlib`.

## License

MIT License

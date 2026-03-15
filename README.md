# DrugClaw — Drug-Specialized Agentic RAG System

A multi-agent agentic RAG system purpose-built for drug knowledge retrieval, reasoning, and synthesis. DrugClaw integrates **68 curated LLM-friendly drug resources** across **15 drug-specific subcategories**, with **25 fully implemented skills** and a vibe-coding Code Agent architecture.

## Overview

DrugClaw implements an iterative, evidence-driven agentic pipeline powered by LangGraph. Six specialized agents collaborate to retrieve, rank, synthesize, and evaluate drug knowledge — covering drug-target interactions (DTI), adverse drug reactions (ADR), drug-drug interactions (DDI), drug mechanisms, pharmacogenomics, drug repurposing, and more.

### Key Features

- **Vibe-Coding Retrieval**: Each skill has its own standalone example code (`example.py`) and description (`SKILL.md`). The Code Agent reads these and writes custom query code per skill — no rigid schema required.
- **25 Implemented Skills**: Fully working skills with example code, covering REST API, CLI, LOCAL_FILE, and DATASET access modes.
- **43 Stub Skills**: Interface preserved for future development; not registered in the default registry.
- **Code Agent**: LLM writes and executes Python code to query each skill in its natural API style.
- **Graph Build Agent**: LLM-driven triple extraction from retrieval results (replaces rigid subgraph assembly).
- **15-Subcategory Skill Tree**: LLM-navigable tree with `✓`/`○` availability markers.
- **Three Thinking Modes**: GRAPH (iterative multi-agent), SIMPLE (one-shot), WEB_ONLY (live search).

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
│  - Extracts key entities                │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│           Code Agent (NEW)              │
│  - Reads skill's example.py + SKILL.md │
│  - Writes custom Python query code     │
│  - Executes and captures results       │
└──────────────────┬──────────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
   ┌────────────┐   ┌────────────────┐
   │ SIMPLE mode│   │  GRAPH mode    │
   │ Direct to  │   │ Graph Builder  │
   │ Responder  │   │ → Reranker     │
   └─────┬──────┘   │ → Responder    │
         │          │ → Reflector    │
         │          └───────┬────────┘
         │                  │
         ▼                  ▼
   ┌──────────────────────────────┐
   │        Final Answer          │
   │   (drug-centric with sources)│
   └──────────────────────────────┘
```

## Implemented Skills (25)

| Category | Skill | Access Mode | Description |
|---|---|---|---|
| **DTI** | ChEMBL | CLI | Bioactivity data (IC50/Ki/EC50) |
| | BindingDB | REST_API | Binding affinity data |
| | DGIdb | REST_API | Drug–gene interactions |
| | Open Targets | REST_API | Drug-target evidence scores |
| | TTD | LOCAL_FILE | Therapeutic target database |
| | STITCH | REST_API | Chemical–protein interactions |
| **ADR** | FAERS | REST_API | FDA adverse event reports |
| | SIDER | LOCAL_FILE | Drug side effects from labels |
| **Knowledgebase** | UniD3 | LOCAL_FILE | Drug discovery KG (GraphML) |
| | DrugBank | REST_API | Comprehensive drug reference |
| | IUPHAR | REST_API | Pharmacology reference |
| | DrugCentral | REST_API | FDA-approved drug info |
| | CPIC | REST_API | Clinical pharmacogenomics |
| **Mechanism** | DRUGMECHDB | REST_API | Mechanism-of-action paths |
| **Labeling** | openFDA | REST_API | FDA drug label search |
| | DailyMed | REST_API | NIH drug labeling |
| | MedlinePlus | REST_API | Patient drug information |
| **Ontology** | RxNorm | REST_API | Drug name normalization |
| | ChEBI | CLI | Chemical entity ontology |
| **Repurposing** | RepoDB | DATASET | Drug repositioning outcomes |
| **PGx** | PharmGKB | REST_API | Pharmacogenomics knowledge |
| **DDI** | MecDDI | LOCAL_FILE | Mechanistic DDI database |
| | DDInter | REST_API | DDI with clinical evidence |
| | KEGG Drug | CLI | Drug interactions with pathway context |
| **Review** | WebMD Reviews | DATASET | Patient drug reviews |

Plus **WebSearch** (DuckDuckGo + PubMed, always-on).

## Skill Directory Structure

Each implemented skill has its own self-contained directory:

```
skills/dti/chembl/
├── __init__.py
├── chembl_skill.py      # RAGSkill class (metadata + retrieve)
├── example.py           # Standalone query code (for Code Agent)
├── SKILL.md             # Skill description (for Code Agent)
└── README.md            # Developer notes
```

The **Code Agent** reads `SKILL.md` and `example.py` to understand how to query the skill, then writes custom Python code for the specific entities being queried.

## 15 Drug Subcategories

| Key | Description | Implemented / Total |
|---|---|---|
| `dti` | Drug-Target Interaction | 6 / 10 |
| `adr` | Adverse Drug Reactions | 2 / 5 |
| `drug_knowledgebase` | Drug Encyclopedias & KGs | 5 / 9 |
| `drug_mechanism` | Mechanism of Action | 1 / 1 |
| `drug_labeling` | FDA Labels & Prescribing Info | 3 / 4 |
| `drug_ontology` | Drug Classification & Ontology | 2 / 4 |
| `drug_repurposing` | Drug Repurposing KGs | 1 / 9 |
| `pharmacogenomics` | PGx Variants & Drug Response | 1 / 1 |
| `ddi` | Drug-Drug Interactions | 3 / 3 |
| `drug_toxicity` | Drug Toxicity & DILI | 0 / 4 |
| `drug_combination` | Drug Combination Synergy | 0 / 4 |
| `drug_molecular_property` | Molecular Properties | 0 / 1 |
| `drug_disease` | Drug-Disease Associations | 0 / 1 |
| `drug_review` | Patient Drug Reviews | 1 / 3 |
| `drug_nlp` | Drug NLP Datasets | 0 / 9 |

## File Structure

```
DrugClaw_V1.0/
├── drugclaw/
│   ├── config.py                # System configuration
│   ├── models.py                # Data models (AgentState, ThinkingMode, etc.)
│   ├── llm_client.py            # LLM API wrapper
│   ├── main_system.py           # LangGraph orchestration
│   ├── agent_retriever.py       # Retriever agent (skill selection)
│   ├── agent_coder.py           # Code agent (writes query code)
│   ├── agent_graph_builder.py   # Graph builder agent (triple extraction)
│   ├── agent_reranker.py        # Re-ranker agent
│   ├── agent_responder.py       # Responder agent
│   ├── agent_reflector.py       # Reflector agent
│   ├── agent_websearch.py       # Web search agent
│   ├── query_logger.py          # Query session logging
│   └── skills -> ../skills      # Symlink to skills package
├── skills/
│   ├── base.py                  # RAGSkill, CLISkillMixin, AccessMode
│   ├── registry.py              # SkillRegistry
│   ├── skill_tree.py            # 15-subcategory Skill Tree
│   ├── dti/                     # Drug-target interaction skills
│   ├── adr/                     # Adverse drug reaction skills
│   ├── drug_knowledgebase/      # Drug encyclopedia skills
│   ├── drug_mechanism/          # Drug mechanism skills
│   ├── drug_labeling/           # Drug labeling skills
│   ├── drug_ontology/           # Drug ontology skills
│   ├── drug_repurposing/        # Drug repurposing skills
│   ├── pharmacogenomics/        # Pharmacogenomics skills
│   ├── ddi/                     # Drug-drug interaction skills
│   ├── drug_toxicity/           # Drug toxicity skills (stubs)
│   ├── drug_combination/        # Drug combination skills (stubs)
│   ├── drug_molecular_property/ # (stub)
│   ├── drug_disease/            # (stub)
│   ├── drug_review/             # Drug review skills
│   ├── drug_nlp/                # Drug NLP skills (stubs)
│   └── web_search/              # WebSearch skill
├── skillexamples/               # Original standalone skill examples
├── resources_metadata/          # Local data files
├── example_usage.py             # Usage examples
└── README.md
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

Update `drugclaw/config.py` to point to your key file. For `LOCAL_FILE` skills (TTD, SIDER, MecDDI, etc.), configure the data paths in `SKILL_CONFIGS`.

Local data files should be placed under `resources_metadata/` following the subcategory structure:
```
resources_metadata/
├── drug_knowledgebase/UniD3/       # GraphML files
├── drug_knowledgebase/DrugBank/    # XML + CSV
├── drug_repurposing/RepoDB/        # full.csv
├── adr/SIDER/                      # meddra_all_se.tsv
├── dti/TTD/                        # TTD flat files
├── ddi/MecDDI/                     # MecDDI CSV
└── ...
```

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

### Three Thinking Modes

```python
from drugclaw.models import ThinkingMode

# GRAPH mode — full multi-agent reasoning (default)
result = system.query("...", thinking_mode=ThinkingMode.GRAPH)

# SIMPLE mode — one-shot retrieval + direct synthesis
result = system.query("...", thinking_mode=ThinkingMode.SIMPLE)

# WEB_ONLY mode — DuckDuckGo + PubMed only
result = system.query("...", thinking_mode=ThinkingMode.WEB_ONLY)
```

### With Resource Filter

```python
# Only query specific skills (bypasses LLM skill selection)
result = system.query(
    "What are the adverse effects of aspirin?",
    resource_filter=["FAERS", "SIDER"],
)
```

### Programmatic Skill Access

```python
from skills import build_default_registry

class DummyConfig:
    SKILL_CONFIGS = {}
    KG_ENDPOINTS = {}

registry = build_default_registry(DummyConfig())

# List all available skills
print(registry.get_all_skill_summaries())

# Get skill info for Code Agent
info = registry.get_skill_info_for_coder("ChEMBL")

# Query specific skills
results = registry.query(
    skill_names=['ChEMBL', 'DGIdb'],
    entities={'drug': ['imatinib']},
    query='imatinib drug targets',
)
```

## Adding a New Skill

1. Create the skill directory under the appropriate subcategory:
```
skills/<subcategory>/<name>/
├── __init__.py
├── <name>_skill.py     # RAGSkill class
├── example.py           # Standalone query code
└── SKILL.md             # Skill description for Code Agent
```

2. Implement the RAGSkill class with `_implemented = True`:
```python
from ...base import RAGSkill, AccessMode, RetrievalResult

class MyDrugDBSkill(RAGSkill):
    name = "MyDrugDB"
    subcategory = "dti"
    resource_type = "Database"
    access_mode = AccessMode.REST_API
    aim = "My drug-target database"
    data_range = "Drug-target pairs from MyDrugDB"
    _implemented = True

    def retrieve(self, entities, query="", max_results=50, **kwargs):
        # Your retrieval logic
        ...
```

3. Write `example.py` — a self-contained script showing how to query the resource.

4. Write `SKILL.md` — description of the API, functions, and usage patterns.

5. Register in `skills/__init__.py` → `build_default_registry()`.

## License

MIT License

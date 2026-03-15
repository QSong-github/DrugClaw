# DrugClaw

<p align="center">
  <img src="./support/DrugClaw_Logo.png" alt="DrugClaw Logo" width="520" />
</p>

<p align="center">
  <strong>Agentic RAG for Drug Knowledge Retrieval, Reasoning, and Evidence Synthesis</strong>
</p>

<p align="center">
  <a href="./README_CN.md">中文文档 / Chinese Version</a>
</p>

<p align="center">
  <img alt="Domain" src="https://img.shields.io/badge/Domain-Drug%20Intelligence-1f6feb">
  <img alt="Resources" src="https://img.shields.io/badge/Resources-68%20Curated-0a7f5a">
  <img alt="Skills" src="https://img.shields.io/badge/Implemented%20Skills-25-f59e0b">
  <img alt="Modes" src="https://img.shields.io/badge/Modes-GRAPH%20%7C%20SIMPLE%20%7C%20WEB__ONLY-7c3aed">
</p>

DrugClaw is a drug-centered multi-agent RAG system designed for queries that generic assistants often handle poorly: drug targets, adverse drug reactions, drug-drug interactions, mechanisms of action, pharmacogenomics, repurposing, and evidence synthesis across heterogeneous biomedical resources.

It is not a generic RAG stack with a biomedical prompt on top. DrugClaw is opinionated around drug-native tasks from resource organization to retrieval strategy, reasoning flow, and final answer structure.

## Why DrugClaw

Most biomedical QA systems stop at "retrieve a few passages and summarize them." Drug questions are harder: they require precise handling of target evidence, ADR provenance, DDI mechanisms, labeling details, and PGx constraints. Some tools connect many databases but flatten them into a single rigid interface; others optimize for conversational UX while relying on weak, thin, or poorly traceable evidence.

- Organizes **68 curated drug resources** into a navigable **15-subcategory skill tree**
- Uses a **Code Agent** to query each source in its native style instead of forcing one rigid abstraction
- Supports **graph-based reasoning** for multi-hop evidence synthesis
- Keeps **Web Search** as a fallback for recent literature and external evidence
- Built around **drug-native tasks**, not generic biomedical branding

In short, DrugClaw is not trying to be just another fluent assistant. Its goal is to raise resource density, retrieval fidelity, and evidence-grounded reasoning at the same time.

## Quick Start

### 1. Install dependencies

```bash
cd /data/boom/Agent/DrugClaw
pip install langgraph openai
```

Optional dependencies for selected CLI-based skills:

```bash
pip install chembl_webresource_client
pip install libchebipy
pip install bioservices
```

### 2. Prepare `navigator_api_keys.json`

First copy the template:

```bash
cp navigator_api_keys.example.json navigator_api_keys.json
```

Then fill in your real credentials:

```json
{
  "OPENAI_API_KEY": "your-api-key-here",
  "base_url": "https://your-endpoint.com/v1"
}
```

DrugClaw currently resolves keys in this order:

- `DRUGCLAW_KEY_FILE`
- `navigator_api_keys.json` in the repository root

### 3. Prepare local resources under `resources_metadata/`

Many skills use `LOCAL_FILE` access mode. Those resources must exist under the local `resources_metadata/` tree rather than being assumed online.

Recommended resolution order:

- Use files already present under `resources_metadata/...`
- If missing, sync from the maintained mirror first
- Only fall back to the original source site if the mirror does not contain the data

Maintained mirror:

- `https://huggingface.co/datasets/Mike2481/DrugClaw_resources_data`

Directory examples:

- `resources_metadata/dti/...`
- `resources_metadata/adr/...`
- `resources_metadata/drug_knowledgebase/...`
- `resources_metadata/drug_repurposing/...`
- `resources_metadata/ddi/...`

If some old `SKILL.md`, `example.py`, or archived docs still show absolute paths, treat them as legacy examples. The active convention is the repository-local `resources_metadata/...` layout.

### 4. Run the official CLI demo

This is the recommended first experience. You can run it without installation:

```bash
python -m drugclaw list
python -m drugclaw doctor
python -m drugclaw demo
```

The default demo uses:

- `SIMPLE` mode
- online labeling-style resources
- a metformin labeling and safety query

You can also run your own query:

```bash
python -m drugclaw run --query "What are the known drug targets of imatinib?"
```

### 5. Install the `drugclaw` command

```bash
pip install -e . --no-build-isolation
git config core.hooksPath .githooks
drugclaw list
drugclaw doctor
drugclaw demo
drugclaw run --query "What are the known drug targets of imatinib?"
```

### 6. Compatibility shortcut: `run_minimal.py`

This script now acts as a lightweight shortcut to the demo flow:

```bash
python run_minimal.py
```

You can also pass CLI arguments through it:

```bash
python run_minimal.py demo --preset label
python run_minimal.py run --query "What prescribing and safety information is available for metformin?"
```

### 7. Run environment checks first

```bash
python -m drugclaw doctor
```

It checks:

- whether `navigator_api_keys.json` exists and is complete
- whether `langgraph` and `openai` are importable
- whether built-in demo presets have the resources they need
- whether the `drugclaw` command is installed
- whether `navigator_api_keys.json` is still tracked by Git
- whether repository Git hooks are enabled

### 8. Enable secret-protection Git hooks

```bash
git config core.hooksPath .githooks
```

These hooks block:

- committing `navigator_api_keys.json`
- pushing a repository where `navigator_api_keys.json` is still tracked

### 9. List built-in demos and recommended entrypoints

```bash
python -m drugclaw list
```

It shows:

- built-in demo presets
- supported thinking modes
- recommended first commands
- common resource filter combinations

### 10. Call DrugClaw from Python

```python
from drugclaw.config import Config
from drugclaw.main_system import DrugClawSystem
from drugclaw.models import ThinkingMode

config = Config(key_file="navigator_api_keys.json")
system = DrugClawSystem(config)

result = system.query(
    "What prescribing and safety information is available for metformin?",
    thinking_mode=ThinkingMode.SIMPLE,
    resource_filter=["DailyMed", "openFDA Human Drug", "MedlinePlus Drug Info"],
)

print(result["answer"])
```

### 11. Thinking modes

```python
from drugclaw.models import ThinkingMode

system.query("...", thinking_mode=ThinkingMode.GRAPH)
system.query("...", thinking_mode=ThinkingMode.SIMPLE)
system.query("...", thinking_mode=ThinkingMode.WEB_ONLY)
```

## Highlights

<p align="center">
  <img src="./support/DrugClaw.png" alt="DrugClaw Overview" width="760" />
</p>

### 1. Vibe-coding retrieval

Each skill ships with its own `SKILL.md` and `example.py`. The Code Agent reads both, learns the source's native usage pattern, and generates query code dynamically for the current task.

That means DrugClaw does not require every database, API, or dataset to pretend to be the same thing.

For `LOCAL_FILE` skills, the recommended default behavior is:

- check `resources_metadata/...` first
- if missing, guide the user to the maintained Hugging Face mirror
- do not assume the original download endpoint is still reliable

### 2. Organized around drug tasks

DrugClaw currently provides **25 implemented skills** across:

- drug targets and activity
- adverse drug reactions and pharmacovigilance
- drug knowledgebases
- mechanisms of action
- labeling and prescribing information
- ontology and normalization
- drug repurposing
- pharmacogenomics
- drug-drug interactions
- patient reviews

### 3. Three working modes

- `GRAPH`: retrieve -> graph build -> rerank -> respond -> reflect
- `SIMPLE`: retrieve and answer directly
- `WEB_ONLY`: use only online search and literature retrieval

### 4. Built for evidence synthesis

DrugClaw is suitable for questions such as:

- "What are the known targets, adverse effects, and interaction risks of imatinib?"
- "Which approved drugs may be repurposed for triple-negative breast cancer?"
- "What pharmacogenomic guidance exists for clopidogrel and CYP2C19?"
- "Are there clinically meaningful interactions between warfarin and NSAIDs?"

## Architecture

```text
User Query
   |
   v
Retriever Agent
   |- navigates the 15-subcategory skill tree
   |- extracts key entities
   |- selects relevant resources
   |
   v
Code Agent
   |- reads SKILL.md + example.py
   |- writes custom query code
   |- executes resource-specific retrieval
   |
   +--> SIMPLE mode --> Responder --> Final Answer
   |
   +--> GRAPH mode
         -> Graph Builder
         -> Reranker
         -> Responder
         -> Reflector
         -> optional Web Search
         -> Final Answer
```

## Implemented Skills

| Category | Skills |
| --- | --- |
| DTI | ChEMBL, BindingDB, DGIdb, Open Targets Platform, TTD, STITCH |
| ADR | FAERS, SIDER |
| Drug Knowledgebase | UniD3, DrugBank, IUPHAR/BPS Guide to Pharmacology, DrugCentral, CPIC |
| Drug Mechanism | DRUGMECHDB |
| Drug Labeling | openFDA Human Drug, DailyMed, MedlinePlus Drug Info |
| Drug Ontology | RxNorm, ChEBI |
| Drug Repurposing | RepoDB |
| Pharmacogenomics | PharmGKB |
| DDI | MecDDI, DDInter, KEGG Drug |
| Reviews | WebMD Drug Reviews |

`WebSearch` is also available as an external retrieval supplement built around DuckDuckGo + PubMed style search.

## Repository Layout

```text
drugclaw/
  config.py
  main_system.py
  llm_client.py
  agent_retriever.py
  agent_coder.py
  agent_graph_builder.py
  agent_reranker.py
  agent_responder.py
  agent_reflector.py
  agent_websearch.py

skills/
  <subcategory>/<skill_name>/
    *_skill.py
    example.py
    SKILL.md
    README.md

resources_metadata/
  local data files
```

## Differentiation

### Resource-native querying instead of forced abstraction

DrugClaw does not require every biomedical source to be flattened into a single interface.

### Graph reasoning instead of flat summarization

DrugClaw can turn free-form retrieval results into triples, subgraphs, ranked paths, and evidence-aware answers rather than simply stitching together excerpts.

### Drug-first scope instead of generic biomedical positioning

This system is built around drug tasks: DTI, ADR, DDI, labeling, repurposing, PGx, and mechanism reasoning.

## Current Notes

- The repository can be imported directly from the project root.
- `pyproject.toml` is now aligned with the current package layout for local CLI usage.
- Some skills still depend on local files under `resources_metadata/`.
- Multi-iteration `GRAPH` behavior still depends on further configuration such as `MAX_ITERATIONS`.

## Citation

If you use DrugClaw in research or product work, cite this repository and the upstream resources used by the selected skills.

## License

MIT License

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
  <em>Resource bundle will be released upon acceptance.</em>
</p>

<p align="center">
  <img alt="Domain" src="https://img.shields.io/badge/Domain-Drug%20Intelligence-1f6feb">
  <img alt="Registry" src="https://img.shields.io/badge/Registry-Source%20of%20Truth-0a7f5a">
  <img alt="Skills" src="https://img.shields.io/badge/Skills-Registry%20Driven-f59e0b">
  <img alt="Modes" src="https://img.shields.io/badge/Modes-GRAPH%20%7C%20SIMPLE%20%7C%20WEB__ONLY-7c3aed">
</p>

DrugClaw is a CLI and agent runtime for drug-focused questions. It prioritizes evidence-grounded retrieval, source attribution, and traceability over answers that only sound fluent.

## Why DrugClaw

- It is not a general chat assistant. It is built for real drug questions such as targets, indications, repurposing, safety, DDIs, PGx, and labeling.
- It aims to return structured evidence and source-grounded conclusions, not just a polished summary.
- It supports both a lightweight minimal mode and a deeper full local-resource mode.

## Get Started in 5 Minutes

If this is your first time using DrugClaw, follow the steps below and you should be able to run a real query quickly.

### 1. Clone the repository

```bash
git clone https://anonymous.4open.science/r/DrugClaw-01A3
cd DrugClaw
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Create `api_keys.json`

DrugClaw reads `api_keys.json` from the repository root by default. If you do not want to pass `--key-file`, put the config file at the repository root.

Create the file and provide at least these fields:

```json
{
  "api_key": "<your-api-key>",
  "base_url": "<your-base-url>",
  "model": "gpt-5-mini"
}
```

If your config file lives somewhere else, pass it explicitly with `--key-file <path>`.

### 4. Verify the environment

```bash
python -m drugclaw doctor
```

If the setup is valid, you should see something like:

```text
Doctor result: setup looks usable.
```

### 5. Run your first query

```bash
python -m drugclaw run --query "What are the known drug targets of imatinib?"
```

If this works, you already have the minimal usable setup running.

## What DrugClaw Is Good At

- Drug targets and mechanisms
- Indications and repurposing evidence
- Safety risks and serious adverse reactions
- Drug-drug interactions
- Pharmacogenomics
- Labeling and prescribing information

## Common Commands

```bash
python -m drugclaw run --query "What pharmacogenomic factors affect clopidogrel efficacy and safety?"
python -m drugclaw run --query "What are the clinically important drug-drug interactions of warfarin?"
python -m drugclaw list
```

## Two Modes

### Minimal Mode

Minimal mode is the default.

The repository only tracks a minimal `resources_metadata/` subtree. That is enough for the CLI, basic queries, and the default test suite. For most new users, this is the right place to start.

Use minimal mode if you want to:

- try DrugClaw quickly
- run the default queries and tests
- avoid downloading large local resource bundles upfront

### Full Mode

If you need deeper and broader local evidence coverage, the full `resources_metadata_full.tar.gz` bundle will be released upon paper acceptance. Once available, extract it at the repository root:

```bash
tar -xzf resources_metadata_full.tar.gz
```

Recommended flow (once the bundle is released):

1. Download `resources_metadata_full.tar.gz`
2. Extract it at the repository root
3. Run `python -m drugclaw doctor` again

This is not just a generic data add-on. It expands the same `resources_metadata/` tree in place, enables more `LOCAL_FILE` resources, and supports deeper local evidence retrieval.

Use full mode if you want to:

- increase local resource coverage
- enable more local-data-backed resources
- run deeper resource-level validation or analysis

## What To Do Next

- Show available resources and recommended entry points:

```bash
python -m drugclaw list
```

- Re-check your environment:

```bash
python -m drugclaw doctor
```

- Explore the built-in demo flow:

```bash
python -m drugclaw demo
```

## Read More

- Repository guide: `docs/repository-guide.md`
- Maintainer guide: `maintainers/README.md`

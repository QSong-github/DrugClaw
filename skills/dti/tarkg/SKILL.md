---
name: TarKG
description: >
  Query the TarKG drug-target discovery knowledge graph. Use whenever the user
  asks about drug-target interactions, drug repurposing, TCM-Western medicine
  bridging, gene-disease associations, or any entity lookup in TarKG (drugs,
  genes, diseases, pathways, compounds, TCM herbs/formulas). Covers ~100K nodes,
  ~1M edges, 171 relation types.
---

# TarKG – Drug Target Discovery Knowledge Graph

| Item | Detail |
|------|--------|
| Source | <https://tarkg.ddtmlab.org/index> |
| Paper | <https://academic.oup.com/bioinformatics/article/40/10/btae598/7818343> |
| Category | Drug-centric KG · Drug-Target Interaction (DTI) |
| Scale | ~100 K nodes · ~1 M edges · 171 relation types |
| Script | `41_TarKG.py` (same directory as this file) |

## Data location

```
/blue/qsong1/wang.qing/AgentLLM/DrugClaw/resources_metadata/dti/TarKG/
```

Or set env `TARKG_DATA` to override.

## CSV schema

**TarKG_nodes.csv** — `index, unify_id, kind, dbid, db_source, name, source`
  - `unify_id` → node ID (e.g. `TC1`, `P00533`, `CTD:Alcoholism`, `DOID:0050524`)
  - `kind` → node type (Compound, Gene, Disease, Pathway, Biological_Process, Anatomy)
  - `name` → human-readable name

**TarKG_edges.csv** — `index, node1, node1_type, relation, node2, node2_type`
  - `node1`/`node2` → endpoints matching `unify_id` in nodes
  - `relation` → edge type (e.g. `target`, `ppi`, `interacts with`, `is a`, `associated with`)

## First-time setup

```python
from importlib.machinery import SourceFileLoader
tkg = SourceFileLoader("tarkg", "<SKILL_DIR>/41_TarKG.py").load_module()
tkg.build_index()          # builds .tarkg_index.db (one-time)
```

Index auto-rebuilds when schema version changes. To force: `tkg.build_index(force=True)`.

## Python API

```python
# Core: n-hop subgraph from a seed entity
sg = tkg.query_subgraph("TC1", n_hops=1)             # 1-hop from compound TC1
sg = tkg.query_subgraph("TC1", n_hops=2)             # 2-hop expansion
sg = tkg.query_subgraph("CTD:Alcoholism", n_hops=1)  # query by unify_id

# Batch
for name in ["TC1", "P53_HUMAN", "CTD:Alcoholism"]:
    sg = tkg.query_subgraph(name, n_hops=1)

# Search by keyword (optional type filter)
tkg.search_nodes("diabetes", node_type="Disease", limit=10)

# Metadata
tkg.get_stats()            # node/edge counts by type
tkg.get_relation_types()   # all relation strings
tkg.get_node_types()       # all node type strings
```

### Return schema for `query_subgraph`

```json
{
  "seed": "TC1",
  "seed_id": "TC1",
  "matched": true,
  "n_hops": 1,
  "total_nodes": 3,
  "total_edges": 4,
  "nodes": {
    "TC1":         {"node_id": "TC1", "node_name": "Hexatantalum Dodecabromide", "node_type": "Compound", "hop": 0},
    "UBA1_HUMAN":  {"node_id": "UBA1_HUMAN", "node_name": "UBA1_HUMAN", "node_type": "Gene", "hop": 1},
    "KCC2A_HUMAN": {"node_id": "KCC2A_HUMAN", "node_name": "KCC2A_HUMAN", "node_type": "Gene", "hop": 1}
  },
  "edges": [
    {"head_id": "TC1", "head_name": "Hexatantalum Dodecabromide", "relation": "target", "tail_id": "UBA1_HUMAN", "tail_name": "UBA1_HUMAN", "hop": 1},
    {"head_id": "TC1", "head_name": "Hexatantalum Dodecabromide", "relation": "interacts with", "tail_id": "UBA1_HUMAN", "tail_name": "UBA1_HUMAN", "hop": 1}
  ]
}
```

`hop=0` is the seed; `hop=k` means discovered at the k-th BFS expansion.

## Direct run

```bash
python 41_TarKG.py
```

Executes built-in examples: build index → stats → sample nodes → 1-hop → 2-hop → keyword search.

## Node types

Compound, Gene, Disease, Pathway, Biological_Process, Anatomy.

## Sample relation types

`target`, `ppi`, `interacts with`, `associated with`, `is a`,
`negative correlate`, `positive correlate`, `participates_in`, etc. (171 total).

## Design notes

- **SQLite index** auto-built on first query, cached as `.tarkg_index.db`.
  Schema-versioned — auto-rebuilds when code updates column mappings.
- **Smart column mapping**: auto-detects `unify_id`/`name`/`kind`/`node1`/`relation`/`node2`
  from CSV headers, no hardcoded positions.
- **n-hop BFS** via `query_subgraph()`: expands outgoing + incoming edges per hop,
  deduplicates edges, tags each node/edge with its hop distance.
- Entity resolution: exact ID → exact name (case-insensitive) → substring match.
- `max_neighbors_per_hop` (default 50) caps fan-out to prevent explosion on hub nodes.
## CLI Usage (Fallback)

When vibe coding fails, run the skill script directly from the command line:

```bash
python skills/dti/tarkg/tarkg_skill.py <entity1> [entity2] ...
```

**Example:**
```bash
python skills/dti/tarkg/tarkg_skill.py aspirin
```

The script imports functions from the sibling `example.py`, executes the query, and prints LLM-readable results to stdout.

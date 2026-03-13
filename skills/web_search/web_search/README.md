# WebSearch

> **Subcategory**: `web_search` &nbsp;|&nbsp; **Access mode**: `REST API`

**Purpose**: Free web search  
**Coverage**: Real-time web results via DuckDuckGo + PubMed E-utilities

## Setup

No API key required.  Optionally install `duckduckgo-search` for richer results:

```bash
pip install duckduckgo-search
```

## Configuration

| Key | Type / Description |
|-----|--------------------|
| `pubmed_email` | str — contact email for NCBI E-utilities (recommended) |
| `pubmed_api_key` | str — optional NCBI API key (raises rate limit 3→10 req/s) |
| `max_ddg` | int — max DuckDuckGo results per query (default: 5) |
| `max_pubmed` | int — max PubMed results per query (default: 5) |
| `timeout` | int — HTTP timeout in seconds (default: 10) |

## Usage

```python
from drugclaw.skills.web_search.web_search import WebSearchSkill

skill = WebSearchSkill(config={
    "pubmed_email": "you@example.com",
    "max_ddg": 5,
    "max_pubmed": 5,
})

# Direct string query
results = skill.search("imatinib BCR-ABL mechanism", max_results=10)

# Or entity-based
results = skill.retrieve(
    entities={"drug": ["imatinib"], "disease": ["CML"]},
    query="mechanism of action",
)
for r in results:
    print(r.source, r.target_entity, r.sources)
```

## Output (`RetrievalResult`)

| Field | Description |
|-------|-------------|
| `source_entity` | Search query string |
| `target_entity` | Page title or paper title |
| `target_type` | `web_page` or `publication` |
| `evidence_text` | Snippet or citation string |
| `sources` | URL or `PMID:xxx` |
| `metadata` | title, url, engine, pmid, authors, date |

## Data Source

- DuckDuckGo: <https://duckduckgo.com>
- PubMed E-utilities: <https://eutils.ncbi.nlm.nih.gov>

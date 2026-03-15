---
name: sematyp-download
description: >
  Access the SemaTyP drug-disease knowledge graph. Use whenever the user asks
  for SemaTyP downloads, literature-mined drug-disease associations, local
  exploration of the extracted dataset, or preview of graph triples for one
  resource or one local extracted folder.
---

# SemaTyP Download Skill

Download the GitHub archive, inspect the extracted directory, and preview
training triples locally.

| Input Pattern | Detected As | Action |
|---|---|---|
| no input | dataset download | `download_sematyp()` |
| local extract dir | dataset inspection | `explore_dataset(base_dir)` |
| local extract dir with train file | triple preview | `preview_triples(data_dir, n)` |

## API

| Function | Input | Returns |
|---|---|---|
| `download_sematyp()` | none | `True` / `False` |
| `explore_dataset(base_dir)` | local directory | prints directory tree preview |
| `preview_triples(data_dir, n=10)` | local directory + count | prints triple-like rows |

## Usage

See `if __name__ == "__main__"` in `66_SemaTyP.py` for runnable examples
covering download, extracted-folder exploration, and triple preview.

## Key Fields

The script does not normalize rows into one fixed schema. It looks for local
`.tsv`, `.txt`, or `.csv` files whose names contain `train`, then prints rows
as `(head) --[relation]--> (tail)` when at least three tab-separated columns
exist.

## Notes

- This is a download-and-local-preview workflow, not a live entity lookup API.
- Live validation on 2026-03-15 confirmed the GitHub archive URL redirected to
  `codeload.github.com` and returned `HTTP 200` with `application/zip`.
- The repository now redirects to a `main` branch archive even though the
  script URL still references `master.zip`; GitHub currently resolves it.

## Data Source

- **Repository**: <https://github.com/ShengtianSang/SemaTyP>
- **Archive URL in script**:
  <https://github.com/ShengtianSang/SemaTyP/archive/refs/heads/master.zip>
- **Paper**: <https://link.springer.com/article/10.1186/s12859-018-2167-5>


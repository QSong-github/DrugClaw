# Repository Guide

## Start Here

If you are new to DrugClaw, read `README.md` first and use the CLI from the repository root:

```bash
python -m drugclaw doctor
python -m drugclaw run --query "What are the known drug targets of imatinib?"
python -m drugclaw list
```

## Top-Level Directories

### `drugclaw/`

The runtime package. This is the main place to look for the CLI, config handling, retrieval flow, and agent orchestration.

### `skills/`

Implemented skill code grouped by drug task category.

### `maintainers/`

Maintainer-oriented smoke scripts, helper utilities, and archived reference assets. These are useful during local development but are not part of the default product surface or the default `pytest` gate.

### `resources_metadata/`

Tracked minimal subtree that keeps the CLI, demos, and tests runnable right after `git clone`. This directory is the starting point for contributors and automated checks.

The full resource overlay bundle will be released upon paper acceptance. Once available, extracting that tarball at the repository root overlays additional files on top of `resources_metadata/` to unlock broader `LOCAL_FILE` coverage. Maintainers can inspect the builder and validator under `maintainers/resources/`.

### `support/`

Project images and visual assets used in the README and related docs.

## Runtime Surface vs Support Material

The main runtime surface is:

- `drugclaw/`
- `python -m drugclaw ...`
- `drugclaw ...` after editable install

Support material includes:

- `maintainers/`
- `docs/`

## Contributor Orientation

If you are debugging the package behavior, start in `drugclaw/`.

If you are checking whether a skill is implemented or data-backed, look in `skills/` and `resources_metadata/`.

If you are validating a specific resource path or maintainer utility, check `skills/` and `maintainers/`.

If you need machine-local scratch scripts, notes, or throwaway dev helpers, keep them under `.devlocal/` so they stay out of version control.

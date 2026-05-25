# Maintainer Utilities

This directory holds maintainer-only tooling that is useful for local development
but is not part of the default DrugClaw product surface.

These scripts are also outside the default `pytest` gate. The supported default
test surface remains `tests/`.

## Layout

- `smoke/`: resource and skill smoke scripts for maintainers
- `bench/`: maintainer wrappers around benchmark and scorecard flows
- `deploy/`: deployment templates for serviceized environments
- `legacy/`: historical notes kept for maintainers
- `archive/`: historical reference assets that are kept for maintainers but are not part of the user-facing surface
- `resources/`: builder, validator, and contract definitions for the full `resources_metadata/` overlay package

## Intended Use

Run these scripts from the repository root when you need deeper resource-level
validation during development:

```bash
python maintainers/smoke/65_FDA_Orange_Book_smoke_test.py
python maintainers/smoke/test_skills_66_68.py
```

If you need machine-local scratch files, temporary runners, or private notes,
put them under `.devlocal/` so they stay out of git history by default.

## Full Resource Overlay

Maintainers who produce the full package should work under `maintainers/resources/`.

The user-facing download will be released upon paper acceptance.

The intended flow is:

1. Build from raw or mirrored source resources under a maintainer-only import tree.
2. Stage a canonical `resources_metadata/` tree.
3. Validate that staging tree against `full_package_contract.json`.
4. Emit `resources_metadata_full.tar.gz`.
5. Upload that tarball to the public mirror once anonymity is no longer required.

The archive is required to stay overlay-compatible with the repository root. Extracting it at the repo root should extend the tracked `resources_metadata/` subtree in place without introducing a second runtime root.

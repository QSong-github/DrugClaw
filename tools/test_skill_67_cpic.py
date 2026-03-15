#!/usr/bin/env python3
"""
Real smoke test for skills.drug_knowledgebase.cpic.CPICSkill.

Checks:
  - import
  - instantiate
  - is_available()
  - standard drug query
  - standard gene query
  - edge query (non-existent entity)
  - result structure validation for DrugClaw consumption
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path("/data/boom/Agent/DrugClaw")
sys.path.insert(0, str(ROOT))


@dataclass
class Report:
    status: str
    commands_executed: list[str]
    checks_performed: list[str]
    sample_returned_records: dict[str, Any]
    problems_found: list[str]
    minimal_fixes_suggested: list[str]


def rr_view(item: Any) -> dict[str, Any]:
    d = item.to_dict() if hasattr(item, "to_dict") else asdict(item)
    return {
        "source_entity": d.get("source_entity"),
        "source_type": d.get("source_type"),
        "target_entity": d.get("target_entity"),
        "target_type": d.get("target_type"),
        "relationship": d.get("relationship"),
        "evidence_text": d.get("evidence_text"),
        "metadata": getattr(item, "metadata", d.get("metadata", {})),
        "sources": d.get("sources", []),
        "source": d.get("source"),
    }


def validate_results(results: list[Any], label: str) -> list[str]:
    problems: list[str] = []
    if not isinstance(results, list):
        return [f"{label}: result is not a list"]
    if not results:
        return [f"{label}: result list is empty"]

    for i, item in enumerate(results):
        source_entity = getattr(item, "source_entity", None)
        target_entity = getattr(item, "target_entity", None)
        relationship = getattr(item, "relationship", None)
        evidence_text = getattr(item, "evidence_text", None)
        metadata = getattr(item, "metadata", None)

        if not source_entity:
            problems.append(f"{label}: result[{i}] missing source_entity")
        if not target_entity:
            problems.append(f"{label}: result[{i}] missing target_entity")
        if not relationship:
            problems.append(f"{label}: result[{i}] missing relationship")
        if not evidence_text:
            problems.append(f"{label}: result[{i}] missing evidence_text")
        if not isinstance(metadata, dict) or not metadata:
            problems.append(f"{label}: result[{i}] metadata empty or not dict")
        else:
            if "drugid" not in metadata and "pair_id" not in metadata and "guideline_id" not in metadata:
                problems.append(f"{label}: result[{i}] metadata missing key business fields")
    return problems


def main() -> int:
    commands = ["python tools/test_skill_67_cpic.py"]
    checks = [
        "read cpic_skill.py",
        "read README.md",
        "read SKILL.md if present",
        "read skills/.../example.py and skillexamples/67_CPIC.py",
        "import CPICSkill",
        "instantiate CPICSkill(timeout=20)",
        "call is_available()",
        "standard query 1: drug=clopidogrel",
        "standard query 2: gene=CYP2D6",
        "edge query: drug=zzz_not_a_real_drug_zzz",
        "validate non-empty structured results for standard queries",
        "validate evidence_text and metadata",
    ]

    problems: list[str] = []
    fixes: list[str] = []
    sample: dict[str, Any] = {}

    from skills.drug_knowledgebase.cpic import CPICSkill

    skill = CPICSkill(config={"timeout": 20})
    sample["is_available"] = skill.is_available()
    if not sample["is_available"]:
        problems.append("is_available() returned False for an implemented REST skill.")

    drug_results = skill.retrieve(
        entities={"drug": ["clopidogrel"]},
        query="pharmacogenomics guideline",
        max_results=5,
    )
    gene_results = skill.retrieve(
        entities={"gene": ["CYP2D6"]},
        query="drug gene pairs",
        max_results=5,
    )
    edge_results = skill.retrieve(
        entities={"drug": ["zzz_not_a_real_drug_zzz"]},
        query="pharmacogenomics guideline",
        max_results=5,
    )

    sample["drug_query_count"] = len(drug_results)
    sample["gene_query_count"] = len(gene_results)
    sample["edge_query_count"] = len(edge_results)
    sample["drug_query_sample"] = [rr_view(r) for r in drug_results[:2]]
    sample["gene_query_sample"] = [rr_view(r) for r in gene_results[:2]]
    sample["edge_query_sample"] = [rr_view(r) for r in edge_results[:2]]

    problems.extend(validate_results(drug_results, "drug_query"))
    problems.extend(validate_results(gene_results, "gene_query"))

    if edge_results:
        problems.append("edge_query: expected empty list for non-existent entity, but got non-empty results")

    status = "PASS" if not problems else "FAIL"
    if problems:
        fixes.append("Keep README/example aligned with live CPIC API shape and stable test entities such as clopidogrel or CYP2D6.")
        fixes.append("If future API changes occur, revalidate /v1/drug and /v1/pair before relying on nested fields.")

    report = Report(
        status=status,
        commands_executed=commands,
        checks_performed=checks,
        sample_returned_records=sample,
        problems_found=problems,
        minimal_fixes_suggested=fixes,
    )
    print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

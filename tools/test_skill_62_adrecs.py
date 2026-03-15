#!/usr/bin/env python3
"""
Real smoke test for skills.adr.adrecs.ADReCSSkill.
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
        "target_entity": d.get("target_entity"),
        "relationship": d.get("relationship"),
        "evidence_text": d.get("evidence_text"),
        "metadata": getattr(item, "metadata", d.get("metadata", {})),
        "source": d.get("source"),
    }


def validate_results(results: list[Any], label: str) -> list[str]:
    problems: list[str] = []
    if not isinstance(results, list):
        return [f"{label}: result is not a list"]
    if not results:
        return [f"{label}: result list is empty"]
    for i, item in enumerate(results):
        evidence = getattr(item, "evidence_text", None)
        metadata = getattr(item, "metadata", None)
        if not evidence:
            problems.append(f"{label}: result[{i}] missing evidence_text")
        if not isinstance(metadata, dict) or not metadata:
            problems.append(f"{label}: result[{i}] metadata empty or not dict")
        else:
            if "adr_id" not in metadata and "hierarchy" not in metadata:
                problems.append(f"{label}: result[{i}] metadata missing key business fields")
    return problems


def main() -> int:
    commands = ["python tools/test_skill_62_adrecs.py"]
    checks = [
        "read adrecs_skill.py",
        "read README.md",
        "read skillexamples/62_ADReCS.py",
        "import ADReCSSkill",
        "instantiate ADReCSSkill(timeout=20)",
        "call is_available()",
        "standard query 1: drug=aspirin",
        "standard query 2: drug=imatinib",
        "edge query: drug=zzz_not_a_real_drug_zzz",
        "validate non-empty structured results for standard queries",
        "validate evidence_text and metadata",
    ]

    problems: list[str] = []
    fixes: list[str] = []
    sample: dict[str, Any] = {}

    from skills.adr.adrecs import ADReCSSkill

    skill = ADReCSSkill(config={"timeout": 20})
    sample["is_available"] = skill.is_available()

    r1 = skill.retrieve({"drug": ["aspirin"]}, query="adverse reactions", max_results=5)
    r2 = skill.retrieve({"drug": ["imatinib"]}, query="adverse reactions", max_results=5)
    edge = skill.retrieve({"drug": ["zzz_not_a_real_drug_zzz"]}, query="adverse reactions", max_results=5)

    sample["aspirin_count"] = len(r1)
    sample["imatinib_count"] = len(r2)
    sample["edge_count"] = len(edge)
    sample["aspirin_sample"] = [rr_view(x) for x in r1[:2]]
    sample["imatinib_sample"] = [rr_view(x) for x in r2[:2]]
    sample["edge_sample"] = [rr_view(x) for x in edge[:2]]

    problems.extend(validate_results(r1, "aspirin_query"))
    problems.extend(validate_results(r2, "imatinib_query"))
    if edge:
        problems.extend(validate_results(edge, "edge_query"))

    status = "PASS" if not problems else "FAIL"
    if problems:
        fixes.append("The current runtime assumes a stable ADReCS REST API at /ADReCS/api/drug, but the live site does not currently respond like a callable API.")
        fixes.append("Convert this skill to a download/local-file workflow, or document it as external-resource blocked until a real API or downloadable structured file is confirmed.")

    print(json.dumps(asdict(Report(
        status=status,
        commands_executed=commands,
        checks_performed=checks,
        sample_returned_records=sample,
        problems_found=problems,
        minimal_fixes_suggested=fixes,
    )), indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

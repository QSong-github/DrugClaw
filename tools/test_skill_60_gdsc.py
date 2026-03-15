#!/usr/bin/env python3
"""
Real smoke test for skills.drug_molecular_property.gdsc.GDSCSkill.

Strategy:
  1. Download the official current-release screened compounds CSV from Sanger.
  2. Instantiate GDSCSkill with that real file.
  3. Validate import / is_available / retrieve on standard + edge queries.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
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
        evidence_text = getattr(item, "evidence_text", None)
        metadata = getattr(item, "metadata", None)
        relationship = getattr(item, "relationship", None)
        if not evidence_text:
            problems.append(f"{label}: result[{i}] missing evidence_text")
        if not isinstance(metadata, dict) or not metadata:
            problems.append(f"{label}: result[{i}] metadata empty or not dict")
        else:
            if "drug_id" not in metadata and "target" not in metadata and "target_pathway" not in metadata:
                problems.append(f"{label}: result[{i}] metadata missing key business fields")
        if not relationship:
            problems.append(f"{label}: result[{i}] missing relationship")
    return problems


def main() -> int:
    commands = ["python tools/test_skill_60_gdsc.py"]
    checks = [
        "read gdsc_skill.py",
        "read README.md",
        "read skillexamples/60_GDSC_GDSC2.py",
        "import GDSCSkill",
        "download official screened_compounds_rel_8.4.csv",
        "instantiate GDSCSkill with real csv_path",
        "call is_available()",
        "standard query 1: drug=Erlotinib",
        "standard query 2: drug=Rapamycin",
        "edge query: drug=zzz_not_a_real_drug_zzz",
        "validate non-empty structured results for standard queries",
        "validate evidence_text and metadata",
    ]

    problems: list[str] = []
    fixes: list[str] = []
    sample: dict[str, Any] = {}

    from skills.drug_molecular_property.gdsc import GDSCSkill
    from importlib.machinery import SourceFileLoader

    example = SourceFileLoader("gdsc_example", str(ROOT / "skillexamples" / "60_GDSC_GDSC2.py")).load_module()

    tmpdir = Path(tempfile.mkdtemp(prefix="gdsc_test_"))
    try:
        example.OUTPUT_DIR = str(tmpdir)
        csv_path = example.download_gdsc_drug_list()
        sample["csv_path"] = csv_path

        skill = GDSCSkill(config={"csv_path": csv_path})
        sample["is_available"] = skill.is_available()
        if not sample["is_available"]:
            problems.append("is_available() returned False with a real official GDSC CSV.")

        r1 = skill.retrieve({"drug": ["Erlotinib"]}, query="target", max_results=5)
        r2 = skill.retrieve({"drug": ["Rapamycin"]}, query="target", max_results=5)
        edge = skill.retrieve({"drug": ["zzz_not_a_real_drug_zzz"]}, query="target", max_results=5)

        sample["erlotinib_count"] = len(r1)
        sample["rapamycin_count"] = len(r2)
        sample["edge_count"] = len(edge)
        sample["erlotinib_sample"] = [rr_view(x) for x in r1[:2]]
        sample["rapamycin_sample"] = [rr_view(x) for x in r2[:2]]
        sample["edge_sample"] = [rr_view(x) for x in edge[:2]]

        problems.extend(validate_results(r1, "erlotinib_query"))
        problems.extend(validate_results(r2, "rapamycin_query"))
        if edge:
            problems.append("edge_query: expected empty list for non-existent drug, but got results")

        status = "PASS" if not problems else "FAIL"
        if problems:
            fixes.append("Keep runtime loader aligned with the real current-release screened compounds CSV from Sanger.")
            fixes.append("If current_release changes version suffix, update the example download URL.")

        print(json.dumps(asdict(Report(
            status=status,
            commands_executed=commands,
            checks_performed=checks,
            sample_returned_records=sample,
            problems_found=problems,
            minimal_fixes_suggested=fixes,
        )), indent=2, ensure_ascii=False))
        return 0 if status == "PASS" else 1
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

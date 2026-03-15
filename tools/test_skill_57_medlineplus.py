from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.drug_labeling.medlineplus.medlineplus_skill import MedlinePlusSkill


def _serialize_result(r):
    return {
        "source_entity": r.source_entity,
        "relationship": r.relationship,
        "target_entity": r.target_entity,
        "evidence_text": r.evidence_text,
        "metadata": r.metadata,
        "sources": r.sources,
    }


def main() -> None:
    report: dict = {
        "skill": "57 MedlinePlus Drug Info",
        "status": "FAIL",
        "commands_executed": ["python tools/test_skill_57_medlineplus.py"],
        "checks_performed": [],
        "sample_returned_records": [],
        "problems_found": [],
        "minimal_fixes_suggested": [],
    }

    skill = MedlinePlusSkill(config={"timeout": 20})
    report["checks_performed"] += [
        "import MedlinePlusSkill",
        "instantiate MedlinePlusSkill(config={'timeout': 20})",
    ]

    available = skill.is_available()
    report["checks_performed"].append(f"is_available() -> {available}")

    aspirin = skill.retrieve({"drug": ["aspirin"]}, query="patient information", max_results=3)
    ibuprofen = skill.retrieve({"drug": ["ibuprofen"]}, query="patient information", max_results=3)
    edge = skill.retrieve({"drug": ["zzz_not_a_real_drug_zzz"]}, query="patient information", max_results=3)

    report["checks_performed"] += [
        f"standard query aspirin -> {len(aspirin)} records",
        f"standard query ibuprofen -> {len(ibuprofen)} records",
        f"edge query -> {len(edge)} records",
    ]

    valid_standard = True
    for results in (aspirin, ibuprofen):
        if not results:
            valid_standard = False
            continue
        for r in results:
            if not r.evidence_text or not r.metadata or "url" not in r.metadata:
                valid_standard = False
        report["sample_returned_records"].append(_serialize_result(results[0]))

    if available and valid_standard and not edge:
        report["status"] = "PASS"
    else:
        if not available:
            report["problems_found"].append("MedlinePlus availability probe failed.")
        if not valid_standard:
            report["problems_found"].append("Standard queries did not return valid structured records.")
        if edge:
            report["problems_found"].append("Edge query unexpectedly returned records.")

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

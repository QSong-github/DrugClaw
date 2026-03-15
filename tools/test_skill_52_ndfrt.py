from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.drug_ontology.ndfrt.ndfrt_skill import NDFRTSkill


def _serialize(r):
    return {
        "source_entity": r.source_entity,
        "relationship": r.relationship,
        "target_entity": r.target_entity,
        "evidence_text": r.evidence_text,
        "metadata": r.metadata,
    }


def main() -> None:
    report = {
        "skill": "52 NDF-RT",
        "status": "FAIL",
        "commands_executed": ["python tools/test_skill_52_ndfrt.py"],
        "checks_performed": [],
        "sample_returned_records": [],
        "problems_found": [],
        "minimal_fixes_suggested": [],
    }

    skill = NDFRTSkill(config={"timeout": 20})
    available = skill.is_available()
    aspirin = skill.retrieve({"drug": ["aspirin"]}, query="classification", max_results=3)
    warfarin = skill.retrieve({"drug": ["warfarin"]}, query="classification", max_results=3)
    edge = skill.retrieve({"drug": ["zzz_not_a_real_drug_zzz"]}, query="classification", max_results=3)

    report["checks_performed"] += [
        "import NDFRTSkill",
        "instantiate NDFRTSkill(config={'timeout': 20})",
        f"is_available() -> {available}",
        f"standard query aspirin -> {len(aspirin)} records",
        f"standard query warfarin -> {len(warfarin)} records",
        f"edge query -> {len(edge)} records",
    ]

    valid = True
    for results in (aspirin, warfarin):
        if not results:
            valid = False
            continue
        for r in results:
            if not r.evidence_text or not r.metadata or "ndfrt_code" not in r.metadata:
                valid = False
        report["sample_returned_records"].append(_serialize(results[0]))

    if available and valid and not edge:
        report["status"] = "PASS"
    else:
        if not available:
            report["problems_found"].append("NDF-RT availability probe failed.")
        if not valid:
            report["problems_found"].append("Standard queries did not return valid structured records.")
        if edge:
            report["problems_found"].append("Edge query unexpectedly returned records.")

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

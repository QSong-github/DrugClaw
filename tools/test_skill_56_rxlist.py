from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.drug_labeling.rxlist.rxlist_skill import RxListSkill


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
        "skill": "56 RxList Drug Descriptions",
        "status": "FAIL",
        "commands_executed": ["python tools/test_skill_56_rxlist.py"],
        "checks_performed": [],
        "sample_returned_records": [],
        "problems_found": [],
        "minimal_fixes_suggested": [],
    }

    skill = RxListSkill(config={"timeout": 20})
    report["checks_performed"] += [
        "import RxListSkill",
        "instantiate RxListSkill(config={'timeout': 20})",
    ]

    available = skill.is_available()
    report["checks_performed"].append(f"is_available() -> {available}")

    standard_queries = [
        ("aspirin", skill.retrieve({"drug": ["aspirin"]}, query="description", max_results=3)),
        ("ibuprofen", skill.retrieve({"drug": ["ibuprofen"]}, query="description", max_results=3)),
    ]
    edge_results = skill.retrieve({"drug": ["zzz_not_a_real_drug_zzz"]}, query="description", max_results=3)

    report["checks_performed"].append(
        f"standard query aspirin -> {len(standard_queries[0][1])} records"
    )
    report["checks_performed"].append(
        f"standard query ibuprofen -> {len(standard_queries[1][1])} records"
    )
    report["checks_performed"].append(f"edge query -> {len(edge_results)} records")

    valid_standard = True
    for _, results in standard_queries:
        if not results:
            valid_standard = False
            continue
        for r in results:
            if not r.evidence_text or not r.metadata or "url" not in r.metadata:
                valid_standard = False
        report["sample_returned_records"].append(_serialize_result(results[0]))

    if available and valid_standard and not edge_results:
        report["status"] = "PASS"
    else:
        if not available:
            report["problems_found"].append("RxList homepage probe failed.")
        if not valid_standard:
            report["problems_found"].append("Standard drug queries did not return valid structured records.")
        if edge_results:
            report["problems_found"].append("Edge query unexpectedly returned records.")

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

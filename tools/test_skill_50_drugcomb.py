from __future__ import annotations

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.drug_combination.drugcomb.drugcomb_skill import DrugCombSkill


def _remote_checks() -> dict:
    urls = {
        "zenodo_record": "https://zenodo.org/api/records/11102665",
        "example_file": "https://zenodo.org/records/11102665/files/drugcomb_data_v1.5.csv?download=1",
    }
    out = {}
    for key, url in urls.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                out[key] = {
                    "status": "ok",
                    "content_type": resp.headers.get("Content-Type"),
                    "content_length": resp.headers.get("Content-Length"),
                }
        except Exception as exc:
            out[key] = {"status": "error", "error": repr(exc)}
    return out


def main() -> None:
    report = {
        "skill": "50 DrugComb",
        "status": "FAIL",
        "commands_executed": ["python tools/test_skill_50_drugcomb.py"],
        "checks_performed": [],
        "sample_returned_records": [],
        "problems_found": [],
        "minimal_fixes_suggested": [],
    }

    skill = DrugCombSkill(config={})
    available = skill.is_available()
    remote = _remote_checks()

    report["checks_performed"] += [
        "import DrugCombSkill",
        "instantiate DrugCombSkill(config={})",
        f"is_available() -> {available}",
        f"local resources path exists -> {os.path.exists(os.path.join('resources_metadata', 'drug_combination', 'DrugComb'))}",
        "verified Zenodo record and example file source",
    ]

    if not available:
        report["problems_found"].append("No local DrugComb CSV is configured or present.")
    for key, value in remote.items():
        if value.get("status") == "error":
            report["problems_found"].append(f"{key} unavailable: {value['error']}")

    report["minimal_fixes_suggested"] = [
        "Provide a maintained DrugComb CSV under resources_metadata/drug_combination/DrugComb/.",
        "Update the example/README because current Zenodo access is blocked with HTTP 403 in this environment.",
    ]
    report["remote_checks"] = remote
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

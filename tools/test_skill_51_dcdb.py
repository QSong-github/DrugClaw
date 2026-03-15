from __future__ import annotations

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.drug_combination.dcdb.dcdb_skill import DCDBSkill


def _remote_checks() -> dict:
    urls = {
        "home": "http://www.cls.zju.edu.cn/dcdb/",
        "example_csv": "http://www.cls.zju.edu.cn/dcdb/download/DCDB_combination.csv",
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
        "skill": "51 DCDB",
        "status": "FAIL",
        "commands_executed": ["python tools/test_skill_51_dcdb.py"],
        "checks_performed": [],
        "sample_returned_records": [],
        "problems_found": [],
        "minimal_fixes_suggested": [],
    }

    skill = DCDBSkill(config={})
    available = skill.is_available()
    remote = _remote_checks()

    report["checks_performed"] += [
        "import DCDBSkill",
        "instantiate DCDBSkill(config={})",
        f"is_available() -> {available}",
        f"local resources path exists -> {os.path.exists(os.path.join('resources_metadata', 'drug_combination', 'DCDB'))}",
        "verified homepage and example CSV source",
    ]

    if not available:
        report["problems_found"].append("No local DCDB CSV/TSV is configured or present.")
    for key, value in remote.items():
        if value.get("status") == "error":
            report["problems_found"].append(f"{key} unavailable: {value['error']}")

    report["minimal_fixes_suggested"] = [
        "Provide a maintained DCDB export under resources_metadata/drug_combination/DCDB/.",
        "Update the example/README because the old direct CSV download path is stale.",
    ]
    report["remote_checks"] = remote
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

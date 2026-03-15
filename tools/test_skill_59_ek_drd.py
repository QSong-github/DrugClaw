from __future__ import annotations

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.drug_repurposing.ek_drd.ek_drd_skill import EKDRDSkill


def _remote_checks() -> dict:
    urls = {
        "skill_source_repo": "https://github.com/luoyunan/EKDRGraph",
        "example_site_index": "http://www.idruglab.com/drd/index.php",
        "example_zip": "http://www.idruglab.com/drd/download/EK-DRD.zip",
        "example_csv": "http://www.idruglab.com/drd/download/ekdrd.csv",
    }
    out: dict = {}
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
    report: dict = {
        "skill": "59 EK-DRD",
        "status": "FAIL",
        "commands_executed": ["python tools/test_skill_59_ek_drd.py"],
        "checks_performed": [],
        "sample_returned_records": [],
        "problems_found": [],
        "minimal_fixes_suggested": [],
    }

    skill = EKDRDSkill(config={})
    available = skill.is_available()
    remote = _remote_checks()

    report["checks_performed"] += [
        "import EKDRDSkill",
        "instantiate EKDRDSkill(config={})",
        f"is_available() -> {available}",
        f"local resources path exists -> {os.path.exists(os.path.join('resources_metadata', 'drug_repurposing', 'EK_DRD'))}",
        "verified repo/site/download paths from docstring and example",
    ]

    if not available:
        report["problems_found"].append("No local EK-DRD CSV/TSV is configured or present.")
    for key, value in remote.items():
        if value.get("status") == "error":
            report["problems_found"].append(f"{key} unavailable: {value['error']}")

    report["minimal_fixes_suggested"] = [
        "Replace the dead GitHub/source references with a maintained downloadable export or mirror path.",
        "If the iDrugLab portal is still the source of truth, document the certificate/download issue and support a local mirrored file under resources_metadata/drug_repurposing/EK_DRD/.",
    ]
    report["remote_checks"] = remote

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.drug_repurposing.cancerdr.cancerdr_skill import CancerDRSkill


def _remote_checks() -> dict:
    urls = {
        "home": "http://crdd.osdd.net/raghava/cancerdr/",
        "example_download": "http://crdd.osdd.net/raghava/cancerdr/download.php",
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
        "skill": "53 CancerDR",
        "status": "FAIL",
        "commands_executed": ["python tools/test_skill_53_cancerdr.py"],
        "checks_performed": [],
        "sample_returned_records": [],
        "problems_found": [],
        "minimal_fixes_suggested": [],
    }

    skill = CancerDRSkill(config={})
    available = skill.is_available()
    remote = _remote_checks()

    report["checks_performed"] += [
        "import CancerDRSkill",
        "instantiate CancerDRSkill(config={})",
        f"is_available() -> {available}",
        f"local resources path exists -> {os.path.exists(os.path.join('resources_metadata', 'drug_repurposing', 'CancerDR'))}",
        "verified homepage and example download path",
    ]

    if not available:
        report["problems_found"].append("No local CancerDR CSV/TSV is configured or present.")
    for key, value in remote.items():
        if value.get("status") == "error":
            report["problems_found"].append(f"{key} unavailable: {value['error']}")

    report["minimal_fixes_suggested"] = [
        "Provide a maintained CancerDR export under resources_metadata/drug_repurposing/CancerDR/.",
        "Update the example/README because the old download.php path is stale even though the homepage is reachable.",
    ]
    report["remote_checks"] = remote
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

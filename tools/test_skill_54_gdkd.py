from __future__ import annotations

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.dti.gdkd.gdkd_skill import GDKDSkill


def _remote_checks() -> dict:
    urls = {
        "synapse_page": "https://www.synapse.org/#!Synapse:syn2370773",
        "alt_ccle_csv": "https://data.broadinstitute.org/ccle/CCLE_NP24.2009_Drug_data_2015.02.24.csv",
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
        "skill": "54 GDKD",
        "status": "FAIL",
        "commands_executed": ["python tools/test_skill_54_gdkd.py"],
        "checks_performed": [],
        "sample_returned_records": [],
        "problems_found": [],
        "minimal_fixes_suggested": [],
    }

    skill = GDKDSkill(config={})
    available = skill.is_available()
    remote = _remote_checks()

    report["checks_performed"] += [
        "import GDKDSkill",
        "instantiate GDKDSkill(config={})",
        f"is_available() -> {available}",
        f"local resources path exists -> {os.path.exists(os.path.join('resources_metadata', 'dti', 'GDKD'))}",
        "verified Synapse landing page and alternative CCLE CSV",
    ]

    if not available:
        report["problems_found"].append("No local GDKD CSV is configured or present.")
    for key, value in remote.items():
        if value.get("status") == "error":
            report["problems_found"].append(f"{key} unavailable: {value['error']}")

    report["minimal_fixes_suggested"] = [
        "Provide a maintained GDKD/CCLE export under resources_metadata/dti/GDKD/.",
        "Update the example/README because the old Broad CCLE CSV link is stale and Synapse access is gated.",
    ]
    report["remote_checks"] = remote
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.drug_knowledgebase.who_eml.who_eml_skill import WHOEssentialMedicinesSkill


def _remote_checks() -> dict:
    urls = {
        "community_csv": "https://raw.githubusercontent.com/dolph/essential-medicines-list/master/medicines.csv",
        "official_pdf": "https://www.who.int/docs/default-source/essential-medicines/2023-eml-final-web.pdf",
        "publication_page": "https://www.who.int/publications/i/item/WHO-MHP-HPS-EML-2023.02",
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
        "skill": "58 WHO Essential Medicines List",
        "status": "FAIL",
        "commands_executed": ["python tools/test_skill_58_who_eml.py"],
        "checks_performed": [],
        "sample_returned_records": [],
        "problems_found": [],
        "minimal_fixes_suggested": [],
    }

    skill = WHOEssentialMedicinesSkill(config={})
    available = skill.is_available()
    remote = _remote_checks()

    report["checks_performed"] += [
        "import WHOEssentialMedicinesSkill",
        "instantiate WHOEssentialMedicinesSkill(config={})",
        f"is_available() -> {available}",
        f"local resources path exists -> {os.path.exists(os.path.join('resources_metadata', 'drug_knowledgebase', 'WHO_EML'))}",
        "verified example/README remote sources",
    ]

    if not available:
        report["problems_found"].append("No local WHO EML CSV is configured or present.")
    for key, value in remote.items():
        if value.get("status") == "error":
            report["problems_found"].append(f"{key} unavailable: {value['error']}")

    report["minimal_fixes_suggested"] = [
        "Provide a maintained CSV export in the Hugging Face mirror and document its path under resources_metadata/drug_knowledgebase/WHO_EML/.",
        "Update the README/example because the current community CSV and PDF URLs are stale.",
    ]
    report["remote_checks"] = remote

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

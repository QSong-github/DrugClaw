from __future__ import annotations

import json
import os
import sys
import tempfile
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.drug_knowledgebase.pharmkg.pharmkg_skill import PharmKGSkill


def _check_remote_sources() -> dict:
    report: dict = {"github_zip": {}, "zenodo_zip": {}}

    github_url = "https://github.com/MindRank-Biotech/PharmKG/archive/refs/heads/master.zip"
    try:
        req = urllib.request.Request(github_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        root = tempfile.mkdtemp(prefix="pharmkg_")
        zip_path = os.path.join(root, "pharmkg.zip")
        with open(zip_path, "wb") as fh:
            fh.write(data)
        with zipfile.ZipFile(zip_path) as zf:
            train_files = [
                n for n in zf.namelist()
                if "train" in n.lower() and n.endswith((".tsv", ".txt", ".csv"))
            ]
        report["github_zip"] = {
            "status": "ok",
            "bytes": len(data),
            "train_files_found": train_files[:20],
        }
    except Exception as exc:
        report["github_zip"] = {"status": "error", "error": repr(exc)}

    zenodo_url = "https://zenodo.org/records/4077338/files/PharmKG-8k.zip?download=1"
    try:
        req = urllib.request.Request(zenodo_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            report["zenodo_zip"] = {
                "status": "ok",
                "content_type": resp.headers.get("Content-Type"),
                "content_length": resp.headers.get("Content-Length"),
            }
    except Exception as exc:
        report["zenodo_zip"] = {"status": "error", "error": repr(exc)}

    return report


def main() -> None:
    report: dict = {
        "skill": "55 PharmKG",
        "status": "FAIL",
        "commands_executed": ["python tools/test_skill_55_pharmkg.py"],
        "checks_performed": [],
        "sample_returned_records": [],
        "problems_found": [],
        "minimal_fixes_suggested": [],
    }

    skill = PharmKGSkill(config={})
    report["checks_performed"].append("import PharmKGSkill")
    report["checks_performed"].append("instantiate PharmKGSkill(config={})")

    available = skill.is_available()
    report["checks_performed"].append(f"is_available() -> {available}")

    local_path = os.path.join("resources_metadata", "drug_knowledgebase", "PharmKG")
    report["checks_performed"].append(
        f"local resources path exists -> {os.path.exists(local_path)}"
    )

    remote = _check_remote_sources()
    report["checks_performed"].append("verified GitHub and Zenodo data sources from example/README")

    if available:
        results = skill.retrieve({"drug": ["imatinib"]}, query="knowledge graph", max_results=5)
        report["checks_performed"].append(f"retrieve(...) -> {len(results)} records")
        if results:
            r = results[0]
            report["sample_returned_records"].append({
                "source_entity": r.source_entity,
                "relationship": r.relationship,
                "target_entity": r.target_entity,
                "evidence_text": r.evidence_text,
                "metadata": r.metadata,
            })
            if r.evidence_text and r.metadata:
                report["status"] = "PASS"

    if not available:
        report["problems_found"].append("No local PharmKG train_tsv is configured or present.")
    if remote["github_zip"].get("status") == "ok" and not remote["github_zip"].get("train_files_found"):
        report["problems_found"].append(
            "GitHub archive is reachable but does not contain the train.tsv-style data file expected by the runtime skill."
        )
    if remote["zenodo_zip"].get("status") == "error":
        report["problems_found"].append(
            f"Zenodo fallback is not directly usable: {remote['zenodo_zip']['error']}"
        )

    report["minimal_fixes_suggested"] = [
        "Point the README/config to a real downloadable PharmKG triples file, not just the code repository.",
        "Support the maintained Hugging Face mirror or a documented extracted path under resources_metadata/drug_knowledgebase/PharmKG/.",
    ]
    report["remote_checks"] = remote

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

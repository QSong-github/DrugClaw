#!/usr/bin/env python3
"""
Runtime smoke tests for skills 66, 67, 68.

Checks performed per skill:
  - import skill class
  - instantiate skill
  - call is_available()
  - call retrieve(...) with a representative input from README/example
  - verify non-empty list
  - verify every item has evidence_text and metadata

This script prefers real external/resource paths over synthetic fixtures.
"""

from __future__ import annotations

import importlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path("/data/boom/Agent/DrugClaw")
SKILL_DIR = ROOT / "skillexamples"


@dataclass
class SkillReport:
    name: str
    status: str
    commands_executed: list[str]
    checks_performed: list[str]
    sample_outputs: dict[str, Any]
    problems_found: list[str]
    minimal_fixes_suggested: list[str]


def _rr_to_dict(item: Any) -> dict[str, Any]:
    if hasattr(item, "to_dict"):
        d = item.to_dict()
    else:
        d = asdict(item)
    return {
        "source_entity": d.get("source_entity"),
        "target_entity": d.get("target_entity"),
        "relationship": d.get("relationship"),
        "evidence_text": d.get("evidence_text"),
        "metadata": d.get("metadata", {}),
        "source": d.get("source"),
    }


def _all_have_fields(results: list[Any]) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for i, item in enumerate(results):
        evidence = getattr(item, "evidence_text", None)
        metadata = getattr(item, "metadata", None)
        if not evidence:
            problems.append(f"result[{i}] missing evidence_text")
        if metadata is None:
            problems.append(f"result[{i}] missing metadata")
    return (len(problems) == 0, problems)


def test_sematyp() -> SkillReport:
    commands = [
        "python tools/test_skills_66_68.py",
        "download via skillexamples/66_SemaTyP.py",
    ]
    checks = [
        "import SemaTyPSkill",
        "instantiate with real local file config if available",
        "call is_available()",
        "call retrieve(...) with README-style drug input",
        "validate evidence_text and metadata",
    ]
    problems: list[str] = []
    fixes: list[str] = []
    sample: dict[str, Any] = {}

    mod = importlib.import_module("skills.drug_disease.sematyp")
    skill_cls = getattr(mod, "SemaTyPSkill")

    example_mod = importlib.import_module("skillexamples.66_SemaTyP")
    tmp_dir = Path(tempfile.mkdtemp(prefix="sematyp_test_"))
    csv_candidate: str | None = None

    try:
        # Use the example's real download path.
        example_mod.OUTPUT_DIR = str(tmp_dir / "download")
        downloaded = example_mod.download_sematyp()
        sample["downloaded"] = downloaded

        extracted_root = Path(example_mod.OUTPUT_DIR)
        sample["extracted_root"] = str(extracted_root)

        for p in extracted_root.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".csv", ".tsv", ".txt"}:
                try:
                    head = p.read_text(encoding="utf-8", errors="ignore").splitlines()[:3]
                except Exception:
                    continue
                joined = " | ".join(head).lower()
                if any(tok in joined for tok in ["subject", "predicate", "object", "drug", "disease", "head", "tail"]):
                    csv_candidate = str(p)
                    sample["candidate_preview"] = head
                    break

        sample["csv_candidate"] = csv_candidate

        config = {"csv_path": csv_candidate} if csv_candidate else {}
        if csv_candidate and csv_candidate.endswith(".tsv"):
            config["delimiter"] = "\t"
        skill = skill_cls(config=config)
        available = skill.is_available()
        sample["is_available"] = available

        results = skill.retrieve(entities={"drug": ["imatinib"]}, query="mechanism", max_results=5)
        sample["result_count"] = len(results)
        sample["sample_results"] = [_rr_to_dict(r) for r in results[:2]]

        if not csv_candidate:
            problems.append("No real triplet file matching the runtime skill schema was found in the downloaded SemaTyP archive.")
            fixes.append("Update 66_SemaTyP.py or README to point to the actual triplet file used by SemaTyPSkill.")
            fixes.append("Alternatively add a loader config example showing the exact CSV/TSV path and delimiter.")
            return SkillReport("66 SemaTyP", "FAIL", commands, checks, sample, problems, fixes)

        if not available:
            problems.append("Skill imported but is_available() returned False with the real downloaded resource.")
        if not results:
            problems.append("retrieve(...) returned an empty list with README-style input.")
        else:
            ok, field_problems = _all_have_fields(results)
            if not ok:
                problems.extend(field_problems)

        status = "PASS" if not problems else "FAIL"
        if problems:
            fixes.append("Verify the archive actually contains drug-disease triplets with headers expected by SemaTyPSkill.")
        return SkillReport("66 SemaTyP", status, commands, checks, sample, problems, fixes)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_cpic() -> SkillReport:
    commands = ["python tools/test_skills_66_68.py"]
    checks = [
        "import CPICSkill",
        "instantiate skill",
        "call is_available()",
        "call retrieve(...) using representative CPIC drug input",
        "validate evidence_text and metadata",
        "validate live CPIC API path indirectly through retrieve(...)",
    ]
    problems: list[str] = []
    fixes: list[str] = []
    sample: dict[str, Any] = {}

    mod = importlib.import_module("skills.drug_knowledgebase.cpic")
    skill_cls = getattr(mod, "CPICSkill")
    skill = skill_cls(config={"timeout": 20})
    sample["is_available"] = skill.is_available()

    # Use the example's representative drug rather than the weak README example.
    results = skill.retrieve(entities={"drug": ["clopidogrel"]}, query="guideline", max_results=5)
    sample["result_count"] = len(results)
    sample["sample_results"] = [_rr_to_dict(r) for r in results[:2]]

    if not sample["is_available"]:
        problems.append("is_available() returned False for an implemented REST skill.")
    if not results:
        problems.append("retrieve(...) returned an empty list for clopidogrel against the live CPIC API.")
        fixes.append("Align CPICSkill with the verified PostgREST schema used in skillexamples/67_CPIC.py.")
        fixes.append("Current implementation queries /v1/drug?name=<drug> and expects nested guidelines/genes fields that the live API does not expose.")
    else:
        ok, field_problems = _all_have_fields(results)
        if not ok:
            problems.extend(field_problems)

    status = "PASS" if not problems else "FAIL"
    return SkillReport("67 CPIC", status, commands, checks, sample, problems, fixes)


def test_kegg() -> SkillReport:
    commands = ["python tools/test_skills_66_68.py"]
    checks = [
        "import KEGGDrugSkill",
        "instantiate skill",
        "call is_available()",
        "call retrieve(...) using representative drug input",
        "validate non-empty list",
        "validate evidence_text and metadata",
        "validate real KEGG REST fallback if bioservices is unavailable",
    ]
    problems: list[str] = []
    fixes: list[str] = []
    sample: dict[str, Any] = {}

    mod = importlib.import_module("skills.ddi.kegg_drug")
    skill_cls = getattr(mod, "KEGGDrugSkill")
    skill = skill_cls(config={"timeout": 20})
    sample["is_available"] = skill.is_available()

    # README uses imatinib; examples show warfarin as a stronger DDI case.
    results = skill.retrieve(entities={"drug": ["warfarin"]}, query="interactions", max_results=5)
    sample["result_count"] = len(results)
    sample["sample_results"] = [_rr_to_dict(r) for r in results[:2]]

    if not sample["is_available"]:
        problems.append("is_available() returned False even though KEGGDrugSkill is marked implemented.")
    if not results:
        problems.append("retrieve(...) returned an empty list for warfarin.")
        fixes.append("If bioservices is absent, ensure REST fallback remains reachable and parses INTERACTION lines correctly.")
    else:
        ok, field_problems = _all_have_fields(results)
        if not ok:
            problems.extend(field_problems)

    status = "PASS" if not problems else "FAIL"
    return SkillReport("68 KEGG Drug", status, commands, checks, sample, problems, fixes)


def main() -> int:
    sys.path.insert(0, str(ROOT))
    reports = [test_sematyp(), test_cpic(), test_kegg()]
    print(json.dumps([asdict(r) for r in reports], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

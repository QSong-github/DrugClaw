"""
Smoke test for 65_FDA_Orange_Book.py.

Purpose
-------
Validate the behavior described in 65_FDA_Orange_Book_SKILL.md:
  1. Bulk Orange Book ZIP can be downloaded and extracted.
  2. Live openFDA NDC query returns approved-drug data.
  3. Live Drugs@FDA query returns approval records.

Run
---
cd /data/boom/Agent/DrugClaw/skillexamples
python 65_FDA_Orange_Book_smoke_test.py
"""

from importlib.machinery import SourceFileLoader
import json
import os
import sys


def _load_module():
    return SourceFileLoader("orange_book", "65_FDA_Orange_Book.py").load_module()


def _check_download(mod):
    ok = mod.download_orange_book()
    zip_path = os.path.join(mod.OUTPUT_DIR, "orange_book_data.zip")
    products_candidates = [
        os.path.join(mod.OUTPUT_DIR, "products.txt"),
        os.path.join(mod.OUTPUT_DIR, "Products.txt"),
    ]
    products_path = next((p for p in products_candidates if os.path.exists(p)), None)
    return {
        "ok": bool(ok and os.path.exists(zip_path) and products_path),
        "zip_path": zip_path if os.path.exists(zip_path) else None,
        "products_path": products_path,
    }


def _check_ndc_query(mod, drug_name="ibuprofen"):
    result = mod.search_approved_drugs(drug_name, limit=3)
    hits = result.get("results", [])
    sample = hits[0] if hits else {}
    return {
        "ok": len(hits) > 0,
        "query": drug_name,
        "hit_count": len(hits),
        "sample": {
            "brand_name": sample.get("brand_name"),
            "generic_name": sample.get("generic_name"),
            "labeler_name": sample.get("labeler_name"),
            "product_ndc": sample.get("product_ndc"),
        },
    }


def _check_approval_query(mod, drug_name="aspirin"):
    result = mod.get_drug_approval_info(drug_name, limit=3)
    hits = result.get("results", [])
    sample = hits[0] if hits else {}
    return {
        "ok": len(hits) > 0,
        "query": drug_name,
        "hit_count": len(hits),
        "sample": {
            "application_number": sample.get("application_number"),
            "sponsor_name": sample.get("sponsor_name"),
            "product_count": len(sample.get("products", []) or []),
        },
    }


def main():
    mod = _load_module()

    report = {
        "skill": "65_FDA_Orange_Book",
        "checks": {},
    }

    try:
        report["checks"]["download"] = _check_download(mod)
    except Exception as exc:
        report["checks"]["download"] = {"ok": False, "error": str(exc)}

    try:
        report["checks"]["ndc_query"] = _check_ndc_query(mod)
    except Exception as exc:
        report["checks"]["ndc_query"] = {"ok": False, "error": str(exc)}

    try:
        report["checks"]["approval_query"] = _check_approval_query(mod)
    except Exception as exc:
        report["checks"]["approval_query"] = {"ok": False, "error": str(exc)}

    check_results = [item.get("ok", False) for item in report["checks"].values()]
    report["passed"] = all(check_results)

    print("=== 65_FDA_Orange_Book Smoke Test ===")
    for name, item in report["checks"].items():
        status = "PASS" if item.get("ok") else "FAIL"
        print(f"{name:16s} {status}")
    print()
    print(json.dumps(report, indent=2, ensure_ascii=False))

    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()

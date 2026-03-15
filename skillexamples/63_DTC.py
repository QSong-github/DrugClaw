"""
DTC - Drug Target Commons 2.0
Category: Drug-centric | Type: DB | Subcategory: Drug-Target Interaction (DTI)
Link: https://drugtargetcommons.fimm.fi/static/Excell_files/DTC_data.csv
Paper: https://academic.oup.com/database/article/doi/10.1093/database/bay083/5096727

Drug Target Commons is a community platform for drug-target interaction data,
providing curated and standardized bioactivity data from multiple public databases.

Access method: Direct CSV download (no registration required).
"""

import urllib.request
import os
import csv

OUTPUT_DIR = "DTC"
# Direct CSV download
CSV_URL = "https://drugtargetcommons.fimm.fi/static/Excell_files/DTC_data.csv"


def download_dtc():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "DTC_data.csv")
    if os.path.exists(fname):
        print(f"Already exists: {fname}")
        return fname
    print(f"Downloading DTC data from {CSV_URL} ...")
    try:
        req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(fname, "wb") as f:
                total = 0
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    total += len(chunk)
                    print(f"\r  Downloaded: {total // 1024 / 1024:.1f} MB", end="")
        print(f"\nSaved to {fname}")
        return fname
    except Exception as e:
        print(f"\nFailed: {e}")
        return None


def preview_dtc(fpath: str, n: int = 5):
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        return
    with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        print(f"Columns: {reader.fieldnames}")
        print(f"\nFirst {n} drug-target interactions:")
        for i, row in enumerate(reader):
            if i >= n:
                break
            drug = row.get("compound_name", row.get("Drug", "?"))
            target = row.get("gene_names", row.get("Target", "?"))
            activity = row.get("standard_type", "?")
            value = row.get("standard_value", "?")
            unit = row.get("standard_unit", "?")
            source = row.get("data_source", row.get("Source", "?"))
            print(f"  Drug: {drug} | Gene: {target} | "
                  f"{activity}={value} {unit} | Source: {source}")


def filter_by_gene(fpath: str, gene_symbol: str, n: int = 10) -> list:
    """Filter DTC entries by gene symbol."""
    results = []
    if not os.path.exists(fpath):
        return results
    with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if gene_symbol.upper() in str(row.get("gene_names", "")).upper():
                results.append(row)
                if len(results) >= n:
                    break
    print(f"Found {len(results)} entries for gene '{gene_symbol}':")
    for row in results[:5]:
        print(f"  Drug: {row.get('compound_name')} | "
              f"Value: {row.get('standard_value')} {row.get('standard_unit')}")
    return results


if __name__ == "__main__":
    fpath = download_dtc()
    if fpath:
        preview_dtc(fpath)
        print("\n=== DTC: Entries for EGFR ===")
        filter_by_gene(fpath, "EGFR")
    else:
        print("\nVisit https://drugtargetcommons.fimm.fi/ to access DTC.")

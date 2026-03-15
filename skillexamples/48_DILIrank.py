"""
DILIrank - Drug-Induced Liver Injury Risk Ranking
Category: Drug-centric | Type: Dataset | Subcategory: Drug Toxicity
Link: https://www.fda.gov/science-research/liver-toxicity-knowledge-base-ltkb/drug-induced-liver-injury-rank-dilirank-dataset
Paper: https://www.sciencedirect.com/science/article/abs/pii/S1359644616300411

DILIrank is an FDA-curated dataset of drugs ranked by their potential to cause
DILI, categorized as most-, less-, no-concern, and ambiguous.

Access method: Download from FDA LTKB website.
"""

import urllib.request
import os
import csv

OUTPUT_DIR = "DILIrank"

# Direct download links from FDA LTKB
DOWNLOAD_URLS = [
    "https://www.fda.gov/files/science%20&%20research/published/drug-induced-liver-injury-rank--dilirank--dataset.csv",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4780519/bin/pr-2015-003113_si_001.xlsx",
]

# Alternative: Published supplemental data
GITHUB_URL = "https://raw.githubusercontent.com/PatWalters/practical_cheminformatics_tutorials/master/data/dilirank_v2.csv"


def download_dilirank():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls_to_try = DOWNLOAD_URLS + [GITHUB_URL]
    for url in urls_to_try:
        fname = os.path.join(OUTPUT_DIR, os.path.basename(url.split("?")[0]))
        if not fname.endswith((".csv", ".xlsx", ".tsv")):
            fname += ".csv"
        print(f"Trying: {url[:80]} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read()
            with open(fname, "wb") as f:
                f.write(content)
            print(f"  Saved to {fname} ({len(content)} bytes)")
            return fname
        except Exception as e:
            print(f"  Failed: {e}")
    return None


def preview_dilirank(fpath: str, n: int = 10):
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        return
    with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        print(f"Columns: {reader.fieldnames}")
        print(f"\nFirst {n} entries:")
        for i, row in enumerate(reader):
            if i >= n:
                break
            drug = row.get("Compound Name", row.get("name", row.get("Drug", "?")))
            category = row.get("vDILIConcern", row.get("DILIrank", row.get("Category", "?")))
            print(f"  Drug: {drug} | DILI Category: {category}")


if __name__ == "__main__":
    fpath = download_dilirank()
    if fpath:
        preview_dilirank(fpath)
    else:
        print(
            "\nDownload failed. Visit:\n"
            "  https://www.fda.gov/science-research/liver-toxicity-knowledge-base-ltkb/"
            "drug-induced-liver-injury-rank-dilirank-dataset\n\n"
            "DILIrank categories:\n"
            "  - Most-DILI-Concern: strong evidence of liver injury\n"
            "  - Less-DILI-Concern: some evidence of liver injury\n"
            "  - No-DILI-Concern: no credible evidence\n"
            "  - Ambiguous-DILI-Concern: conflicting evidence"
        )

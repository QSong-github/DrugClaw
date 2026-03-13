"""
EK-DRD - Enhanced Knowledgebase of Drug Resistance Data
Category: Drug-centric | Type: DB | Subcategory: Drug Repurposing
Link: http://www.idruglab.com/drd/index.php
Paper: https://pubs.acs.org/doi/10.1021/acs.jcim.9b00365

EK-DRD provides curated information on drug resistance mechanisms and associated
gene mutations/variants to support personalized medicine and treatment decisions.

Access method: Web interface and download from the iDrugLab portal.
"""

import urllib.request
import urllib.parse
import os

BASE_URL = "http://www.idruglab.com/drd"
OUTPUT_DIR = "EK_DRD"


def check_website():
    """Check connectivity to EK-DRD website."""
    req = urllib.request.Request(
        f"{BASE_URL}/index.php",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    return html


def download_ekdrd():
    """Attempt to download EK-DRD dataset."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls = [
        f"{BASE_URL}/download/EK-DRD.zip",
        f"{BASE_URL}/download/ekdrd.csv",
        f"{BASE_URL}/download.php",
    ]
    for url in urls:
        ext = ".zip" if url.endswith(".zip") else ".csv" if url.endswith(".csv") else ".html"
        fname = os.path.join(OUTPUT_DIR, f"EK_DRD{ext}")
        print(f"Trying: {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read()
            if len(content) > 1000:
                with open(fname, "wb") as f:
                    f.write(content)
                print(f"  Saved to {fname} ({len(content)} bytes)")
                return fname
        except Exception as e:
            print(f"  Failed: {e}")
    return None


def describe_ekdrd():
    print("=== EK-DRD (Enhanced Knowledgebase of Drug Resistance Data) ===")
    print("Content:")
    print("  - Drug resistance mutations for ~100 drugs")
    print("  - Gene/protein variants associated with resistance")
    print("  - Cancer type and disease context")
    print("  - Clinical evidence (FDA-approved biomarkers)")
    print("  - Computational predictions")
    print("\nKey drug categories:")
    print("  - Kinase inhibitors (imatinib, erlotinib, gefitinib)")
    print("  - Antiretrovirals (HIV resistance)")
    print("  - Antibiotics (bacterial resistance)")
    print("  - Chemotherapy agents")


if __name__ == "__main__":
    describe_ekdrd()
    print()
    print("=== Checking EK-DRD website ===")
    try:
        html = check_website()
        print(f"Website accessible ({len(html)} bytes).")
    except Exception as e:
        print(f"Website error: {e}")

    print("\n=== Attempting data download ===")
    fpath = download_ekdrd()
    if not fpath:
        print(f"\nDirect download failed. Visit {BASE_URL}/index.php")

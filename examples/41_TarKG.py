"""
TarKG - Drug Target Discovery Knowledge Graph
Category: Drug-centric | Type: KG | Subcategory: Drug-Target Interaction (DTI)
Link: https://tarkg.ddtmlab.org/index
Paper: https://academic.oup.com/bioinformatics/article/40/10/btae598/7818343

TarKG is a comprehensive biomedical knowledge graph focused on target discovery,
integrating multi-source data including TCM knowledge, with 171 relation types.

Access method: Download from the TarKG website or GitHub.
"""

import urllib.request
import os
import zipfile

OUTPUT_DIR = "TarKG"

# TarKG GitHub repository
GITHUB_ZIP = "https://github.com/ddtmlab/TarKG/archive/refs/heads/main.zip"
# Alternative: direct data download from the website
DATA_URL = "https://tarkg.ddtmlab.org/static/download/TarKG.zip"


def download_tarkg():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls_to_try = [DATA_URL, GITHUB_ZIP]
    for url in urls_to_try:
        fname = os.path.join(OUTPUT_DIR, "TarKG.zip")
        print(f"Trying: {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(fname, "wb") as f:
                    f.write(resp.read())
            print(f"  Saved to {fname}")
            with zipfile.ZipFile(fname, "r") as zf:
                zf.extractall(OUTPUT_DIR)
            print(f"  Extracted to {OUTPUT_DIR}/")
            return True
        except Exception as e:
            print(f"  Failed: {e}")
    return False


def describe_tarkg():
    print("=== TarKG Knowledge Graph ===")
    print("Entities:")
    print("  - Drug (ChEMBL, DrugBank, TCM compounds)")
    print("  - Gene/Protein (UniProt, Ensembl)")
    print("  - Disease (MeSH, OMIM)")
    print("  - Pathway (KEGG, Reactome)")
    print("  - TCM Herb, TCM Formula")
    print("Relation types: 171 relation types")
    print("Scale: ~100K nodes, ~1M edges")
    print("\nUse cases:")
    print("  - Drug target prediction")
    print("  - Drug repurposing")
    print("  - TCM-Western medicine bridging")


if __name__ == "__main__":
    describe_tarkg()
    print()
    success = download_tarkg()
    if success:
        for root, dirs, files in os.walk(OUTPUT_DIR):
            depth = root.replace(OUTPUT_DIR, "").count(os.sep)
            if depth <= 1:
                indent = "  " * depth
                print(f"{indent}{os.path.basename(root) or OUTPUT_DIR}/")
                for f in sorted(files)[:5]:
                    print(f"{indent}  {f}")
    else:
        print("\nDownload failed. Visit https://tarkg.ddtmlab.org/index "
              "to access TarKG interactively.")

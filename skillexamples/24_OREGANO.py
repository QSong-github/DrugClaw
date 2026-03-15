"""
OREGANO - Drug Repurposing Knowledge Graph
Category: Drug-centric | Type: DB | Subcategory: Drug Repurposing
Link: https://gitub.u-bordeaux.fr/erias/oregano
Paper: https://www.nature.com/articles/s41597-023-02757-0

OREGANO is a biomedical knowledge graph for drug repurposing, integrating drug,
disease, gene, and pathway data.

Access method: Download from GitLab repository or Zenodo.
"""

import urllib.request
import os
import zipfile

# Zenodo deposit for OREGANO
ZENODO_URL = "https://zenodo.org/records/8350859/files/oregano.zip"
GITLAB_ZIP = "https://gitub.u-bordeaux.fr/erias/oregano/-/archive/main/oregano-main.zip"
OUTPUT_DIR = "OREGANO"


def download_oregano():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls_to_try = [ZENODO_URL, GITLAB_ZIP]
    for url in urls_to_try:
        fname = os.path.join(OUTPUT_DIR, "oregano.zip")
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
            list_contents(OUTPUT_DIR)
            return True
        except Exception as e:
            print(f"  Failed: {e}")
    return False


def list_contents(directory: str, max_depth: int = 2):
    for root, dirs, files in os.walk(directory):
        depth = root.replace(directory, "").count(os.sep)
        if depth >= max_depth:
            continue
        indent = "  " * depth
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = "  " * (depth + 1)
        for f in files[:5]:
            print(f"{sub_indent}{f}")


if __name__ == "__main__":
    success = download_oregano()
    if not success:
        print(
            "\nDownload failed. Visit https://gitub.u-bordeaux.fr/erias/oregano "
            "or the Zenodo record to access OREGANO.\n\n"
            "OREGANO KG includes:\n"
            "  - Drug nodes (DrugBank, ChEMBL)\n"
            "  - Disease nodes (OMIM, Orphanet)\n"
            "  - Gene nodes (Ensembl, UniProt)\n"
            "  - Pathway nodes (Reactome, KEGG)\n"
            "  - Edges: drug-disease, drug-gene, gene-disease, ..."
        )

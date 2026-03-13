"""
PharmGKB/ClinPGx - Pharmacogenomics Knowledge Curation
Category: Drug-related (indirect) | Type: DB | Subcategory: Pharmacogenomics
Link: https://www.pharmgkb.org/
Paper: https://academic.oup.com/nar/article/30/1/163/1332715

PharmGKB curates pharmacogenomics relationships between genetic variants and
drug response phenotypes. ClinPGx extends this to clinical implementation.

API docs: https://api.pharmgkb.org/
No API key required.
"""

import urllib.request
import urllib.parse
import json
import os

BASE_URL = "https://api.pharmgkb.org/v1"


def search_gene(gene_symbol: str) -> dict:
    """Search PharmGKB for a gene by symbol."""
    params = urllib.parse.urlencode({"symbol": gene_symbol})
    url = f"{BASE_URL}/data/gene?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_gene_pgx_summary(pharmgkb_id: str) -> dict:
    """Get pharmacogenomics gene summary."""
    url = f"{BASE_URL}/data/gene/{pharmgkb_id}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def search_drug(drug_name: str) -> dict:
    """Search PharmGKB for a drug by name."""
    params = urllib.parse.urlencode({"name": drug_name})
    url = f"{BASE_URL}/data/chemical?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_clinical_annotations(gene_symbol: str = None, drug_name: str = None,
                              limit: int = 5) -> dict:
    """Get clinical pharmacogenomics annotations."""
    params = {"view": "max"}
    if gene_symbol:
        params["gene.symbol"] = gene_symbol
    if drug_name:
        params["chemical.name"] = drug_name
    params_str = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/data/clinicalAnnotation?{params_str}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    return data


def download_pharmgkb_annotations():
    """Download PharmGKB clinical annotation data."""
    os.makedirs("PharmGKB", exist_ok=True)
    # Direct download: https://www.pharmgkb.org/downloads
    url = "https://api.pharmgkb.org/v1/download/file/data/clinicalAnnotations.zip"
    fname = "PharmGKB/clinicalAnnotations.zip"
    print(f"Downloading PharmGKB clinical annotations ...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(fname, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {fname}")
        import zipfile
        with zipfile.ZipFile(fname, "r") as zf:
            zf.extractall("PharmGKB")
        print("Extracted.")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


if __name__ == "__main__":
    print("=== PharmGKB: Search gene 'CYP2D6' ===")
    result = search_gene("CYP2D6")
    genes = result.get("data", [])
    for gene in genes[:2]:
        print(f"  ID: {gene.get('id')} | Symbol: {gene.get('symbol')} | Name: {gene.get('name')}")

    if genes:
        pgkb_id = genes[0].get("id")
        print(f"\n=== PharmGKB: Gene detail for {pgkb_id} ===")
        detail = get_gene_pgx_summary(pgkb_id)
        d = detail.get("data", {})
        print(f"  Symbol: {d.get('symbol')}")
        print(f"  Has variant annotations: {bool(d.get('hasVariantAnnotation'))}")

    print("\n=== PharmGKB: Search drug 'warfarin' ===")
    result = search_drug("warfarin")
    drugs = result.get("data", [])
    for drug in drugs[:2]:
        print(f"  ID: {drug.get('id')} | Name: {drug.get('name')}")

    print("\n=== PharmGKB: Clinical annotations for CYP2D6 ===")
    annots = get_clinical_annotations(gene_symbol="CYP2D6", limit=3)
    annotation_list = annots.get("data", [])[:3]
    for ann in annotation_list:
        print(f"  Drug: {ann.get('relatedChemicals', [{}])[0].get('name', 'N/A')} | "
              f"Level: {ann.get('level')} | "
              f"Phenotype: {ann.get('phenotypeCategory')}")

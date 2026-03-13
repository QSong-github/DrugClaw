"""
GDKD - Genomics-Drug Knowledge Database
Category: Drug-centric | Type: DB | Subcategory: Drug-Target Interaction (DTI)
Link: https://www.synapse.org/#!Synapse:syn2370773
Paper: https://doi.org/10.1038/nature11003

GDKD integrates genomic features with drug response data across multiple cancer
cell line pharmacogenomics datasets (CCLE, GDSC, NCI-60).

Access method:
  - Synapse platform (requires free registration): https://www.synapse.org/
  - Install: pip install synapseclient
  - The original paper data: Barretina et al. 2012 (CCLE)

This script demonstrates how to access the data via the Synapse client.
"""

import os


SYNAPSE_ID = "syn2370773"


def download_via_synapseclient():
    """
    Download GDKD/CCLE data via the Synapse Python client.
    Requires: pip install synapseclient
    And a free Synapse account at https://www.synapse.org/
    """
    try:
        import synapseclient
        syn = synapseclient.Synapse()
        print("Logging in to Synapse (using cached credentials or env vars) ...")
        # Try auto-login from .synapseConfig or SYNAPSE_AUTH_TOKEN env var
        syn.login()
        print(f"Downloading Synapse entity {SYNAPSE_ID} ...")
        entity = syn.get(SYNAPSE_ID)
        print(f"Downloaded: {entity.path}")
        return entity.path
    except ImportError:
        print("Install Synapse client: pip install synapseclient")
        return None
    except Exception as e:
        print(f"Synapse error: {e}")
        print("Ensure you have a Synapse account and valid credentials.")
        return None


def download_ccle_data_alternative():
    """
    Download CCLE data directly from the Broad Institute portal.
    CCLE is the main dataset underlying GDKD.
    """
    import urllib.request
    os.makedirs("GDKD", exist_ok=True)
    # CCLE pharmacological data (older release, publicly accessible)
    url = "https://data.broadinstitute.org/ccle/CCLE_NP24.2009_Drug_data_2015.02.24.csv"
    fname = "GDKD/CCLE_drug_data.csv"
    print(f"Downloading CCLE drug sensitivity data ...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(fname, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {fname}")
        return fname
    except Exception as e:
        print(f"Failed: {e}")
        return None


def describe_gdkd():
    print("=== GDKD (Genomics-Drug Knowledge Database) ===")
    print("Based on: CCLE (Cancer Cell Line Encyclopedia)")
    print("Content:")
    print("  - Drug response (IC50) for 24 drugs in 479 cancer cell lines")
    print("  - Genomic features: mutations, copy number, expression")
    print("  - Cancer type annotations")
    print("  - Drug target information")
    print("\nFor larger-scale data:")
    print("  - GDSC (60_GDSC_GDSC2.py): ~500 drugs, ~1000 cell lines")
    print("  - CCLE portal: https://sites.broadinstitute.org/ccle/")
    print("  - DepMap: https://depmap.org/")


if __name__ == "__main__":
    describe_gdkd()
    print()

    print("=== Attempting Synapse access ===")
    fpath = download_via_synapseclient()

    if not fpath:
        print("\n=== Trying alternative CCLE download ===")
        fpath = download_ccle_data_alternative()

        if fpath and os.path.exists(fpath):
            import csv
            with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                print(f"Columns: {reader.fieldnames}")
                for i, row in enumerate(reader):
                    if i >= 3:
                        break
                    print(f"  {row}")
        else:
            print(
                "\nAccess requires Synapse registration.\n"
                "Visit https://www.synapse.org/#!Synapse:syn2370773\n"
                "Or use the CCLE portal: https://sites.broadinstitute.org/ccle/"
            )

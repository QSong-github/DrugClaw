"""
DDI Corpus 2013 - Drug-Drug Interaction Extraction NLP Benchmark
Category: Drug-centric | Type: Dataset | Subcategory: Drug NLP/Text Mining
Link: https://github.com/isegura/DDICorpus
Paper: https://www.sciencedirect.com/science/article/pii/S1532046413001123

The DDI Corpus 2013 is a benchmark for DDI extraction from biomedical text,
containing manually annotated interactions from DrugBank and MEDLINE.

Access method: Download from GitHub repository.
"""

import urllib.request
import os
import zipfile
import xml.etree.ElementTree as ET

REPO_ZIP = "https://github.com/isegura/DDICorpus/archive/refs/heads/master.zip"
OUTPUT_DIR = "DDI_Corpus_2013"


def download_ddi_corpus():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "DDICorpus-master.zip")
    print(f"Downloading DDI Corpus 2013 from GitHub ...")
    try:
        urllib.request.urlretrieve(REPO_ZIP, fname)
        print(f"Saved to {fname}")
        with zipfile.ZipFile(fname, "r") as zf:
            zf.extractall(OUTPUT_DIR)
        print(f"Extracted to {OUTPUT_DIR}/DDICorpus-master/")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def parse_ddi_xml(xml_dir: str, n: int = 3):
    """Parse DDI Corpus XML files and extract DDI annotations."""
    if not os.path.exists(xml_dir):
        print(f"Directory not found: {xml_dir}")
        return []
    examples = []
    for fname in os.listdir(xml_dir)[:5]:
        if not fname.endswith(".xml"):
            continue
        fpath = os.path.join(xml_dir, fname)
        tree = ET.parse(fpath)
        root = tree.getroot()
        for sentence in root.findall(".//sentence"):
            text = sentence.get("text", "")
            for pair in sentence.findall("pair"):
                ddi = pair.get("ddi", "false")
                ddi_type = pair.get("type", "")
                e1 = pair.get("e1", "")
                e2 = pair.get("e2", "")
                if ddi == "true":
                    examples.append({
                        "text": text[:100],
                        "e1": e1, "e2": e2,
                        "type": ddi_type,
                    })
    print(f"Found {len(examples)} DDI-positive pairs in sampled files")
    for ex in examples[:n]:
        print(f"  Entities: ({ex['e1']}, {ex['e2']}) | Type: {ex['type']}")
        print(f"  Text: {ex['text']}...")
    return examples


if __name__ == "__main__":
    success = download_ddi_corpus()
    if success:
        # Try to find the DrugBank training set
        extract_dir = os.path.join(OUTPUT_DIR, "DDICorpus-master")
        xml_dir = os.path.join(extract_dir, "Train", "DrugBank")
        if not os.path.exists(xml_dir):
            # Explore available directories
            print("Contents of extracted dir:")
            for item in os.listdir(extract_dir):
                print(f"  {item}")
        else:
            print(f"\n=== DDI Corpus: DrugBank training annotations ===")
            parse_ddi_xml(xml_dir)

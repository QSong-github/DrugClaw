"""
PHEE - Pharmacovigilance Event Extraction Dataset
Category: Drug-centric | Type: Dataset | Subcategory: Drug NLP/Text Mining
Link: https://zenodo.org/records/7689970
Paper: https://arxiv.org/abs/2210.12560

PHEE contains 5,000+ annotated pharmacovigilance events from public medical
case reports, covering adverse and potential therapeutic events with rich
argument structure (subject, treatment, effect, demographics).

Access method: Download from Zenodo.
"""

import urllib.request
import os
import zipfile
import json

OUTPUT_DIR = "PHEE"
ZENODO_URL = "https://zenodo.org/records/7689970/files/PHEE.zip?download=1"


def download_phee():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, "PHEE.zip")
    print("Downloading PHEE dataset from Zenodo ...")
    try:
        req = urllib.request.Request(ZENODO_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(fname, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {fname}")
        with zipfile.ZipFile(fname, "r") as zf:
            zf.extractall(OUTPUT_DIR)
        print(f"Extracted to {OUTPUT_DIR}/")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


def load_phee_json(json_path: str, n: int = 3):
    """Load and preview PHEE JSON annotation file."""
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return []
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    examples = data if isinstance(data, list) else data.get("data", [])
    print(f"Total examples: {len(examples)}")
    for ex in examples[:n]:
        print(f"\n  Text: {str(ex.get('text', ''))[:150]}")
        events = ex.get("events", [])
        for ev in events[:2]:
            print(f"    Event type: {ev.get('event_type')}")
            print(f"    Trigger: {ev.get('trigger', {}).get('text', '')}")
    return examples


if __name__ == "__main__":
    success = download_phee()
    if success:
        # Find JSON files
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for fname in files:
                if fname.endswith(".json"):
                    print(f"\n=== Loading {fname} ===")
                    load_phee_json(os.path.join(root, fname))
                    break
            else:
                continue
            break
        print("\nDirectory contents:")
        for root, dirs, files in os.walk(OUTPUT_DIR):
            depth = root.replace(OUTPUT_DIR, "").count(os.sep)
            if depth <= 2:
                indent = "  " * depth
                print(f"{indent}{os.path.basename(root) or OUTPUT_DIR}/")
                for f in sorted(files)[:5]:
                    print(f"{indent}  {f}")
    else:
        print("Visit https://zenodo.org/records/7689970 to download PHEE manually.")

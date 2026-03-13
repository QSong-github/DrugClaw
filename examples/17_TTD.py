"""
TTD - Therapeutic Target Database
Category: Drug-centric | Type: DB | Subcategory: Drug-Target Interaction (DTI)
Link: https://ttd.idrblab.cn/
Paper: https://academic.oup.com/nar/article/52/D1/D1465/7275004

TTD provides information about therapeutic protein/nucleic acid targets,
targeted diseases, pathway information, and drugs for each target.

Access method: Download flat files from the TTD website.
"""

import urllib.request
import os

# TTD download links
DOWNLOAD_URLS = {
    "drug_download": "https://db.idrblab.net/ttd/sites/default/files/ttd_database/P1-01-TTD_target_download.txt",
    "target_drug": "https://db.idrblab.net/ttd/sites/default/files/ttd_database/P2-01-TTD_target_drug.txt",
}
OUTPUT_DIR = "TTD"


def download_ttd():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, url in DOWNLOAD_URLS.items():
        fname = os.path.join(OUTPUT_DIR, os.path.basename(url))
        print(f"Downloading {name} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(fname, "wb") as f:
                    f.write(resp.read())
            print(f"  Saved to {fname}")
        except Exception as e:
            print(f"  Failed: {e}")


def parse_target_drug_file(fpath: str, n: int = 10):
    """Parse TTD target-drug flat file (tab-separated key-value format)."""
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        return []
    entries = []
    current = {}
    with open(fpath, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                if current:
                    entries.append(current)
                    current = {}
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                current[parts[1]] = parts[2]
            elif len(parts) == 2:
                current[parts[0]] = parts[1]
    if current:
        entries.append(current)
    print(f"Total entries: {len(entries)}")
    for entry in entries[:n]:
        print(f"  {entry}")
    return entries


if __name__ == "__main__":
    download_ttd()
    fpath = os.path.join(OUTPUT_DIR, "P2-01-TTD_target_drug.txt")
    if os.path.exists(fpath):
        parse_target_drug_file(fpath, n=5)
    else:
        print(f"\nFile not downloaded. Visit https://ttd.idrblab.cn/ to "
              "download TTD datasets manually.")

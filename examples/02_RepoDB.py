"""
RepoDB - Standard Drug Repurposing Database
Category: Drug-centric | Type: DB | Subcategory: Drug Repurposing
Link: https://unmtid-shinyapps.net/shiny/repodb/
Paper: https://www.nature.com/articles/sdata201729

RepoDB links approved and failed drugs to diseases based on clinical trial
outcomes, widely used as a benchmark for computational drug repurposing.

Access method: Download CSV files directly from the GitHub release.
"""

import urllib.request
import csv
import os

# Direct CSV download from the published data release
CSV_URL = "https://raw.githubusercontent.com/the-dong/repodb/master/repodb.csv"
FALLBACK_URL = (
    "https://raw.githubusercontent.com/brown-data-science/repodb/master/repodb.csv"
)
OUTPUT_FILE = "repodb.csv"


def download_repodb():
    urls_to_try = [CSV_URL, FALLBACK_URL]
    for url in urls_to_try:
        try:
            print(f"Trying {url} ...")
            urllib.request.urlretrieve(url, OUTPUT_FILE)
            print(f"Downloaded to {OUTPUT_FILE}")
            return True
        except Exception as e:
            print(f"  Failed: {e}")
    return False


def preview_repodb(n=5):
    if not os.path.exists(OUTPUT_FILE):
        print("File not found. Run download_repodb() first.")
        return
    with open(OUTPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print(f"Columns: {reader.fieldnames}")
        for i, row in enumerate(reader):
            if i >= n:
                break
            print(row)


if __name__ == "__main__":
    ok = download_repodb()
    if ok:
        preview_repodb()
    else:
        print("Download failed. Visit https://unmtid-shinyapps.net/shiny/repodb/ "
              "to access RepoDB interactively.")

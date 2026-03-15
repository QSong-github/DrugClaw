---
name: fda-orange-book-query
description: >
  Query the FDA Orange Book and related openFDA endpoints. Use whenever the
  user asks about approved drug products, Orange Book bulk files, application
  numbers, approval details, labeler information, or wants FDA-approved drug
  lookups by one entity or a small list of entities.
---

# FDA Orange Book Query Skill

Use the FDA Orange Book ZIP for bulk local inspection and openFDA for live
entity lookup.

| Input Pattern | Detected As | Action |
|---|---|---|
| no input | bulk download | `download_orange_book()` then `preview_products_file()` |
| `ibuprofen` / `aspirin` | drug name | live openFDA query via NDC or Drugs@FDA |
| `["ibuprofen", "acetaminophen"]` | list of drug names | iterate `search_approved_drugs()` or `get_drug_approval_info()` |

## API

| Function | Input | Returns |
|---|---|---|
| `download_orange_book()` | none | `True` / `False` after ZIP download + extract |
| `search_approved_drugs(drug_name, limit=5)` | single drug name | raw openFDA NDC JSON |
| `get_drug_approval_info(drug_name, limit=3)` | single drug name | raw openFDA Drugs@FDA JSON |
| `preview_products_file()` | none | prints header/sample rows from extracted products file |

## Usage

See `if __name__ == "__main__"` in `65_FDA_Orange_Book.py` for runnable
examples covering: bulk ZIP download, `ibuprofen` NDC lookup, and `aspirin`
approval lookup.

## Key Fields

**NDC search results** often include: `brand_name`, `generic_name`,
`labeler_name`, `product_ndc`, `dosage_form`, `route`,
`marketing_start_date`.

**Drugs@FDA results** often include: `application_number`, `sponsor_name`,
`products`, `submissions`, `openfda`.

**Bulk Orange Book files** may include text files such as `products.txt`,
patent/exclusivity files, and applicant mappings.

## Notes

- Bulk and live-query paths are both currently usable.
- Live validation on 2026-03-15 confirmed
  `https://www.fda.gov/media/76860/download` returned `HTTP 200` as a ZIP file
  (`EOBZIP_2026_02.zip` in headers).
- Live validation on 2026-03-15 also confirmed the openFDA NDC query for
  `ibuprofen` returned JSON successfully.
- The script currently takes one entity at a time for live API calls; list
  input should be handled by looping at the caller level.

## Data Source

- **Orange Book**: <https://www.accessdata.fda.gov/scripts/cder/ob/>
- **Bulk ZIP**: <https://www.fda.gov/media/76860/download>
- **openFDA NDC**: <https://api.fda.gov/drug/ndc.json>
- **openFDA Drugs@FDA**: <https://api.fda.gov/drug/drugsfda.json>


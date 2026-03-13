"""
VigiAccess - Global Pharmacovigilance Data
Category: Drug-centric | Type: DB | Subcategory: Adverse Drug Reaction (ADR)
Link: http://www.vigiaccess.org/

VigiAccess provides public access to the WHO global database of individual
case safety reports (VigiBase), allowing query of adverse event reports globally.

Note: VigiAccess does NOT provide a public REST API. Access is through the
web interface at http://www.vigiaccess.org/. For research API access to
VigiBase, contact the Uppsala Monitoring Centre (UMC): https://www.who-umc.org/

This script demonstrates how to make a web request to retrieve summary
statistics from the VigiAccess public portal.
"""

import urllib.request
import urllib.parse


VIGIACCESS_URL = "http://www.vigiaccess.org/"


def get_vigiaccess_page():
    """Fetch the VigiAccess homepage to confirm connectivity."""
    req = urllib.request.Request(
        VIGIACCESS_URL,
        headers={"User-Agent": "Mozilla/5.0 (research use)"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    return html


def demonstrate_access():
    """
    VigiAccess is a web-only interface.
    For programmatic access to VigiBase, use:
    - WHO-UMC VigiLyze (requires UMC account): https://vigimed.who-umc.org/
    - FAERS as a US proxy (see 03_FAERS.py)
    - EU EudraVigilance (see below)
    """
    print("VigiAccess URL:", VIGIACCESS_URL)
    print(
        "\nFor programmatic pharmacovigilance data access, alternatives include:\n"
        "1. openFDA FAERS API (US): https://api.fda.gov/drug/event.json\n"
        "2. EU EudraVigilance API: https://www.ema.europa.eu/en/human-regulatory/"
        "research-development/pharmacovigilance/eudravigilance\n"
        "3. WHO UMC VigiLyze (requires institutional access)\n"
    )
    try:
        html = get_vigiaccess_page()
        print(f"VigiAccess page loaded successfully ({len(html)} bytes).")
        if "vigiaccess" in html.lower() or "vigibase" in html.lower():
            print("Confirmed: VigiAccess / VigiBase content detected.")
    except Exception as e:
        print(f"Could not connect to VigiAccess: {e}")


if __name__ == "__main__":
    demonstrate_access()

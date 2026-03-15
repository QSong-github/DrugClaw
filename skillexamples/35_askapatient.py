"""
AskaPatient - Patient Drug Experience Ratings
Category: Drug-centric | Type: DB | Subcategory: Drug Review/Patient Report
Link: https://www.askapatient.com/

AskaPatient.com is a website where patients report experiences with prescription
medications, including ratings for effectiveness, side effects, and ease of use.

Access method: Web scraping (terms of service permitting).
Note: Always check robots.txt and terms of service before scraping.
For structured data, consider the WebMD Drug Reviews dataset (10_WebMD_Drug_Reviews.py)
or the PsyTAR dataset (36_PsyTAR.py) which are derived from AskaPatient.
"""

import urllib.request
import urllib.parse
import html
import re


BASE_URL = "https://www.askapatient.com"


def get_drug_reviews(drug_name: str, num_pages: int = 1) -> list:
    """
    Fetch patient reviews for a drug from AskaPatient.com.
    Returns a list of review dicts with rating and comment fields.
    """
    reviews = []
    for page in range(1, num_pages + 1):
        params = urllib.parse.urlencode({
            "drug": drug_name,
            "page": page,
        })
        url = f"{BASE_URL}/viewrating.asp?{params}"
        print(f"GET {url}")
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (research use)"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="replace")
            # Simple regex-based extraction (no external parser needed)
            # Extract rating divs
            rating_pattern = re.compile(
                r'<td[^>]*class="[^"]*rating[^"]*"[^>]*>(.*?)</td>',
                re.IGNORECASE | re.DOTALL,
            )
            comment_pattern = re.compile(
                r'<td[^>]*class="[^"]*comment[^"]*"[^>]*>(.*?)</td>',
                re.IGNORECASE | re.DOTALL,
            )
            ratings = [html.unescape(re.sub(r"<[^>]+>", "", m)) for m in rating_pattern.findall(content)]
            comments = [html.unescape(re.sub(r"<[^>]+>", "", m)).strip()[:100]
                        for m in comment_pattern.findall(content)]
            for r, c in zip(ratings, comments):
                reviews.append({"rating": r.strip(), "comment": c})
        except Exception as e:
            print(f"  Error fetching page {page}: {e}")
    return reviews


def check_robots_txt():
    """Check AskaPatient robots.txt before scraping."""
    robots_url = f"{BASE_URL}/robots.txt"
    try:
        with urllib.request.urlopen(robots_url, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="replace")
        print("=== robots.txt ===")
        print(content[:500])
        return content
    except Exception as e:
        print(f"Could not fetch robots.txt: {e}")
        return ""


if __name__ == "__main__":
    print("Checking AskaPatient robots.txt ...")
    check_robots_txt()

    print("\n=== Fetching reviews for 'metformin' ===")
    reviews = get_drug_reviews("metformin", num_pages=1)
    if reviews:
        print(f"Found {len(reviews)} review snippets:")
        for r in reviews[:3]:
            print(f"  Rating: {r['rating']} | Comment: {r['comment']}")
    else:
        print("No reviews parsed. The site may require JavaScript rendering.")
        print(f"Visit {BASE_URL}/viewrating.asp?drug=metformin directly.")

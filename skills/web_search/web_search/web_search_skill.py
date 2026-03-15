"""
WebSearchSkill — Free web search via DuckDuckGo HTML + PubMed E-utilities.

Subcategory : web_search
Access mode : REST_API
Sources     : DuckDuckGo (https://duckduckgo.com) — no API key required
              PubMed E-utilities (https://eutils.ncbi.nlm.nih.gov) — free

This skill provides real-time web retrieval for drug-related queries.
DuckDuckGo is the primary engine (free, no key, no rate limits for casual use).
PubMed is automatically queried when the query contains drug/disease/gene terms.

Optionally install the duckduckgo-search package for richer results:
    pip install duckduckgo-search

Config keys
-----------
pubmed_email   : str  contact email for NCBI E-utilities (recommended)
pubmed_api_key : str  NCBI API key (optional; raises rate limit 3→10 req/s)
max_ddg        : int  max DuckDuckGo results per query (default: 5)
max_pubmed     : int  max PubMed results per query (default: 5)
timeout        : int  HTTP timeout in seconds (default: 10)
"""
from __future__ import annotations

import json
import logging
import re
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from ...base import RAGSkill, RetrievalResult, AccessMode

logger = logging.getLogger(__name__)

# PubMed biomedical keywords — triggers PubMed search when any appear in query
_BIOMEDICAL_KW = {
    "drug", "compound", "molecule", "inhibitor", "agonist", "antagonist",
    "gene", "protein", "target", "receptor", "enzyme", "pathway",
    "disease", "cancer", "tumor", "diabetes", "hypertension", "infection",
    "toxicity", "side effect", "adverse", "clinical", "trial", "therapy",
    "pharmacology", "pharmacokinetics", "mechanism", "ic50", "ki", "ec50",
}


class WebSearchSkill(RAGSkill):
    """
    Free web search skill — DuckDuckGo (HTML) + PubMed E-utilities.

    No API key required for basic usage.  PubMed is included automatically
    for any query that mentions drug/gene/disease terms.
    """

    name = "WebSearch"
    subcategory = "web_search"
    resource_type = "WebSearch"
    access_mode = AccessMode.REST_API
    aim = "Free web search"
    data_range = "Real-time web results via DuckDuckGo + PubMed E-utilities"
    _implemented = True

    # ------------------------------------------------------------------ #
    # Availability                                                         #
    # ------------------------------------------------------------------ #

    def is_available(self) -> bool:
        """Always available — only needs outbound HTTP."""
        return True

    # ------------------------------------------------------------------ #
    # Public interface                                                     #
    # ------------------------------------------------------------------ #

    def retrieve(
        self,
        entities: Dict[str, List[str]],
        query: str = "",
        max_results: int = 10,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        """Build search string from entities + query and search."""
        search_q = self._build_query(entities, query)
        return self.search(search_q, max_results=max_results)

    def search(self, query: str, max_results: int = 10) -> List[RetrievalResult]:
        """
        Search DuckDuckGo (and PubMed for biomedical queries).

        Parameters
        ----------
        query      : plain-text search string
        max_results: total results to return across all sources

        Returns list of RetrievalResult objects.
        """
        results: List[RetrievalResult] = []

        max_ddg    = min(self.config.get("max_ddg",    max_results // 2 or 5), max_results)
        max_pubmed = min(self.config.get("max_pubmed", max_results // 2 or 5), max_results)
        timeout    = self.config.get("timeout", 10)

        # DuckDuckGo — always
        try:
            results += self._ddg_search(query, max_ddg, timeout)
        except Exception as exc:
            logger.warning("WebSearch DDG error: %s", exc)

        # PubMed — only for biomedical queries
        if self._is_biomedical(query):
            try:
                results += self._pubmed_search(query, max_pubmed, timeout)
            except Exception as exc:
                logger.warning("WebSearch PubMed error: %s", exc)

        return results[:max_results]

    # ------------------------------------------------------------------ #
    # DuckDuckGo                                                           #
    # ------------------------------------------------------------------ #

    def _ddg_search(
        self, query: str, max_results: int, timeout: int
    ) -> List[RetrievalResult]:
        """Query DuckDuckGo; tries duckduckgo-search package then HTML API."""
        # Prefer installed package for cleaner results
        try:
            return self._ddg_package(query, max_results)
        except ImportError:
            pass
        return self._ddg_html(query, max_results, timeout)

    def _ddg_package(self, query: str, max_results: int) -> List[RetrievalResult]:
        """Use duckduckgo-search package (pip install duckduckgo-search)."""
        from duckduckgo_search import DDGS  # type: ignore
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(RetrievalResult(
                    source_entity=query,
                    source_type="query",
                    target_entity=r.get("title", ""),
                    target_type="web_page",
                    relationship="web_result",
                    weight=1.0,
                    source="DuckDuckGo",
                    skill_category="web_search",
                    evidence_text=r.get("body", ""),
                    sources=[r.get("href", "")],
                    metadata={
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                        "engine": "DuckDuckGo",
                    },
                ))
        return results

    def _ddg_html(
        self, query: str, max_results: int, timeout: int
    ) -> List[RetrievalResult]:
        """Fallback: scrape DuckDuckGo HTML lite endpoint."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120 Safari/537.36"
            ),
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Extract result titles + snippets + URLs from HTML
        results: List[RetrievalResult] = []
        # pattern: <a class="result__a" href="...">TITLE</a> … <a class="result__snippet">SNIPPET</a>
        links = re.findall(
            r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            html,
        )
        snippets = re.findall(
            r'<a[^>]+class="result__snippet"[^>]*>([^<]+)</a>', html
        )
        for i, (href, title) in enumerate(links[:max_results]):
            snippet = snippets[i] if i < len(snippets) else ""
            title = re.sub(r"<[^>]+>", "", title).strip()
            snippet = re.sub(r"<[^>]+>", "", snippet).strip()
            results.append(RetrievalResult(
                source_entity=query,
                source_type="query",
                target_entity=title,
                target_type="web_page",
                relationship="web_result",
                weight=1.0 - i * 0.05,
                source="DuckDuckGo",
                skill_category="web_search",
                evidence_text=snippet,
                sources=[href],
                metadata={
                    "title": title,
                    "url": href,
                    "snippet": snippet,
                    "engine": "DuckDuckGo",
                },
            ))
        return results

    # ------------------------------------------------------------------ #
    # PubMed E-utilities                                                   #
    # ------------------------------------------------------------------ #

    def _pubmed_search(
        self, query: str, max_results: int, timeout: int
    ) -> List[RetrievalResult]:
        """Search PubMed via NCBI E-utilities (free, no key required)."""
        base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        email     = self.config.get("pubmed_email", "drugclaw@example.com")
        api_key   = self.config.get("pubmed_api_key", "")
        rate_delay = 0.1 if api_key else 0.34

        # esearch
        params: Dict[str, str] = {
            "db": "pubmed", "term": query,
            "retmax": str(max_results), "retmode": "json", "sort": "relevance",
            "email": email,
        }
        if api_key:
            params["api_key"] = api_key
        search_url = base + "esearch.fcgi?" + urllib.parse.urlencode(params)
        time.sleep(rate_delay)
        with urllib.request.urlopen(search_url, timeout=timeout) as resp:
            search_data = json.loads(resp.read())
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []

        # esummary
        sum_params: Dict[str, str] = {
            "db": "pubmed", "id": ",".join(id_list),
            "retmode": "json", "email": email,
        }
        if api_key:
            sum_params["api_key"] = api_key
        sum_url = base + "esummary.fcgi?" + urllib.parse.urlencode(sum_params)
        time.sleep(rate_delay)
        with urllib.request.urlopen(sum_url, timeout=timeout) as resp:
            sum_data = json.loads(resp.read())

        results: List[RetrievalResult] = []
        for pmid in id_list:
            art = sum_data.get("result", {}).get(pmid, {})
            title   = art.get("title", "")
            journal = art.get("fulljournalname", art.get("source", ""))
            date    = art.get("pubdate", "")
            authors = [a.get("name", "") for a in art.get("authors", [])[:3]]
            author_str = "; ".join(authors) + (" et al." if len(art.get("authors", [])) > 3 else "")
            results.append(RetrievalResult(
                source_entity=query,
                source_type="query",
                target_entity=title,
                target_type="publication",
                relationship="literature_result",
                weight=1.0,
                source="PubMed",
                skill_category="web_search",
                evidence_text=f"{title} — {author_str} ({date}). {journal}.",
                sources=[f"PMID:{pmid}"],
                metadata={
                    "pmid": pmid,
                    "title": title,
                    "journal": journal,
                    "date": date,
                    "authors": author_str,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "engine": "PubMed",
                },
            ))
        return results

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _build_query(self, entities: Dict[str, List[str]], query: str) -> str:
        """Combine entity names and free-text query into a search string."""
        parts: List[str] = []
        for etype, names in entities.items():
            parts.extend(names[:3])
        if query:
            parts.append(query)
        return " ".join(parts) if parts else query

    def _is_biomedical(self, query: str) -> bool:
        """Return True if the query likely benefits from a PubMed search."""
        q_lower = query.lower()
        return any(kw in q_lower for kw in _BIOMEDICAL_KW)

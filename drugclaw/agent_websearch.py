"""
Web Search Agent - Supplements DrugClaw's structured drug knowledge retrieval
with web search across drug literature, clinical publications, and pharmacology databases
"""
from typing import List, Dict, Any, Optional
from .models import AgentState
from .llm_client import LLMClient
import json
import requests
import time
from xml.etree import ElementTree as ET
from urllib.parse import quote_plus
import re


class SearchAPIAdapter:
    """Base adapter for search APIs"""
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Execute search and return standardized results"""
        raise NotImplementedError


class PubMedAdapter(SearchAPIAdapter):
    """Adapter for PubMed E-utilities API"""
    
    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.email = email
        self.api_key = api_key
        self.rate_limit_delay = 0.34 if not api_key else 0.1
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search PubMed and return standardized results"""
        try:
            # Step 1: Search for article IDs
            search_url = f"{self.base_url}esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance'
            }
            if self.email:
                search_params['email'] = self.email
            if self.api_key:
                search_params['api_key'] = self.api_key
            
            time.sleep(self.rate_limit_delay)
            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            search_result = response.json()
            id_list = search_result.get('esearchresult', {}).get('idlist', [])
            
            if not id_list:
                return []
            
            # Step 2: Fetch article details
            time.sleep(self.rate_limit_delay)
            fetch_url = f"{self.base_url}esummary.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(id_list),
                'retmode': 'json'
            }
            if self.email:
                fetch_params['email'] = self.email
            if self.api_key:
                fetch_params['api_key'] = self.api_key
            
            response = requests.get(fetch_url, params=fetch_params, timeout=10)
            response.raise_for_status()
            
            fetch_result = response.json()
            
            # Step 3: Parse and standardize results
            results = []
            for pmid in id_list:
                article = fetch_result.get('result', {}).get(pmid, {})
                if article:
                    authors = [author.get('name', '') for author in article.get('authors', [])]
                    results.append({
                        'query': query,
                        'title': article.get('title', 'No title'),
                        'source': 'PubMed',
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        'snippet': article.get('title', '') + ' - ' + ', '.join(authors[:3]),
                        'metadata': {
                            'pmid': pmid,
                            'authors': authors,
                            'pub_date': article.get('pubdate', ''),
                            'journal': article.get('fulljournalname', ''),
                            'pub_type': article.get('pubtype', [])
                        },
                        'relevance_score': 0.9
                    })
            
            return results
            
        except Exception as e:
            print(f"[PubMed] Error searching: {e}")
            return []


class ClinicalTrialsAdapter(SearchAPIAdapter):
    """Adapter for ClinicalTrials.gov API v2"""
    
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search ClinicalTrials.gov and return standardized results"""
        try:
            params = {
                'query.term': query,
                'format': 'json',
                'pageSize': min(max_results, 100)
            }
            
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            studies = data.get('studies', [])
            
            results = []
            for study in studies[:max_results]:
                protocol = study.get('protocolSection', {})
                identification = protocol.get('identificationModule', {})
                status = protocol.get('statusModule', {})
                conditions = protocol.get('conditionsModule', {})
                interventions = protocol.get('armsInterventionsModule', {})
                
                nct_id = identification.get('nctId', 'Unknown')
                title = identification.get('officialTitle', '') or identification.get('briefTitle', 'No title')
                
                results.append({
                    'query': query,
                    'title': title,
                    'source': 'ClinicalTrials.gov',
                    'url': f"https://clinicaltrials.gov/study/{nct_id}",
                    'snippet': identification.get('briefSummary', {}).get('description', '')[:300],
                    'metadata': {
                        'nct_id': nct_id,
                        'status': status.get('overallStatus', 'Unknown'),
                        'phase': protocol.get('designModule', {}).get('phases', []),
                        'conditions': conditions.get('conditions', []),
                        'interventions': [
                            i.get('name', '') for i in interventions.get('interventions', [])
                        ],
                        'start_date': status.get('startDateStruct', {}).get('date', ''),
                        'enrollment': protocol.get('designModule', {}).get('enrollmentInfo', {}).get('count', 0)
                    },
                    'relevance_score': 0.85
                })
            
            return results
            
        except Exception as e:
            print(f"[ClinicalTrials] Error searching: {e}")
            return []


class DuckDuckGoAdapter(SearchAPIAdapter):
    """Adapter for DuckDuckGo search"""
    
    def __init__(self):
        # Try new package name first, then old one
        self.ddgs_available = False
        try:
            from ddgs import DDGS
            self.DDGS = DDGS
            self.ddgs_available = True
            print("[DuckDuckGo] Using ddgs package")
        except ImportError:
            try:
                from duckduckgo_search import DDGS
                self.DDGS = DDGS
                self.ddgs_available = True
                print("[DuckDuckGo] Using duckduckgo_search package (deprecated)")
            except ImportError:
                print("[DuckDuckGo] Neither ddgs nor duckduckgo-search installed.")
                print("Install with: pip install ddgs")
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search DuckDuckGo and return standardized results"""
        if not self.ddgs_available:
            return []
        
        try:
            results = []
            with self.DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                for i, result in enumerate(search_results):
                    results.append({
                        'query': query,
                        'title': result.get('title', 'No title'),
                        'source': 'DuckDuckGo',
                        'url': result.get('href', ''),
                        'snippet': result.get('body', ''),
                        'metadata': {},
                        'relevance_score': max(0.9 - (i * 0.05), 0.5)
                    })
            return results
                
        except Exception as e:
            print(f"[DuckDuckGo] Error searching: {e}")
            return []


class BaiduAdapter(SearchAPIAdapter):
    """Adapter for Baidu search (using web scraping as fallback)"""
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Baidu and return standardized results"""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("[Baidu] BeautifulSoup not installed. Run: pip install beautifulsoup4")
            return []
        
        try:
            url = f"https://www.baidu.com/s?wd={quote_plus(query)}&rn={max_results}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for i, item in enumerate(soup.find_all('div', class_='result', limit=max_results)):
                try:
                    title_elem = item.find('h3') or item.find('a')
                    title = title_elem.get_text(strip=True) if title_elem else 'No title'
                    
                    link_elem = item.find('a')
                    url_link = link_elem.get('href', '') if link_elem else ''
                    
                    snippet_elem = item.find('div', class_='c-abstract') or item.find('span', class_='content-right_8Zs40')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    if title and url_link:
                        results.append({
                            'query': query,
                            'title': title,
                            'source': 'Baidu',
                            'url': url_link,
                            'snippet': snippet,
                            'metadata': {},
                            'relevance_score': max(0.85 - (i * 0.05), 0.5)
                        })
                except Exception as e:
                    print(f"[Baidu] Error parsing result {i}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"[Baidu] Error searching: {e}")
            return []


class GoogleScholarAdapter(SearchAPIAdapter):
    """Adapter for Google Scholar"""
    
    def __init__(self, serpapi_key: Optional[str] = None):
        self.serpapi_key = serpapi_key
        if not serpapi_key:
            try:
                from scholarly import scholarly
                self.scholarly_available = True
            except ImportError:
                print("[GoogleScholar] Neither SerpAPI key nor scholarly package available")
                print("Install scholarly: pip install scholarly")
                self.scholarly_available = False
        else:
            self.scholarly_available = False
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Google Scholar and return standardized results"""
        
        if self.serpapi_key:
            return self._search_with_serpapi(query, max_results)
        
        if self.scholarly_available:
            return self._search_with_scholarly(query, max_results)
        
        return []
    
    def _search_with_serpapi(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using SerpAPI"""
        try:
            url = "https://serpapi.com/search"
            params = {
                'engine': 'google_scholar',
                'q': query,
                'api_key': self.serpapi_key,
                'num': max_results
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for i, item in enumerate(data.get('organic_results', [])[:max_results]):
                results.append({
                    'query': query,
                    'title': item.get('title', 'No title'),
                    'source': 'Google Scholar',
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'metadata': {
                        'cited_by': item.get('inline_links', {}).get('cited_by', {}).get('total', 0),
                        'authors': item.get('publication_info', {}).get('authors', [])
                    },
                    'relevance_score': max(0.9 - (i * 0.05), 0.5)
                })
            
            return results
            
        except Exception as e:
            print(f"[GoogleScholar/SerpAPI] Error searching: {e}")
            return []
    
    def _search_with_scholarly(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using scholarly package"""
        try:
            from scholarly import scholarly
            
            search_query = scholarly.search_pubs(query)
            results = []
            
            for i in range(max_results):
                try:
                    paper = next(search_query)
                    results.append({
                        'query': query,
                        'title': paper.get('bib', {}).get('title', 'No title'),
                        'source': 'Google Scholar',
                        'url': paper.get('pub_url', '') or paper.get('eprint_url', ''),
                        'snippet': paper.get('bib', {}).get('abstract', '')[:300],
                        'metadata': {
                            'cited_by': paper.get('num_citations', 0),
                            'authors': paper.get('bib', {}).get('author', []),
                            'year': paper.get('bib', {}).get('pub_year', '')
                        },
                        'relevance_score': max(0.9 - (i * 0.05), 0.5)
                    })
                except StopIteration:
                    break
                except Exception as e:
                    print(f"[GoogleScholar/scholarly] Error parsing result {i}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"[GoogleScholar/scholarly] Error searching: {e}")
            return []


class WebSearchAgent:
    """
    Web Search Agent — supplements DrugClaw's structured retrieval with live search.

    Search is now delegated to WebSearchSkill (DuckDuckGo + PubMed, free APIs).
    Legacy adapter classes (PubMedAdapter, DuckDuckGoAdapter, etc.) are kept in
    this file for compatibility but are no longer the primary search path.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        web_search_skill=None,       # WebSearchSkill instance (injected by DrugClawSystem)
        pubmed_email: Optional[str] = None,
        pubmed_api_key: Optional[str] = None,
        serpapi_key: Optional[str] = None,
    ):
        self.llm = llm_client
        self._web_skill = web_search_skill  # primary path

        # Legacy adapters kept as fallback when web_search_skill is None
        self.adapters = {
            'pubmed': PubMedAdapter(email=pubmed_email, api_key=pubmed_api_key),
            'clinical_trials': ClinicalTrialsAdapter(),
            'duckduckgo': DuckDuckGoAdapter(),
            'baidu': BaiduAdapter(),
            'google_scholar': GoogleScholarAdapter(serpapi_key=serpapi_key),
        }
    
    def get_system_prompt(self) -> str:
        """System prompt for the web search agent"""
        return """You are the Web Search Agent of DrugClaw — a drug-specialized agentic RAG system. You supplement the structured drug knowledge retrieval (from 68 curated resources) with live web search to fill gaps or find the latest drug-related information.

Your role is to search for drug-focused information including:

- Drug mechanisms of action and pharmacodynamics
- Drug-target interaction evidence from recent literature
- Adverse drug reactions and pharmacovigilance reports
- Drug-drug interaction warnings and clinical case reports
- Drug repurposing hypotheses and clinical trial results
- Pharmacogenomics variants affecting drug response
- Drug approval status, labeling updates, and regulatory actions
- Drug combination synergy or antagonism data

You should:
1. Prioritize drug-specific, pharmacology-focused sources over general biomedical sources
2. Generate drug-centric search queries (include drug name, target, indication, or interaction partner)
3. Retrieve and synthesize information with emphasis on clinical relevance and evidence level
4. Provide structured summaries citing the drug knowledge source
5. Distinguish between clinical evidence, experimental data, and computational predictions

Focus on accurate, recent, and authoritative drug information from sources like PubMed, FDA, DrugBank publications, and pharmacology journals."""
    
    def get_search_query_prompt(
        self,
        original_query: str,
        evidence_gaps: List[str],
        candidate_entities: List[str]
    ) -> str:
        """Generate prompt for creating search queries"""
        gaps_str = "\n".join([f"- {gap}" for gap in evidence_gaps]) if evidence_gaps else "- General information needed"
        entities_str = ", ".join(candidate_entities) if candidate_entities else "To be determined"
        
        return f"""Original Query: {original_query}

Key Entities/Concepts: {entities_str}

Information Gaps Identified:
{gaps_str}

Generate 3-5 web search queries to address the user's query and information gaps.

For each query, specify the most appropriate search source based on the information need:
- "pubmed" - for peer-reviewed research, disease mechanisms, treatment studies, molecular biology
- "clinical_trials" - for clinical trial data, treatment protocols, interventional studies
- "google_scholar" - for comprehensive academic search, systematic reviews, meta-analyses
- "duckduckgo" - for general medical information, guidelines, patient resources, recent news
- "baidu" - for Chinese medical literature or resources (if relevant)

Provide queries in JSON format:
{{
    "search_queries": [
        {{
            "query": "specific search terms",
            "purpose": "What information this query aims to find",
            "source": "most_appropriate_source"
        }}
    ]
}}"""
    
    def get_synthesis_prompt(
        self,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """Generate prompt for synthesizing search results"""
        # Group results by source
        results_by_source = {}
        for result in search_results:
            source = result.get('source', 'Unknown')
            if source not in results_by_source:
                results_by_source[source] = []
            results_by_source[source].append(result)
        
        results_str = ""
        for source, results in results_by_source.items():
            results_str += f"\n=== {source} Results ===\n"
            for i, result in enumerate(results[:5]):
                results_str += f"\nResult {i+1}:\n"
                results_str += f"Title: {result.get('title', 'N/A')}\n"
                results_str += f"URL: {result.get('url', 'N/A')}\n"
                results_str += f"Snippet: {result.get('snippet', 'N/A')[:200]}...\n"
                # Only include metadata if not empty
                metadata = result.get('metadata', {})
                if metadata:
                    # Filter out empty values
                    clean_metadata = {k: v for k, v in metadata.items() if v}
                    if clean_metadata:
                        results_str += f"Metadata: {json.dumps(clean_metadata, indent=2)}\n"
        
        return f"""Search Results from Multiple Sources:
{results_str}

Synthesize these search results into a structured summary relevant to the original query.

Organize the information based on what was found. Include sections as appropriate.

IMPORTANT: Return ONLY valid JSON. Do not include any explanatory text, code blocks, or markdown.
Ensure all string values are properly escaped and quoted.

Provide summary in this JSON format:
{{
    "key_findings": [
        {{"topic": "string", "summary": "string", "source": "string"}}
    ],
    "research_evidence": [
        {{"topic": "string", "findings": "string", "source": "string"}}
    ],
    "clinical_data": [
        {{"description": "string", "results": "string", "source": "string"}}
    ],
    "citations": [
        {{"title": "string", "url": "string", "source": "string", "relevance": "string"}}
    ]
}}"""
    
    def execute(self, state: AgentState) -> AgentState:
        """Execute web search (when needed)"""
        print(f"\n[Web Search Agent] Iteration {state.iteration}")
        
        if not self._should_search(state):
            print("[Web Search Agent] Web search not needed at this iteration")
            return state
        
        evidence_gaps = self._extract_evidence_gaps(state.reflection_feedback)
        candidate_entities = self._extract_key_entities(state.current_answer, state.original_query)
        
        print(f"[Web Search Agent] Evidence gaps: {evidence_gaps}")
        print(f"[Web Search Agent] Key entities: {candidate_entities}")
        
        search_queries = self._generate_search_queries(
            state.original_query,
            evidence_gaps,
            candidate_entities
        )
        
        if not search_queries:
            print("[Web Search Agent] No search queries generated")
            return state
        
        print(f"[Web Search Agent] Generated {len(search_queries)} search queries")
        
        all_search_results = self._execute_searches(search_queries)
        
        if not all_search_results:
            print("[Web Search Agent] No search results found")
            return state
        
        print(f"[Web Search Agent] Found {len(all_search_results)} total results")
        
        synthesis = self._synthesize_results(all_search_results)
        
        state.web_search_results = all_search_results
        
        if all_search_results:
            state.current_answer += (
                f"\n\n## Web Search Evidence\n"
                f"{self._format_synthesis(synthesis)}"
            )
        
        return state
    
    def _should_search(self, state: AgentState) -> bool:
        """Determine if web search is needed"""
        if state.iteration == 0:
            return False
        
        if not state.evidence_sufficient:
            marginal_gain = state.get_marginal_gain()
            if marginal_gain < self.llm.config.EVIDENCE_THRESHOLD_EPSILON:
                return True
        
        if state.reflection_feedback:
            search_keywords = [
                'clinical', 'trial', 'study', 'research', 'publication',
                'evidence', 'data', 'literature', 'recent', 'current',
                'guideline', 'protocol', 'standard', 'FDA', 'approved',
                'patient', 'outcome', 'statistics', 'epidemiology'
            ]
            if any(kw in state.reflection_feedback.lower() for kw in search_keywords):
                return True
        
        return False
    
    def _extract_evidence_gaps(self, reflection: str) -> List[str]:
        """Extract evidence gaps from reflection feedback"""
        if not reflection:
            return ["General information needed"]
        
        gaps = []
        reflection_lower = reflection.lower()
        
        gap_patterns = {
            'clinical': ['clinical', 'trial', 'treatment', 'intervention'],
            'research': ['research', 'study', 'publication', 'literature'],
            'mechanism': ['mechanism', 'pathway', 'molecular', 'biological'],
            'epidemiology': ['prevalence', 'incidence', 'epidemiology', 'population'],
            'safety': ['safety', 'adverse', 'side effect', 'toxicity', 'risk'],
            'efficacy': ['efficacy', 'effectiveness', 'outcome', 'result'],
            'guideline': ['guideline', 'protocol', 'standard', 'recommendation'],
            'diagnostic': ['diagnostic', 'diagnosis', 'screening', 'detection'],
            'data': ['data', 'statistics', 'measurement', 'quantitative']
        }
        
        for gap_type, keywords in gap_patterns.items():
            if any(kw in reflection_lower for kw in keywords):
                gaps.append(f"{gap_type.capitalize()} information needed")
        
        return gaps if gaps else ["General information needed"]
    
    def _extract_key_entities(self, answer: str, query: str) -> List[str]:
        """Extract key entities from answer and query"""
        entities = []
        text = (answer or "") + " " + (query or "")
        
        if not text.strip():
            return entities
        
        patterns = [
            r'\b[A-Z][a-z]+(?:mab|nib|pril|sartan|statin|cillin|mycin|olol|pam|ine|ide|one)\b',
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b',
            r'\b[A-Z]{2,}[0-9]*\b',
            r'\b[A-Z]{2,5}\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        common_words = {'The', 'This', 'That', 'With', 'From', 'And', 'For', 'Are', 'But', 'Not', 'Can', 'May'}
        entities = [e for e in set(entities) if e not in common_words]
        
        return entities[:10]
    
    def _generate_search_queries(
        self,
        query: str,
        gaps: List[str],
        entities: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate web search queries using LLM"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self.get_search_query_prompt(
                query, gaps, entities
            )}
        ]
        
        try:
            result = self.llm.generate_json(messages, temperature=0.3)
            queries = result.get("search_queries", [])
            
            for q in queries:
                if 'source' not in q or q['source'] not in self.adapters:
                    q['source'] = 'pubmed'
            
            return queries
            
        except Exception as e:
            print(f"[Web Search Agent] Error generating queries: {e}")
            return self._generate_fallback_queries(query, entities)
    
    def _generate_fallback_queries(
        self, 
        query: str, 
        entities: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate fallback queries if LLM fails"""
        queries = []
        
        queries.append({
            'query': query,
            'purpose': 'Find research literature',
            'source': 'pubmed'
        })
        
        clinical_keywords = ['treatment', 'therapy', 'trial', 'patient', 'clinical']
        if any(kw in query.lower() for kw in clinical_keywords):
            queries.append({
                'query': query,
                'purpose': 'Find clinical trials',
                'source': 'clinical_trials'
            })
        
        queries.append({
            'query': query,
            'purpose': 'Find general information',
            'source': 'duckduckgo'
        })
        
        return queries
    
    def _execute_searches(
        self,
        queries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute web searches — uses WebSearchSkill if available, else legacy adapters."""
        all_results: List[Dict[str, Any]] = []

        for query_info in queries:
            query_str = query_info.get("query", "")
            purpose   = query_info.get("purpose", "Search")
            if not query_str:
                continue
            print(f"[Web Search Agent] Searching for: {query_str}")

            if self._web_skill is not None:
                # Primary path: WebSearchSkill (DuckDuckGo + PubMed)
                try:
                    rr_list = self._web_skill.search(query_str, max_results=6)
                    for rr in rr_list:
                        meta = rr.metadata or {}
                        all_results.append({
                            "title":   meta.get("title", rr.target_entity),
                            "url":     (rr.sources or [""])[0],
                            "snippet": rr.evidence_text,
                            "source":  rr.source,
                            "metadata": meta,
                            "search_purpose": purpose,
                        })
                    print(f"[Web Search Agent] WebSearchSkill returned {len(rr_list)} results")
                except Exception as exc:
                    print(f"[Web Search Agent] WebSearchSkill error: {exc}")
            else:
                # Legacy fallback: adapter routing
                source  = query_info.get("source", "pubmed")
                adapter = self.adapters.get(source) or self.adapters["pubmed"]
                try:
                    results = adapter.search(query_str, max_results=5)
                    for r in results:
                        r["search_purpose"] = purpose
                    all_results.extend(results)
                except Exception as exc:
                    print(f"[Web Search Agent] Legacy adapter error: {exc}")

            time.sleep(0.3)

        # Deduplicate by URL
        seen: set = set()
        unique: List[Dict[str, Any]] = []
        for r in all_results:
            url = r.get("url", "")
            if url and url not in seen:
                seen.add(url)
                unique.append(r)
            elif not url:
                unique.append(r)
        return unique

    # ------------------------------------------------------------------
    # WEB_ONLY mode — direct search without graph reasoning
    # ------------------------------------------------------------------

    def execute_direct(self, state: AgentState) -> AgentState:
        """
        WEB_ONLY mode: search the original query directly (no evidence gap analysis).

        Flow: generate search queries → search → synthesize → set current_answer.
        Does not require any prior retrieval or graph building.
        """
        print(f"\n[Web Search Agent] WEB_ONLY direct search")
        query = state.original_query

        # Generate search queries from the raw query
        search_queries = self._generate_fallback_queries(query)
        print(f"[Web Search Agent] Generated {len(search_queries)} queries")

        all_results = self._execute_searches(search_queries)
        if not all_results:
            state.current_answer = (
                "No web search results found. Check your network or try a different query."
            )
            return state

        print(f"[Web Search Agent] Total results: {len(all_results)}")
        synthesis = self._synthesize_results(all_results)
        state.web_search_results = all_results

        answer_parts = [
            f"## Web Search Results for: {query}\n",
            self._format_synthesis(synthesis),
        ]
        state.current_answer = "\n".join(answer_parts)
        print(f"[Web Search Agent] Direct answer ({len(state.current_answer)} chars)")
        return state
    
    def _clean_json_string(self, text: str) -> str:
        """Clean and fix common JSON issues in LLM output"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Fix common escaping issues
        text = text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _synthesize_results(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize search results using LLM"""
        if not results:
            return {}
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self.get_synthesis_prompt(results)}
        ]
        
        try:
            # Try to get JSON from LLM
            synthesis = self.llm.generate_json(messages, temperature=0.3)
            return synthesis
            
        except json.JSONDecodeError as e:
            print(f"[Web Search Agent] JSON decode error: {e}")
            print("[Web Search Agent] Falling back to basic synthesis")
            return self._create_basic_synthesis(results)
            
        except Exception as e:
            print(f"[Web Search Agent] Error synthesizing results: {e}")
            return self._create_basic_synthesis(results)
    
    def _create_basic_synthesis(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a basic synthesis when LLM fails"""
        synthesis = {
            'key_findings': [],
            'research_evidence': [],
            'clinical_data': [],
            'citations': []
        }
        
        for result in results[:15]:
            source = result.get('source', '')
            
            if source == 'ClinicalTrials.gov':
                metadata = result.get('metadata', {})
                synthesis['clinical_data'].append({
                    'description': result.get('title', 'N/A'),
                    'results': f"Status: {metadata.get('status', 'N/A')}, Phase: {', '.join(metadata.get('phase', []))}",
                    'source': result.get('url', '')
                })
            
            elif source == 'PubMed':
                synthesis['research_evidence'].append({
                    'topic': result.get('title', 'N/A'),
                    'findings': result.get('snippet', '')[:200],
                    'source': result.get('url', '')
                })
            
            else:
                synthesis['key_findings'].append({
                    'topic': result.get('title', 'N/A'),
                    'summary': result.get('snippet', '')[:200],
                    'source': result.get('source', 'N/A')
                })
            
            synthesis['citations'].append({
                'title': result.get('title', 'N/A'),
                'url': result.get('url', ''),
                'source': source,
                'relevance': result.get('search_purpose', 'Related information')
            })
        
        return synthesis
    
    def _format_synthesis(self, synthesis: Dict[str, Any]) -> str:
        """Format synthesis for inclusion in answer"""
        if not synthesis:
            return "No additional evidence found from web search."
        
        sections = []
        
        findings = synthesis.get('key_findings', [])
        if findings:
            sections.append("### Key Findings:")
            for finding in findings[:5]:
                sections.append(f"- **{finding.get('topic', 'N/A')}**: {finding.get('summary', 'N/A')}")
            sections.append("")
        
        research = synthesis.get('research_evidence', [])
        if research:
            sections.append("### Research Evidence:")
            for item in research[:5]:
                sections.append(f"- {item.get('topic', 'N/A')}")
                sections.append(f"  {item.get('findings', 'N/A')}")
                sections.append(f"  [Source]({item.get('source', '#')})")
            sections.append("")
        
        clinical = synthesis.get('clinical_data', [])
        if clinical:
            sections.append("### Clinical Trials/Studies:")
            for item in clinical[:5]:
                sections.append(f"- **{item.get('description', 'N/A')}**")
                sections.append(f"  {item.get('results', 'N/A')}")
                sections.append(f"  [Details]({item.get('source', '#')})")
            sections.append("")
        
        citations = synthesis.get('citations', [])
        if citations:
            sections.append("### References:")
            for i, cite in enumerate(citations[:10], 1):
                sections.append(
                    f"{i}. [{cite.get('title', 'N/A')}]({cite.get('url', '#')}) "
                    f"({cite.get('source', 'N/A')})"
                )
        
        return "\n".join(sections) if sections else "No structured evidence available."

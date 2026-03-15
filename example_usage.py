"""
DrugClaw — Example Usage
========================

Demonstrates the three thinking modes and resource_filter parameter.

Thinking modes
--------------
  ThinkingMode.GRAPH    (default) — full multi-agent graph reasoning:
                                    retrieve → rerank → respond → reflect → [web search]
  ThinkingMode.SIMPLE             — 1-round flat retrieval → LLM synthesis (fast)
  ThinkingMode.WEB_ONLY           — DuckDuckGo + PubMed only, no structured skill retrieval

Optional parameters (any mode)
-------------------------------
  resource_filter  : list[str]  — restrict to specific skill names, e.g. ["ChEMBL","DGIdb"]
  omics_constraints: OmicsConstraints — biological constraints (genes, pathways, diseases)

Implemented skills (25)
-----------------------
  DTI:            ChEMBL, BindingDB, DGIdb, Open Targets Platform, TTD, STITCH
  ADR:            FAERS, SIDER
  Knowledgebase:  UniD3, DrugBank, IUPHAR/BPS Guide to Pharmacology, DrugCentral, CPIC
  Mechanism:      DRUGMECHDB
  Labeling:       openFDA Human Drug, DailyMed, MedlinePlus Drug Info
  Ontology:       RxNorm, ChEBI
  Repurposing:    RepoDB
  Pharmacogenomics: PharmGKB
  DDI:            MecDDI, DDInter, KEGG Drug
  Drug Review:    WebMD Drug Reviews
  Web Search:     WebSearch (always-on)
"""

from drugclaw.config import Config
from drugclaw.models import OmicsConstraints, ThinkingMode
from drugclaw.main_system import DrugClawSystem


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _print_result(result: dict) -> None:
    mode = result.get("mode", "?")
    rf   = result.get("resource_filter", [])
    print(f"\n--- Result Summary ---")
    print(f"  Mode            : {mode}")
    if rf:
        print(f"  Resource filter : {rf}")
    print(f"  Iterations      : {result.get('iterations', 'N/A')}")
    print(f"  Graph size      : {result.get('evidence_graph_size', 'N/A')} entities")
    reward = result.get("final_reward", 0.0)
    if isinstance(reward, float):
        print(f"  Final reward    : {reward:.3f}")
    print(f"  Success         : {result.get('success', False)}")
    web = result.get("web_search_results", [])
    if web:
        print(f"  Web results     : {len(web)}")


# ---------------------------------------------------------------------------
# Example 1 — GRAPH mode (default), plain query
# ---------------------------------------------------------------------------

def example_1_graph_basic():
    """Full multi-agent graph reasoning on an adverse event query."""
    print("\n" + "="*80)
    print("EXAMPLE 1: GRAPH mode — FAERS adverse events for ibuprofen")
    print("="*80)

    system = DrugClawSystem(Config())

    result = system.query(
        "Give me information about the drug ANTIMICROBIAL?",
        thinking_mode=ThinkingMode.GRAPH,   # default; can be omitted
        resource_filter=["UniD3"],  # pin to specific skills (optional
    )
    _print_result(result)


# ---------------------------------------------------------------------------
# Example 2 — GRAPH mode + omics_constraints + resource_filter
# ---------------------------------------------------------------------------

def example_2_graph_constrained():
    """Graph reasoning restricted to two specific resources with biological constraints."""
    print("\n" + "="*80)
    print("EXAMPLE 2: GRAPH mode — resource_filter + OmicsConstraints")
    print("="*80)

    system = DrugClawSystem(Config())

    constraints = OmicsConstraints(
        gene_sets=["INS", "INSR", "IRS1", "PIK3CA", "AKT1"],
        pathway_sets=["Insulin signaling pathway", "PI3K-Akt signaling"],
        disease_terms=["Type 2 Diabetes", "Diabetes Mellitus"],
        tissue_types=["pancreas", "muscle", "liver"],
    )

    result = system.query(
        "Find drugs targeting insulin signaling that could treat type 2 diabetes",
        thinking_mode=ThinkingMode.GRAPH,
        # Only query ChEMBL and Open Targets — skip LLM skill selection
        resource_filter=["ChEMBL", "Open Targets Platform"],
        omics_constraints=constraints,
    )
    _print_result(result)

    # Show reasoning history if available
    for step in result.get("reasoning_history", []):
        print(f"\n  [Iteration {step['step']}]"
              f"  reward={step['reward']:.3f}"
              f"  sufficiency={step['evidence_sufficiency']:.3f}")


# ---------------------------------------------------------------------------
# Example 3 — SIMPLE mode (fast, 1-round retrieval)
# ---------------------------------------------------------------------------

def example_3_simple():
    """
    SIMPLE mode: one retrieval round, flat evidence list → LLM synthesises answer.
    No graph building, no reflection loop.  Good for quick factual lookups.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: SIMPLE mode — ADR lookup for aspirin")
    print("="*80)

    system = DrugClawSystem(Config())

    result = system.query(
        "What are the known adverse drug reactions of aspirin?",
        thinking_mode=ThinkingMode.SIMPLE,
        # Pin to the two implemented ADR skills
        resource_filter=["SIDER", "FAERS"],
    )
    _print_result(result)


# ---------------------------------------------------------------------------
# Example 4 — SIMPLE mode, no resource_filter (LLM picks skills)
# ---------------------------------------------------------------------------

def example_4_simple_auto():
    """SIMPLE mode where the LLM still selects skills (no resource_filter)."""
    print("\n" + "="*80)
    print("EXAMPLE 4: SIMPLE mode — DDI check, LLM-selected skills")
    print("="*80)

    system = DrugClawSystem(Config())

    result = system.query(
        "Are there any dangerous interactions between warfarin and NSAIDs?",
        thinking_mode=ThinkingMode.SIMPLE,
    )
    _print_result(result)


# ---------------------------------------------------------------------------
# Example 5 — WEB_ONLY mode (DuckDuckGo + PubMed, no structured retrieval)
# ---------------------------------------------------------------------------

def example_5_web_only():
    """
    WEB_ONLY mode: skips all structured skills, searches DuckDuckGo + PubMed.
    Useful for very recent data, news, or broad literature sweeps.
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: WEB_ONLY mode — latest COVID drug repurposing news")
    print("="*80)

    system = DrugClawSystem(Config())

    result = system.query(
        "What drugs are currently being investigated for COVID-19 treatment in 2024?",
        thinking_mode=ThinkingMode.WEB_ONLY,
        # resource_filter is ignored in WEB_ONLY mode
    )
    _print_result(result)
    web = result.get("web_search_results", [])
    for i, r in enumerate(web[:3], 1):
        print(f"\n  [{i}] {r.get('source','?')} — {r.get('title','(no title)')[:80]}")
        url = r.get("url", "")
        if url:
            print(f"      {url}")


# ---------------------------------------------------------------------------
# Example 6 — GRAPH mode + cancer repurposing (multi-gene constraints)
# ---------------------------------------------------------------------------

def example_6_cancer_repurposing():
    """Full graph reasoning for cancer drug repurposing with gene constraints."""
    print("\n" + "="*80)
    print("EXAMPLE 6: GRAPH mode — triple-negative breast cancer repurposing")
    print("="*80)

    config = Config()
    config.MAX_ITERATIONS = 3          # allow up to 3 reflect-retrieve loops
    config.MIN_EVIDENCE_SCORE = 0.65   # accept slightly lower evidence threshold

    system = DrugClawSystem(config)

    constraints = OmicsConstraints(
        gene_sets=["TP53", "BRCA1", "EGFR", "PTEN", "MYC"],
        pathway_sets=["EGFR signaling", "DNA repair", "Cell cycle"],
        disease_terms=["Triple-negative breast cancer", "TNBC"],
    )

    result = system.query(
        "Identify approved drugs that could be repurposed to treat triple-negative breast cancer",
        thinking_mode=ThinkingMode.GRAPH,
        omics_constraints=constraints,
    )
    _print_result(result)


# ---------------------------------------------------------------------------
# Example 7 — resource_filter with SIMPLE mode (pin exact skills)
# ---------------------------------------------------------------------------

def example_7_pinned_resources_simple():
    """
    Pin multiple implemented skills across different subcategories in SIMPLE mode.
    Useful when you know exactly which knowledge bases are relevant.
    """
    print("\n" + "="*80)
    print("EXAMPLE 7: SIMPLE mode — multi-resource pin (DDI + labeling + ontology)")
    print("="*80)

    system = DrugClawSystem(Config())

    result = system.query(
        "What is known about metformin drug interactions and prescribing information?",
        thinking_mode=ThinkingMode.SIMPLE,
        resource_filter=[
            "MecDDI",       # mechanism-based DDI
            "DDInter",      # drug-drug interactions
            "DailyMed",     # prescribing / labeling
            "RxNorm",       # drug nomenclature / ontology
            "ChEMBL",       # bioactivity
        ],
    )
    _print_result(result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    examples = [
        ("GRAPH — basic",                    example_1_graph_basic),
        ("GRAPH — constrained + filter",     example_2_graph_constrained),
        ("SIMPLE — ADR lookup (pinned)",     example_3_simple),
        ("SIMPLE — DDI check (auto-select)", example_4_simple_auto),
        ("WEB_ONLY — COVID 2024",            example_5_web_only),
        ("GRAPH — cancer repurposing",       example_6_cancer_repurposing),
        ("SIMPLE — multi-resource pin",      example_7_pinned_resources_simple),
    ]

    print("\n" + "="*80)
    print("DrugClaw — Usage Examples")
    print("="*80)

    for i, (name, fn) in enumerate(examples, 1):
        try:
            print(f"\n\n### Running Example {i}: {name} ###")
            fn()
        except Exception as exc:
            import traceback
            print(f"\nExample {i} failed: {exc}")
            traceback.print_exc()

    print("\n\n" + "="*80)
    print("ALL EXAMPLES COMPLETED")
    print("="*80)


if __name__ == "__main__":
    # Run a single quick example by default
    # example_1_graph_basic()
    example_2_graph_constrained()
    # example_3_simple()
    # example_4_simple_auto()
    # example_5_web_only()
    # example_6_cancer_repurposing()
    # example_7_pinned_resources_simple()

    # Uncomment to run all examples:
    # main()

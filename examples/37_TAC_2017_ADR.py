"""
TAC 2017 ADR - Adverse Drug Reaction Extraction from Drug Labels
Category: Drug-centric | Type: Dataset | Subcategory: Drug NLP/Text Mining
Link: https://bionlp.nlm.nih.gov/tac2017adversereactions/
Paper: https://tac.nist.gov/publications/2017/additional.papers/TAC2017.ADR_overview.proceedings.pdf

TAC 2017 ADR provides FDA drug labels annotated with adverse reactions,
including reaction mentions, MedDRA normalization, and severity levels.

Access method:
  - Registration required at https://bionlp.nlm.nih.gov/tac2017adversereactions/
  - After registration, download the dataset from the portal.
  - HuggingFace mirror: https://huggingface.co/datasets/bigbio/tac2017_adr

This script shows how to use the HuggingFace mirror.
"""


def load_tac2017_from_huggingface():
    """Load TAC 2017 ADR dataset via HuggingFace."""
    try:
        from datasets import load_dataset
        print("Loading TAC 2017 ADR from HuggingFace (bigbio/tac2017_adr) ...")
        dataset = load_dataset("bigbio/tac2017_adr",
                               name="tac2017_adr_bigbio_kb",
                               trust_remote_code=True)
        print(f"Splits: {list(dataset.keys())}")
        split = list(dataset.values())[0]
        print(f"Examples in first split: {len(split)}")
        example = split[0]
        print(f"\nFirst example ID: {example.get('id')}")
        passages = example.get("passages", [])
        for p in passages[:1]:
            print(f"  Text: {p.get('text', [''])[0][:200]}")
        entities = example.get("entities", [])
        print(f"\nEntities ({len(entities)} total):")
        for ent in entities[:3]:
            print(f"  Type: {ent.get('type')} | Text: {ent.get('text', [''])[0][:50]}")
        return dataset
    except ImportError:
        print("Install HuggingFace datasets: pip install datasets")
        return None
    except Exception as e:
        print(f"Error loading TAC 2017 ADR: {e}")
        print(
            "For direct access, register at:\n"
            "  https://bionlp.nlm.nih.gov/tac2017adversereactions/"
        )
        return None


def describe_tac2017():
    print("=== TAC 2017 ADR Dataset ===")
    print("Source: FDA drug package inserts (label sections)")
    print("Sections annotated: Adverse Reactions, Boxed Warnings, Warnings and Precautions")
    print("Annotation types:")
    print("  - AdverseReaction (drug side effect mentions)")
    print("  - Severity (mild, moderate, severe)")
    print("  - Factor (condition modifiers)")
    print("  - DrugClass, Negation, Animal")
    print("Normalization: MedDRA preferred terms")
    print("Stats: 200 drug labels, ~2,700 ADR mentions")


if __name__ == "__main__":
    describe_tac2017()
    print()
    load_tac2017_from_huggingface()

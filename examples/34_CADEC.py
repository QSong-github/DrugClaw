"""
CADEC - CSIRO Adverse Drug Event Corpus
Category: Drug-centric | Type: Dataset | Subcategory: Drug NLP/Text Mining
Link: https://data.csiro.au/collection/csiro:10948
Paper: https://www.sciencedirect.com/science/article/pii/S1532046415000532

CADEC is annotated with adverse drug event mentions extracted from patient
forum posts (AskaPatient.com), enabling NLP research on consumer health text.

Access method:
  1. CSIRO Data Access Portal: https://data.csiro.au/collection/csiro:10948
     (requires free registration)
  2. HuggingFace mirror: https://huggingface.co/datasets/bigbio/cadec

This script uses the HuggingFace version (no registration required).
"""


def load_cadec_from_huggingface():
    """Load CADEC via HuggingFace datasets library."""
    try:
        from datasets import load_dataset
        print("Loading CADEC from HuggingFace (bigbio/cadec) ...")
        dataset = load_dataset("bigbio/cadec",
                               name="cadec_bigbio_kb",
                               trust_remote_code=True)
        print(f"Splits: {list(dataset.keys())}")
        train = dataset["train"]
        print(f"Train examples: {len(train)}")
        example = train[0]
        print(f"\nFirst example ID: {example['id']}")
        passages = example.get("passages", [])
        for p in passages[:1]:
            print(f"  Text snippet: {p.get('text', [''])[0][:200]}")
        entities = example.get("entities", [])
        print(f"\nEntities ({len(entities)} total):")
        for ent in entities[:5]:
            print(f"  Type: {ent.get('type')} | "
                  f"Text: {ent.get('text', [''])[0][:50]}")
        return dataset
    except ImportError:
        print("Install HuggingFace datasets: pip install datasets")
        return None
    except Exception as e:
        print(f"Error loading CADEC: {e}")
        print("Try loading without bigbio schema:")
        print("  ds = load_dataset('bigbio/cadec')")
        return None


def describe_cadec():
    print("=== CADEC Dataset Schema ===")
    print("Source: AskaPatient.com patient forum posts")
    print("Annotation types:")
    print("  - ADR (Adverse Drug Reaction)")
    print("  - Drug (medication mentions)")
    print("  - Disease (condition mentions)")
    print("  - Symptom")
    print("  - Finding")
    print("Normalization: MedDRA for ADRs, AMT for drugs")
    print("\nStats: ~1,250 posts, ~7,600 annotations")


if __name__ == "__main__":
    describe_cadec()
    print()
    load_cadec_from_huggingface()

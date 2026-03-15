"""
PsyTAR - Psychiatric Treatment Adverse Reaction Corpus
Category: Drug-centric | Type: Dataset | Subcategory: Drug NLP/Text Mining
Link: https://huggingface.co/datasets/bigbio/psytar
Paper: https://dl.acm.org/doi/10.1016/j.jbi.2018.12.005

PsyTAR contains annotated user reviews for psychiatric medications, labeled
with adverse drug reactions, drug indications, and withdrawal symptoms.

Access method: HuggingFace datasets library.
"""


def load_psytar():
    """Load PsyTAR dataset from HuggingFace."""
    try:
        from datasets import load_dataset
        print("Loading PsyTAR from HuggingFace (bigbio/psytar) ...")
        dataset = load_dataset("bigbio/psytar",
                               name="psytar_bigbio_text",
                               trust_remote_code=True)
        print(f"Splits: {list(dataset.keys())}")
        train = dataset.get("train", list(dataset.values())[0])
        print(f"Total examples: {len(train)}")
        example = train[0]
        print(f"\nFirst example ID: {example.get('id')}")
        print(f"Text: {str(example.get('text', ''))[:200]}")
        print(f"Labels: {example.get('labels', example.get('label', 'N/A'))}")
        return dataset
    except ImportError:
        print("Install HuggingFace datasets: pip install datasets")
        return None
    except Exception as e:
        print(f"Error: {e}")
        # Try default config
        try:
            from datasets import load_dataset
            dataset = load_dataset("bigbio/psytar", trust_remote_code=True)
            return dataset
        except Exception as e2:
            print(f"Also failed with default config: {e2}")
            return None


def describe_psytar():
    print("=== PsyTAR Dataset ===")
    print("Source: AskaPatient.com reviews for psychiatric drugs")
    print("Drugs covered: Zoloft, Lexapro, Cymbalta, Effexor, Wellbutrin, etc.")
    print("Annotation types:")
    print("  - ADR (Adverse Drug Reaction)")
    print("  - WD (Withdrawal Symptom)")
    print("  - EF (Effectiveness)")
    print("  - DI (Drug Indication)")
    print("Stats: ~891 reviews, ~6,000 sentence-level annotations")
    print("\nHuggingFace: https://huggingface.co/datasets/bigbio/psytar")


if __name__ == "__main__":
    describe_psytar()
    print()
    load_psytar()

"""
n2c2 2018 Track 2 - Drug and Adverse Event Extraction from Clinical Notes
Category: Drug-centric | Type: Dataset | Subcategory: Drug NLP/Text Mining
Link: https://huggingface.co/datasets/bigbio/n2c2_2018_track2
Paper: https://academic.oup.com/jamia/article-abstract/27/1/3/5581277

n2c2 2018 Track 2 provides annotated clinical discharge summaries for
extraction of adverse drug events and medication entities.

Access method: Via HuggingFace datasets library.
Note: Requires accepting the dataset agreement on HuggingFace.
"""


def load_n2c2_from_huggingface():
    """
    Load the n2c2 2018 Track 2 dataset via HuggingFace datasets.
    Requires: pip install datasets
    Note: May require HuggingFace login and dataset agreement acceptance.
    """
    try:
        from datasets import load_dataset
        print("Loading n2c2_2018_track2 from HuggingFace ...")
        # bigbio schema for NLP benchmarking
        dataset = load_dataset("bigbio/n2c2_2018_track2",
                               name="n2c2_2018_track2_bigbio_kb",
                               trust_remote_code=True)
        print(f"Dataset splits: {list(dataset.keys())}")
        print(f"Train examples: {len(dataset['train'])}")
        # Preview first example
        example = dataset["train"][0]
        print(f"\nFirst document ID: {example.get('id')}")
        print(f"Passages: {len(example.get('passages', []))}")
        entities = example.get("entities", [])
        print(f"Entities: {len(entities)}")
        for ent in entities[:3]:
            print(f"  Type: {ent.get('type')} | Text: {ent.get('text', [''])[0][:50]}")
        return dataset
    except ImportError:
        print("Install HuggingFace datasets: pip install datasets")
        return None
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print(
            "Some n2c2 datasets require accepting data use agreements.\n"
            "Visit https://huggingface.co/datasets/bigbio/n2c2_2018_track2\n"
            "or https://portal.dbmi.hms.harvard.edu/ to request access."
        )
        return None


def describe_dataset():
    """Describe the n2c2 2018 Track 2 dataset schema."""
    print("=== n2c2 2018 Track 2 Dataset Schema ===")
    print("Task: Adverse Drug Event extraction from clinical notes")
    print("Source: MIMIC-III discharge summaries")
    print("Entity types:")
    print("  - Drug (medication name)")
    print("  - ADE (adverse drug event)")
    print("  - Reason (indication for drug)")
    print("  - Frequency, Dosage, Route, Duration, Strength, Form")
    print("Relation types:")
    print("  - Drug-ADE, Drug-Reason, Drug-Frequency, ...")
    print("\nAccess via HuggingFace:")
    print("  from datasets import load_dataset")
    print("  ds = load_dataset('bigbio/n2c2_2018_track2', name='n2c2_2018_track2_bigbio_kb')")


if __name__ == "__main__":
    describe_dataset()
    print("\n=== Attempting to load dataset ===")
    dataset = load_n2c2_from_huggingface()

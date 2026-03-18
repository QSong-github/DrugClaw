# LiverTox Entity Lookup Skill

## Description

Retrieve liver toxicity information for drug entities from the LiverTox knowledge base (NCBI Bookshelf NBK547852).

This skill searches the structured NXML documents and returns relevant sections mentioning the entities.

## Example Entities

acetaminophen  
amoxicillin  
isoniazid  

Multiple entities can be queried together.

Example entity list:

acetaminophen  
amoxicillin  

## Output

Returns JSON containing relevant sections.

Example:

{
  "acetaminophen": [
    {
      "section": "Hepatotoxicity",
      "snippet": "Acetaminophen overdose is the most common cause..."
    }
  ]
}

## Notes

- Entity matching is case-insensitive.
- Up to 5 relevant sections are returned for each entity.
- Data source: LiverTox (NCBI Bookshelf NBK547852).
## CLI Usage (Fallback)

When vibe coding fails, run the skill script directly from the command line:

```bash
python skills/drug_toxicity/livertox/livertox_skill.py <entity1> [entity2] ...
```

**Example:**
```bash
python skills/drug_toxicity/livertox/livertox_skill.py aspirin
```

The script imports functions from the sibling `example.py`, executes the query, and prints LLM-readable results to stdout.

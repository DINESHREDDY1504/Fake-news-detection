import json
import logging
from typing import Dict, List, Any

# Canonical schema derived from docs/dataset_requirements.md
REQUIRED_FIELDS = {"article_id", "headline", "label"}
OPTIONAL_FIELDS = {"body", "image_path", "source_name", "source_url", "publication_date", "dataset_name", "original_record_id"}
VALID_LABELS = {"real", "fake", "unknown"}

def load_dataset(filepath: str) -> List[Dict[str, Any]]:
    """Loads a JSON or JSONL dataset file."""
    records = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            if filepath.endswith(".jsonl"):
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
            elif filepath.endswith(".json"):
                data = json.load(f)
                if isinstance(data, list):
                    records.extend(data)
                elif isinstance(data, dict) and "data" in data: # Common pattern
                     records.extend(data["data"])
                else:
                    logging.warning(f"Unexpected JSON structure in {filepath}")
            else:
                 logging.warning(f"Unsupported file format: {filepath}")
    except Exception as e:
        logging.error(f"Error loading {filepath}: {e}")
    return records

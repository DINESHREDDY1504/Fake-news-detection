import csv
import json
import logging
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ['article_id', 'headline', 'label']
OPTIONAL_COLUMNS = [
    'body', 'image_path', 'source_name', 'source_url',
    'publication_date', 'dataset_name', 'original_record_id'
]

# Explicit Label Mapping Policy
LABEL_MAPPING = {
    # Map to real
    'true': 'real',
    'real': 'real',
    'verified': 'real',
    'accurate': 'real',

    # Map to fake
    'false': 'fake',
    'fake': 'fake',
    'pants on fire': 'fake',
    'fabricated': 'fake',

    # Map to unknown
    'unknown': 'unknown',
    'disputed': 'unknown',
    'mixed': 'unknown',
    'half-true': 'unknown',
    'mostly true': 'unknown',
    'satire': 'unknown',
    'unlabeled': 'unknown'
}

class DatasetLoader:
    def __init__(self, mapping: Optional[Dict[str, str]] = None, strict_labels: bool = False):
        """
        Initializes the dataset loader.

        Args:
            mapping: A dictionary mapping source file columns to canonical columns.
            strict_labels: If True, exclude records with 'unknown' labels.
        """
        self.mapping = mapping or {}
        self.strict_labels = strict_labels
        self.records: List[Dict[str, Any]] = []
        self.report = {
            'total_rows_processed': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'missing_required_fields': 0,
            'unknown_labels_dropped': 0,
            'errors': []
        }

    def _normalize_label(self, raw_label: str) -> str:
        """Normalizes a raw label to 'real', 'fake', or 'unknown'."""
        if not raw_label:
            return 'unknown'

        clean_label = str(raw_label).strip().lower()
        return LABEL_MAPPING.get(clean_label, 'unknown')

    def load(self, filepath: str) -> List[Dict[str, Any]]:
        """Loads a dataset from a CSV or TSV file."""
        if not filepath.endswith('.csv') and not filepath.endswith('.tsv') and not filepath.endswith('.txt'):
            self.report['errors'].append(f"Unsupported format for file: {filepath}")
            return []

        delimiter = '\t' if filepath.endswith('.tsv') else ','

        try:
            with open(filepath, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                # Check for empty file
                if not reader.fieldnames:
                    self.report['errors'].append(f"Empty or missing header in file: {filepath}")
                    return []

                for row_num, row in enumerate(reader, start=1):
                    self.report['total_rows_processed'] += 1
                    mapped_row = self._map_row(row)

                    if self._validate_row(mapped_row, row_num):
                        normalized_label = self._normalize_label(mapped_row['label'])

                        if normalized_label == 'unknown' and self.strict_labels:
                            self.report['unknown_labels_dropped'] += 1
                            self.report['invalid_records'] += 1
                        else:
                            mapped_row['label'] = normalized_label
                            self.records.append(mapped_row)
                            self.report['valid_records'] += 1
                    else:
                        self.report['invalid_records'] += 1

        except FileNotFoundError:
            self.report['errors'].append(f"File not found: {filepath}")
        except Exception as e:
            self.report['errors'].append(f"Error loading {filepath}: {str(e)}")

        return self.records

    def _map_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Maps original row columns to canonical columns."""
        mapped = {}
        for canonical_col in REQUIRED_COLUMNS + OPTIONAL_COLUMNS:
            # If mapping is provided, look up the source column name
            source_col = self.mapping.get(canonical_col, canonical_col)
            # Fetch from the row, defaulting to None if missing
            val = row.get(source_col)
            # Convert empty strings to None, otherwise strip
            mapped[canonical_col] = val.strip() if val else None

        return mapped

    def _validate_row(self, row: Dict[str, Any], row_num: int) -> bool:
        """Validates that a row has all required fields."""
        missing = [col for col in REQUIRED_COLUMNS if not row.get(col)]
        if missing:
            self.report['missing_required_fields'] += 1
            self.report['errors'].append(f"Row {row_num} missing required fields: {', '.join(missing)}")
            return False

        return True

    def get_integrity_report(self) -> Dict[str, Any]:
        """Returns the dataset integrity report."""
        return self.report

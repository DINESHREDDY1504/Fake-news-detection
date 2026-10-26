"""
Dataset Loading Utilities.

This module provides reusable utilities to load text-based fake-news datasets,
mapping them to the project's canonical schema.
"""

import uuid
import pandas as pd
from typing import Dict, Optional

# Expected Canonical Schema fields
CANONICAL_COLUMNS = [
    'article_id',
    'headline',
    'body',
    'label',
    'image_path',
    'source_name',
    'source_url',
    'publication_date',
    'dataset_name',
    'original_record_id'
]

REQUIRED_MAPPED_FIELDS = ['headline'] # Depending on the config, 'label' is usually required but handled in mapping. We will validate after mapping.

def load_dataset(
    filepath: str,
    column_mapping: Dict[str, str],
    label_mapping: Optional[Dict[str, str]] = None,
    dataset_name: Optional[str] = None,
    sep: str = ',',
    encoding: str = 'utf-8',
) -> pd.DataFrame:
    """
    Loads a CSV or TSV dataset and maps it to the canonical schema.

    Args:
        filepath (str): The path to the dataset file.
        column_mapping (Dict[str, str]): A dictionary mapping source column names to canonical schema fields.
        label_mapping (Optional[Dict[str, str]]): A dictionary mapping source labels to canonical labels ('real', 'fake', 'unknown').
        dataset_name (Optional[str]): A descriptive name for the dataset.
        sep (str): The delimiter for the file (default is ',').
        encoding (str): The file encoding (default is 'utf-8').

    Returns:
        pd.DataFrame: A Pandas DataFrame conforming to the canonical schema.

    Raises:
        ValueError: If a required mapped column is missing from the dataset.
        FileNotFoundError: If the file does not exist.
        pd.errors.EmptyDataError: If the file is empty.
        UnicodeDecodeError: If there's an encoding issue.
        pd.errors.ParserError: If the file has malformed rows.
    """
    try:
        df = pd.read_csv(filepath, sep=sep, encoding=encoding)
    except pd.errors.EmptyDataError as e:
        raise pd.errors.EmptyDataError(f"The dataset file is empty: {filepath}") from e
    except pd.errors.ParserError as e:
        raise pd.errors.ParserError(f"The dataset file contains malformed rows: {filepath}") from e
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end, f"Encoding error reading file: {filepath}") from e

    if df.empty:
        raise pd.errors.EmptyDataError(f"The dataset file is empty: {filepath}")

    # Validate that required source columns defined in mapping are present
    missing_source_cols = [col for col in column_mapping.keys() if col not in df.columns]
    if missing_source_cols:
        raise ValueError(f"Missing configured source columns in dataset: {missing_source_cols}")

    # Check if a label column is mapped and if label_mapping is provided
    canonical_mapped_cols = list(column_mapping.values())
    if 'label' in canonical_mapped_cols and label_mapping is None:
        raise ValueError("A label column is mapped, but label_mapping is not provided.")

    # Create a new DataFrame for canonical format to avoid modifying original dataset
    canonical_df = pd.DataFrame()

    # Map the columns
    for source_col, canonical_col in column_mapping.items():
        if canonical_col in CANONICAL_COLUMNS:
            canonical_df[canonical_col] = df[source_col]

    # Assign original_record_id if we have one or just preserve index as fallback if not provided
    if 'original_record_id' not in canonical_df.columns:
        canonical_df['original_record_id'] = df.index.astype(str)

    # Ensure required canonical fields are present
    if 'headline' not in canonical_df.columns:
        raise ValueError("The 'headline' field is required but was not mapped.")

    # Process Labels
    if 'label' in canonical_df.columns:
        if label_mapping:
            # Map labels, default to 'unknown' for anything not in the mapping
            canonical_df['label'] = canonical_df['label'].astype(str).map(label_mapping).fillna('unknown')
    else:
        # If no label column is mapped, default all to 'unknown'
        canonical_df['label'] = 'unknown'

    # Fill missing optional fields with None
    for col in CANONICAL_COLUMNS:
        if col not in canonical_df.columns:
            canonical_df[col] = None

    # Generate article_id if not mapped
    if canonical_df['article_id'].isnull().all():
        canonical_df['article_id'] = [str(uuid.uuid4()) for _ in range(len(canonical_df))]

    # Set dataset_name if provided
    if dataset_name:
        canonical_df['dataset_name'] = dataset_name

    # Return only canonical columns in correct order
    return canonical_df[CANONICAL_COLUMNS]

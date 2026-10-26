import os
import pytest
import pandas as pd
from src.data_loading.loader import load_dataset, CANONICAL_COLUMNS

@pytest.fixture
def sample_csv(tmp_path):
    """Creates a sample CSV file for testing."""
    df = pd.DataFrame({
        'title': ['Real News', 'Fake News', 'Unknown News'],
        'text': ['This is real.', 'This is fake.', 'This is something.'],
        'class': ['True', 'False', 'Satire']
    })
    filepath = tmp_path / "sample.csv"
    df.to_csv(filepath, index=False)
    return str(filepath)

@pytest.fixture
def empty_csv(tmp_path):
    """Creates an empty CSV file for testing."""
    filepath = tmp_path / "empty.csv"
    filepath.touch()
    return str(filepath)

@pytest.fixture
def headers_only_csv(tmp_path):
    """Creates a CSV file with only headers."""
    df = pd.DataFrame(columns=['title', 'text', 'class'])
    filepath = tmp_path / "headers_only.csv"
    df.to_csv(filepath, index=False)
    return str(filepath)

def test_load_dataset_success(sample_csv):
    """Test successful loading and column mapping."""
    column_mapping = {
        'title': 'headline',
        'text': 'body',
        'class': 'label'
    }
    label_mapping = {
        'True': 'real',
        'False': 'fake'
    }
    df = load_dataset(sample_csv, column_mapping, label_mapping, dataset_name="TestDataset")

    assert list(df.columns) == CANONICAL_COLUMNS
    assert len(df) == 3
    assert df['headline'].tolist() == ['Real News', 'Fake News', 'Unknown News']
    assert df['body'].tolist() == ['This is real.', 'This is fake.', 'This is something.']
    assert df['label'].tolist() == ['real', 'fake', 'unknown']
    assert df['dataset_name'].tolist() == ['TestDataset', 'TestDataset', 'TestDataset']

    # Check that article_id is populated
    assert not df['article_id'].isnull().any()

    # Check that original_record_id is populated (defaults to index if not mapped)
    assert not df['original_record_id'].isnull().any()

def test_load_dataset_missing_source_column(sample_csv):
    """Test that missing configured source columns raise ValueError."""
    column_mapping = {
        'nonexistent_column': 'headline'
    }
    with pytest.raises(ValueError, match="Missing configured source columns"):
        load_dataset(sample_csv, column_mapping)

def test_load_dataset_missing_headline(sample_csv):
    """Test that missing 'headline' canonical mapping raises ValueError."""
    column_mapping = {
        'text': 'body'
    }
    with pytest.raises(ValueError, match="The 'headline' field is required"):
        load_dataset(sample_csv, column_mapping)

def test_load_dataset_label_mapping_missing(sample_csv):
    """Test that if label is mapped, label_mapping must be provided."""
    column_mapping = {
        'title': 'headline',
        'class': 'label'
    }
    with pytest.raises(ValueError, match="A label column is mapped, but label_mapping is not provided."):
        load_dataset(sample_csv, column_mapping)

def test_load_dataset_no_label_mapped(sample_csv):
    """Test behavior when no label is mapped."""
    column_mapping = {
        'title': 'headline'
    }
    df = load_dataset(sample_csv, column_mapping)
    assert df['label'].tolist() == ['unknown', 'unknown', 'unknown']

def test_empty_dataset(empty_csv):
    """Test that an empty file raises pd.errors.EmptyDataError."""
    column_mapping = {'title': 'headline'}
    with pytest.raises(pd.errors.EmptyDataError, match="The dataset file is empty"):
        load_dataset(empty_csv, column_mapping)

def test_headers_only_dataset(headers_only_csv):
    """Test that a file with only headers raises pd.errors.EmptyDataError."""
    column_mapping = {'title': 'headline'}
    with pytest.raises(pd.errors.EmptyDataError, match="The dataset file is empty"):
        load_dataset(headers_only_csv, column_mapping)

def test_malformed_csv(tmp_path):
    """Test that malformed rows raise pd.errors.ParserError."""
    filepath = tmp_path / "malformed.csv"
    with open(filepath, 'w') as f:
        f.write("col1,col2\nval1,val2\nval3,val4,val5\n") # Malformed row 2

    column_mapping = {'col1': 'headline'}
    with pytest.raises(pd.errors.ParserError):
        load_dataset(str(filepath), column_mapping)

def test_encoding_error(tmp_path):
    """Test that encoding errors raise UnicodeDecodeError."""
    filepath = tmp_path / "encoding_error.csv"
    # Write some bytes that aren't valid UTF-8
    with open(filepath, 'wb') as f:
        f.write(b"col1,col2\n\xff\xfe,val2\n")

    column_mapping = {'col1': 'headline'}
    with pytest.raises(UnicodeDecodeError):
        load_dataset(str(filepath), column_mapping, encoding='utf-8')

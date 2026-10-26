import pytest
import os
import tempfile
from src.dataset_loader import DatasetLoader

@pytest.fixture
def fixtures_dir():
    return os.path.join(os.path.dirname(__file__), 'fixtures')

def test_load_valid_basic_csv(fixtures_dir):
    loader = DatasetLoader()
    filepath = os.path.join(fixtures_dir, 'valid_basic.csv')
    records = loader.load(filepath)

    assert len(records) == 3

    # Check basic loading
    assert records[0]['article_id'] == 'test_1'
    assert records[0]['headline'] == 'Valid Real Headline'
    assert records[0]['label'] == 'real'

    assert records[1]['label'] == 'fake'

    # Check unknown label mapping
    assert records[2]['label'] == 'unknown'

    report = loader.get_integrity_report()
    assert report['total_rows_processed'] == 3
    assert report['valid_records'] == 3
    assert report['invalid_records'] == 0

def test_load_valid_basic_tsv(fixtures_dir):
    loader = DatasetLoader()
    filepath = os.path.join(fixtures_dir, 'valid_basic.tsv')
    records = loader.load(filepath)

    assert len(records) == 3
    assert records[0]['label'] == 'real'
    assert records[1]['label'] == 'fake'
    assert records[2]['label'] == 'unknown'

def test_strict_labels(fixtures_dir):
    loader = DatasetLoader(strict_labels=True)
    filepath = os.path.join(fixtures_dir, 'valid_basic.csv')
    records = loader.load(filepath)

    # Should drop the 'Mostly True' row
    assert len(records) == 2
    report = loader.get_integrity_report()
    assert report['unknown_labels_dropped'] == 1
    assert report['invalid_records'] == 1

def test_multimodal(fixtures_dir):
    loader = DatasetLoader()
    filepath = os.path.join(fixtures_dir, 'multimodal.csv')
    records = loader.load(filepath)

    assert len(records) == 4
    assert records[0]['image_path'] == 'images/img1.jpg'
    assert records[1]['image_path'] == 'images/img2.png'
    assert records[3]['image_path'] == 'images/img4.jpg'
    assert records[3]['body'] is None

def test_invalid_missing(fixtures_dir):
    loader = DatasetLoader()
    filepath = os.path.join(fixtures_dir, 'invalid_missing.csv')
    records = loader.load(filepath)

    # Original has 6 rows.
    # test_1 is valid (real)
    # test_2 missing headline
    # test_3 missing id
    # test_4 missing label
    # test_5 invalid label (maps to unknown)
    # test_6 satire (maps to unknown)

    assert len(records) == 3 # test_1, test_5, test_6 (the invalid ones are mapped to unknown but still valid records if not strict)
    report = loader.get_integrity_report()
    assert report['total_rows_processed'] == 6
    assert report['missing_required_fields'] == 3
    assert report['invalid_records'] == 3

    # Test 5 mapped to unknown
    assert any(r['article_id'] == 'test_5' and r['label'] == 'unknown' for r in records)

def test_custom_mapping(fixtures_dir):
    mapping = {
        'article_id': 'id_col',
        'headline': 'title',
        'body': 'text',
        'label': 'fake_label'
    }
    loader = DatasetLoader(mapping=mapping)
    filepath = os.path.join(fixtures_dir, 'custom_mapping.csv')
    records = loader.load(filepath)

    assert len(records) == 2
    assert records[0]['article_id'] == 'id1'
    assert records[0]['headline'] == 'Title 1'
    assert records[0]['body'] == 'Text 1'
    assert records[0]['label'] == 'real'

def test_empty_file(fixtures_dir):
    loader = DatasetLoader()
    filepath = os.path.join(fixtures_dir, 'empty.csv')
    records = loader.load(filepath)

    assert len(records) == 0
    report = loader.get_integrity_report()
    assert len(report['errors']) == 1
    assert "Empty or missing header" in report['errors'][0]

def test_missing_file():
    loader = DatasetLoader()
    records = loader.load("non_existent_file.csv")

    assert len(records) == 0
    report = loader.get_integrity_report()
    assert len(report['errors']) == 1
    assert "File not found" in report['errors'][0]

def test_unsupported_format(fixtures_dir):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"dummy")
        name = f.name

    loader = DatasetLoader()
    records = loader.load(name)
    assert len(records) == 0
    report = loader.get_integrity_report()
    assert "Unsupported format" in report['errors'][0]
    os.remove(name)


def test_source_data_immutability(fixtures_dir):
    filepath = os.path.join(fixtures_dir, 'valid_basic.csv')
    stat_before = os.stat(filepath)

    loader = DatasetLoader()
    loader.load(filepath)

    stat_after = os.stat(filepath)
    assert stat_before.st_mtime == stat_after.st_mtime
    assert stat_before.st_size == stat_after.st_size

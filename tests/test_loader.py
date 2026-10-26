import pytest
import os
from unittest.mock import patch, MagicMock
from src.data.loader import DatasetLoader, ImageStatus

@pytest.fixture
def temp_data_root(tmp_path):
    """Fixture providing a temporary directory for tests."""
    return str(tmp_path)

@pytest.fixture
def loader(temp_data_root):
    """Fixture providing a DatasetLoader instance."""
    return DatasetLoader(temp_data_root)

def test_add_text_only_record(loader):
    """Test loading a text-only record."""
    record_data = {
        'article_id': 'id1',
        'headline': 'Test Headline',
        'label': 'real',
        'body': 'Test Body'
    }

    record = loader.add_record(record_data)

    assert record.article_id == 'id1'
    assert record.headline == 'Test Headline'
    assert record.label == 'real'
    assert record.body == 'Test Body'
    assert record.image_path is None
    assert record.image_status == ImageStatus.MISSING
    assert record.resolved_image_path is None

    loader.check_image_status('id1')
    assert loader.records['id1'].image_status == ImageStatus.MISSING

def test_repeated_ids_raise_error(loader):
    """Test that adding a record with an existing ID raises an error."""
    record_data = {
        'article_id': 'id1',
        'headline': 'Test Headline',
        'label': 'real'
    }

    loader.add_record(record_data)

    with pytest.raises(ValueError, match="Duplicate article_id: id1"):
        loader.add_record(record_data)

def test_missing_required_fields(loader):
    """Test that missing required fields raise an error."""
    with pytest.raises(ValueError, match="Missing required field: article_id"):
        loader.add_record({'headline': 'Test', 'label': 'real'})

    with pytest.raises(ValueError, match="Missing required field: headline"):
        loader.add_record({'article_id': 'id', 'label': 'real'})

    with pytest.raises(ValueError, match="Missing required field: label"):
        loader.add_record({'article_id': 'id', 'headline': 'Test'})

def test_local_image_reference(loader, temp_data_root):
    """Test loading a record with a local image reference."""
    # Create a dummy image file
    img_path = os.path.join(temp_data_root, 'test_image.jpg')
    with open(img_path, 'w') as f:
        f.write("dummy image data")

    record_data = {
        'article_id': 'id2',
        'headline': 'Image Test',
        'label': 'fake',
        'image_path': 'test_image.jpg'
    }

    record = loader.add_record(record_data)

    assert record.image_path == 'test_image.jpg'
    assert record.image_status == ImageStatus.UNCHECKED
    assert record.resolved_image_path == img_path

    loader.check_image_status('id2')
    assert loader.records['id2'].image_status == ImageStatus.AVAILABLE

def test_broken_local_reference(loader):
    """Test handling of a broken local image reference."""
    record_data = {
        'article_id': 'id3',
        'headline': 'Broken Image Test',
        'label': 'fake',
        'image_path': 'missing_image.jpg'
    }

    loader.add_record(record_data)
    loader.check_image_status('id3')

    assert loader.records['id3'].image_status == ImageStatus.BROKEN

def test_path_traversal_prevention(loader):
    """Test that unsafe relative paths are rejected."""
    record_data = {
        'article_id': 'id4',
        'headline': 'Unsafe Path Test',
        'label': 'fake',
        'image_path': '../outside_image.jpg'
    }

    with pytest.raises(ValueError, match="Path traversal detected"):
        loader.add_record(record_data)

@patch('requests.head')
def test_remote_url_reference_available(mock_head, loader):
    """Test loading a record with an available remote URL."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_head.return_value = mock_response

    record_data = {
        'article_id': 'id5',
        'headline': 'Remote Image Test',
        'label': 'real',
        'image_path': 'http://example.com/image.jpg'
    }

    record = loader.add_record(record_data)

    assert record.image_path == 'http://example.com/image.jpg'
    assert record.image_status == ImageStatus.UNCHECKED
    assert record.resolved_image_path == 'http://example.com/image.jpg'

    loader.check_image_status('id5')
    assert loader.records['id5'].image_status == ImageStatus.AVAILABLE
    mock_head.assert_called_once_with('http://example.com/image.jpg', timeout=5, allow_redirects=True)

@patch('requests.head')
def test_remote_url_reference_inaccessible(mock_head, loader):
    """Test handling of an inaccessible remote URL."""
    # Mock unsuccessful response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_head.return_value = mock_response

    record_data = {
        'article_id': 'id6',
        'headline': 'Remote Image Broken Test',
        'label': 'real',
        'image_path': 'http://example.com/missing.jpg'
    }

    loader.add_record(record_data)
    loader.check_image_status('id6')

    assert loader.records['id6'].image_status == ImageStatus.INACCESSIBLE

@patch('requests.head')
def test_remote_url_request_exception(mock_head, loader):
    """Test handling of a request exception for a remote URL."""
    import requests
    # Mock request exception
    mock_head.side_effect = requests.RequestException("Connection error")

    record_data = {
        'article_id': 'id7',
        'headline': 'Remote Image Exception Test',
        'label': 'real',
        'image_path': 'http://example.com/error.jpg'
    }

    loader.add_record(record_data)
    loader.check_image_status('id7')

    assert loader.records['id7'].image_status == ImageStatus.INACCESSIBLE

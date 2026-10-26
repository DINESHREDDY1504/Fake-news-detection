import pytest
import os
from src.dataset_registry import DatasetConfig, DatasetRegistry

def test_dataset_config_valid():
    config = DatasetConfig(
        identifier="test_valid",
        display_name="Test Valid Dataset",
        local_file_path="valid/data.csv",
        expected_format="csv",
        label_mapping={"Real News": "real", "Fake News": "fake"},
        text_field_mapping={"headline": "title"}
    )
    # Should not raise an exception
    config.validate()

def test_dataset_config_missing_required_fields():
    with pytest.raises(ValueError, match="missing required identifier"):
        DatasetConfig(
            identifier="",
            display_name="Test Dataset",
            local_file_path="valid/data.csv",
            expected_format="csv",
            label_mapping={"Real News": "real"},
            text_field_mapping={"headline": "title"}
        ).validate()

def test_dataset_config_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported expected_format"):
        DatasetConfig(
            identifier="test",
            display_name="Test Dataset",
            local_file_path="valid/data.xml",
            expected_format="xml",
            label_mapping={"Real News": "real"},
            text_field_mapping={"headline": "title"}
        ).validate()

def test_dataset_config_invalid_label_mapping():
    with pytest.raises(ValueError, match="Invalid canonical label"):
        DatasetConfig(
            identifier="test",
            display_name="Test Dataset",
            local_file_path="valid/data.csv",
            expected_format="csv",
            label_mapping={"Real News": "true_news"}, # Invalid canonical label
            text_field_mapping={"headline": "title"}
        ).validate()

def test_dataset_config_empty_label_mapping():
    with pytest.raises(ValueError, match="label_mapping cannot be empty"):
        DatasetConfig(
            identifier="test",
            display_name="Test Dataset",
            local_file_path="valid/data.csv",
            expected_format="csv",
            label_mapping={},
            text_field_mapping={"headline": "title"}
        ).validate()

def test_dataset_config_empty_text_field_mapping():
    with pytest.raises(ValueError, match="text_field_mapping cannot be empty"):
        DatasetConfig(
            identifier="test",
            display_name="Test Dataset",
            local_file_path="valid/data.csv",
            expected_format="csv",
            label_mapping={"Real News": "real"},
            text_field_mapping={}
        ).validate()

def test_get_absolute_path(monkeypatch):
    config = DatasetConfig(
        identifier="test",
        display_name="Test Dataset",
        local_file_path="my_dataset/data.csv",
        expected_format="csv",
        label_mapping={"Real News": "real"},
        text_field_mapping={"headline": "title"}
    )

    # Test default fallback
    monkeypatch.delenv("PROJECT_DATA_DIR", raising=False)
    expected_default_path = os.path.join("./data", "my_dataset/data.csv")
    assert config.get_absolute_path() == expected_default_path

    # Test environment variable usage
    monkeypatch.setenv("PROJECT_DATA_DIR", "/custom/data/path")
    expected_custom_path = os.path.join("/custom/data/path", "my_dataset/data.csv")
    assert config.get_absolute_path() == expected_custom_path

def test_registry_register_and_get():
    registry = DatasetRegistry()
    config = DatasetConfig(
        identifier="registry_test_1",
        display_name="Registry Test 1",
        local_file_path="data.csv",
        expected_format="csv",
        label_mapping={"Real": "real"},
        text_field_mapping={"headline": "title"}
    )
    registry.register(config)

    retrieved = registry.get("registry_test_1")
    assert retrieved == config

def test_registry_register_duplicate():
    registry = DatasetRegistry()
    config = DatasetConfig(
        identifier="registry_test_2",
        display_name="Registry Test 2",
        local_file_path="data.csv",
        expected_format="csv",
        label_mapping={"Real": "real"},
        text_field_mapping={"headline": "title"}
    )
    registry.register(config)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(config)

def test_registry_get_not_found():
    registry = DatasetRegistry()
    with pytest.raises(KeyError, match="not registered"):
        registry.get("nonexistent_dataset")

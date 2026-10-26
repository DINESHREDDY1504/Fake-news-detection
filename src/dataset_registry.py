import os
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any


@dataclass
class DatasetConfig:
    """
    Configuration for a dataset that the system can load.

    Attributes:
        identifier: A stable, unique string identifying this dataset (e.g., "fake_news_corpus_v1").
        display_name: A human-readable name for the dataset.
        local_file_path: The path to the dataset file, relative to the PROJECT_DATA_DIR.
        expected_format: The format of the file (e.g., "csv", "json").
        label_mapping: A dictionary mapping the dataset's original labels to our canonical labels:
                       'real', 'fake', or 'unknown'.
                       Example: {"True": "real", "False": "fake"}
        text_field_mapping: A dictionary mapping expected fields to the dataset's columns/keys.
                            Expected keys might include 'headline', 'body', 'original_record_id'.
        source_url: The original URL where the dataset can be found (if public).
        image_reference_field: The field in the dataset that points to an associated image, if any.
        provenance_info: Additional metadata about how the dataset was collected, licensing, etc.
    """
    identifier: str
    display_name: str
    local_file_path: str
    expected_format: str
    label_mapping: Dict[str, str]
    text_field_mapping: Dict[str, str]
    source_url: Optional[str] = None
    image_reference_field: Optional[str] = None
    provenance_info: Optional[Dict[str, Any]] = field(default_factory=dict)

    def validate(self):
        """
        Validates the dataset configuration to ensure it meets system requirements.
        Raises ValueError if any configuration is invalid.
        """
        if not self.identifier or not self.display_name or not self.local_file_path:
            raise ValueError("Dataset configuration is missing required identifier, display_name, or local_file_path.")

        supported_formats = ["csv", "json", "jsonl"]
        if self.expected_format.lower() not in supported_formats:
            raise ValueError(f"Unsupported expected_format: '{self.expected_format}'. Supported formats are: {supported_formats}")

        if not self.label_mapping:
            raise ValueError("label_mapping cannot be empty.")

        allowed_canonical_labels = {"real", "fake", "unknown"}
        for original_label, canonical_label in self.label_mapping.items():
            if canonical_label not in allowed_canonical_labels:
                raise ValueError(
                    f"Invalid canonical label '{canonical_label}' for original label '{original_label}'. "
                    f"Must be one of {allowed_canonical_labels}."
                )

        if not self.text_field_mapping:
            raise ValueError("text_field_mapping cannot be empty.")

    def get_absolute_path(self) -> str:
        """
        Resolves the local_file_path against the PROJECT_DATA_DIR environment variable.
        Defaults to './data' if the environment variable is not set.
        """
        base_dir = os.environ.get("PROJECT_DATA_DIR", "./data")
        return os.path.join(base_dir, self.local_file_path)


class DatasetRegistry:
    """
    A registry to manage and retrieve registered datasets.
    """
    def __init__(self):
        self._datasets: Dict[str, DatasetConfig] = {}

    def register(self, config: DatasetConfig):
        """
        Registers a dataset configuration.
        Raises ValueError if a dataset with the same identifier is already registered.
        """
        config.validate()
        if config.identifier in self._datasets:
            raise ValueError(f"Dataset with identifier '{config.identifier}' is already registered.")
        self._datasets[config.identifier] = config

    def get(self, identifier: str) -> DatasetConfig:
        """
        Retrieves a dataset configuration by its identifier.
        Raises KeyError if the dataset is not found.
        """
        if identifier not in self._datasets:
            raise KeyError(f"Dataset with identifier '{identifier}' is not registered.")
        return self._datasets[identifier]

    def list_datasets(self) -> List[DatasetConfig]:
        """
        Returns a list of all registered dataset configurations.
        """
        return list(self._datasets.values())


# Global instance of the dataset registry
registry = DatasetRegistry()

# -------------------------------------------------------------------------
# Example Configuration and Registration
# -------------------------------------------------------------------------
# Documenting how a new dataset can be registered:
# To register a new dataset, instantiate a DatasetConfig object with the
# relevant properties and mappings. Ensure the expected format is supported
# and the label mapping correctly resolves to 'real', 'fake', or 'unknown'.
# Then, call registry.register() with your configuration object.
#
# Example placeholder dataset (No actual file needs to exist for registration):
example_config = DatasetConfig(
    identifier="example_fake_news_dataset",
    display_name="Example Fake News Placeholder Dataset",
    local_file_path="example_dataset/data.csv",
    expected_format="csv",
    label_mapping={
        "True": "real",
        "False": "fake",
        "Mostly True": "unknown",
        "Pants on Fire": "fake"
    },
    text_field_mapping={
        "headline": "title_column",
        "body": "text_column",
        "original_record_id": "id"
    },
    source_url="https://example.com/dataset",
    provenance_info={
        "description": "This is a placeholder for demonstrating registration.",
        "license": "CC-BY-4.0"
    }
)

registry.register(example_config)

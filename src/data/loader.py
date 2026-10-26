import os
import urllib.parse
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict
import requests

class ImageStatus(Enum):
    """Represents the status of an image reference in a dataset."""
    MISSING = "missing"
    UNCHECKED = "unchecked"
    AVAILABLE = "available"
    BROKEN = "broken"
    INACCESSIBLE = "inaccessible"

@dataclass
class ArticleRecord:
    """
    Represents a canonical record in the dataset.
    Follows the schema defined in docs/dataset_requirements.md.
    """
    article_id: str
    headline: str
    label: str
    body: Optional[str] = None
    image_path: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    publication_date: Optional[str] = None
    dataset_name: Optional[str] = None
    original_record_id: Optional[str] = None

    # Internal status tracking
    image_status: ImageStatus = ImageStatus.MISSING
    resolved_image_path: Optional[str] = None

class DatasetLoader:
    """
    Loads and manages dataset records, ensuring compliance with the canonical schema.

    Assumption: Each article record is associated with at most one image. If a dataset
    contains multiple images per article, they must be combined or selected prior to
    loading, or the schema must be extended.
    """

    def __init__(self, data_root: str):
        """
        Initializes the DatasetLoader.

        Args:
            data_root (str): The root directory where local datasets are stored.
                             All local image paths will be resolved relative to this root.
        """
        self.data_root = os.path.abspath(data_root)
        self.records: Dict[str, ArticleRecord] = {}

    def _is_url(self, path: str) -> bool:
        """Checks if a given path is a URL."""
        try:
            result = urllib.parse.urlparse(path)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _resolve_and_validate_path(self, path: str) -> str:
        """
        Resolves a local path against the data root and ensures it does not
        traverse outside the data root.

        Raises ValueError if the path attempts traversal outside the data root.
        """
        resolved_path = os.path.abspath(os.path.join(self.data_root, path))

        # Check for path traversal by ensuring the resolved path is actually within the data root
        # We ensure it ends with os.sep so that /var/data_secrets isn't considered inside /var/data
        root_with_sep = self.data_root if self.data_root.endswith(os.sep) else self.data_root + os.sep
        if not resolved_path.startswith(root_with_sep) and resolved_path != self.data_root:
            raise ValueError(f"Path traversal detected: {path} resolves outside {self.data_root}")

        return resolved_path

    def add_record(self, record_data: dict) -> ArticleRecord:
        """
        Adds a single record to the dataset.

        Args:
            record_data (dict): A dictionary containing the record fields.

        Raises:
            ValueError: If required fields are missing or if the article_id is a duplicate.
        """
        # Validate required fields
        required_fields = ['article_id', 'headline', 'label']
        for field in required_fields:
            if field not in record_data or not record_data[field]:
                raise ValueError(f"Missing required field: {field}")

        article_id = record_data['article_id']
        if article_id in self.records:
            raise ValueError(f"Duplicate article_id: {article_id}")

        # Create the record
        record = ArticleRecord(
            article_id=article_id,
            headline=record_data['headline'],
            label=record_data['label'],
            body=record_data.get('body'),
            image_path=record_data.get('image_path'),
            source_name=record_data.get('source_name'),
            source_url=record_data.get('source_url'),
            publication_date=record_data.get('publication_date'),
            dataset_name=record_data.get('dataset_name'),
            original_record_id=record_data.get('original_record_id')
        )

        if record.image_path:
            record.image_status = ImageStatus.UNCHECKED
            if self._is_url(record.image_path):
                record.resolved_image_path = record.image_path
            else:
                record.resolved_image_path = self._resolve_and_validate_path(record.image_path)

        self.records[article_id] = record
        return record

    def check_image_status(self, article_id: str) -> None:
        """
        Checks the availability of the image associated with the given article_id
        and updates the image_status accordingly. Does not download remote images.
        """
        if article_id not in self.records:
            raise ValueError(f"Record with id {article_id} not found.")

        record = self.records[article_id]

        if not record.image_path:
            record.image_status = ImageStatus.MISSING
            return

        if self._is_url(record.resolved_image_path):
            try:
                # Use HEAD request to check availability without downloading
                response = requests.head(record.resolved_image_path, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    record.image_status = ImageStatus.AVAILABLE
                else:
                    record.image_status = ImageStatus.INACCESSIBLE
            except requests.RequestException:
                record.image_status = ImageStatus.INACCESSIBLE
        else:
            if os.path.isfile(record.resolved_image_path):
                record.image_status = ImageStatus.AVAILABLE
            else:
                record.image_status = ImageStatus.BROKEN

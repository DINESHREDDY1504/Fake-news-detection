# Dataset Provenance, Licenses, and Usage Rules

This document outlines the rules and procedures for acquiring, documenting, and using datasets within the AI-Based Fake News Detection System. Our goal is to make dataset collection transparent, reproducible, and legally responsible.

## 1. General Principles

*   **Repository Limits:** Large datasets and downloaded image archives must be kept out of version control (Git) unless explicitly permitted, reviewed, and necessary for small-scale testing. Always use the `.gitignore` rules (which exclude directories like `data/`, `datasets/`, `archives/` and files like `*.csv`, `*.parquet`).
*   **Different Rights for Different Modalities:** Code, article text, images, and metadata often have distinct licensing terms and copyright conditions even when distributed together in a single dataset. Always evaluate rights per data modality.
*   **Official Routes:** Data must be obtained through approved, official routes (e.g., official APIs, direct downloads from creator-hosted repositories) as documented below.

## 2. Dataset Reproducibility

To ensure models can be consistently retrained, all datasets must have their provenance, versioning, and integrity checks documented:
*   **Version:** Record the explicit version number or release date of the dataset.
*   **Checksums:** Compute and record SHA-256 (or MD5) checksums for all raw dataset files upon download to verify integrity later.
*   **Provenance:** Document exactly how the data was obtained, including the source URL, download scripts used, and the exact date accessed.

## 3. Dataset Approval Checklist

Before a new dataset can be ingested into the training pipeline, it must pass the following checks:
- [ ] Source identity and official URL are documented.
- [ ] License or terms of use for *all* relevant data types (text, images, metadata) are reviewed.
- [ ] Attribution requirements are identified and can be fulfilled by the project.
- [ ] Unresolved licensing questions are clearly marked for legal/manual review.
- [ ] Version and checksums are computed and recorded.
- [ ] Download instructions/scripts are created (data is not pushed to Git).
- [ ] Dataset complies with schema requirements in `docs/dataset_requirements.md`.

## 4. Current Datasets Provenance

*(Note: Currently, there are no approved datasets in this repository. When adding a dataset, use the template below.)*

### [Dataset Name] (Template)
*   **Official Source URL:** [e.g., https://example.com/dataset]
*   **Access Date:** [YYYY-MM-DD]
*   **Version:** [Version or Date]
*   **Checksum (SHA-256):** [Checksum of raw file]
*   **License/Terms:** [e.g., CC BY-NC 4.0]
    *   **Status:** [Verified / Needs Manual Review]
*   **Attribution Requirements:** [e.g., "Must cite Smith et al., 2020"]
*   **Intended Use:** [e.g., Training the text classification model]
*   **Redistribution Restrictions:** [e.g., "Cannot distribute raw text, only derived models"]
*   **Download Instructions:** [e.g., "Run `scripts/download_dataset.sh` which fetches the data from the official source."]
*   **Notes on Modality Rights:** [e.g., "Text is CC BY 4.0, but images are under Fair Use and cannot be redistributed."]

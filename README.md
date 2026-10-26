# AI-Based Fake News Detection System

Welcome to the AI-Based Fake News Detection System project!

This system is currently under development. Its goal is to use machine learning, natural language processing (NLP), and image analysis to identify potentially false or misleading information.

## Planned Features

*   **Text Classification:** Analyzing the textual content of news articles using machine learning (e.g., scikit-learn models) to classify them as real or fake.
*   **Optical Character Recognition (OCR):** Extracting text from images or memes using Tesseract OCR to analyze the content of visual media.
*   **Image Analysis:** Analyzing images to detect potential manipulation or inconsistencies using OpenCV and Pillow.
*   **User Interface:** A web interface built with Streamlit for users to input text or upload images and receive predictions.

## Documentation

*   [Dataset Requirements and Schema](docs/dataset_requirements.md): Details the data schema, labeling policies, and requirements for future dataset ingestion.

## Data Layout and Loading

The system handles both text-only and multimodal records using the `DatasetLoader` module located in `src/data/loader.py`.
*   **Canonical Schema:** Datasets must match the schema outlined in `docs/dataset_requirements.md`. Crucial fields include `article_id`, `headline`, and `label`.
*   **Multimodal Support:** Records may optionally include an `image_path` linking to a local file or remote URL. Local paths are safely resolved relative to a designated `data_root` directory.
*   **Image Availability:** The loader can check if images (local or remote) are accessible without fully downloading them. Missing images for text-only records are properly handled.

## Project Status
Currently, this project contains only the foundational folder structure, documentation, and basic utilities to support future development. We are not yet training models or downloading large datasets.

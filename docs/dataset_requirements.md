# Dataset Requirements and Schema

This document outlines the data requirements, expected schemas, and label policies for the AI-Based Fake News Detection System. Before collecting or processing any datasets, all incoming data must conform to these definitions.

## 1. Project Overview

*   **Objectives:** To build a system that analyzes news text and images to classify content as potentially real or fake. It will eventually incorporate an evidence-analysis component for factual verification when sources are available.
*   **Intended Users:** General users seeking to verify suspicious news articles or memes, researchers, and students analyzing misinformation trends.
*   **Supported Inputs:**
    1.  News article text (including a headline and an optional article body).
    2.  News images or screenshots (containing a headline, claim, or relevant visual evidence).
*   **Expected Outputs:** A classification result indicating the likelihood that the input is "real" or "fake," accompanied by a confidence score.

## 2. Factual Truth vs. Dataset Label

It is crucial to distinguish between a **dataset label** and **independently verified factual truth**.
*   **Dataset Label:** This is the ground truth provided by a specific dataset's authors (e.g., a "fake" label derived from a specific fact-checking API or crowd-sourced consensus). It is heavily dependent on the dataset's methodology, timeline, and inherent biases.
*   **Factual Truth:** An objective, independently verified reality. Our models learn to predict the *dataset label*, not absolute truth. Thus, a prediction of "fake" means "this resembles data labeled as fake in our training set," not "this is universally proven false."

## 3. Canonical Record Schema

All datasets ingested into the system must be mapped to the following canonical format.

| Field Name | Type | Required? | Description |
| :--- | :--- | :--- | :--- |
| `article_id` | String | **Yes** | A unique identifier for the record within our system. |
| `headline` | String | **Yes** | The title, headline, or primary claim of the news item. |
| `body` | String | No | The main text content of the article. |
| `label` | String | **Yes** | The canonical label: `real`, `fake`, or `unknown`. |
| `image_path` | String | No* | Path or URL to an associated image. (*Required only if the record is primarily image-based, otherwise optional). |
| `source_name` | String | No | The name of the publication or platform (e.g., "Reuters", "Facebook"). |
| `source_url` | String | No | The original URL where the content was found. |
| `publication_date` | String/Date | No | The date the article or image was published (ISO 8601 preferred). |
| `dataset_name` | String | No | The name of the original dataset this record was sourced from. |
| `original_record_id`| String | No | The ID used in the original source dataset, useful for traceability. |

## 4. Explicit Label Policy

Different datasets use varying terminology (e.g., "True", "Mostly True", "Pants on Fire", "False"). We must explicitly map these to our binary classification target or exclude them. The system does not silently guess ambiguous labels.

*   **Map to `real`:** Labels explicitly confirming veracity, e.g., "True", "Real", "Verified", "Accurate".
*   **Map to `fake`:** Labels explicitly confirming falsehood, e.g., "False", "Fake", "Pants on Fire", "Fabricated".
*   **Map to `unknown` / Exclude:**
    *   **Disputed / Mixed / Half-True:** Examples that contain a mix of truth and falsehood must be mapped to `unknown` or excluded from the binary training set, as they introduce noise.
    *   **Satire:** Satirical content (e.g., The Onion) is often intentionally false for comedic effect. Unless we are specifically training a satire-detection model, these should be excluded or marked as `unknown` for the primary real/fake classifier.
    *   **Unlabeled:** Any data without a clear label must be assigned `unknown` and reserved for unsupervised learning, clustering, or excluded from supervised training.

## 5. Dataset Considerations and Risks

*   **Licensing:** Ensure all datasets used allow for research or commercial use as intended by the project. Verify the licenses (e.g., Creative Commons) before ingestion.
*   **Privacy:** Datasets should not contain Personally Identifiable Information (PII) of non-public figures. If social media data is used, ensure compliance with the platform's Terms of Service regarding data retention and user anonymity.
*   **Provenance:** Always maintain the `dataset_name` and `original_record_id` to trace the data back to its origin. This is vital for auditing model bias.
*   **Train/Test Leakage Risks:**
    *   Ensure that duplicate articles or highly similar variations (e.g., the same syndicated article published by two different outlets) do not appear in both the training and testing sets.
    *   Split data temporally (e.g., train on 2018-2021 data, test on 2022 data) to better simulate real-world performance on novel news events. Random splitting can artificially inflate accuracy due to the model memorizing specific ongoing events rather than general deceptive patterns.

## 6. Unresolved Decisions
*   How should we handle multi-modal records where the text claims one thing but the image implies another?
*   Should we establish a separate tertiary classification category specifically for "Satire"?

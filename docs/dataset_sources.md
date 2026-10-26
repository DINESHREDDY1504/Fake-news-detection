# Dataset Sources and Comparison

This document details the public datasets evaluated for the AI-Based Fake News Detection System. We have assessed two primary candidates: **FakeNewsNet** (for article text and social context) and **Fakeddit** (for multimodal text and image data).

## Candidate Comparison Table

| Feature | FakeNewsNet | Fakeddit |
| :--- | :--- | :--- |
| **Primary Focus** | Text articles, Social context (Twitter) | Multimodal (Text and Images from Reddit) |
| **Official URL** | [FakeNewsNet GitHub](https://github.com/KaiDMML/FakeNewsNet) | [Fakeddit GitHub](https://github.com/entitize/Fakeddit) / [Website](https://fakeddit.netlify.app/) |
| **Formats** | CSV (for IDs), JSON (for content and tweets) | TSV (text/metadata), Images (direct download via Google Drive or URLs) |
| **Size (Approx)** | Varies; relies on active Twitter links to download full dataset. | Over 1 million samples across multiple categories. |
| **Provided Fields** | `id`, `url`, `title`, `tweet_ids`, `text`, `images`, `publish date` | Text (title/body), `image_url`, Comments, Label columns (2-way, 3-way, 6-way) |
| **Label Definitions** | `fake` or `real` based on PolitiFact and GossipCop ground truth. | Fine-grained labels derived via distant supervision (2-way, 3-way, 6-way). |
| **Image Availability** | URLs provided in the article JSON, requires scraping. | Distributed directly via a zip file or URLs in the dataset. |
| **Language** | Primarily English | English |
| **Access Method** | Clone repo, configure Twitter API keys, and run Python scripts to download. | Direct download of TSVs and images from Google Drive links provided in the repo. |
| **License / Terms** | Not explicitly stated in GitHub repo; requires review (academic use implied). | Not explicitly stated in GitHub repo; requires review (academic use implied). |

## Canonical Schema Mapping

Both datasets must be mapped to our Canonical Schema defined in `docs/dataset_requirements.md`.

### Mapping FakeNewsNet

| Canonical Field | FakeNewsNet Source Field | Mapping Logic |
| :--- | :--- | :--- |
| `article_id` | `id` | Use directly. |
| `headline` | `title` | Found in the initial CSVs. |
| `body` | `text` | Extracted from `news content.json` after downloading. |
| `label` | File path/source | Mapped from source folder (`fake` -> `fake`, `real` -> `real`). |
| `image_path` | `images` (List of URLs) | Select a primary image URL or leave empty if un-scrapable. |
| `source_name` | Source Domain | Extract from `url` field. |
| `source_url` | `url` | Use directly. |
| `publication_date`| `publish date` | Extracted from `news content.json`. |
| `dataset_name` | Static value | "FakeNewsNet" |
| `original_record_id`| `id` | Same as `article_id`. |

### Mapping Fakeddit

| Canonical Field | Fakeddit Source Field | Mapping Logic |
| :--- | :--- | :--- |
| `article_id` | `id` or row index | Unique identifier in the TSV. |
| `headline` | `clean_title` | Use the filtered title text. |
| `body` | (Optional comments) | Fakeddit primarily relies on the title/image combo; comments can optionally be mapped here. |
| `label` | 2-way label column | Map 2-way binary label to `real` (e.g., true) or `fake` (e.g., false). Sub-categories must be mapped to `unknown` or ignored if not clearly real/fake. |
| `image_path` | `image_url` or local path | Path to the locally downloaded image from the provided zip. |
| `source_name` | "Reddit" | Static value. |
| `source_url` | Submission URL | Based on Reddit submission ID if available. |
| `publication_date`| Timestamp (if available) | Convert to ISO 8601; else null. |
| `dataset_name` | Static value | "Fakeddit" |
| `original_record_id`| `id` | Unique ID in the original TSV. |

## Limitations and Download Requirements

### FakeNewsNet
*   **Download Requirements:** Requires a Twitter Developer Account and API keys to fetch the social context (tweets, user profiles).
*   **Dependencies:** Python 3.6+, specific libraries in `requirements.txt`. Requires running a local flask server for key management during collection.
*   **Limitations:** Because it relies on scraping Twitter and live news sites based on URLs, many links (especially for fake news) may be dead (404), leading to a smaller dataset than originally published.

### Fakeddit
*   **Download Requirements:** Direct download from Google Drive links provided in the README. An optional python script `image_downloader.py` is provided for fetching images from URLs.
*   **Limitations:** Labels are generated via distant supervision (heuristics based on subreddits) rather than professional fact-checkers. This introduces noise. We must use the `multimodal_only_samples` folder for text+image consistency as noted in their documentation.

## Recommendations for Initial Development

**Initial Dataset Recommendation:**
We recommend using a small, manageable subset of **FakeNewsNet (PolitiFact subset)** for initial text-only pipeline development. It provides high-quality ground-truth labels directly from professional fact-checkers, which is critical for early baseline testing.

For multimodal development, we recommend downloading a small sample (e.g., 10,000 records) of the **Fakeddit** `multimodal_only_samples` set using the provided Google Drive links, as it provides a ready-to-use combination of text and images without complex scraping setups.

**Evaluation Strategy:**
As per the constraints in `docs/dataset_requirements.md`:
1.  **Temporal Splitting:** We should split our training and testing sets temporally (e.g., train on older data, test on the most recent data available in the subset) to evaluate the model's ability to generalize to novel events.
2.  **Cross-Domain Testing:** Train the model on the PolitiFact subset and test it on the GossipCop subset (or vice versa) to see how well the features transfer across different domains of news (political vs. entertainment).

## Sources Accessed During Research
*   [FakeNewsNet GitHub Repository](https://github.com/KaiDMML/FakeNewsNet) (README and Structure)
*   [Fakeddit GitHub Repository](https://github.com/entitize/Fakeddit) (README)
*   ArXiv abstracts for both original papers to confirm dataset scales and goals.

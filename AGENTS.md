# Development Guidelines for AI-Based Fake News Detection System

This document outlines guidelines for future tasks and agents contributing to this project. Please adhere to these principles to maintain code quality and ease of learning.

## Principles

1.  **Modularity:** Write small, single-purpose functions. Separate concerns by using the modules defined in the `src/` directory (preprocessing, classification, ocr, image analysis).
2.  **Readability:** Write clean Python code. Use descriptive variable names and provide docstrings for every function and class. Include inline comments for complex logic to aid learning.
3.  **Testing First:** Before implementing a new feature, write a test for it in the `tests/` directory. Run `pytest` frequently to catch regressions.
4.  **No Hallucinated Data/Results:** Do not claim that fake-news detection works until a model is actually trained and evaluated. Do not invent model accuracy metrics.
5.  **Datasets:** Do not download large datasets automatically during setup or testing unless explicitly instructed to do so in a specific task. Use small, mocked data for testing utilities.
6.  **Dependency Management:** If a new library is required, ensure it is added to `requirements.txt` and is compatible with existing dependencies.

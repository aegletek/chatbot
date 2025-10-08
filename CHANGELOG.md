# Change Log

All notable changes to this project will be documented in this file.
The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [0.1.0] - 2025-10-07

### Added

- **Change:** Initial project setup with a RAG-based chatbot architecture.
- **Reason:** To create a foundational chatbot for a government website that can answer questions based on a private knowledge base of PDF documents.
- **Changed Outcome:** A working bare-bones application consisting of data ingestion, a retrieval-augmented backend, and a FastAPI for user interaction.

- **Change:** Implemented PDF data ingestion from a dedicated `/data` directory.
- **Reason:** To allow the chatbot's knowledge base to be easily updated with official PDF documents, following the project's rulebook structure.
- **Changed Outcome:** The chatbot now learns from PDF files placed in the `/data` folder instead of a sample text file.

- **Change:** Created a FastAPI backend to serve the chatbot.
- **Reason:** To expose the chatbot's functionality via an API, allowing it to be integrated into a website front-end.
- **Changed Outcome:** The chatbot is now accessible via a `/chat` endpoint and can be interacted with programmatically.

- **Change:** Implemented a user-centric document download feature.
- **Reason:** To prioritize user experience by providing direct download links to forms and documents, reducing user navigation fatigue.
- **Changed Outcome:** The chatbot's API response now includes direct URLs to relevant PDFs. The chatbot's core prompt has been updated to offer these links proactively.

- **Change:** Established project structure and dependency management using `uv` and `pyproject.toml`.
- **Reason:** To align the project with the standards defined in the `rulebook.txt`, ensuring a clean and repeatable development environment.
- **Changed Outcome:** The project now has a formal structure, a `.gitignore` file, and a `pyproject.toml` to manage dependencies.

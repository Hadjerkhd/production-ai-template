# 🚀 Production AI Full-Stack Template


<p>
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/uv-Astral-purple?style=for-the-badge" alt="uv">
</p>

[![CI/CD Pipeline](https://github.com/Hadjerkhd/production-ai-template/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Hadjerkhd/production-ai-template/actions/workflows/ci-cd.yml)

This is a production-ready template for building full-stack AI applications using modern Python tooling.

## Tech Stack

- **FastAPI**: High-performance backend API framework.
- **LangChain**: Framework for building LLM applications (using LCEL).
- **Streamlit**: Rapid frontend development for data apps.
- **UV**: Extremely fast Python package installer and resolver.
- **Docker**: Containerization for consistent deployment.
- **Ruff & Mypy**: Advanced linting and type checking.

## Project Structure

```
├── app/
│   ├── routes/         # API route handlers
│   ├── config.py       # Configuration and environment variables
│   ├── schemas/        # Pydantic models for request/response
│   ├── services/       # Business logic and specialized services (LLM, etc.)
│   └── main.py         # Application entry point
├── tests/              # Unit and integration tests
├── ui/
│   └── app.py              # Streamlit frontend application
├── .env.example            # Example environment variables
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── pyproject.toml          # Dependencies and project metadata
└── uv.lock                 # Lock file for reproducible installs
```

## Prerequisites

- [uv](https://github.com/astral-sh/uv)
- [pre-commit](https://pre-commit.com/)
- [Docker](https://www.docker.com/) (optional, for containerized run)
- Python 3.9+

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your API keys (e.g., `OPENAI_API_KEY`) if you plan to use real LLM providers.

## Quick Start (Local)

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Start the Backend**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

3. **Start the Frontend** (in a new terminal):
   ```bash
   uv run streamlit run ui/app.py
   ```
   - UI: [http://localhost:8501](http://localhost:8501)

## Quick Start (Docker)

You can run the entire stack (Backend + Frontend) using Docker.

1. **Build and Run**:
   ```bash
   docker-compose up --build
   ```
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Frontend UI: [http://localhost:8501](http://localhost:8501)

## Development

- **Linting & Formatting**:
  ```bash
  uv run ruff check . --fix
  uv run ruff format .
  ```
- **Type Checking**:
  ```bash
  uv run mypy .
  ```
- **Testing**:
  ```bash
  uv run pytest
  ```
  or using the makefile:
  ```bash
  make test
  ```

- **Pre-commit Hooks**:
  This project uses `pre-commit` to ensure code quality. To install the hooks locally:
  ```bash
  uv run pre-commit install
  ```
  Once installed, the hooks (Ruff, formatting, etc.) will run automatically on every `git commit`. You can also run them manually:
  ```bash
  uv run pre-commit run --all-files
  ```

## CI/CD Pipeline

This project includes a GitHub Actions workflow that automatically:
1.  **Checks Quality**: Runs `ruff` formatting/linting and `mypy` type checking.
2.  **Builds & Publishes**: Builds the Docker image and pushes it to **GitHub Container Registry (GHCR)**.

The workflow runs on every push to the `main` branch. No manual secret configuration is needed as it uses the default `GITHUB_TOKEN`.

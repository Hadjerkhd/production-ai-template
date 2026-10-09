# Production AI Full-Stack Template


<p>
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain">
   <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/uv-Astral-purple?style=for-the-badge" alt="uv">
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" alt="MLflow">
</p>

[![CI/CD Pipeline](https://github.com/Hadjerkhd/production-ai-template/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Hadjerkhd/production-ai-template/actions/workflows/ci-cd.yml)

This is a production-ready template for building full-stack AI applications using modern Python tooling.

## Tech Stack

- **FastAPI**: High-performance backend API framework.
- **LangChain**: Framework for building LLM applications (using LCEL).
- **Streamlit**: Lightweight UI for the FastAPI backend.
- **Vertex AI**: Gemini access through the Cloud Run service account and ADC.
- **UV**: Extremely fast Python package installer and resolver.
- **Docker**: Containerization for consistent deployment.
- **Ruff & Mypy**: Advanced linting and type checking.
- **MLflow**: Open-source platform for managing the end-to-end machine learning lifecycle, used here for LLM tracing and observability.

## Project Structure

```
├── app/
│   ├── routes/         # API route handlers
│   ├── config.py       # Configuration and environment variables
│   ├── schemas/        # Pydantic models for request/response
│   ├── services/       # Business logic and specialized services (LLM, etc.)
│   └── main.py         # Application entry point
├── tests/              # Unit and integration tests
├── ui/                  # Streamlit UI
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
- Python 3.10+

## Configuration

1. Copy the backend example environment file:
   ```bash
   cp .env.example .env
   ```
2. Configure local development. The API does not authenticate callers; no Vertex key is stored in `.env`. Use Application Default Credentials:
   ```env
   GCP_PROJECT_ID="your-project"
   ```
   For Vertex AI access, run `gcloud auth application-default login`.

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

3. **Start the UI** (in a new terminal):
   ```bash
   uv run streamlit run ui/main.py
   ```
   - UI: [http://localhost:8501](http://localhost:8501)

## Quick Start (Docker)

You can run the entire stack (FastAPI + Streamlit) using Docker.

1. **Build and Run**:
   ```bash
   docker-compose up --build
   ```
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Streamlit UI: [http://localhost:8501](http://localhost:8501)

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

The `deploy-backend-public.yml` workflow builds the backend image, pushes it to Artifact Registry, and deploys the FastAPI backend to Cloud Run. It does not deploy the Streamlit UI.

Configure repository variables `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_WIF_PROVIDER`, `GCP_DEPLOYER_SERVICE_ACCOUNT`, and `GCP_RUNTIME_SERVICE_ACCOUNT`.

The API is deployed to Cloud Run with IAM authentication required. Grant `roles/run.invoker` only to intended callers. The Streamlit UI currently runs locally or through Docker Compose and is not configured to authenticate to the protected Cloud Run service.

### GCP bootstrap

Enable Cloud Run, Artifact Registry, Vertex AI, and IAM Credentials APIs. Create the Artifact Registry repository and grant the runtime service account `roles/aiplatform.user`.

Create a GitHub OIDC provider restricted to this repository and grant the deployer service account `roles/run.admin`, `roles/artifactregistry.writer`, and `roles/iam.serviceAccountUser`. Do not place service-account JSON keys or Vertex credentials in GitHub.

## Observability & LLM Tracing

This template includes built-in support for LLM tracing using **MLflow**.

### 1. Start the MLflow Server

In a separate terminal, start the MLflow tracking server:
```bash
make start-mlflow
```
The server will be available at [http://localhost:5000](http://localhost:5000).

### 2. Automatic Tracing

The application uses `mlflow.langchain.autolog()` to automatically capture traces of all LangChain calls. This includes:
- Prompts and completions
- Chain execution metadata
- Token usage (if available from provider)
- Latency and errors

Traces are automatically associated with the experiment name defined in `MLFLOW_EXPERIMENT_NAME`.

## Todo
- [x] observability
- [ ] automatic eval in ci/cd
- [ ] code security/vulnerability analysis in ci/cd
- [ ] lock commits on main branch

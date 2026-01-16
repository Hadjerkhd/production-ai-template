# 🚀 Modern AI Full-Stack Template


<p>
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/uv-Astral-purple?style=for-the-badge" alt="uv">
</p>

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
│   ├── api/
│   │   └── routes/         # API route handlers
│   ├── core/
│   │   └── config.py       # Configuration and environment variables
│   ├── schemas/            # Pydantic models for request/response
│   ├── services/           # Business logic and specialized services (LLM, etc.)
│   └── main.py             # Application entry point
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

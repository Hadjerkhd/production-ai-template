pull-docker-image:
	docker pull ghcr.io/hadjerkhd/production-ai-template:latest

test:
	uv run pytest

start-mlflow:
	uv run mlflow server --host 0.0.0.0 --port 5000

pull-docker-image:
	docker pull ghcr.io/hadjerkhd/production-ai-template:latest

test:
	uv run pytest
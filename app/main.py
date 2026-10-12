import logging
import time
import uuid

import mlflow
from fastapi import FastAPI, Request

from app.config import settings
from app.logging_config import configure_logging, request_id_context
from app.routes import health, llm

configure_logging()
logger = logging.getLogger(__name__)

# Configure MLflow
if settings.ENABLE_MLFLOW:
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    experiment = mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)
    experiment_id = experiment.experiment_id

    # Enable LangChain autologging for LLM traces
    mlflow.langchain.autolog()

app = FastAPI(title=settings.PROJECT_NAME)


@app.middleware("http")
async def log_request(request: Request, call_next):
    request_id = uuid.uuid4().hex
    context_token = request_id_context.set(request_id)
    route = request.scope.get("route")
    route_path = getattr(route, "path", request.url.path)
    started_at = time.perf_counter()
    status_code = 500
    error_type = None

    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as error:
        error_type = type(error).__name__
        raise
    finally:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        severity = (
            logging.ERROR
            if status_code >= 500
            else logging.WARNING
            if status_code >= 400
            else logging.INFO
        )
        logger.log(
            severity,
            "HTTP request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "route": route_path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "error_type": error_type,
            },
        )
        request_id_context.reset(context_token)


app.include_router(llm.router, prefix="/api/v1", tags=["llm"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the LLM Service API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

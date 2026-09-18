import mlflow
from fastapi import FastAPI

from app.config import settings
from app.routes import llm

# Configure MLflow
if settings.ENABLE_MLFLOW:
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    experiment = mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)
    experiment_id = experiment.experiment_id

    # Enable LangChain autologging for LLM traces
    mlflow.langchain.autolog()

app = FastAPI(title=settings.PROJECT_NAME)


app.include_router(llm.router, prefix="/api/v1", tags=["llm"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the LLM Service API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

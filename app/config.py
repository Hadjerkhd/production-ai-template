from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Production AI Template"
    API_V1_STR: str = "/api/v1"

    GCP_PROJECT_ID: str | None = None
    VERTEX_AI_LOCATION: str = "europe-west1"
    VERTEX_AI_MODEL: str = "gemini-2.5-flash-lite"
    LOG_LEVEL: str = "INFO"
    MAX_PROMPT_CHARACTERS: int = 12000
    MAX_OUTPUT_TOKENS: int = 512
    VERTEX_AI_TIMEOUT_SECONDS: float = 35.0
    GENERATE_RATE_LIMIT_PER_MINUTE: int = 20

    # MLflow Settings
    ENABLE_MLFLOW: bool = False
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "llm-traces"

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )


settings = Settings()

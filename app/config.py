from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Production AI Template"
    API_V1_STR: str = "/api/v1"

    # Example validation for keys
    OPENAI_API_KEY: str = "OPENAI_API_KEY"

    # MLflow Settings
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "llm-traces"

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )


settings = Settings()

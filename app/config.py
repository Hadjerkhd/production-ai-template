from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Production AI Template"
    API_V1_STR: str = "/api/v1"

    # Example validation for keys
    OPENAI_API_KEY: str = "OPENAI_API_KEY"

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )


settings = Settings()

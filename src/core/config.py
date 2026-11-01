from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ZITADEL_ISSUER: str
    ZITADEL_JWKS_URL: str
    ZITADEL_CLIENT_ID: str
    ZITADEL_PROJECT_ID: str  # Tokenin aud kısmında bulunmalı - yoksa albot için üretilmemiş bri tokendir

    database_url: str
    # DATABASE_URL: str


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    NVIDIA_API_KEY: str
    NVIDIA_BASE_URL: str
    LLM_MODEL: str


# settings = Settings()
llm_settings = LLMSettings()

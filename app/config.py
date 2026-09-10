from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url: str="sqlite:///./security_review.db"
    sentry_dsn: str=""
    github_token: str=""
    openai_api_key: str=""
    anthropic_api_key: str=""
    ai_provider: str="openai"
    ai_model: str="gpt-4.1-mini"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()

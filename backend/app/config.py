from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://prreview:prreview@localhost:5432/prreview"

    llm_provider: str = "anthropic"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384

    github_token: str = ""
    github_webhook_secret: str = ""
    github_api_url: str = "https://api.github.com"

    # Ingestion limits (keep LLM cost and latency bounded)
    max_source_fetches: int = 30        # max files whose full source we fetch per PR
    max_file_bytes: int = 200_000       # skip function mapping for bigger files


settings = Settings()

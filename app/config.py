from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  """Application settings loaded from environment variables / .env file."""

  llm_api_key: str
  llm_base_url: str = "https://openrouter.ai/api/v1"
  llm_provider: str = "openrouter"
  llm_model: str = "nvidia/nemotron-3-super-120b-a12b:free"
  frontend_origin: str = "http://localhost:5173"
  env: str = "development"

  model_config = {
    "env_file": ".env",
    "env_file_encoding": "utf-8",
  }


settings = Settings()

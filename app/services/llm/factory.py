from app.config import settings
from app.services.llm.base import LLMClient
from app.services.llm.openrouter import OpenRouterClient

def get_llm_client() -> LLMClient:
  provider = settings.llm_provider.lower()
  if provider == "openrouter":
    return OpenRouterClient()
  raise ValueError(f"Unknown LLM provider: {provider}")

client: LLMClient = get_llm_client()
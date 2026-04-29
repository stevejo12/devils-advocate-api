from openai import AsyncOpenAI
from app.config import settings
from app.services.llm.base import LLMClient

class OpenRouterClient(LLMClient):
  def __init__(self) -> None:
    self._client = AsyncOpenAI(
      api_key=settings.llm_api_key,
      base_url=settings.llm_base_url,
    )

  async def generate(
    self,
    messages: list[dict[str, str]],
    system: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
  ) -> str:
    full_messages = [{"role": "system", "content": system}, *messages]

    response = await self._client.chat.completions.create(
      model=settings.llm_model,
      max_tokens=max_tokens,
      temperature=temperature,
      messages=full_messages,
      stop=["[The Pragmatist]:", "[The Contrarian]:", "[The Wildcard]:", "[User]:"],
    )

    return response.choices[0].message.content or ""
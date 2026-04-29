from abc import ABC, abstractmethod

class LLMClient(ABC):
  @abstractmethod
  async def generate(
    self,
    messages: list[dict[str, str]],
    system: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
  ) -> str:
    """Generate a completion.

    Args:
      messages: conversation history in OpenAI shape — list of {role, content}
        where role is "user" or "assistant". System prompt is passed separately.
      system: the system prompt for this call.
      max_tokens: maximum tokens to generate.
      temperature: sampling temperature.

    Returns:
      The generated text content.
    """
    ... # to make sure the generation of a class not abstract (act as an extension)
"""Orchestrator: fans out to three personas in parallel via asyncio.gather()."""
import asyncio
from openai import AsyncOpenAI
from app.config import settings
from app.models.enums import PersonaName, SenderType
from app.models.responses import Message, PersonaResponse
from app.services.personas import load_persona_prompt

_client = AsyncOpenAI(
  api_key=settings.llm_api_key,
  base_url=settings.llm_base_url,
)

# Map SenderType to display labels used inside the conversation history
_SENDER_LABELS: dict[SenderType, str] = {
  SenderType.USER: "User",
  SenderType.PRAGMATIST: "The Pragmatist",
  SenderType.CONTRARIAN: "The Contrarian",
  SenderType.WILDCARD: "The Wildcard",
}


def _build_openai_messages(
  history: list[Message],
  current_persona: PersonaName,
  system_prompt: str,
) -> list[dict[str, str]]:
  """Convert our internal message history into OpenAI-compatible message format.

  All three personas share the same conversation history. The current
  persona's messages become "assistant" role (so the model continues as
  that persona); everything else becomes "user" role.
  """
  messages: list[dict[str, str]] = [
    {"role": "system", "content": system_prompt},
  ]

  for msg in history:
    label = _SENDER_LABELS[msg.sender]
    prefixed_content = f"[{label}]: {msg.content}"

    if msg.sender == SenderType(current_persona.value):
      role = "assistant"
      # Assistant messages don't need the prefix — the model knows it's itself
      content = msg.content
    else:
      role = "user"
      content = prefixed_content

    # OpenAI API requires alternating user/assistant roles.
    # If two consecutive messages have the same role, merge them.
    if len(messages) > 1 and messages[-1]["role"] == role:
      messages[-1]["content"] += f"\n\n{content}"
    else:
      messages.append({"role": role, "content": content})

  # The API expects the last message to be from "user" for a new response.
  # If the last message is assistant, add a placeholder.
  if messages[-1]["role"] == "assistant":
    messages.append(
      {"role": "user", "content": "[System]: It's your turn to respond."}
    )

  return messages


async def _call_persona(
  persona: PersonaName,
  history: list[Message],
) -> PersonaResponse:
  """Make a single LLM call for one persona."""
  system_prompt = load_persona_prompt(persona)
  messages = _build_openai_messages(history, persona, system_prompt)

  response = await _client.chat.completions.create(
    model=settings.llm_model,
    max_tokens=1024,
    messages=messages,
  )

  content = response.choices[0].message.content

  return PersonaResponse(
    persona=persona,
    display_name=persona.display_name,
    content=content,
  )


async def run_debate_round(
  history: list[Message],
) -> list[PersonaResponse]:
  """Fan out to all three personas in parallel and return their responses."""
  tasks = [_call_persona(persona, history) for persona in PersonaName]
  results = await asyncio.gather(*tasks)
  return list(results)

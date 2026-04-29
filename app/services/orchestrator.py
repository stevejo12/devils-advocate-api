import asyncio
from app.services.llm import client
# from app.config import settings
from app.models.enums import PersonaName, SenderType
from app.models.responses import Message, PersonaResponse
from app.services.personas import load_persona_prompt

_SENDER_LABELS: dict[SenderType, str] = {
  SenderType.USER: "User",
  SenderType.PRAGMATIST: "The Pragmatist",
  SenderType.CONTRARIAN: "The Contrarian",
  SenderType.WILDCARD: "The Wildcard",
}

DEBATE_ORDER: list[PersonaName] = [
  PersonaName.PRAGMATIST,
  PersonaName.CONTRARIAN,
  PersonaName.WILDCARD,
]

def _build_conversation_messages(
  history: list[Message],
  current_persona: PersonaName,
) -> list[dict[str, str]]:
  """Convert internal message history into OpenAI-shape conversation messages.

  System prompt is NOT included here — it's passed separately to client.generate().
  Current persona's messages become "assistant"; everything else is "user".
  Consecutive same-role messages are merged to satisfy strict alternation.
  """
  messages: list[dict[str, str]] = []

  for msg in history:
    label = _SENDER_LABELS[msg.sender]
    prefixed_content = f"[{label}]: {msg.content}"

    if msg.sender == SenderType(current_persona.value):
      role = "assistant"
      content = msg.content  # no prefix needed for self
    else:
      role = "user"
      content = prefixed_content

    if messages and messages[-1]["role"] == role:
      messages[-1]["content"] += f"\n\n{content}"
    else:
      messages.append({"role": role, "content": content})

  # Ensure the last message is from "user" so the model has something to respond to
  if not messages or messages[-1]["role"] == "assistant":
    messages.append(
      {"role": "user", "content": f"[System]: You are {current_persona.display_name}. Respond now in your own voice. Do NOT include the [{current_persona.display_name}]: prefix — it will be added automatically. Do NOT speak as any other persona."}
    )

  return messages


async def _call_persona(
  persona: PersonaName,
  history: list[Message],
) -> PersonaResponse:
  system_prompt = load_persona_prompt(persona)
  messages = _build_conversation_messages(history, persona)

  content = await client.generate(
    messages=messages,
    system=system_prompt,
    max_tokens=1500,
  )

  for label in _SENDER_LABELS.values():
    prefix = f"[{label}]:"
    if content.lstrip().startswith(prefix):
      content = content.lstrip()[len(prefix):].lstrip()

  # If after stripping the response is empty or trivially short, that's a generation failure
  if len(content.strip()) < 20:
    # Decide your policy: retry once, raise, or return a placeholder. For now, raise.
    raise ValueError(f"Persona {persona.value} produced empty/glitched response")

  return PersonaResponse(
    persona=persona,
    display_name=persona.display_name,
    content=content,
  )

async def run_debate_round(
  history: list[Message],
) -> list[PersonaResponse]:
  """Run one round of debate sequentially: each persona sees prior personas' replies.

  Returns responses in the order they were generated. The caller is responsible
  for appending them to session history.
  """
  responses: list[PersonaResponse] = []
  # Build up the working history as personas speak. Don't mutate the caller's list.
  working_history = list(history)

  for persona in DEBATE_ORDER:
    response = await _call_persona(persona, working_history)
    responses.append(response)
    # Add this persona's reply to the working history so the next persona sees it
    working_history.append(
      Message(sender=SenderType(persona.value), content=response.content)
    )

  return responses

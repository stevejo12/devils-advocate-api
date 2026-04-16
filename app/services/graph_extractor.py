"""Extracts argument graph metadata (nodes + edges) from persona responses.

Uses the OpenRouter API (OpenAI-compatible) with function calling to pull
out argument nodes, their stances, and edges between them.
"""
import json
from openai import AsyncOpenAI

from app.config import settings
from app.models.graph import ArgumentEdge, ArgumentNode, GraphUpdate
from app.models.responses import PersonaResponse

_client = AsyncOpenAI(
  api_key=settings.llm_api_key,
  base_url=settings.llm_base_url,
)

_EXTRACTION_SYSTEM_PROMPT = """\
You are an argument-graph extractor. Given a set of debate responses from \
three personas (The Pragmatist, The Contrarian, The Wildcard), extract the \
key arguments as graph nodes and the relationships between them as edges.

Each node should have:
- id: a short unique slug (e.g., "risk-of-failure", "autonomy-value")
- label: a concise description of the argument (< 10 words)
- persona: which persona made this argument
- stance: "support", "oppose", or "neutral" relative to the user's original position

Each edge should have:
- source: the id of the source node
- target: the id of the target node
- relation: "supports", "counters", or "elaborates"

Return valid JSON matching the schema in the function definition.
"""

_GRAPH_FUNCTION = {
  "name": "submit_graph_update",
  "description": "Submit the extracted argument graph nodes and edges.",
  "parameters": {
    "type": "object",
    "properties": {
      "nodes": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string"},
            "label": {"type": "string"},
            "persona": {"type": "string"},
            "stance": {
              "type": "string",
              "enum": ["support", "oppose", "neutral"],
            },
          },
          "required": ["id", "label", "persona", "stance"],
        },
      },
      "edges": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "source": {"type": "string"},
            "target": {"type": "string"},
            "relation": {
              "type": "string",
              "enum": ["supports", "counters", "elaborates"],
            },
          },
          "required": ["source", "target", "relation"],
        },
      },
    },
    "required": ["nodes", "edges"],
  },
}


async def extract_graph(
  user_message: str,
  responses: list[PersonaResponse],
) -> GraphUpdate:
  """Extract an argument graph update from the latest debate round."""
  # Build the content for the extraction prompt
  response_text = "\n\n".join(
    f"[{r.display_name}]: {r.content}" for r in responses
  )

  prompt = (
    f"The user said: \"{user_message}\"\n\n"
    f"The personas responded:\n\n{response_text}\n\n"
    f"Extract the argument graph from these responses."
  )

  result = await _client.chat.completions.create(
    model=settings.llm_model,
    max_tokens=1024,
    messages=[
      {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
      {"role": "user", "content": prompt},
    ],
    tools=[{
      "type": "function",
      "function": _GRAPH_FUNCTION,
    }],
    tool_choice={
      "type": "function",
      "function": {"name": "submit_graph_update"},
    },
  )

  # Parse the tool call result
  message = result.choices[0].message
  if message.tool_calls:
    for tool_call in message.tool_calls:
      if tool_call.function.name == "submit_graph_update":
        data = json.loads(tool_call.function.arguments)
        nodes = [ArgumentNode(**n) for n in data.get("nodes", [])]
        edges = [ArgumentEdge(**e) for e in data.get("edges", [])]
        return GraphUpdate(nodes=nodes, edges=edges)

  # Fallback if no tool call was returned
  return GraphUpdate(nodes=[], edges=[])

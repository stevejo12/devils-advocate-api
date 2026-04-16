"""SSE event formatting helpers."""
import json
from typing import Any

def format_sse_event(
  event: str,
  data: Any,
  event_id: str | None = None,
) -> str:
  """Format a payload as a Server-Sent Event string.

  Args:
    event: The SSE event type (e.g., "persona_response", "graph_update").
    data: The data payload — will be JSON-serialized.
    event_id: Optional event ID for client-side reconnection tracking.

  Returns:
    A properly formatted SSE string.
  """
  lines: list[str] = []
  if event_id:
    lines.append(f"id: {event_id}")
  lines.append(f"event: {event}")
  lines.append(f"data: {json.dumps(data)}")
  lines.append("")  # trailing newline to terminate the event
  return "\n".join(lines) + "\n"


def format_persona_event(persona: str, content: str) -> str:
  """Convenience wrapper for a persona response SSE event."""
  return format_sse_event(
    event="persona_response",
    data={"persona": persona, "content": content},
  )


def format_error_event(message: str) -> str:
  """Format an error as an SSE event."""
  return format_sse_event(event="error", data={"message": message})


def format_done_event() -> str:
  """Format a stream-complete SSE event."""
  return format_sse_event(event="done", data={})

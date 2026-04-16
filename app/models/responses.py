from pydantic import BaseModel, Field

from app.models.enums import PersonaName, SenderType

class Message(BaseModel):
  """A single message in the conversation history."""

  sender: SenderType
  content: str


class PersonaResponse(BaseModel):
  """One persona's response in a debate round."""

  persona: PersonaName
  display_name: str
  content: str


class DebateStartResponse(BaseModel):
  """Response body for POST /debate/start."""

  session_id: str
  responses: list[PersonaResponse] = Field(
    ...,
    description="The three persona responses to the user's initial message.",
  )


class DebateRespondResponse(BaseModel):
  """Response body for POST /debate/respond."""

  session_id: str
  responses: list[PersonaResponse]


class DebateSummaryResponse(BaseModel):
  """Response body for GET /debate/summary."""

  session_id: str
  message_count: int
  history: list[Message]

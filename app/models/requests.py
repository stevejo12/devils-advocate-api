from pydantic import BaseModel, Field

class DebateStartRequest(BaseModel):
  """Request body for POST /debate/start."""
  message: str = Field(
    ...,
    min_length=1,
    max_length=5000,
    description="The user's initial belief or decision to debate.",
    examples=["I think I should skip my co-op and build a startup."],
  )


class DebateRespondRequest(BaseModel):
  """Request body for POST /debate/respond."""

  session_id: str = Field(
    ...,
    description="The session ID returned from /debate/start.",
  )
  message: str = Field(
    ...,
    min_length=1,
    max_length=5000,
    description="The user's follow-up message in the debate.",
  )

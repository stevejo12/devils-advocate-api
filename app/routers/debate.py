from uuid import uuid4
from fastapi import APIRouter, HTTPException

from app.models.enums import SenderType
from app.models.requests import DebateRespondRequest, DebateStartRequest
from app.models.responses import (
  DebateStartResponse,
  DebateRespondResponse,
  DebateSummaryResponse,
  Message,
  PersonaResponse,
)
from app.services.orchestrator import run_debate_round

router = APIRouter(prefix="/debate", tags=["debate"])

# In-memory session store: session_id -> list[Message]
_sessions: dict[str, list[Message]] = {}

def _append_persona_responses(
  session_id: str, responses: list[PersonaResponse]
) -> None:
  """Add persona responses to the session history."""
  for r in responses:
    _sessions[session_id].append(
      Message(sender=SenderType(r.persona.value), content=r.content)
    )


@router.post("/start", response_model=DebateStartResponse)
async def start_debate(body: DebateStartRequest) -> DebateStartResponse:
  """Start a new debate session.

  Accepts the user's initial belief/decision, fans out to three personas,
  and returns their responses along with a session ID for follow-ups.
  """
  session_id = str(uuid4())

  # Initialize session with the user's opening message
  user_msg = Message(sender=SenderType.USER, content=body.message)
  _sessions[session_id] = [user_msg]

  # Run the three personas in parallel
  responses = await run_debate_round(_sessions[session_id])

  # Store persona responses in session history
  _append_persona_responses(session_id, responses)

  return DebateStartResponse(session_id=session_id, responses=responses)


@router.post("/respond", response_model=DebateRespondResponse)
async def respond_to_debate(body: DebateRespondRequest) -> DebateRespondResponse:
  """Continue an existing debate session with a follow-up message.

  The user's new message is appended to the session history, then all three
  personas respond with awareness of the full conversation so far.
  """
  if body.session_id not in _sessions:
    raise HTTPException(status_code=404, detail="Session not found.")

  # Append user's follow-up to history
  user_msg = Message(sender=SenderType.USER, content=body.message)
  _sessions[body.session_id].append(user_msg)

  # Run another debate round with full history
  responses = await run_debate_round(_sessions[body.session_id])

  # Store persona responses
  _append_persona_responses(body.session_id, responses)

  return DebateRespondResponse(session_id=body.session_id, responses=responses)


@router.get("/summary/{session_id}", response_model=DebateSummaryResponse)
async def get_debate_summary(session_id: str) -> DebateSummaryResponse:
  """Retrieve the full conversation history for a debate session."""
  if session_id not in _sessions:
    raise HTTPException(status_code=404, detail="Session not found.")

  history = _sessions[session_id]
  return DebateSummaryResponse(
    session_id=session_id,
    message_count=len(history),
    history=history,
  )

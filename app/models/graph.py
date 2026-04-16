from typing import Literal

from pydantic import BaseModel, Field


class ArgumentNode(BaseModel):
  """A single argument or claim in the debate graph."""

  id: str = Field(..., description="Unique node identifier.")
  label: str = Field(..., description="Short label for the node.")
  persona: str = Field(..., description="Which persona made this argument.")
  stance: Literal["support", "oppose", "neutral"] = Field(
    ..., description="Stance toward the user's original position."
  )


class ArgumentEdge(BaseModel):
  """A directed edge between two argument nodes."""

  source: str = Field(..., description="ID of the source node.")
  target: str = Field(..., description="ID of the target node.")
  relation: Literal["supports", "counters", "elaborates"] = Field(
    ..., description="How source relates to target."
  )


class GraphUpdate(BaseModel):
  """An incremental update to the argument graph after a debate round."""

  nodes: list[ArgumentNode] = Field(default_factory=list)
  edges: list[ArgumentEdge] = Field(default_factory=list)

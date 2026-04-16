from enum import StrEnum

class PersonaName(StrEnum):
  """The three debate personas."""

  PRAGMATIST = "pragmatist"
  CONTRARIAN = "contrarian"
  WILDCARD = "wildcard"

  @property
  def display_name(self) -> str:
    return {
      "pragmatist": "The Pragmatist",
      "contrarian": "The Contrarian",
      "wildcard": "The Wildcard",
    }[self.value]


class SenderType(StrEnum):
  """Who sent a message in the conversation."""

  USER = "user"
  PRAGMATIST = "pragmatist"
  CONTRARIAN = "contrarian"
  WILDCARD = "wildcard"

"""Persona prompt loader with simple in-memory caching."""
from pathlib import Path
from app.models.enums import PersonaName
_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
_cache: dict[PersonaName, str] = {}


def load_persona_prompt(persona: PersonaName) -> str:
  """Load the system prompt for a persona from its markdown file.

  Results are cached so disk I/O only happens once per persona per process.
  """
  if persona in _cache:
    return _cache[persona]

  prompt_file = _PROMPTS_DIR / f"{persona.value}.md"
  if not prompt_file.exists():
    raise FileNotFoundError(
      f"Prompt file not found for persona '{persona.value}': {prompt_file}"
    )

  text = prompt_file.read_text(encoding="utf-8")
  _cache[persona] = text
  return text


def load_all_prompts() -> dict[PersonaName, str]:
  """Load and return system prompts for all three personas."""
  return {persona: load_persona_prompt(persona) for persona in PersonaName}

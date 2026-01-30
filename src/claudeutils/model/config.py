"""Pydantic models for model configuration."""

from pydantic import BaseModel


class LiteLLMModel(BaseModel):
    """LiteLLM model configuration."""

    name: str
    litellm_model: str
    tiers: list[str]
    arena_rank: int
    input_price: float
    output_price: float
    api_key_env: str
    api_base: str | None = None

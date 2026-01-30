"""Pydantic models for model configuration."""

import re

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


def parse_model_entry(yaml_text: str) -> LiteLLMModel:
    """Extract model_name and litellm_model from YAML entry.

    Args:
        yaml_text: YAML entry containing model_name and litellm_params.model

    Returns:
        LiteLLMModel with parsed data
    """
    model_name_match = re.search(r"model_name:\s*(.+?)(?:\n|$)", yaml_text)
    litellm_model_match = re.search(r"model:\s*(.+?)(?:\n|$)", yaml_text)

    if not model_name_match or not litellm_model_match:
        msg = "Could not extract model_name or model from YAML"
        raise ValueError(msg)

    model_name = model_name_match.group(1).strip()
    litellm_model = litellm_model_match.group(1).strip()

    # Extract tiers from comment line (e.g., "# haiku,sonnet - arena:5")
    tiers = []
    tiers_match = re.search(r"#\s*([a-z,]+)\s*-", yaml_text)
    if tiers_match:
        tiers_str = tiers_match.group(1)
        tiers = [t.strip() for t in tiers_str.split(",")]

    return LiteLLMModel(
        name=model_name,
        litellm_model=litellm_model,
        tiers=tiers,
        arena_rank=0,
        input_price=0.0,
        output_price=0.0,
        api_key_env="",
    )

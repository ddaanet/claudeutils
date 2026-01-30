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

    # Extract arena rank (e.g., "arena:5")
    arena_rank = 0
    arena_match = re.search(r"arena:(\d+)", yaml_text)
    if arena_match:
        arena_rank = int(arena_match.group(1))

    # Extract pricing (e.g., "$0.25/$1.25")
    input_price = 0.0
    output_price = 0.0
    pricing_match = re.search(r"\$(\d+\.\d+)/\$(\d+\.\d+)", yaml_text)
    if pricing_match:
        input_price = float(pricing_match.group(1))
        output_price = float(pricing_match.group(2))

    return LiteLLMModel(
        name=model_name,
        litellm_model=litellm_model,
        tiers=tiers,
        arena_rank=arena_rank,
        input_price=input_price,
        output_price=output_price,
        api_key_env="",
    )

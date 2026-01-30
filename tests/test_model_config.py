"""Test model configuration with Pydantic models."""

from claudeutils.model import LiteLLMModel


def test_litellm_model_creation() -> None:
    """LiteLLMModel can be instantiated with required fields."""
    model = LiteLLMModel(
        name="Claude 3.5 Sonnet",
        litellm_model="claude-3-5-sonnet-20241022",
        tiers=["plan", "api"],
        arena_rank=1,
        input_price=3.0,
        output_price=15.0,
        api_key_env="ANTHROPIC_API_KEY",
        api_base=None,
    )
    assert model.name == "Claude 3.5 Sonnet"
    assert model.litellm_model == "claude-3-5-sonnet-20241022"
    assert model.tiers == ["plan", "api"]
    assert model.arena_rank == 1
    assert model.input_price == 3.0
    assert model.output_price == 15.0
    assert model.api_key_env == "ANTHROPIC_API_KEY"
    assert model.api_base is None

from app.core.llm.pricing import estimate_cost_usd


def test_free_model_zero_cost():
    cost = estimate_cost_usd(
        "google/gemma-4-26b-a4b-it:free",
        {"prompt_tokens": 100, "completion_tokens": 50},
    )
    assert cost == 0.0

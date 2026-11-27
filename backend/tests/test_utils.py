"""Offline tests for preference summarization and reward fallback logic."""
from types import SimpleNamespace

import app.utils as utils
import app.gemini_api as gemini_api


def test_preference_summary_includes_structured_profile_fields(monkeypatch):
    monkeypatch.setattr(utils, "generate_text_embedding", lambda text: text)
    preferences = {
        "age": 29,
        "income": 900000,
        "income_period": "annual",
        "spending": {"dining": 4000, "fuel": 0},
        "custom_spending": {"subscriptions": 500},
        "reward_preferences": ["cashback"],
        "bank_preference": "Example Bank",
        "special_features": ["airport lounge"],
        "annual_fee_preference": False,
        "credit_score": "good",
        "existing_cards": ["Example Card"],
    }

    summary = utils.generate_text_embedding_from_preferences(preferences)

    assert "Age: 29" in summary
    assert "Income: 900000 (annual)" in summary
    assert "dining: ₹4000/mo" in summary
    assert "subscriptions: ₹500/mo" in summary
    assert "Reward Preferences: cashback" in summary
    assert "Bank Preference: Example Bank" in summary
    assert "Annual Fee Preference: False" in summary


def test_reward_simulation_uses_deterministic_fallback_when_llm_fails(monkeypatch):
    def fail_generation(**kwargs):
        raise RuntimeError("offline test: no external API")

    monkeypatch.setattr(
        gemini_api,
        "genai_client",
        SimpleNamespace(models=SimpleNamespace(generate_content=fail_generation)),
    )

    message, details = utils.simulate_rewards(
        {"reward_rate": "5% cashback on dining"},
        {"spending": {"dining": 1000}},
    )

    assert message == "You could earn approx. ₹600/year"
    assert len(details) == 1
    assert "5% cashback on dining" in details[0]

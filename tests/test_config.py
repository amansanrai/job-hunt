from career_os.config import Settings


def test_airtable_api_key_alias(monkeypatch):
    monkeypatch.delenv("AIRTABLE_TOKEN", raising=False)
    monkeypatch.setenv("AIRTABLE_API_KEY", "pat_test")
    settings = Settings.from_env()
    assert settings.airtable_token == "pat_test"


def test_airtable_api_key_alias_strips_whitespace(monkeypatch):
    monkeypatch.delenv("AIRTABLE_TOKEN", raising=False)
    monkeypatch.setenv("AIRTABLE_API_KEY", "  pat_test  ")
    settings = Settings.from_env()
    assert settings.airtable_token == "pat_test"


def test_airtable_token_fallback_strips_whitespace(monkeypatch):
    monkeypatch.delenv("AIRTABLE_API_KEY", raising=False)
    monkeypatch.setenv("AIRTABLE_TOKEN", "  pat_fallback  ")
    settings = Settings.from_env()
    assert settings.airtable_token == "pat_fallback"

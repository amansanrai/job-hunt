from career_os.config import Settings


def test_airtable_api_key_alias(monkeypatch):
    monkeypatch.delenv("AIRTABLE_TOKEN", raising=False)
    monkeypatch.setenv("AIRTABLE_API_KEY", "pat_test")
    settings = Settings.from_env()
    assert settings.airtable_token == "pat_test"

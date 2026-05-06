from career_os.config import Settings


def test_airtable_api_key_alias(monkeypatch):
    monkeypatch.delenv("AIRTABLE_TOKEN", raising=False)
    monkeypatch.setenv("AIRTABLE_API_KEY", "pat_test")
    settings = Settings.from_env()
    assert settings.airtable_token == "pat_test"


def test_secret_values_are_stripped(monkeypatch):
    monkeypatch.setenv("AIRTABLE_API_KEY", "  pat_test\n")
    monkeypatch.setenv("AIRTABLE_BASE_ID", "\tapp_test ")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", " token_test\n")
    settings = Settings.from_env()
    assert settings.airtable_token == "pat_test"
    assert settings.airtable_base_id == "app_test"
    assert settings.telegram_bot_token == "token_test"

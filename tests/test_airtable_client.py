from career_os.airtable_client import AirtableClient
from career_os.config import Settings


def _settings() -> Settings:
    return Settings(
        airtable_token="pat_test",
        airtable_base_id="app_test",
        airtable_applications_table="Applications",
        airtable_skills_table="Skills",
        airtable_daily_tasks_table="Daily Tasks",
        airtable_resume_versions_table="Resume Versions",
        telegram_bot_token=None,
        telegram_chat_id=None,
        nvidia_api_key=None,
        nvidia_model="model",
        dropbox_token=None,
        adzuna_app_id=None,
        adzuna_app_key=None,
        dry_run=False,
    )


def test_airtable_write_error_is_nonfatal(monkeypatch):
    def fail_post_json(*args, **kwargs):
        raise RuntimeError("HTTP 403 Forbidden")

    monkeypatch.setattr("career_os.airtable_client.post_json", fail_post_json)
    client = AirtableClient(_settings())
    assert client.create_record("Daily Tasks", {"Task": "test"}) is False


def test_airtable_writes_with_typecast(monkeypatch):
    captured = {}

    def fake_post_json(url, payload, headers, timeout):
        captured["url"] = url
        captured["payload"] = payload
        captured["headers"] = headers
        captured["timeout"] = timeout
        return {"id": "rec_test"}

    monkeypatch.setattr("career_os.airtable_client.post_json", fake_post_json)
    client = AirtableClient(_settings())

    assert client.create_record("Applications", {"Status": "Pending"}) is True
    assert captured["payload"] == {"fields": {"Status": "Pending"}, "typecast": True}
    assert captured["headers"]["Authorization"] == "Bearer pat_test"


def test_has_record_for_date_true_when_found(monkeypatch):
    captured = {}

    def fake_get_json(url, params, headers, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        captured["timeout"] = timeout
        return {"records": [{"id": "rec123"}]}

    monkeypatch.setattr("career_os.airtable_client.get_json", fake_get_json)
    client = AirtableClient(_settings())

    assert client.has_record_for_date("Daily Tasks", "2026-05-08") is True
    assert captured["params"]["maxRecords"] == "1"
    assert "2026-05-08" in captured["params"]["filterByFormula"]


def test_has_record_for_date_false_on_read_error(monkeypatch):
    def fail_get_json(*args, **kwargs):
        raise RuntimeError("HTTP 403 Forbidden")

    monkeypatch.setattr("career_os.airtable_client.get_json", fail_get_json)
    client = AirtableClient(_settings())
    assert client.has_record_for_date("Daily Tasks", "2026-05-08") is False

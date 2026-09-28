from app.ingestion.sanitize import sanitize_text_for_postgres


def test_sanitize_text_for_postgres_strips_nul():
    assert sanitize_text_for_postgres("hello\x00world") == "helloworld"
    assert sanitize_text_for_postgres("ok") == "ok"

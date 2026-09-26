from app.db.url import (
    database_url_with_ssl_query,
    normalize_database_url,
    sqlalchemy_connect_args,
)


def test_normalize_database_url_postgres_scheme():
    assert (
        normalize_database_url("postgres://u:p@host/db")
        == "postgresql://u:p@host/db"
    )


def test_normalize_database_url_strips_quotes():
    assert (
        normalize_database_url('"postgresql://u:p@host/db"')
        == "postgresql://u:p@host/db"
    )


def test_sqlalchemy_connect_args_supabase_host():
    url = "postgresql://u:p@db.abc.supabase.co:5432/postgres"
    assert sqlalchemy_connect_args(url) == {"sslmode": "require"}


def test_sqlalchemy_connect_args_local_empty():
    assert sqlalchemy_connect_args("postgresql://u:p@localhost:5432/db") == {}


def test_database_url_with_ssl_query_adds_sslmode():
    url = "postgresql://u:p@db.abc.supabase.co:5432/postgres"
    out = database_url_with_ssl_query(url)
    assert "sslmode=require" in out

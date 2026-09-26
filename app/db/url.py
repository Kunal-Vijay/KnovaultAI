from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def normalize_database_url(url: str) -> str:
    """Normalize postgres:// to postgresql:// for SQLAlchemy."""
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


def sqlalchemy_connect_args(database_url: str) -> dict:
    """Return psycopg2 connect_args; enforce SSL for Supabase hosts."""
    parsed = urlparse(database_url)
    host = (parsed.hostname or "").lower()
    if "supabase.co" not in host:
        return {}

    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if query.get("sslmode"):
        return {}

    query["sslmode"] = "require"
    return {"sslmode": "require"}


def database_url_with_ssl_query(database_url: str) -> str:
    """Ensure sslmode=require in URL for Supabase when missing (Alembic uses URL string)."""
    url = normalize_database_url(database_url)
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if "supabase.co" not in host:
        return url

    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if query.get("sslmode"):
        return url

    query["sslmode"] = "require"
    return urlunparse(parsed._replace(query=urlencode(query)))

import socket
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def _ipv4_hostaddr(hostname: str) -> str | None:
    """Resolve an IPv4 address for hosts where only AAAA is reachable (e.g. Render → Supabase)."""
    try:
        infos = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)
    except OSError:
        return None
    if not infos:
        return None
    return infos[0][4][0]


def normalize_database_url(url: str) -> str:
    """Normalize postgres:// to postgresql:// for SQLAlchemy."""
    url = url.strip().strip('"').strip("'")
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


def sqlalchemy_connect_args(database_url: str) -> dict:
    """Return psycopg2 connect_args; enforce SSL for Supabase hosts."""
    parsed = urlparse(database_url)
    host = (parsed.hostname or "").lower()
    if "supabase.co" not in host:
        return {}

    args: dict = {"sslmode": "require"}

    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if query.get("sslmode"):
        args["sslmode"] = query["sslmode"]

    # Direct db.<ref>.supabase.co often resolves to IPv6; many PaaS networks have no IPv6 egress.
    if host.startswith("db.") and host.endswith(".supabase.co"):
        hostaddr = _ipv4_hostaddr(host)
        if hostaddr:
            args["hostaddr"] = hostaddr

    return args


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

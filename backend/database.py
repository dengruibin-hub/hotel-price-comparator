import os
from contextlib import contextmanager

try:
    import psycopg
except ImportError:  # Database support is optional for the MVP.
    psycopg = None


DATABASE_URL = os.getenv("DATABASE_URL", "")


@contextmanager
def get_connection():
    """Yield a PostgreSQL connection when DATABASE_URL is configured."""
    if psycopg is None:
        raise RuntimeError("psycopg is not installed")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    with psycopg.connect(DATABASE_URL) as connection:
        yield connection

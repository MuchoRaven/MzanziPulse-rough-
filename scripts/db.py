"""
Central database connection module.
Returns a psycopg2 connection to Supabase PostgreSQL.
All Flask API files and helper classes import from here.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')


def get_db():
    """Return a Supabase PostgreSQL connection with dict-style row access."""
    if not SUPABASE_DB_URL:
        raise RuntimeError("SUPABASE_DB_URL is not set in your .env file")
    conn = psycopg2.connect(SUPABASE_DB_URL, cursor_factory=RealDictCursor)
    conn.autocommit = False
    return conn


def get_db_path():
    """Legacy helper — returns a human-readable label for logging."""
    return "Supabase PostgreSQL"

"""
Migrate MzansiPulse Data from SQLite to Supabase PostgreSQL
============================================================
Migrates in dependency order:
  1. users
  2. businesses       (FK -> users)
  3. cash_wallets     (FK -> businesses)
  4. cash_transactions (FK -> cash_wallets)

Usage:
    pip install psycopg2-binary python-dotenv
    python scripts/migrate_to_supabase.py
"""

import sqlite3
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Force UTF-8 output so emojis print correctly on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

SQLITE_DB       = os.path.join(os.path.dirname(__file__), '..', 'database', 'mzansipulse.db')
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

# Tables in strict dependency order (parents before children)
TABLES = [
    'users',
    'businesses',
    'cash_wallets',
    'cash_transactions',
]

# Primary key column per table (used to reset Postgres SERIAL sequences)
PRIMARY_KEYS = {
    'users':             'user_id',
    'businesses':        'business_id',
    'cash_wallets':      'wallet_id',
    'cash_transactions': 'cash_transaction_id',
}

SEP  = "=" * 58
SEP2 = "-" * 58


# -----------------------------------------------------------------------------
# VALIDATION
# -----------------------------------------------------------------------------

def validate_config():
    errors = []
    if not SUPABASE_DB_URL:
        errors.append(
            "  [FAIL] SUPABASE_DB_URL not found in .env\n"
            "         Add: SUPABASE_DB_URL=postgresql://user:pass@host:port/dbname"
        )
    sqlite_path = os.path.abspath(SQLITE_DB)
    if not os.path.exists(sqlite_path):
        errors.append(
            f"  [FAIL] SQLite database not found at:\n"
            f"         {sqlite_path}"
        )
    if errors:
        print("\n".join(errors))
        sys.exit(1)


# -----------------------------------------------------------------------------
# CONNECTIONS
# -----------------------------------------------------------------------------

def connect_sqlite():
    sqlite_path = os.path.abspath(SQLITE_DB)
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn


def connect_postgres():
    conn = psycopg2.connect(SUPABASE_DB_URL, cursor_factory=RealDictCursor)
    conn.autocommit = False
    return conn


# -----------------------------------------------------------------------------
# SCHEMA HELPERS
# -----------------------------------------------------------------------------

def sqlite_to_pg_type(sqlite_type: str) -> str:
    """Map SQLite column type to a compatible PostgreSQL type."""
    mapping = {
        'INTEGER': 'INTEGER',
        'TEXT':    'TEXT',
        'REAL':    'DOUBLE PRECISION',
        'BLOB':    'BYTEA',
        'NUMERIC': 'NUMERIC',
    }
    return mapping.get(sqlite_type.upper().strip(), 'TEXT')


def get_sqlite_column_info(sqlite_conn, table: str) -> list:
    """Return list of (name, type) tuples for all columns in a SQLite table."""
    cur = sqlite_conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return [(row['name'], row['type']) for row in cur.fetchall()]


def get_sqlite_columns(sqlite_conn, table: str) -> list:
    return [name for name, _ in get_sqlite_column_info(sqlite_conn, table)]


def get_pg_columns(pg_conn, table: str) -> set:
    """Return set of column names that already exist in the Postgres table."""
    cur = pg_conn.cursor()
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = %s",
        (table,)
    )
    return {row['column_name'] for row in cur.fetchall()}


def sync_schema(sqlite_conn, pg_conn, table: str):
    """
    Add any columns that exist in SQLite but are missing from the Postgres table.
    This is non-destructive — it only adds, never drops or modifies columns.
    """
    sqlite_cols = get_sqlite_column_info(sqlite_conn, table)
    pg_cols     = get_pg_columns(pg_conn, table)

    missing = [(name, dtype) for name, dtype in sqlite_cols if name not in pg_cols]

    if not missing:
        print(f"     Schema OK — no missing columns")
        return

    print(f"     Adding {len(missing)} missing column(s) to Postgres:")
    pg_cur = pg_conn.cursor()

    for col_name, sqlite_type in missing:
        pg_type = sqlite_to_pg_type(sqlite_type)
        print(f"       + {col_name}  ({sqlite_type} -> {pg_type})")
        pg_cur.execute(
            f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "{col_name}" {pg_type}'
        )

    pg_conn.commit()
    print(f"     Schema sync complete")


# -----------------------------------------------------------------------------
# MIGRATION CORE
# -----------------------------------------------------------------------------

def migrate_table(sqlite_conn, pg_conn, table: str) -> int:
    """
    Copy every row from `table` in SQLite into the matching Postgres table.

    - Syncs schema first (adds any missing columns).
    - Preserves original primary key values (OVERRIDING SYSTEM VALUE).
    - Skips duplicate rows (ON CONFLICT DO NOTHING) so the script is safe
      to run more than once.
    - Resets the Postgres SERIAL sequence after insert so future INSERTs
      won't collide.
    - Returns the number of rows successfully inserted.
    """
    print(f"\n[>>] Migrating table: {table}")

    # Step 1: sync schema before touching data
    sync_schema(sqlite_conn, pg_conn, table)

    columns = get_sqlite_columns(sqlite_conn, table)
    print(f"     Columns ({len(columns)}): {', '.join(columns)}")

    # Fetch all rows from SQLite
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute(f"SELECT * FROM {table}")
    rows = sqlite_cur.fetchall()

    if not rows:
        print(f"     [WARN] No rows found in SQLite '{table}' -- skipping")
        return 0

    # Build Postgres INSERT statement
    col_list     = ', '.join(f'"{c}"' for c in columns)
    placeholders = ', '.join(['%s'] * len(columns))
    pk_col       = PRIMARY_KEYS.get(table)

    insert_sql = (
        f'INSERT INTO "{table}" ({col_list})\n'
        f'OVERRIDING SYSTEM VALUE\n'
        f'VALUES ({placeholders})\n'
        f'ON CONFLICT ("{pk_col}") DO NOTHING'
    )

    pg_cur   = pg_conn.cursor()
    inserted = 0
    failed   = 0

    for row in rows:
        values = [row[col] for col in columns]
        try:
            pg_cur.execute(insert_sql, values)
            inserted += 1
        except Exception as row_err:
            failed += 1
            pk_val = row[pk_col] if pk_col else '?'
            print(f"     [WARN] Row {pk_col}={pk_val} failed: {row_err}")
            pg_conn.rollback()
            pg_cur = pg_conn.cursor()

    # Commit this table
    try:
        pg_conn.commit()
    except Exception as commit_err:
        print(f"     [FAIL] Commit failed for '{table}': {commit_err}")
        pg_conn.rollback()
        return 0

    # Reset SERIAL sequence so future inserts don't collide with migrated IDs
    if pk_col:
        try:
            pg_cur.execute(
                f"SELECT setval(pg_get_serial_sequence('\"{table}\"', '{pk_col}'), "
                f"COALESCE((SELECT MAX(\"{pk_col}\") FROM \"{table}\"), 1), true)"
            )
            pg_conn.commit()
        except Exception as seq_err:
            print(f"     [WARN] Sequence reset skipped for '{table}.{pk_col}': {seq_err}")
            pg_conn.rollback()

    if failed:
        print(f"     [OK] Migrated {inserted} rows  ({failed} rows skipped)")
    else:
        print(f"     [OK] Migrated {inserted} rows")

    return inserted


# -----------------------------------------------------------------------------
# VERIFICATION
# -----------------------------------------------------------------------------

def verify_migration(sqlite_conn, pg_conn):
    """Compare row counts between SQLite and Postgres for each table."""
    print("\n" + SEP)
    print("  VERIFICATION -- Row Count Comparison")
    print(SEP)
    print(f"  {'Table':<25} {'SQLite':>8} {'Postgres':>10}  Match")
    print("  " + SEP2)

    all_match  = True
    sqlite_cur = sqlite_conn.cursor()
    pg_cur     = pg_conn.cursor()

    for table in TABLES:
        try:
            sqlite_cur.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cur.fetchone()[0]
        except Exception:
            sqlite_count = "ERR"

        try:
            pg_cur.execute(f'SELECT COUNT(*) FROM "{table}"')
            pg_count = pg_cur.fetchone()['count']
        except Exception:
            pg_count = "ERR"

        match = sqlite_count == pg_count
        if not match:
            all_match = False
        icon = "[OK]" if match else "[!!]"
        print(f"  {table:<25} {str(sqlite_count):>8} {str(pg_count):>10}  {icon}")

    print(SEP)
    return all_match


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main():
    print("\n" + SEP)
    print("  MZANSIPULSE DATA MIGRATION")
    print("  SQLite  ->  Supabase PostgreSQL")
    print(SEP)

    validate_config()

    print("\n[..] Connecting to databases...")

    try:
        sqlite_conn = connect_sqlite()
        print(f"     [OK] Connected to SQLite  ({os.path.abspath(SQLITE_DB)})")
    except Exception as e:
        print(f"     [FAIL] SQLite connection failed: {e}")
        sys.exit(1)

    try:
        pg_conn = connect_postgres()
        print("     [OK] Connected to Supabase PostgreSQL")
    except Exception as e:
        print(f"     [FAIL] Supabase connection failed: {e}")
        print("            Check SUPABASE_DB_URL in your .env file")
        sqlite_conn.close()
        sys.exit(1)

    print("\n" + SEP2)
    print("  Starting migration...")
    print(SEP2)

    total_migrated = 0

    for table in TABLES:
        try:
            count = migrate_table(sqlite_conn, pg_conn, table)
            total_migrated += count
        except Exception as table_err:
            print(f"\n     [FAIL] Fatal error migrating '{table}': {table_err}")
            print("            Rolling back and aborting.")
            pg_conn.rollback()
            sqlite_conn.close()
            pg_conn.close()
            sys.exit(1)

    all_match = verify_migration(sqlite_conn, pg_conn)

    print(f"\n  Total records migrated: {total_migrated}")
    if all_match:
        print("  [OK] All row counts match -- migration successful!\n")
    else:
        print("  [!!] Some counts differ -- check warnings above.\n")

    sqlite_conn.close()
    pg_conn.close()


if __name__ == '__main__':
    main()

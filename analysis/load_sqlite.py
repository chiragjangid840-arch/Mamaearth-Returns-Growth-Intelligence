import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCHEMA_FILE = ROOT / "sql" / "schema.sql"
DB_FILE = ROOT / "mamaearth_returns.db"

def load_csv_to_sqlite():
    tables = {
        "customers": pd.read_csv(DATA / "customers.csv"),
        "products": pd.read_csv(DATA / "products.csv"),
        "orders": pd.read_csv(DATA / "orders.csv"),
    }

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        # Recreate tables from the project's schema
        conn.executescript("""
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;
        """)

        conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))

        # Insert CSV rows into schema-defined tables
        for table, df in tables.items():
            df = df.astype(object).where(pd.notna(df), None)
            columns = list(df.columns)
            column_sql = ", ".join(f'"{c}"' for c in columns)
            placeholders = ", ".join("?" for _ in columns)
            sql = f'INSERT INTO "{table}" ({column_sql}) VALUES ({placeholders})'
            conn.executemany(sql, df.itertuples(index=False, name=None))

        print("SQLite database created:", DB_FILE.name)

        for table in tables:
            count = conn.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]
            print(f"{table}: {count} rows")

        print("Orders foreign keys:",
              conn.execute("PRAGMA foreign_key_list(orders)").fetchall())

if __name__ == "__main__":
    load_csv_to_sqlite()

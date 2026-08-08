#!/usr/bin/env python3
"""Simple DB inspection helper for the development container.

Usage (from project root):
    docker compose exec backend python /app/backend/inspect_db.py
"""
import os
import sqlite3
import sys


def main():
    db_path = "/app/data/fitwise.db"
    print("Inspecting DB at:", db_path)
    if not os.path.exists(db_path):
        print("Database file not found:", db_path)
        sys.exit(2)

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables:", tables)

    for name in tables:
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{name}"')
            count = cur.fetchone()[0]
        except Exception as e:
            count = f"ERROR: {e}"
        print(f"{name}: {count}")

    con.close()


if __name__ == "__main__":
    main()

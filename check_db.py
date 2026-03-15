"""
check_db.py  —  quick inspection of data_pilot/scheduler.db
Run from project root:  python check_db.py
"""
import sys, sqlite3
sys.path.insert(0, '.')
from db import database

database.init_db()
conn = sqlite3.connect(database.DB_PATH)
conn.row_factory = sqlite3.Row

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
).fetchall()

print(f"\n{'='*60}")
print(f"  DB: {database.DB_PATH}")
print(f"  Tables: {[t['name'] for t in tables]}")
print(f"{'='*60}")

for table in tables:
    name = table['name']
    rows = conn.execute(f"SELECT * FROM {name}").fetchall()
    print(f"\n--- {name} [{len(rows)} rows] ---")
    if rows:
        cols = rows[0].keys()
        col_widths = {c: max(len(c), max(len(str(r[c])) for r in rows)) for c in cols}
        header = "  ".join(c.ljust(col_widths[c]) for c in cols)
        divider = "  ".join("-" * col_widths[c] for c in cols)
        print(header)
        print(divider)
        for row in rows:
            print("  ".join(str(row[c]).ljust(col_widths[c]) for c in cols))
    else:
        print("  (empty)")

print(f"\n{'='*60}\n")
conn.close()

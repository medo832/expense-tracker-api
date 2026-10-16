"""
Print everything stored in expenses.db.

Run it any time - the server does not need to be running.
"""

import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), "expenses.db")

if not os.path.exists(DB):
    print("No expenses.db here yet. Run initdb.bat first.")
    raise SystemExit(0)

con = sqlite3.connect(DB)

print("tables:", [r[0] for r in con.execute(
    "select name from sqlite_master where type='table'")])
print()

rows = list(con.execute(
    "select id, product_name, quantity, unit, category,"
    " price_paid, currency_paid, created_at from expenses"))

print(f"{len(rows)} row(s) in 'expenses'")
print("-" * 78)
for r in rows:
    print(f"{r[0]}  {r[1]:<14} {r[2]:>6} {r[3]:<6} {r[4]:<12} "
          f"{r[5]:>8} {r[6]}  {r[7]}")

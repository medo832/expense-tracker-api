"""
Quick test for the API - no Swagger UI needed.

How to run:
    1. start the server in one window   ->  run.bat
    2. double-click                     ->  test.bat
"""

import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"


def call(method, path, body=None):
    """Send one request and return (status_code, parsed_body)."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read().decode("utf-8")
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        return e.code, (json.loads(raw) if raw else None)
    except urllib.error.URLError:
        print("Cannot reach the server. Is run.bat running?")
        raise SystemExit(1)


def show(title, status, body):
    print()
    print("-" * 60)
    print(title)
    print("status:", status)
    print(json.dumps(body, indent=2, ensure_ascii=False))


GOOD = {
    "product_name": "Bananas",
    "quantity": 3,
    "unit": "kg",
    "category": "Groceries",
    "price_paid": 45,
    "currency_paid": "EGP",
}

BAD = dict(GOOD, quantity="hello")   # quantity is not a number


s, b = call("GET", "/health")
show("GET /health", s, b)

s, b = call("POST", "/expenses", GOOD)
show("POST /expenses  (first time)", s, b)
first_id = b["id"] if s == 201 else None

s, b = call("POST", "/expenses", GOOD)
show("POST /expenses  (same data again)", s, b)

s, b = call("POST", "/expenses", BAD)
show("POST /expenses  (quantity is text -> should be 422)", s, b)

s, b = call("GET", "/expenses")
show("GET /expenses", s, b)
print()
print("stored:", len(b), "expenses")
print("ids:   ", [e["id"] for e in b])

# --- uncomment when you add DELETE ---
# s, b = call("DELETE", f"/expenses/{first_id}")
# show(f"DELETE /expenses/{first_id}", s, b)
# s, b = call("DELETE", "/expenses/does-not-exist")
# show("DELETE /expenses/does-not-exist  (should be 404)", s, b)

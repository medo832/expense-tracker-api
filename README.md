# Expense Tracker API

A personal expense tracker built backend-first: a FastAPI service with SQLite
storage, designed to be driven later by a phone front-end and an AI receipt
reader.

Built as a learning project — the design document and the API contract were
written and reviewed **before** the first line of server code.

---

## What it does today

- Records an expense and gives it a server-generated `id` and timestamp
- Stores it in SQLite — data survives a restart
- Lists and deletes expenses
- Validates every request automatically (Pydantic) and returns a precise error
  pointing at the bad field

## Endpoints

| Method | Path | Purpose | Code |
|---|---|---|---|
| `GET` | `/health` | Service is alive | 200 |
| `GET` | `/settings` | Base currency | 200 |
| `POST` | `/expenses` | Create an expense | 201 |
| `GET` | `/expenses` | List expenses | 200 |
| `DELETE` | `/expenses/{id}` | Delete one expense | 204 / 404 |

Interactive docs are generated from the code at `/docs`.

### Example

```
POST /expenses
{
  "product_name": "Bananas",
  "quantity": 3,
  "unit": "kg",
  "category": "Groceries",
  "price_paid": 45,
  "currency_paid": "EGP"
}

201 Created
{
  "id": "7fc43d86",
  "product_name": "Bananas",
  "quantity": 3.0,
  "unit": "kg",
  "category": "Groceries",
  "price_paid": 45.0,
  "currency_paid": "EGP",
  "created_at": "2026-10-16T19:26:26.394200+03:00"
}
```

The client sends what happened. The server adds what follows from it —
`id`, `created_at`, and (next) the currency conversion.

---

## Design decisions

How it works today, end to end: [`ARCHITECTURE.md`](ARCHITECTURE.md).
Full reasoning in [`design.md`](design.md) and [`api-spec.md`](api-spec.md).
The short version:

**Currency is converted at the moment of purchase, not at display time.**
An expense is a past event, so its value must not move. Converting with
today's rate would make last month's total change every day, and the
"how much more than last month" number would measure the exchange rate
instead of the spending.

**User verification of the AI result is not an endpoint.**
The model's output is held on the front-end and corrected there. The server
is called once, when the final expense is saved — so nothing half-ready is
ever stored.

**Receipt images will be kept, for evaluation.**
An evaluation record needs three things together: the image, the raw model
output, and the user's correction. Storing only the correction makes
measuring the model impossible.

**The storage layer knows nothing about HTTP.**
`storage.py` returns `True`/`False`; `main.py` decides what a 404 is.
Swapping SQLite for Postgres touches one file.

---

## Running it

Requires Python 3.11+.

```bash
cd api
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows
.venv/Scripts/python storage.py                           # create the table
.venv/Scripts/python -m uvicorn main:app --reload
```

Then open <http://127.0.0.1:8000/docs>.

On Windows you can also just double-click `setup.bat`, then `run.bat`.
`test.bat` runs the API through its paces; `showdb.bat` prints what is
actually in the database.

## Layout

```
api/
  main.py       HTTP layer - endpoints, status codes, validation
  storage.py    data layer  - engine, table, queries
  expenses.db   SQLite file (not tracked)
design.md       the design document
api-spec.md     the API contract
ARCHITECTURE.md how a request flows through the system
```

## Roadmap

- [ ] `GET /expenses?month=` and `PATCH /expenses/{id}`
- [ ] Currency conversion with a stored rate
- [ ] `POST /expenses/scan` — receipt image to structured expense
- [ ] Monthly and daily summaries
- [ ] Web front-end (PWA)
- [ ] Deploy with Postgres

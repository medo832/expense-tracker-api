# How the system works

A walkthrough of what actually happens inside the service today.
Written so that anyone — including future me — can open the repo and
understand it without reading every line of code.

---

## The shape

```
        HTTP request
             |
             v
   +---------------------+
   |      main.py        |   endpoints, status codes, validation
   |    (HTTP layer)     |   knows nothing about SQL
   +---------------------+
             |  plain python dicts and objects
             v
   +---------------------+
   |     storage.py      |   engine, table, queries
   |    (data layer)     |   knows nothing about HTTP
   +---------------------+
             |
             v
       expenses.db  (SQLite file)
```

One rule holds the design together:

**`storage.py` never raises an HTTP error, and `main.py` never writes SQL.**

`storage.delete_expense()` returns `True` or `False`. Turning `False` into
a `404` is a decision about the web, so it lives in `main.py`. That is why
swapping SQLite for Postgres later touches exactly one file.

---

## Two kinds of models, on purpose

This is the part that confuses people most, so it is worth being explicit.

| Class | Library | Describes | Lives in |
|---|---|---|---|
| `ExpenseIN` | Pydantic | what the client is allowed to send | `main.py` |
| `Expense` | Pydantic | what the API gives back | `main.py` |
| `ExpenseRow` | SQLAlchemy | a row in the `expenses` table | `storage.py` |

They look similar today. They are kept separate because they answer
different questions, and they will drift apart: the database will hold
columns the API never exposes, and the API will expose values the database
never stores.

`Expense` inherits from `ExpenseIN` and adds the two fields the **server**
produces:

```python
class Expense(ExpenseIN):
    id: str
    created_at: str
    model_config = {"from_attributes": True}
```

`from_attributes` lets Pydantic read a SQLAlchemy object, which is what
makes `response_model=list[Expense]` work on `GET /expenses`.

---

## What happens on `POST /expenses`

```
1.  Request arrives with a JSON body.

2.  FastAPI parses it into ExpenseIN.
    A wrong type stops here: 422, with the exact field named.
    Nothing reaches the database.

3.  main.py builds an Expense:
        id          = uuid4().hex[:8]
        created_at  = now, ISO 8601, with the timezone offset
    The client never sends either one.

4.  storage.save_expense(expense.model_dump())
        - open a Session
        - build an ExpenseRow from the dict
        - session.add(...)      -> "I intend to insert this"
        - session.commit()      -> actually written to disk

5.  201 Created, with the saved expense as the body.
```

The dict in step 4 is the border between the two layers. `main.py` speaks
Pydantic, `storage.py` speaks SQLAlchemy, and a plain dict is the only thing
they share.

## What happens on `DELETE /expenses/{id}`

```
1.  storage.delete_expense(id)
        row = session.get(ExpenseRow, id)
```

`session.get` looks the row up by primary key — no loop, no scan. The
database has an index on `id`, which is the practical payoff of making it
the primary key.

```
2.  row is None   ->  return False  ->  main.py raises 404
    row found     ->  session.delete(row), commit, return True  ->  204
```

`204` means "done, and there is no body to send". The status code *is* the
message.

---

## The database

One table. It is created at startup by `storage.init_db()` if it does not
already exist.

```sql
CREATE TABLE expenses (
    id            VARCHAR NOT NULL,
    product_name  VARCHAR NOT NULL,
    quantity      FLOAT   NOT NULL,
    unit          VARCHAR NOT NULL,
    category      VARCHAR NOT NULL,
    price_paid    FLOAT   NOT NULL,
    currency_paid VARCHAR NOT NULL,
    created_at    VARCHAR NOT NULL,
    PRIMARY KEY (id)
)
```

Nobody wrote that SQL. SQLAlchemy generated it from the `ExpenseRow` class,
including every `NOT NULL` — those come from the type hints being
`Mapped[str]` rather than `Mapped[str | None]`.

**A known limit:** `create_all()` creates missing tables but never alters an
existing one. The moment a column is added to `ExpenseRow`, the live table
will not change. That is the job of a migration tool (Alembic), and it is
the next piece of infrastructure this project needs.

---

## Validation comes free

```json
POST /expenses   {"quantity": "three", ...}

422 Unprocessable Content
{
  "detail": [{
    "loc": ["body", "quantity"],
    "msg": "Input should be a valid number",
    "type": "float_parsing"
  }]
}
```

No hand-written checks produce this. It falls out of declaring
`quantity: float` on the model. `loc` tells a front-end exactly which input
to mark red.

---

## What is not built yet

| Missing | Why it matters |
|---|---|
| `PATCH /expenses/{id}` | editing a saved expense |
| `?month=` filter | the list is unbounded today |
| Currency conversion | `price_paid` is stored raw; the base-currency value and the rate used are not stored yet |
| `POST /expenses/scan` | receipt image to structured expense |
| `scans` table | image + raw model output + user correction — the three parts an evaluation record needs |
| Summaries | monthly totals, change vs last month, top category |
| Migrations | see the `create_all` limit above |
| Auth | there is exactly one user today, and the server assumes it |

The reasoning behind the first two and the currency design is in
[`design.md`](design.md); the full endpoint contract is in
[`api-spec.md`](api-spec.md).

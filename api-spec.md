# Expense Tracker — API Spec v1

> The contract the server code and the front-end code are both written against.
> The user is identified by their login, so no `/users/{id}` appears in any path.

---

## 1. Endpoints

| Method | Path | Purpose | Input | Output | Success |
|---|---|---|---|---|---|
| `GET` | `/health` | Check the service is alive | — | `{"status": "ok"}` | 200 |
| `POST` | `/expenses/scan` | Extract expense data from a receipt image | Body: `multipart` (image file) | Extracted data + `scan_id` | 200 |
| `POST` | `/expenses` | Save an expense after the user confirms it | Body: expense data (+ optional `scan_id`) | The saved expense | 201 |
| `GET` | `/expenses` | List the expenses of one month | Query: `month=YYYY-MM` | Array of expenses | 200 |
| `GET` | `/expenses/{id}` | Get one expense with its details | Path: `id` | One expense | 200 |
| `PATCH` | `/expenses/{id}` | Edit an expense, or hide it | Path: `id` · Body: changed fields only | The updated expense | 200 |
| `DELETE` | `/expenses/{id}` | Delete permanently | Path: `id` | — | 204 |
| `GET` | `/summary/monthly` | Month totals: total, % change, top category | Query: `month=YYYY-MM` | Numbers | 200 |
| `GET` | `/summary/daily` | Day totals (the source of the daily message) | Query: `date=YYYY-MM-DD` | Numbers | 200 |
| `GET` | `/settings` | Read settings (base currency) | — | Settings | 200 |
| `PATCH` | `/settings` | Change the base currency | Body: `{"base_currency": "EGP"}` | Updated settings | 200 |

**Deferred to v2:** `GET /scans` — pull the evaluation data (image + raw model
output + user correction) when measuring model accuracy.

---

## 2. Why the resources are shaped this way

| Decision | Reason |
|---|---|
| `/summary/daily` rather than `/daily-message` | The server sends **numbers**; the client turns them into a message. A resource name describes the data, not the way it is displayed |
| Monthly analysis lives under `/summary/*`, not `/expenses` | `/expenses` returns **stored rows**. A summary returns **values that are computed and exist nowhere in the database**. Two different resources |
| `/summary/monthly` and `/summary/daily` are separate paths | One path with a different filter would force the server to inspect which filter arrived — complexity with no benefit |
| `GET /expenses/{id}` exists | The expense detail screen needs it |
| `GET /settings` exists | The app must know the base currency the moment it opens |
| `PATCH /settings`, not `/settings/currency` | A second setting (language, notifications) should not need a new path |
| `GET /health` exists | The first endpoint to deploy. Its presence on the public internet is the proof the service is running |
| `POST /expenses/scan` returns a `scan_id` | It is what links the model's answer to the user's correction — the core of the evaluation system |

**User verification of the AI result is not an endpoint.** The model's output
is held on the front-end and corrected there, because that needs neither to
read nor to change server data. The server is called once, when the final
expense is submitted to `POST /expenses` — so nothing half-ready is ever
stored.

---

## 3. Data shapes

### `POST /expenses/scan`

```
request:  multipart/form-data  ->  file: receipt.jpg

response: 200
{
  "scan_id": "scn_9c21af",
  "model": "gpt-4o-mini-2026-05",
  "extracted": {
    "product_name": "Bananas",
    "quantity": 3,
    "unit": "kg",
    "price_paid": 45.0,
    "currency_paid": "EGP",
    "category": "Groceries",
    "purchased_at": "2026-09-15T19:42:00+03:00"
  },
  "missing_fields": ["quantity"]
}
```

`missing_fields` tells the front-end where to put the cursor — the fields the
model could not read.

### `POST /expenses`

```
request:
{
  "scan_id": "scn_9c21af",          // optional - absent for manual entry
  "product_name": "Bananas",
  "quantity": 3,
  "unit": "kg",
  "price_paid": 45.0,
  "currency_paid": "EGP",
  "category": "Groceries",
  "purchased_at": "2026-09-15T19:42:00+03:00"
}

response: 201
{
  "id": "exp_4b7e12",
  "product_name": "Bananas",
  "quantity": 3,
  "unit": "kg",
  "price_paid": 45.0,
  "currency_paid": "EGP",
  "base_currency": "EGP",
  "price_in_base": 45.0,
  "exchange_rate": 1.0,
  "category": "Groceries",
  "purchased_at": "2026-09-15T19:42:00+03:00",
  "hidden": false,
  "created_at": "2026-09-15T19:42:06+03:00"
}
```

**Note:** the client sent `price_paid` and `currency_paid` only. The server
added `id`, `base_currency`, `price_in_base`, `exchange_rate` and
`created_at` — all of them either derived values or server decisions.

### `GET /summary/monthly?month=2026-09`

```
{
  "month": "2026-09",
  "base_currency": "EGP",
  "total": 4820.5,
  "previous_total": 4100.0,
  "change_percent": 17.6,
  "top_category": {"name": "Groceries", "total": 2100.0},
  "by_category": [
    {"name": "Groceries", "total": 2100.0},
    {"name": "Transport", "total": 980.5}
  ]
}
```

Numbers only. No charts, no sentences — drawing and wording are the
front-end's job.

---

## 4. The `scans` table (for evaluation)

Separate from `expenses`:

```
scan_id · image_ref · raw_model_output (JSON) · model_name · model_version · created_at
```

`expenses.scan_id` links the two. The difference between `raw_model_output`
and the saved expense is **a labelled correction, produced automatically**.

The image goes to object storage (R2 / Supabase Storage), not into the
database, resized to 1024px wide.

---

## 5. Failure cases — the minimum for v1

| Case | Response |
|---|---|
| Missing field, or wrong type, in the body | `400` + the name of the offending field |
| `id` not found | `404` |
| The model cannot read the receipt | `200` with an empty `extracted` and a filled `missing_fields` — **not an error**; this is the manual-entry path |
| The exchange-rate API is down | Store the expense in its original currency with `exchange_rate: null`, and convert later |

The last row is a deliberate decision: **a failing external service must never
stop the user from recording an expense.**

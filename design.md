# Expense Tracker — Design

Version 1. Written before any code.
Language note: this file is in simple English on purpose, so the same words are used in the code.

---

## 1. Scope

**Who uses it:** any person who wants to follow their own spending and know if they are saving or overspending.

**Problem it solves:** people spend a lot and cannot follow where the money goes, so they cannot build a plan from it.

**It will NOT do:**
- companies (it is for individuals only)
- financial planning

The app is a tracker. It shows results and analysis. It does not make decisions for the user.

---

## 2. Main flow

1. The user takes a photo of the receipt.
2. The AI reads the photo and returns the expense fields.
3. The user checks the result on the screen and fixes anything wrong.
4. The user types the quantity if the AI could not read it.
5. The app saves the expense.

If there is no receipt (market, street seller), the user types everything by hand. This is a normal path, not a fallback for errors.

---

## 3. Expense fields

| Field | Type | Who fills it | Required |
|---|---|---|---|
| `id` | string | system, one per expense | yes |
| `product_name` | string | AI from OCR, user confirms | yes |
| `quantity` | float | AI if the receipt shows it, else user | yes |
| `unit` | string | user | yes |
| `price_paid` | float | AI from OCR, user confirms | yes |
| `currency_paid` | string | AI or user | yes |
| `base_currency` | string | from settings | yes |
| `price_in_base` | float | server (after conversion) | yes |
| `exchange_rate` | float | server (rate API) | yes |
| `category` | string | AI, from the product name | yes |
| `purchased_at` | ISO 8601 | system | yes |
| `hidden` | bool | system, when the user asks | yes (default `false`) |

Rule: the client sends what happened (`price_paid`, `currency_paid`). The server computes what follows from it (`price_in_base`, `exchange_rate`, `id`, `created_at`).

---

## 4. Decisions and why

### 4.1 Currency

The user picks a **base currency** the first time the app opens. He can change it later if he travels.

If he pays in another currency, the app converts **at the moment of purchase**, not at the moment of viewing. It stores the amount paid, the currency paid, the base currency, and the rate used that day.

**Why:** an expense is a past event. Past events must not change. If we converted with today's rate, last month's total would change every day, and the "how much more than last month" number would measure the exchange rate instead of the spending.

If base currency = currency paid, `price_in_base` equals `price_paid` and `exchange_rate` is `1.0`. Every record has the same shape, so no calculation needs an `if`.

The exchange rate comes from a normal API, not from the AI. The AI is for unclear input (an image, free text). An API is for values that have one correct answer.

### 4.2 Time

One field, ISO 8601, with the time zone offset. Example: `2026-09-15T19:42:00+03:00`.

**Why:** a display string like `"11:05 pm"` cannot be sorted or filtered. The offset matters because the user may buy something while travelling.

### 4.3 Categories

The AI reads the category from the product name. A fixed list is better than free text, because "Food", "food" and "أكل" would break the monthly report.

### 4.4 Delete and hide

Delete is permanent, after the user confirms.
Hide keeps the record but takes it out of the normal view.

### 4.5 Receipt images

Images **are stored**, for model evaluation.

An evaluation record needs three things together:
1. the input (the receipt image)
2. the raw model answer
3. the corrected answer (what the user saved)

So `POST /expenses/scan` saves a scan record and returns a `scan_id`. `POST /expenses` sends that `scan_id` back. The difference between the raw model answer and the saved expense is a labelled correction, produced automatically.

Scan record: `scan_id · image_ref · raw_model_output · model_name · model_version · created_at`

Images go to object storage (R2 / Supabase Storage), not into the database, resized to 1024px wide.

---

## 5. Endpoints

| Method | Path | Purpose | Input | Output | Code |
|---|---|---|---|---|---|
| `GET` | `/health` | Check the server is alive | — | `{"status": "ok"}` | 200 |
| `POST` | `/expenses/scan` | Extract expense data from a receipt image | Body: multipart image | Extracted data + `scan_id` | 200 |
| `POST` | `/expenses` | Save an expense after the user confirms it | Body: expense data (+ `scan_id`) | The saved expense | 201 |
| `GET` | `/expenses` | List the expenses of one month | Query: `month=YYYY-MM` | Array of expenses | 200 |
| `GET` | `/expenses/{id}` | Get one expense | Path: `id` | One expense | 200 |
| `PATCH` | `/expenses/{id}` | Edit an expense or hide it | Path: `id` + Body: changed fields | Updated expense | 200 |
| `DELETE` | `/expenses/{id}` | Delete permanently | Path: `id` | — | 204 |
| `GET` | `/summary/monthly` | Month total, change %, top category | Query: `month=YYYY-MM` | Numbers | 200 |
| `GET` | `/summary/daily` | Day numbers for the daily message | Query: `date=YYYY-MM-DD` | Numbers | 200 |
| `GET` | `/settings` | Read settings (base currency) | — | Settings | 200 |
| `PATCH` | `/settings` | Change the base currency | Body: `{"base_currency": "EGP"}` | Updated settings | 200 |

Later (v2): `GET /scans` — pull the evaluation data when measuring model accuracy.

**User verification is not an endpoint.** The model answer stays on the frontend. The user edits it there. The server is called once, when the final expense is saved. Nothing half-ready is stored.

**Where data goes:**
- path → which one (`/expenses/{id}`)
- query → filter (`?month=2026-09`)
- body → the data itself (`POST` and `PATCH` only)

---

## 6. AI features

1. **Receipt reading** — the model fills product name, price, currency, category and unit from the image.
2. **Automatic category** — from the product name.
3. **Monthly analysis** — total, percent change from last month, where the money went.
4. **Daily message** — today's total, and whether he is saving or spending more.

The user correction in step 3 of the flow is the evaluation data. It is collected from day one. The review interface comes later, not in v1.

---

## 7. Failure cases (minimum for v1)

| Case | Answer |
|---|---|
| Missing or wrong field in the body | `400` + the name of the bad field |
| `id` not found | `404` |
| The model cannot read the receipt | `200`, empty `extracted`, filled `missing_fields`. **Not an error** — this is the manual path |
| The exchange rate API is down | Save the expense in its own currency with `exchange_rate: null`, convert later |

Rule: a broken external service must never stop the user from recording an expense.

---

## 8. Open decisions

- [ ] A field that marks a value as "written by AI" or "corrected by user" — not needed for v1, needed for accuracy measurement
- [ ] `unit`: user types it, or AI suggests and user edits?
- [ ] Daily message: a push notification, or a screen shown when the app opens? (PWA on iOS limits notifications)
- [ ] Salary input: is that tracking or planning? Section 1 excluded planning
- [ ] Wallet and card payments: in scope, or later?
- [ ] Conversion when the phone has no internet at the moment of purchase

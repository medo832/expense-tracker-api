# Expense Tracker — API Spec v1

> العقد اللي هيتكتب عليه كود السيرفر وكود الواجهة.
> اليوزر معروف من تسجيل الدخول، فمفيش `/users/{id}` في أي مسار.

---

## 1. الجدول

| Method | Path | Purpose | Input | Output | Success |
|---|---|---|---|---|---|
| `GET` | `/health` | التأكد إن السيرفر عايش | — | `{"status": "ok"}` | 200 |
| `POST` | `/expenses/scan` | استخراج بيانات المصروف من صورة فاتورة | Body: `multipart` (ملف صورة) | البيانات المستخرجة + `scan_id` | 200 |
| `POST` | `/expenses` | حفظ مصروف بعد ما اليوزر أكّده | Body: بيانات المصروف (+ `scan_id` اختياري) | المصروف بعد الحفظ | 201 |
| `GET` | `/expenses` | قائمة مصاريف شهر | Query: `month=YYYY-MM` | مصفوفة مصاريف | 200 |
| `GET` | `/expenses/{id}` | مصروف واحد بتفاصيله | Path: `id` | مصروف | 200 |
| `PATCH` | `/expenses/{id}` | تعديل مصروف أو إخفاؤه | Path: `id` · Body: الحقول المتغيرة بس | المصروف بعد التعديل | 200 |
| `DELETE` | `/expenses/{id}` | حذف نهائي | Path: `id` | — | 204 |
| `GET` | `/summary/monthly` | أرقام الشهر (إجمالي، نسبة التغير، أعلى تصنيف) | Query: `month=YYYY-MM` | أرقام | 200 |
| `GET` | `/summary/daily` | أرقام اليوم (مادة الرسالة اليومية) | Query: `date=YYYY-MM-DD` | أرقام | 200 |
| `GET` | `/settings` | قراءة الإعدادات (العملة الأساسية) | — | إعدادات | 200 |
| `PATCH` | `/settings` | تغيير العملة الأساسية | Body: `{"base_currency": "EGP"}` | الإعدادات بعد التعديل | 200 |

**مؤجَّل لـ v2:** `GET /scans` — لسحب بيانات التقييم (الصورة + رد المودل + التصحيح) لما تيجي تقيس دقة الموديل.

---

## 2. الفروق عن جدولك ولماذا

| التغيير | السبب |
|---|---|
| `/daily-message` → `/summary/daily` | السيرفر بيبعت **أرقام**، والموبايل هو اللي بيصيغ منها رسالة. اسم المورد يوصف البيانات مش شكل العرض |
| التحليل الشهري بقى `/summary/monthly` مش `/expenses` | `/expenses` بترجّع **صفوف محفوظة**، والملخص بيرجّع **حسابات مش موجودة في الداتابيز**. موردين مختلفين |
| `/summary/monthly` و `/summary/daily` مسارين منفصلين | لو الاتنين نفس المسار بفلتر مختلف، السيرفر هيحتاج يفحص أنهي فلتر جه — تعقيد بلا فايدة |
| رجعت `DELETE /expenses/{id}` | كانت في المحاولة التانية وسقطت من النهائية |
| اتضافت `GET /expenses/{id}` | شاشة تفاصيل المصروف محتاجاها |
| اتضافت `GET /settings` | التطبيق لازم يعرف العملة الأساسية أول ما يفتح |
| `/settings/currency` → `/settings` | لما تزود إعداد تاني (اللغة، التنبيهات) مش هتعمل مسار جديد لكل واحد |
| اتضافت `GET /health` | أول endpoint هتنشره. وجوده على الإنترنت = إثبات إن السيرفر شغال |
| `POST /expenses/scan` بقى بيرجّع `scan_id` | ده اللي بيربط رد المودل بالتصحيح — قلب نظام التقييم |

---

## 3. شكل البيانات

### `POST /expenses/scan`

```
request:  multipart/form-data  →  file: receipt.jpg

response: 200
{
  "scan_id": "scn_9c21af",
  "model": "gpt-4o-mini-2026-05",
  "extracted": {
    "product_name": "موز",
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

`missing_fields` بتقول للواجهة تحطّ المؤشر فين — الحقول اللي المودل مقدرش يطلعها.

### `POST /expenses`

```
request:
{
  "scan_id": "scn_9c21af",          // اختياري — مش موجود في الإدخال اليدوي
  "product_name": "موز",
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
  "product_name": "موز",
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

**لاحظ:** العميل بعت `price_paid` و `currency_paid` بس. السيرفر هو اللي ضاف `id` و `base_currency` و `price_in_base` و `exchange_rate` و `created_at` — دي كلها مشتقات أو قرارات سيرفر.

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

أرقام بس. مفيش رسوم ولا نصوص — الرسم والصياغة شغل الواجهة.

---

## 4. جدول الـ scans (للتقييم)

منفصل عن `expenses`:

```
scan_id · image_ref · raw_model_output (JSON) · model_name · model_version · created_at
```

و `expenses.scan_id` بيربط الاتنين. الفرق بين `raw_model_output` والمصروف المحفوظ = **تصحيح متصنَّف اتولد لوحده**.

الصورة تتخزن في object storage (R2 / Supabase Storage) مش في الداتابيز، مصغّرة لـ 1024px عرض.

---

## 5. حالات الفشل — أقل حاجة في v1

| الحالة | الرد |
|---|---|
| بيانات ناقصة أو نوعها غلط في الـ body | `400` + اسم الحقل الغلط |
| `id` مش موجود | `404` |
| المودل مقدرش يقرا الفاتورة | `200` + `extracted` فاضية + `missing_fields` مليانة — **مش خطأ**، ده طريق الإدخال اليدوي |
| API سعر الصرف واقع | تخزّن المصروف بعملته الأصلية و `exchange_rate: null`، وتحسبه بعدين |

الصف الأخير قرار مهم: **فشل خدمة خارجية ميمنعش اليوزر من تسجيل مصروفه.**

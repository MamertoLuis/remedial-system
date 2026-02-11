# PERFORMANCE_OPTIMIZATION_GUIDE.md

## Django Banking System (Low Bandwidth + Modest Server)

---

# 1️⃣ Optimize for Slow Networks First

In rural branches:

* 3G / unstable fiber
* High latency
* Shared WiFi
* Old hardware

### Your Goal:

* Pages load under 1–2 seconds
* Tables render quickly
* No heavy JS
* Minimal page weight

---

# 2️⃣ Frontend Performance Rules

## ✅ Keep Initial Page Under 500KB

Check in browser DevTools → Network tab.

### Remove:

* Unused JS libraries
* CDN analytics
* Large fonts
* Icon libraries (FontAwesome full set is heavy)

### Prefer:

* Bootstrap CSS (minified)
* HTMX (~14KB)
* One small `app.css`
* One small `app.js`

---

## ✅ Use Server Rendering (You Already Do)

Server-rendered HTML is faster than SPA on weak devices.

Avoid:

* JSON-heavy rendering
* Frontend filtering logic

---

## ✅ Paginate Everything

Never render 1,000 rows.

Correct:

```python
class LoanListView(ListView):
    paginate_by = 25
```

---

## ✅ Use HTMX for Partial Refresh Only

Good use cases:

* Table filter
* Search
* Modal form

Bad:

* Entire dashboard auto-refresh every 5 seconds

---

# 3️⃣ Database Performance (Critical for Banking)

## 🔥 Always Index These Fields

For Loans:

* status
* branch
* due_date
* customer
* tenant (if multi-tenant)

Example:

```python
class Meta:
    indexes = [
        models.Index(fields=["tenant", "status"]),
        models.Index(fields=["due_date"]),
    ]
```

---

## 🔥 Use select_related & prefetch_related

Avoid N+1 queries.

Bad:

```python
for loan in loans:
    loan.customer.name
```

Good:

```python
Loan.objects.select_related("customer")
```

---

## 🔥 Use Aggregation in Database

Compute totals in SQL, not Python loops.

Good:

```python
Loan.objects.filter(status="A").aggregate(Sum("amount"))
```

Bad:

```python
sum(loan.amount for loan in loans)
```

---

## 🔥 Avoid Large JOINs in Reports

For large reports:

* Filter by date range
* Limit branch
* Require user input before query

Never auto-run full portfolio reports.

---

# 4️⃣ Gunicorn Optimization (Ubuntu Server)

## Recommended Config

```bash
gunicorn config.wsgi:application \
  --workers 3 \
  --worker-class sync \
  --timeout 60
```

### Workers Rule of Thumb

```
workers = (2 x CPU cores) + 1
```

For small VPS (2 cores):

```
workers = 3–5
```

---

## Use Keepalive

Add:

```
--keep-alive 5
```

---

# 5️⃣ Whitenoise Optimization

In settings:

```python
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

Benefits:

* Gzip
* Brotli
* Hashed filenames
* Long-term caching

---

# 6️⃣ PostgreSQL Optimization

For small rural deployments:

## Increase shared_buffers

In `postgresql.conf`:

```
shared_buffers = 256MB
```

(Adjust based on RAM)

---

## Enable Slow Query Logging

```
log_min_duration_statement = 500
```

This logs queries >500ms.

---

# 7️⃣ Caching Strategy (Keep It Simple)

Avoid Redis early.

Use:

### Per-view caching for reports

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)
def par_report(request):
```

Only cache:

* Dashboard summaries
* Heavy reports

Never cache:

* Transaction posting screens

---

# 8️⃣ File Upload & Media Optimization

For scanned collateral, KYC docs:

* Limit max upload size
* Compress images server-side
* Avoid storing massive PDFs

---

# 9️⃣ Logging & Monitoring

Enable:

```python
LOGGING = {
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "django.log",
        },
    }
}
```

Monitor:

* Slow pages
* Errors
* Database spikes

---

# 🔟 Query Optimization Workflow

When page is slow:

1. Enable Django Debug Toolbar (dev only)
2. Count queries
3. Fix N+1
4. Add index
5. Optimize aggregation

Do NOT guess.

---

# 1️⃣1️⃣ Dashboard Optimization

For banking dashboards:

Instead of live computing:

* Create daily snapshot table
* Compute metrics once per day
* Dashboard reads snapshot

This dramatically reduces load.

---

# 1️⃣2️⃣ Rural Environment Specific Tips

✔ Avoid large background polling
✔ Avoid auto-refresh
✔ Avoid animated charts
✔ Avoid 5MB libraries
✔ Keep UI static and stable

Design for:

* Older laptops
* Low memory PCs
* Shared networks

---

# 1️⃣3️⃣ Performance Checklist Before Go-Live

* [ ] All tables paginated
* [ ] Indexes on status/branch/date
* [ ] No N+1 queries
* [ ] Static files compressed
* [ ] Page size < 500KB
* [ ] Gunicorn workers tuned
* [ ] Reports filtered by date/branch
* [ ] No debug mode in production
* [ ] Database vacuumed/analyzed

---

# 1️⃣4️⃣ When to Upgrade Architecture

Upgrade only if:

* > 200 concurrent users
* Heavy analytics
* Multi-region SaaS

Then consider:

* Nginx
* Redis cache
* Background jobs
* Read replica DB

Not before.

---

# Final Philosophy

For a rural banking system:

> Stability > Speed
> Simplicity > Scalability
> Predictable performance > Fancy UI


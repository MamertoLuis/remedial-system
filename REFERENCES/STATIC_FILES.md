# Static Files Best Practices (Django Production-Ready)

---

## 1️⃣ Understand the 3 Static Contexts

There are three environments to think about:

| Context     | Purpose                      | Served By           |
| ----------- | ---------------------------- | ------------------- |
| Development | Local testing                | `runserver`         |
| Production  | Real users                   | Whitenoise / Nginx  |
| Build       | Asset compilation (optional) | Node / Tailwind CLI |

Do not mix them.

---

## 2️⃣ Recommended Static Structure

```
project/
├── static/
│   ├── css/
│   │   ├── bootstrap.min.css
│   │   ├── app.css
│   ├── js/
│   │   ├── htmx.min.js
│   │   ├── app.js
│   ├── img/
│   └── vendor/
```

Inside apps (only if needed):

```
apps/loans/static/loans/
```

### Rule:

* Global UI → `project/static/`
* App-specific static → `apps/<app>/static/<app>/`

Avoid duplication.

---

## 3️⃣ Always Use `{% load static %}`

Never hardcode paths.

Correct:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/app.css' %}">
```

Wrong:

```html
<link rel="stylesheet" href="/static/css/app.css">
```

Hardcoded paths break in production.

---

## 4️⃣ Production: Use Whitenoise Correctly

In `settings.py`:

```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

Why this matters:

* Adds hashed filenames (`app.2938fjs.css`)
* Enables browser cache busting
* Compresses files (gzip/brotli)

---

## 5️⃣ Always Run collectstatic Before Deployment

```bash
python manage.py collectstatic
```

Production serves from `STATIC_ROOT`, not `static/`.

---

## 6️⃣ Enable Long-Term Caching (Important)

Whitenoise + Manifest storage automatically gives:

* Cache forever headers
* Hash-based invalidation

This is critical for performance.

---

## 7️⃣ Minify CSS & JS in Production

If using Bootstrap or Tailwind:

* Use `.min.css`
* Use `.min.js`
* Avoid shipping dev builds

If custom CSS grows:

* Minify during build step
* Keep development readable version

---

## 8️⃣ Keep JavaScript Minimal

Since you use HTMX:

* No React
* No state management
* No complex bundles

Typical JS should be:

* htmx
* optional small helper functions
* Bootstrap JS bundle

If JS grows beyond 300–400 lines:

* Refactor
* Modularize into files

---

## 9️⃣ Tailwind (If Used) — Recommended Pattern

If using Tailwind:

* Use CLI build
* Generate `app.css`
* Don’t load full CDN in production

Example:

```
tailwindcss -i ./static/src/input.css -o ./static/css/app.css --minify
```

---

## 🔟 Avoid These Static Mistakes

❌ Storing user uploads in static
❌ Serving static via Django in production without Whitenoise
❌ Using inline CSS
❌ Copying same CSS into multiple files
❌ Not hashing filenames
❌ Including 20 vendor libraries

---

## 1️⃣1️⃣ Media vs Static (Important)

Static = code assets
Media = user uploads

Use:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

Never mix the two.

---

## 1️⃣2️⃣ Keep CSS Structured

Recommended structure:

```
app.css
├── variables
├── layout
├── components
├── utilities
```

Avoid writing random rules everywhere.

---

## 1️⃣3️⃣ Performance Checklist

Before production:

* [ ] Using CompressedManifestStaticFilesStorage
* [ ] collectstatic ran
* [ ] Files are minified
* [ ] No large unused libraries
* [ ] Browser caching enabled
* [ ] Static files < 2MB total (initial load)

---

## 1️⃣4️⃣ CDN — When to Use

Use CDN only if:

* Public SaaS
* Many users
* Multiple geographic regions

For internal rural bank systems:

* Whitenoise is enough.

---

## 1️⃣5️⃣ Security Considerations

* Do not allow static file directory browsing
* Do not expose source maps in production (unless debugging)
* Never store secrets in JS

---

# Recommended Minimal Production Setup (Your Stack)

For your Ubuntu server:

* Gunicorn
* Whitenoise
* STATIC_ROOT configured
* collectstatic run during deploy
* No Nginx required for small-medium systems

---

# Ideal Static Files Strategy for Your Banking System

Given your rural bank system:

* Keep Bootstrap local (not CDN)
* Keep HTMX local
* Minimal custom CSS
* Strict UI consistency
* No fancy animations
* Fast load over low-bandwidth connections

---

If you want, I can next provide:

* A **production-ready `settings.py` static configuration template**
* Or a **static file deployment checklist for Ubuntu**
* Or a **performance optimization guide specifically for low-bandwidth provincial environments** (very relevant for rural banks)

Which direction do you want?

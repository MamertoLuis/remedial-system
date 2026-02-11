

```
PROJECT_BOOTSTRAP.md
```

---

# PROJECT_BOOTSTRAP.md — Django Project Initialization Script for AI Agents

> This document defines the **exact steps** an AI agent must follow to create a new Django project that complies with `AGENTS.md`.

The AI must execute these steps **in order**. No improvisation.

---

## 0. Environment Assumptions

Target OS: **Ubuntu 22.04+**
Python: **3.11+**
Database: **PostgreSQL**

---

## 1. Create Project Folder

```bash
mkdir project
cd project
```

---

## 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Required Packages

```bash
pip install Django psycopg[binary] django-htmx \
django-allauth django-crispy-forms crispy-bootstrap5 \
python-dotenv django-environ whitenoise gunicorn
```

---

## 4. Start Django Project

```bash
django-admin startproject config .
```

---

## 5. Create Required Folder Structure

```bash
mkdir apps
mkdir templates
mkdir static
```

---

## 6. Edit `config/settings.py`

### Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    "django.contrib.sites",

    # third party
    "django_htmx",
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",

    # local
    "apps.core",
]
```

### Add

```python
SITE_ID = 1
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

### Templates DIR

```python
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]
```

### Static

```python
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

### Whitenoise

```python
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
```

---

## 7. Create First App (`core`)

```bash
python manage.py startapp core apps/core
```

Fix `apps.py` name to:

```python
name = "apps.core"
```

---

## 8. Configure Root URLs (`config/urls.py`)

```python
from django.urls import path, include

urlpatterns = [
    path("", include("apps.core.urls")),
    path("accounts/", include("allauth.urls")),
]
```

---

## 9. Create Base Templates

### `templates/base.html`

```html
<!DOCTYPE html>
<html>
<head>
  <title>{% block title %}App{% endblock %}</title>
  {% load static %}
  <link href="{% static 'css/bootstrap.min.css' %}" rel="stylesheet">
</head>
<body>
  <div class="container mt-4">
    {% block content %}{% endblock %}
  </div>
</body>
</html>
```

---

## 10. Create Core URLs and View

### `apps/core/urls.py`

```python
from django.urls import path
from .views import home

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
]
```

### `apps/core/views.py`

```python
from django.shortcuts import render

def home(request):
    return render(request, "core/home.html")
```

### `templates/core/home.html`

```html
{% extends "base.html" %}
{% block content %}
<h1>Project Ready</h1>
{% endblock %}
```

---

## 11. Run Migrations and Create Superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 12. Run Server

```bash
python manage.py runserver
```

At this point, the project is ready and compliant with `AGENTS.md`.

---

## 13. Creating a New Business App (Example: loans)

When adding a feature:

```bash
python manage.py startapp loans apps/loans
```

Add to `INSTALLED_APPS`:

```python
"apps.loans",
```

Create standard files:

```
models.py
admin.py
urls.py
views.py
forms.py
services.py
selectors.py
```

Wire URLs in `config/urls.py`:

```python
path("loans/", include("apps.loans.urls")),
```

Follow rules from `AGENTS.md`.

---

## 14. PostgreSQL Configuration (.env)

Create `.env`

```
DB_NAME=project
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
```

Use `django-environ` in settings.

---

## 15. Gunicorn Production Test

```bash
gunicorn config.wsgi:application
```

---

## Completion Condition for AI

The AI should stop once:

* Home page loads
* Admin works
* Allauth login works
* Folder structure matches standard

No extra features should be added.

---

## Final Rule

After bootstrap, all future development must strictly follow **AGENTS.md**.


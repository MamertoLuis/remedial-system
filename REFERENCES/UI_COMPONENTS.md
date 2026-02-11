

```
UI_COMPONENTS.md
```

---

# UI_COMPONENTS.md — Standard UI Library for Django Templates (Bootstrap + HTMX)

> This document defines the **mandatory UI patterns** for all templates in this project.
> AI agents and developers must **reuse these components** instead of inventing new markup.

Framework: **Bootstrap 5 + Crispy Forms + HTMX**

---

## 0. Design Principles

All pages must be:

* Clean
* Consistent
* Predictable
* Business-oriented (dashboard/backoffice style)
* Desktop-first, responsive second

Never invent new layout patterns.

---

## 1. Base Layout

All templates extend:

```html
{% extends "base.html" %}
```

Page layout order is always:

```
Title
Actions Bar
Content (table / form / cards)
```

---

## 2. Page Title + Actions Bar

### Component: `components/page_header.html`

```html
<div class="d-flex justify-content-between align-items-center mb-3">
  <h2 class="mb-0">{{ title }}</h2>
  <div>
    {{ actions|safe }}
  </div>
</div>
```

### Usage

```html
{% include "components/page_header.html" with title="Loans" actions=actions %}
```

---

## 3. Standard Table

### Component: `components/table.html`

```html
<table class="table table-striped table-hover align-middle">
  <thead class="table-light">
    {{ header|safe }}
  </thead>
  <tbody>
    {{ body|safe }}
  </tbody>
</table>
```

### Rules

* Always striped
* Always hoverable
* No custom table styles per page

---

## 4. Table Wrapped in Card

### Component: `components/table_card.html`

```html
<div class="card shadow-sm">
  <div class="card-body">
    {% include "components/table.html" %}
  </div>
</div>
```

Tables never float alone on the page.

---

## 5. Standard Form Layout

Forms must be rendered using crispy.

```html
<form method="post">
  {% csrf_token %}
  {{ form|crispy }}
  <button type="submit" class="btn btn-primary">Save</button>
</form>
```

Never handcraft form fields.

---

## 6. Standard Buttons

| Purpose        | Class                    |
| -------------- | ------------------------ |
| Primary action | `btn btn-primary`        |
| Secondary      | `btn btn-secondary`      |
| Danger         | `btn btn-danger`         |
| Small          | `btn btn-sm btn-primary` |

Buttons are never styled inline.

---

## 7. Card Layout

### Component: `components/card.html`

```html
<div class="card shadow-sm mb-3">
  <div class="card-body">
    {{ content|safe }}
  </div>
</div>
```

Used for:

* Detail pages
* Dashboards
* Forms
* Tables

---

## 8. HTMX Partial Pattern

Partials live in:

```
templates/<app>/partials/
```

Example:

```
loans/partials/loan_table.html
```

This file must render:

* Both full page load
* HTMX refresh

No duplicated markup.

---

## 9. Standard Detail Page Pattern

```
Page Header
Card
  Key-Value table
Related tables (in cards)
```

Key-value table:

```html
<table class="table table-bordered">
  <tr><th>Borrower</th><td>{{ loan.borrower }}</td></tr>
  <tr><th>Amount</th><td>{{ loan.amount }}</td></tr>
</table>
```

---

## 10. Navbar (Global Include)

### `includes/navbar.html`

Simple, flat, professional.

```html
<nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
  <div class="container-fluid">
    <a class="navbar-brand" href="/">System</a>
  </div>
</nav>
```

Included in `base.html`.

---

## 11. Messages / Alerts

### `includes/messages.html`

```html
{% if messages %}
  {% for message in messages %}
    <div class="alert alert-{{ message.tags }}">
      {{ message }}
    </div>
  {% endfor %}
{% endif %}
```

---

## 12. Modal (HTMX Friendly)

### `components/modal.html`

Standard modal markup used everywhere.
Never rewrite modals per page.

---

## 13. Spacing Rules

Use Bootstrap spacing only:

```
mb-3, mt-3, p-3, px-4
```

No inline margins or padding.

---

## 14. What AI Must Never Do

❌ Create new table styles
❌ Handcraft form HTML
❌ Create new layout patterns
❌ Inline CSS
❌ Duplicate markup across pages

Always reuse components.

---

## 15. Example Page Assembly

```html
{% extends "base.html" %}

{% block content %}

{% include "components/page_header.html" with title="Loans" %}

<div class="card shadow-sm">
  <div class="card-body">
    {% include "loans/partials/loan_table.html" %}
  </div>
</div>

{% endblock %}
```

---

## Final Rule

If two pages look visually different, the AI did it wrong.

All pages must feel like the same system.

---

With these three files, your AI agents now know:

1. How to code
2. How to start the project
3. How the UI must look



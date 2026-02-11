

```
CODE_PATTERNS.md
```

---

# CODE_PATTERNS.md — Canonical Django Patterns for This Project

> This document provides **reference implementations**.
> AI agents must **copy these patterns** when generating code.

Do not invent new structures. Reuse these.

---

## 1. Model Pattern

```python
# apps/loans/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Loan(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "A", "Active"
        CLOSED = "C", "Closed"
        DEFAULTED = "D", "Defaulted"

    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.ACTIVE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan #{self.pk} - {self.borrower}"
```

Rules:

* Always use `TextChoices`
* Always include timestamps
* No business logic here

---

## 2. Admin Pattern

```python
# apps/loans/admin.py
from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("id", "borrower", "amount", "status", "created_at")
    search_fields = ("borrower__username",)
    list_filter = ("status",)
```

---

## 3. Selector Pattern (All Queries)

```python
# apps/loans/selectors.py
from .models import Loan


def active_loans():
    return Loan.objects.filter(status=Loan.Status.ACTIVE)


def loan_by_id(pk: int) -> Loan:
    return Loan.objects.get(pk=pk)
```

---

## 4. Service Pattern (All Business Logic)

```python
# apps/loans/services.py
from .models import Loan


def close_loan(loan: Loan):
    loan.status = Loan.Status.CLOSED
    loan.save()
```

---

## 5. Form Pattern

```python
# apps/loans/forms.py
from django import forms
from .models import Loan


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ["borrower", "amount"]

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount
```

---

## 6. CRUD CBV Pattern

```python
# apps/loans/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Loan


class LoanListView(ListView):
    model = Loan
    paginate_by = 25


class LoanDetailView(DetailView):
    model = Loan


class LoanCreateView(CreateView):
    model = Loan
    form_class = LoanForm
    success_url = reverse_lazy("loans:list")


class LoanUpdateView(UpdateView):
    model = Loan
    form_class = LoanForm
    success_url = reverse_lazy("loans:list")
```

---

## 7. Workflow Function View Pattern

```python
from django.shortcuts import get_object_or_404, redirect
from . import services


def close_loan_view(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    services.close_loan(loan)
    return redirect("loans:detail", pk=pk)
```

---

## 8. HTMX Table Partial Pattern

### View

```python
def loan_table(request):
    loans = selectors.active_loans()
    return render(request, "loans/partials/loan_table.html", {"loans": loans})
```

### Template (`partials/loan_table.html`)

```html
<table class="table table-striped">
  {% for loan in loans %}
  <tr>
    <td>{{ loan.id }}</td>
    <td>{{ loan.borrower }}</td>
    <td>{{ loan.amount }}</td>
  </tr>
  {% endfor %}
</table>
```

---

## 9. URLs Pattern

```python
# apps/loans/urls.py
from django.urls import path
from . import views

app_name = "loans"

urlpatterns = [
    path("", views.LoanListView.as_view(), name="list"),
    path("<int:pk>/", views.LoanDetailView.as_view(), name="detail"),
    path("create/", views.LoanCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.LoanUpdateView.as_view(), name="edit"),
    path("<int:pk>/close/", views.close_loan_view, name="close"),
]
```

---

## 10. List Template Pattern

```html
{% extends "base.html" %}

{% block content %}
<h2>Loans</h2>

<a href="{% url 'loans:create' %}" class="btn btn-primary mb-3">New Loan</a>

{% include "loans/partials/loan_table.html" %}
{% endblock %}
```

---

## 11. Detail Template Pattern

```html
{% extends "base.html" %}

{% block content %}
<h2>Loan Detail</h2>

<table class="table table-bordered">
  <tr><th>Borrower</th><td>{{ object.borrower }}</td></tr>
  <tr><th>Amount</th><td>{{ object.amount }}</td></tr>
</table>

<a href="{% url 'loans:close' object.id %}" class="btn btn-danger">Close Loan</a>

{% endblock %}
```

---

## 12. What AI Must Copy Exactly

When creating new apps:

* Copy model pattern
* Copy admin pattern
* Copy selector/service separation
* Copy CBV structure
* Copy template layout

Do not invent new patterns.

---

## Final Rule

If the generated code does not resemble these patterns, it is incorrect.

---



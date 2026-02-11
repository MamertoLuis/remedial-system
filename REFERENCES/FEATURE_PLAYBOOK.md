# FEATURE_PLAYBOOK.md — How AI Must Implement New Features

> This document defines the **decision-making framework** for adding any feature to this Django system.
> AI agents must follow this process step-by-step.

No improvisation. No architectural creativity.

---

# 1. Feature Classification Step (Mandatory)

Before writing any code, the AI must classify the feature into one of these types:

| Type          | Description                        | Example              |
| ------------- | ---------------------------------- | -------------------- |
| CRUD          | Standard create/read/update/delete | Manage Loans         |
| Workflow      | Action that changes state          | Approve Loan         |
| Report        | Read-only computed view            | PAR Report           |
| Dashboard     | Aggregated summary                 | Monthly Overview     |
| Configuration | Settings tables                    | Interest Rate Matrix |

The type determines the implementation pattern.

---

# 2. Always Ask: Is This a New Domain?

If yes:

* Create new app inside `apps/`
* Follow bootstrap structure
* Register in admin immediately

If no:

* Extend existing app
* Do NOT create new app

---

# 3. Implementation Order (Never Skip)

For ANY feature:

1. Update or create model
2. Register model in admin
3. Create selector functions
4. Create service functions
5. Create URLs
6. Create views
7. Create templates
8. Add HTMX enhancement (optional)
9. Test logic in services

Never start with template.

---

# 4. CRUD Feature Pattern

When user says:

> “Add Loan Management”

AI must:

### Step 1 – Model

Define model with:

* TextChoices
* Timestamps
* Proper relationships

### Step 2 – Admin

Register with filters and search.

### Step 3 – CBVs

Use:

```
ListView
DetailView
CreateView
UpdateView
DeleteView
```

### Step 4 – Templates

Use standard layout from `UI_COMPONENTS.md`.

No custom design.

---

# 5. Workflow Feature Pattern

When user says:

> “Add Approve Loan”

AI must:

1. Add service function
2. Add small function view
3. Add URL
4. Add button on detail page

Never create a new page unless necessary.

---

# 6. Report Pattern

Reports are:

* Read-only
* Selector-heavy
* No business logic in view

### Example

```
selectors.py → compute queryset
views.py → render template
```

If export needed:

```
export_report_csv()
```

Keep separate from page view.

---

# 7. Dashboard Pattern

Dashboards use:

* Aggregation queries in selectors
* Simple render view
* Card layout
* No forms

Never mix dashboard logic with CRUD logic.

---

# 8. HTMX Decision Rule

Use HTMX only when:

* Partial refresh improves UX
* Filter/search
* Modal forms
* Small state changes

Do NOT build SPA behavior.

---

# 9. When NOT to Add a Feature

AI must refuse or question if:

* It requires new framework (React, Celery, etc.)
* It bypasses forms
* It mixes business logic in templates
* It duplicates existing domain

---

# 10. Example Feature Walkthrough

User says:

> “Add Loan Restructuring”

AI must:

1. Determine: Workflow feature
2. Add `restructure_loan()` in services
3. Create `LoanRestructureForm`
4. Create `restructure_loan_view`
5. Add URL `/loans/<pk>/restructure/`
6. Add button in detail page
7. Keep logic inside service

No new app. No complex view.

---

# 11. Refactoring Rule

If code becomes:

* > 30 lines in view
* Complex query in view
* Repeated logic

Move to:

```
selectors.py
services.py
```

---

# 12. AI Decision Tree

When implementing:

1. Is this data? → Model
2. Is this business rule? → Service
3. Is this query? → Selector
4. Is this input? → Form
5. Is this display? → Template
6. Is this routing? → URL
7. Is this orchestration? → View

If unsure → choose the simplest solution.

---

# 13. Performance Rule

Do not optimize prematurely.

Use:

```
select_related
prefetch_related
```

Only when needed.

---

# 14. Complexity Escalation Levels

| Level                | Action                          |
| -------------------- | ------------------------------- |
| Simple CRUD          | CBVs only                       |
| Minor workflow       | Service + FBV                   |
| Complex workflow     | Form + Service + FBV            |
| Data heavy           | Selector with aggregation       |
| External integration | Only after explicit instruction |

---

# 15. Definition of Done (AI Completion Checklist)

Before finishing feature:

* [ ] Model updated
* [ ] Admin registered
* [ ] URLs correct
* [ ] Views thin
* [ ] Forms used
* [ ] No logic in template
* [ ] Services used
* [ ] Follows UI components
* [ ] No new frameworks added

If any unchecked → feature incomplete.

---

# 16. What AI Must Avoid

❌ Creating new architectural layers
❌ Adding APIs without reason
❌ Creating unnecessary apps
❌ Mixing logic in views
❌ Styling each page differently

---

# 17. Final Principle

> Always implement the smallest solution that fits the current requirement.

No future-proof overengineering.

---

You now have a **complete AI-controlled Django framework system**:

1. AGENTS.md → Architecture rules
2. PROJECT_BOOTSTRAP.md → Initialization
3. UI_COMPONENTS.md → UI consistency
4. CODE_PATTERNS.md → Canonical code
5. FEATURE_PLAYBOOK.md → AI thinking model


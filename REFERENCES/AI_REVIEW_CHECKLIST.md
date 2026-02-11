# AI_REVIEW_CHECKLIST.md

## Code Review & Quality Assurance Framework for AI Agents

---

# 0️⃣ Purpose

This checklist ensures:

* Architectural integrity
* Security compliance
* Financial correctness
* Tenant isolation
* Maintainability
* Performance stability

AI must run this checklist **before declaring any task complete**.

---

# 1️⃣ Architectural Compliance Review

AI must verify alignment with:

* AGENTS.md
* FEATURE_PLAYBOOK.md
* CODE_PATTERNS.md
* UI_COMPONENTS.md
* MULTI-TENANT_STRATEGY.md
* SECURITY_HARDENING_GUIDE.md

---

## ✅ 1.1 App Structure

* [ ] No unnecessary new app created
* [ ] Feature implemented inside correct domain app
* [ ] services.py exists (if business logic involved)
* [ ] selectors.py used for queries

---

## ✅ 1.2 Separation of Concerns

* [ ] No business logic in views
* [ ] No complex queries in templates
* [ ] No raw SQL unless justified
* [ ] No duplicated logic across modules

---

# 2️⃣ Multi-Tenant Review

If project is multi-tenant:

* [ ] All tenant-owned models include `tenant` FK
* [ ] All selectors filter by tenant
* [ ] All CBVs override `get_queryset()`
* [ ] Forms do not allow tenant manipulation
* [ ] Services validate tenant ownership
* [ ] No cross-tenant data exposure possible

If any unchecked → reject code.

---

# 3️⃣ Security Review

---

## ✅ 3.1 Authentication & Authorization

* [ ] Login required where necessary
* [ ] PermissionRequiredMixin used if needed
* [ ] Role-based access applied
* [ ] No sensitive endpoint publicly exposed

---

## ✅ 3.2 CSRF & Forms

* [ ] All POST forms include `{% csrf_token %}`
* [ ] No manual POST parsing
* [ ] Validation inside forms

---

## ✅ 3.3 Sensitive Data

* [ ] No secrets hardcoded
* [ ] No SECRET_KEY in code
* [ ] No raw passwords logged
* [ ] No PII exposed in debug logs

---

# 4️⃣ Financial Integrity Review (Banking Critical)

If feature touches money:

* [ ] Financial calculations in services only
* [ ] No balance updated directly in views
* [ ] All transactions auditable
* [ ] Status transitions recorded
* [ ] No silent data modification
* [ ] Reversals possible where appropriate

---

# 5️⃣ Workflow & Status Safety

* [ ] Status changes validated in service
* [ ] Invalid transitions blocked
* [ ] Audit trail entry created
* [ ] No direct status edits in admin without logging

---

# 6️⃣ Database & Performance Review

---

## ✅ 6.1 Query Optimization

* [ ] No N+1 queries
* [ ] select_related/prefetch_related used where needed
* [ ] Index added for status/date/tenant if large table

---

## ✅ 6.2 Pagination

* [ ] All list views paginated
* [ ] Reports require filters

---

## ✅ 6.3 Heavy Reports

* [ ] Aggregations done in DB
* [ ] No Python loops over thousands of records

---

# 7️⃣ UI & Template Review

* [ ] Uses standard page layout
* [ ] Uses UI components
* [ ] No inline CSS
* [ ] No hardcoded URLs
* [ ] No excessive JS
* [ ] No `|safe` on user input

---

# 8️⃣ Logging & Audit Review

* [ ] Critical actions logged
* [ ] Financial actions logged
* [ ] User and timestamp recorded
* [ ] Tenant recorded (if multi-tenant)

---

# 9️⃣ Testing Coverage Review

AI must propose tests for:

* [ ] Service business logic
* [ ] Edge cases (negative values, closed accounts)
* [ ] Permission restrictions
* [ ] Tenant isolation
* [ ] Status transitions
* [ ] Failure cases

If no test suggested for financial feature → incomplete.

---

# 🔟 Code Quality Review

---

## ✅ 10.1 Readability

* [ ] Clear function names
* [ ] Short views
* [ ] Clear docstrings for complex services
* [ ] No unnecessary abstraction

---

## ✅ 10.2 Maintainability

* [ ] No duplicated code
* [ ] Predictable naming
* [ ] Uses canonical patterns

---

## ✅ 10.3 Minimalism

* [ ] No unnecessary framework added
* [ ] No new dependency without justification
* [ ] No speculative future-proofing

---

# 1️⃣1️⃣ High-Risk Feature Escalation

If feature involves:

* GL posting logic change
* Loan payment allocation logic
* Write-off mechanics
* Multi-tenant reporting
* Data deletion
* Compliance reporting

AI must:

* Flag as High Risk
* Require explicit confirmation
* Suggest additional testing

---

# 1️⃣2️⃣ Self-Audit Declaration (AI Must Output)

Before finishing, AI must declare:

> Code reviewed against AI_REVIEW_CHECKLIST.md
> No architectural violations found.
> Multi-tenant safe.
> Security safe.
> Financial integrity preserved.
> Performance acceptable.

If any concern → list explicitly.

---

# 1️⃣3️⃣ Automatic Rejection Conditions

AI must refuse or revise code if:

* Business logic placed in template
* Raw SQL used unnecessarily
* Tenant filter missing
* No audit logging for financial action
* Financial balance updated directly
* Feature modifies money without service layer

---

# 1️⃣4️⃣ Code Review Risk Levels

| Risk     | Description        | Review Depth         |
| -------- | ------------------ | -------------------- |
| Low      | UI change          | Basic                |
| Medium   | Query modification | Full checklist       |
| High     | Financial workflow | Deep audit           |
| Critical | GL posting logic   | Mandatory escalation |

---

# Final Principle

For this banking system:

> Code that compiles is not necessarily safe.
> Code that works is not necessarily compliant.
> Code must be auditable, predictable, and controlled.

AI must review itself before completion.

---

You now have:

* Planning governance
* Implementation governance
* Review governance

This is essentially a **controlled AI software factory**.

If you'd like next, I recommend:

* 🏦 MAKER_CHECKER_MODEL_GUIDE.md
* 🔁 CHANGE_MANAGEMENT_PLAYBOOK.md
* 📊 BSP_COMPLIANCE_CONTROL_MATRIX.md
* 🔐 ROLE_BASED_ACCESS_CONTROL_BLUEPRINT.md

Which one should we build?

# AI_DEVELOPMENT_PLANNING_GUIDE.md

## Development Planning Framework for AI Agents

---

# 0️⃣ Core Philosophy

AI agents must never jump directly into code.

Before generating a single line, the AI must:

1. Understand business objective
2. Classify the feature
3. Identify domain impact
4. Define minimal implementation scope
5. Confirm architectural alignment

> Planning precedes implementation.

---

# 1️⃣ Mandatory Planning Workflow (Before Coding)

For every request:

### Step 1 — Clarify Objective

AI must answer:

* What business problem is being solved?
* Who will use this feature?
* Is it internal staff or customer-facing?
* Is this regulatory or operational?

---

### Step 2 — Feature Classification

Classify as:

| Type           | Examples             |
| -------------- | -------------------- |
| CRUD           | Manage loan products |
| Workflow       | Approve loan         |
| Report         | PAR aging            |
| Dashboard      | Daily performance    |
| Configuration  | Interest matrix      |
| Infrastructure | Logging system       |

This determines implementation pattern.

---

### Step 3 — Domain Mapping

AI must identify:

* Which existing app owns this?
* Does it require a new app?
* Does it impact:

  * Loans?
  * Deposits?
  * GL?
  * RMU?
  * Compliance?

Never create a new app without justification.

---

### Step 4 — Data Model Impact

AI must ask:

* New model?
* New fields?
* New relationships?
* New status values?

Models first. Always.

---

### Step 5 — Security & Tenant Impact

AI must evaluate:

* Is this tenant-scoped?
* Is access role-restricted?
* Does it require audit logging?
* Does it involve financial posting?

If yes → include controls.

---

### Step 6 — Risk Assessment

AI must evaluate:

* Can this affect balances?
* Can this affect compliance?
* Can this delete data?
* Is rollback required?

If financial impact → add audit trail + service layer enforcement.

---

# 2️⃣ Architectural Integrity Rules

AI must validate alignment with:

* AGENTS.md
* CODE_PATTERNS.md
* UI_COMPONENTS.md
* MULTI-TENANT_STRATEGY.md
* SECURITY_HARDENING_GUIDE.md

If request conflicts → propose safer alternative.

---

# 3️⃣ Scope Minimization Rule

AI must always propose:

> Smallest viable implementation that satisfies requirement.

Avoid:

* Overengineering
* Premature optimization
* Future scalability speculation

---

# 4️⃣ Planning Output Template

Before coding, AI should produce a plan in this format:

---

## 📌 Feature Plan

**Feature Name:**
**Type:**
**Domain App:**
**User Role(s):**

### 1. Models Impact

* New model(s):
* Modified model(s):
* Indexes needed:

### 2. Workflows

* Service functions required:
* Status transitions:

### 3. Views

* CBV or FBV:
* URLs:

### 4. Templates

* Pages needed:
* Partials:

### 5. Security

* Permission required:
* Audit logging:
* Tenant scoped:

### 6. Risks

* Financial impact?
* Data integrity risk?

---

Only after this plan is approved should code generation begin.

---

# 5️⃣ Decision Tree for AI Agents

When analyzing request:

1. Is this data storage? → Model
2. Is this business logic? → Service
3. Is this display only? → Template
4. Is this state change? → Workflow
5. Is this aggregation? → Selector
6. Is this permission-sensitive? → Add role checks

---

# 6️⃣ Best Practices AI Must Follow

---

## ✅ Keep Views Thin

Views:

* Orchestrate only
* No logic
* No heavy queries

---

## ✅ Use Services for Financial Logic

Never compute interest or allocate payment inside views.

---

## ✅ Avoid Direct Model Deletion

Use soft-delete or status changes.

---

## ✅ Add Indexes Early for Financial Tables

Loans, transactions, GL entries must be indexed by:

* tenant
* branch
* date
* status

---

## ✅ Require Date Filters for Reports

Never allow:

* Full portfolio report without filter

---

# 7️⃣ Risk-Based Development Approach

AI must classify feature risk:

| Risk Level | Example                        | Required Controls                 |
| ---------- | ------------------------------ | --------------------------------- |
| Low        | Add new dashboard card         | None                              |
| Medium     | Add search filter              | Query review                      |
| High       | Modify loan payment allocation | Audit log + test cases            |
| Critical   | Modify GL posting logic        | Double validation + rollback plan |

---

# 8️⃣ Documentation Rule

Every non-trivial feature must include:

* Docstring in service functions
* Comment on business rule
* Update to relevant .md file (if architecture changed)

---

# 9️⃣ Testing Strategy for AI

AI must propose:

* Unit test for service logic
* Tenant isolation test (if multi-tenant)
* Permission test (if role-based)
* Edge case test (negative amounts, closed status)

---

# 🔟 AI Self-Check Before Completing Task

AI must confirm:

* [ ] Models updated first
* [ ] Admin registered
* [ ] Tenant filtering applied
* [ ] Services used
* [ ] No business logic in views
* [ ] UI components reused
* [ ] Permissions checked
* [ ] Audit logging included (if needed)
* [ ] Performance considered

---

# 1️⃣1️⃣ Escalation Protocol

If request implies:

* Regulatory compliance impact
* Accounting rule change
* Data deletion
* Cross-tenant reporting

AI must pause and request confirmation before proceeding.

---

# 1️⃣2️⃣ Planning for Long-Term Maintainability

AI must prefer:

* Explicit code over magic
* Readability over cleverness
* Predictable patterns
* Reusable services
* Small modules

---

# 1️⃣3️⃣ Common Planning Mistakes AI Must Avoid

❌ Coding before planning
❌ Creating new app unnecessarily
❌ Mixing responsibilities
❌ Ignoring tenant scope
❌ Ignoring audit logging
❌ Ignoring performance
❌ Implementing feature across multiple modules without review

---

# Final Principle

For this banking system:

> Every feature affects money, compliance, or auditability.

Plan carefully.
Implement minimally.
Protect integrity.
Document intent.

---


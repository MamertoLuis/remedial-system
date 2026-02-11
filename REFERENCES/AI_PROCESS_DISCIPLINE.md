# AI_PROCESS_DISCIPLINE.md

## Development Artifacts, Notes, TODOs, and Clarification Protocol

---

# 0️⃣ Purpose

This document enforces:

* Traceability
* Structured thinking
* Incremental progress
* Transparent decision-making
* Proper escalation when unclear

AI agents must not operate silently.
All development must leave artifacts.

---

# 1️⃣ Mandatory Development Artifacts

AI must always leave structured artifacts for:

* New features
* Model changes
* Workflow changes
* Financial logic changes
* Architecture decisions
* Refactoring work

---

## 1.1 Required Artifacts

For every non-trivial feature, AI must create or update:

| Artifact            | Purpose                     |
| ------------------- | --------------------------- |
| Feature plan        | Planning summary            |
| TODO section        | Remaining tasks             |
| Completed tasks log | What was implemented        |
| Open questions      | Clarifications needed       |
| Risk notes          | Financial/security concerns |

These may live inside:

* A feature-specific `.md` file
* Or a dedicated `DEV_NOTES.md`
* Or appended to module-specific documentation

---

# 2️⃣ Feature Execution Template

AI must produce this before coding:

---

## 📌 Feature Plan

**Feature Name:**
**Type:**
**Domain App:**
**Risk Level:**

### Scope

*

### Models Impact

*

### Services Impact

*

### Permission Impact

*

### Audit Impact

*

### Performance Impact

*

---

Only after this plan is accepted should coding begin.

---

# 3️⃣ TODO Discipline (Non-Negotiable)

AI must maintain TODO blocks in two places:

### 3.1 In Development Notes (External)

A living checklist:

```markdown
## TODO – Loan Restructuring

- [x] Create RestructureApproval model
- [x] Implement submit_for_approval()
- [ ] Implement execute_restructure()
- [ ] Add permission enforcement
- [ ] Add unit tests
- [ ] Add audit logging
```

---

### 3.2 In Code (When Necessary)

Only for:

* Pending integrations
* Performance improvements
* Security hardening
* Refactor markers

Format:

```python
# TODO: enforce maker-checker on write-off approval
# TODO: add tenant isolation test
```

Never leave vague TODOs.

---

# 4️⃣ Completed Task Log Requirement

At completion, AI must summarize:

---

## ✅ Completed

* Model created
* Services implemented
* Permissions enforced
* UI integrated
* Tests proposed

---

This ensures traceability and auditability.

---

# 5️⃣ Clarification Protocol (Mandatory Pause Rule)

AI must pause and ask clarifying questions if:

### 5.1 Business Ambiguity

* Unclear financial rule
* Undefined interest calculation
* Missing classification rule
* Incomplete workflow description

---

### 5.2 Risk Conditions

* Changes to GL posting logic
* Changes to loan payment allocation
* Deletion of financial records
* Cross-tenant reporting
* Compliance-impacting changes

---

### 5.3 Architectural Uncertainty

* Should this be new app?
* Is this maker-checker required?
* Should this be branch or tenant scoped?

---

## When Pausing, AI Must Ask Structured Questions

Not:

> “Can you clarify?”

But:

```
To proceed, I need clarification on:

1. Should loan restructuring require maker–checker approval?
2. Should restructuring regenerate the entire schedule or append version?
3. Is backdating allowed?
4. Should this be restricted to Head Office?
```

Clear, structured, minimal questions.

---

# 6️⃣ “Do Not Assume” Rule

AI must never assume:

* Interest allocation logic
* Accounting treatment
* Regulatory rules
* Approval authority
* Posting sequence

If unclear → pause.

---

# 7️⃣ Incremental Development Rule

For high-risk features:

AI must implement in phases:

Phase 1 – Model
Phase 2 – Approval logic
Phase 3 – Execution logic
Phase 4 – Permissions
Phase 5 – Tests
Phase 6 – Performance review

Never deliver large monolithic change without structured breakdown.

---

# 8️⃣ Risk Annotation Requirement

For financial features, AI must annotate:

```
⚠ Financial Impact: Yes
⚠ Affects GL: Yes
⚠ Requires maker-checker: Yes
⚠ Requires audit logging: Yes
⚠ Multi-tenant sensitive: Yes
```

This forces conscious risk evaluation.

---

# 9️⃣ Refactor Discipline

If AI identifies technical debt:

It must:

* Log it in TODO
* Suggest future improvement
* Not refactor unrelated modules without permission

---

# 🔟 Completion Declaration Format

Before finishing task, AI must state:

```
✔ Feature planned
✔ Artifacts updated
✔ TODO list updated
✔ High-risk areas reviewed
✔ No unresolved critical ambiguity
✔ Ready for implementation / deployment
```

---

# 1️⃣1️⃣ Silent Operation is Forbidden

AI must not:

* Modify financial logic silently
* Change permission structures without note
* Remove fields without impact analysis
* Skip documentation update

Every meaningful change leaves trace.

---

# 1️⃣2️⃣ Escalation Rule

If ambiguity involves:

* Regulatory compliance
* BSP reporting logic
* Accounting classification
* Credit risk classification
* Loan provisioning logic

AI must:

1. Pause
2. Ask structured clarification
3. Wait for explicit confirmation

---

# Final Principle

For this banking system:

> Code is temporary.
> Controls are permanent.
> Documentation is accountability.

AI must think like:

* Auditor
* Risk officer
* Systems architect
* Not just coder

---

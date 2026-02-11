# CHANGE_MANAGEMENT_PLAYBOOK.md

## Controlled Change, Deployment, and Rollback Framework for Banking Systems

---

# 0️⃣ Purpose

This playbook defines:

* How changes are proposed
* How changes are reviewed
* How changes are deployed
* How changes are rolled back
* How emergency fixes are handled

For a banking system:

> Stability > Speed
> Control > Convenience
> Traceability > Agility

No direct changes to production without process.

---

# 1️⃣ Change Classification

Every change must be classified before implementation.

| Type            | Example                   | Risk     |
| --------------- | ------------------------- | -------- |
| Cosmetic        | UI label change           | Low      |
| Feature         | New dashboard             | Medium   |
| Workflow        | Add approval step         | High     |
| Financial Logic | Change payment allocation | Critical |
| Security        | Auth modification         | High     |
| Infrastructure  | DB change                 | High     |
| Regulatory      | Reporting modification    | Critical |

---

# 2️⃣ Change Lifecycle

All changes follow this lifecycle:

```
Proposal → Planning → Implementation → Review → Staging Test → Approval → Deployment → Post-Deployment Review
```

No shortcuts.

---

# 3️⃣ Change Proposal Template

Before coding:

---

## 📌 Change Proposal

**Title:**
**Type:**
**Risk Level:**
**Affected Modules:**

### Description

What is being changed?

### Reason

Why is this change needed?

### Financial Impact

Yes / No

### Compliance Impact

Yes / No

### Data Migration Required

Yes / No

### Rollback Complexity

Low / Medium / High

---

Only after proposal review can implementation begin.

---

# 4️⃣ Implementation Phase Rules

During implementation:

* Use feature branches
* Update documentation
* Leave TODO artifacts
* Maintain auditability
* Do not modify production data directly

---

# 5️⃣ Code Review Requirements

Before staging:

* Run AI_REVIEW_CHECKLIST.md
* If financial feature → enter Auditor Mode
* If security change → enter Security Reviewer Mode
* If DB change → review migrations carefully

Checklist:

* [ ] Tenant safe
* [ ] Permission safe
* [ ] Audit logging intact
* [ ] No silent balance change
* [ ] Tests written (or at least proposed)

---

# 6️⃣ Database Migration Controls

For any migration:

### 6.1 Before Running Migration

* Backup database
* Review migration file manually
* Confirm no destructive drop without confirmation

---

### 6.2 Destructive Changes Require:

* Backup confirmation
* Explicit approval
* Rollback plan

Never:

* Drop financial tables
* Drop audit logs
* Modify historical transaction structure without versioning

---

# 7️⃣ Staging Environment Rule

Changes must first deploy to:

* Local development
* Staging server (if available)

Test:

* Approval flows
* Posting flows
* Reports
* Permissions
* Tenant isolation

Only then production.

---

# 8️⃣ Deployment Procedure (Production)

Follow:

* UBUNTU_DEPLOYMENT_CHECKLIST.md

Deployment sequence:

1. Pull latest code
2. Activate virtualenv
3. Install requirements (if changed)
4. Backup DB
5. Run migrations
6. Collectstatic
7. Restart Gunicorn
8. Smoke test critical flows

---

# 9️⃣ Smoke Test Checklist (Banking Critical)

Immediately after deployment test:

* [ ] Login works
* [ ] Dashboard loads
* [ ] Loan list loads
* [ ] Deposit posting works
* [ ] Approval workflow works
* [ ] Journal posting works
* [ ] No 500 errors
* [ ] No missing static files

---

# 🔟 Rollback Strategy

Rollback depends on change type.

---

## 10.1 Code-Only Change (No Migration)

Rollback steps:

1. Checkout previous stable commit
2. Restart Gunicorn

Done.

---

## 10.2 Migration Applied (Non-Destructive)

If migration safe:

1. Revert code
2. Run reverse migration (if safe)

---

## 10.3 Financial Logic Change

If incorrect logic deployed:

1. Disable feature
2. Restore DB backup (if severe)
3. Reverse incorrect transactions manually
4. Document incident

Never silently patch financial miscalculation.

---

## 10.4 Emergency Reversal Protocol

For critical bug:

* Announce maintenance mode
* Disable posting features
* Patch minimally
* Deploy hotfix
* Post-incident review required

---

# 1️⃣1️⃣ Hotfix Policy

Hotfix allowed only when:

* Production outage
* Financial miscalculation
* Security vulnerability

Hotfix steps:

1. Minimal change
2. Focused fix
3. Immediate smoke test
4. Document change
5. Schedule full review later

---

# 1️⃣2️⃣ Post-Deployment Review

After any high/critical change:

Create:

---

## Post-Deployment Report

**Change ID:**
**Deployment Date:**
**Issues Encountered:**
**Unexpected Behavior:**
**Performance Impact:**
**Security Impact:**
**Follow-up Required:**

---

This builds institutional memory.

---

# 1️⃣3️⃣ Incident Response (Banking Grade)

If incident affects:

* GL balances
* Loan schedules
* Payment allocation
* Compliance reporting
* Cross-tenant exposure

Immediate actions:

1. Freeze affected module
2. Preserve logs
3. Identify scope
4. Restore if necessary
5. Document findings
6. Implement corrective patch
7. Audit report

---

# 1️⃣4️⃣ Versioning Strategy

Follow semantic versioning:

```
MAJOR.MINOR.PATCH
```

* MAJOR → Structural or regulatory change
* MINOR → New feature
* PATCH → Bug fix

Tag production releases.

---

# 1️⃣5️⃣ Forbidden Deployment Practices

❌ Direct DB modification in production
❌ Running migrations without backup
❌ Skipping smoke test
❌ Deploying unreviewed financial logic
❌ Deploying on Friday night
❌ Modifying permissions silently

---

# 1️⃣6️⃣ Governance Integration

This playbook works with:

* AI_DEVELOPMENT_PLANNING_GUIDE.md
* AI_REVIEW_CHECKLIST.md
* MAKER_CHECKER_MODEL_GUIDE.md
* SECURITY_HARDENING_GUIDE.md
* UBUNTU_DEPLOYMENT_CHECKLIST.md

Change management overrides speed.

---

# Final Principle

For a banking system:

> Every change is a risk event.
> Every deployment is a control event.
> Every rollback must be possible.

You are not shipping a web app.
You are maintaining a financial system.

---

You now have a fully governed:

* Development system
* Execution model
* Review framework
* Deployment control
* Security model
* RBAC model
* Maker-checker system



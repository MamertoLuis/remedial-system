# ROLE_BASED_ACCESS_CONTROL_BLUEPRINT.md

## Django RBAC for Banking Backoffice Systems (Pragmatic + Auditable)

> This blueprint defines the **role-based access control (RBAC)** model for this banking system, including:

* Roles and permissions
* Branch/tenant scoping
* Maker–checker support (optional)
* Implementation rules for Django (Groups/Permissions)
* Audit requirements

This system prioritizes **simplicity, auditability, and least privilege**.

---

## 0) Core Principles

1. **Least privilege by default**: users get only what they need.
2. **Separation of duties**: transaction entry ≠ approval/posting.
3. **Scope matters**: permissions apply within the user’s **tenant** and **branch**.
4. **Audit everything important**: approvals, postings, reversals, write-offs.
5. **No security through obscurity**: never “hide” features instead of enforcing permissions.

---

## 1) Identity & Scope Model

### 1.1 User Profile (Required)

Store scope and job function in a profile linked to Django user:

* `tenant` (required if multi-tenant)
* `branch` (required unless HO-only)
* `is_head_office` (bool)
* `position_title` (optional)
* `employee_id` (optional)

**Rule:** user tenant must match `request.tenant`. No exceptions.

### 1.2 Scope Levels

Use these scope levels consistently:

| Scope  | Meaning                               |
| ------ | ------------------------------------- |
| Tenant | All branches within a tenant          |
| Branch | Only the assigned branch              |
| Self   | Only records created/assigned to user |

---

## 2) Roles (Recommended)

These roles map to common rural bank operations. Adjust names, but keep structure.

### 2.1 Core Roles

1. **System Admin (Platform/IT)**

   * Manages users, roles, system settings
   * No financial posting authority unless explicitly granted

2. **Branch Manager**

   * Approves branch-level transactions
   * Views branch-level dashboards/reports

3. **Teller / Cashier**

   * Posts deposit transactions (maker)
   * Views deposit accounts for branch

4. **Loan Officer / Account Officer**

   * Creates loan applications, updates borrower info
   * Views assigned portfolio (branch or self scope)

5. **Credit Approver / Credit Committee**

   * Approves loans (checker)
   * Can reject/return for correction

6. **Bookkeeper / Accountant**

   * Creates draft journal entries
   * Manages COA (optional)
   * Produces financial statements

7. **GL Poster (Checker)**

   * Posts journal entries
   * Creates reversals
   * Final authority on GL posting

8. **RMU Collector**

   * Manages delinquency cases, logs actions, prints notices

9. **ROPA Custodian**

   * Manages acquired assets registry, expenses, disposition

10. **Compliance Officer**

* KYC monitoring, AML flags, audit logs, compliance reports

11. **Auditor (Read-Only)**

* Read-only access to everything in tenant scope
* Cannot post/approve/modify

---

## 3) Permission Matrix (High-Level)

> These are “capabilities.” They map to Django permissions and/or custom permissions.

### 3.1 Deposits

| Capability                       | Teller    | Branch Mgr      | Compliance | Auditor |
| -------------------------------- | --------- | --------------- | ---------- | ------- |
| View deposit accounts            | ✅         | ✅               | ✅          | ✅       |
| Create deposit txn (cash in/out) | ✅ (maker) | ✅               | ❌          | ❌       |
| Approve/review deposit txn       | ❌         | ✅               | ❌          | ❌       |
| Reverse deposit txn              | ❌         | ✅ (with reason) | ✅ (review) | ❌       |

### 3.2 Loans

| Capability                       | Loan Officer | Credit Approver | Branch Mgr       | Auditor |
| -------------------------------- | ------------ | --------------- | ---------------- | ------- |
| Create loan application          | ✅            | ❌               | ✅                | ❌       |
| Edit application before approval | ✅            | ❌               | ✅                | ❌       |
| Approve loan                     | ❌            | ✅               | ✅ (if delegated) | ❌       |
| Release loan proceeds            | ✅ (maker)    | ✅ (if policy)   | ✅                | ❌       |
| Post payment                     | ✅/Teller     | ✅               | ✅                | ❌       |
| Restructure                      | ✅ propose    | ✅ approve       | ✅ approve        | ❌       |
| Write-off / charge-off           | ❌            | ✅ (policy)      | ✅ (policy)       | ❌       |

### 3.3 GL

| Capability        | Bookkeeper  | GL Poster         | Branch Mgr   | Auditor |
| ----------------- | ----------- | ----------------- | ------------ | ------- |
| Create draft JE   | ✅           | ✅                 | ✅ (limited)  | ❌       |
| Post JE           | ❌           | ✅                 | ✅ (optional) | ❌       |
| Reverse posted JE | ❌           | ✅ (with approval) | ✅ (policy)   | ❌       |
| Manage COA        | ✅ (HO only) | ✅ (HO only)       | ❌            | ❌       |

### 3.4 RMU/ROPA/Compliance

| Capability              | RMU | ROPA | Compliance | Auditor |
| ----------------------- | --- | ---- | ---------- | ------- |
| View delinquency cases  | ✅   | ❌    | ✅          | ✅       |
| Log collection actions  | ✅   | ❌    | ✅          | ❌       |
| Generate demand letters | ✅   | ❌    | ✅          | ❌       |
| Create ROPA asset       | ❌   | ✅    | ✅          | ❌       |
| KYC due list            | ❌   | ❌    | ✅          | ✅       |
| AML match log           | ❌   | ❌    | ✅          | ✅       |
| View audit logs         | ❌   | ❌    | ✅          | ✅       |

---

## 4) Maker–Checker Model (Recommended for Posting/Approvals)

### 4.1 Where Maker–Checker Applies

Use maker–checker for:

* Loan approval
* Loan release
* GL posting
* Transaction reversals
* Write-offs
* Restructuring approval

### 4.2 Rule

Maker cannot approve their own transaction.

Implementation requirement:

* store `created_by`
* store `approved_by`
* enforce `approved_by != created_by`

---

## 5) Django Implementation Standard

### 5.1 Use Django Groups as Roles

* Each role is a Django Group
* Assign users to groups
* Groups grant permissions

### 5.2 Use Django Model Permissions + Custom Permissions

Model permissions:

* `add`, `change`, `delete`, `view`

Custom permissions (examples):

* `loans.approve_loan`
* `loans.release_loan`
* `gl.post_journalentry`
* `gl.reverse_journalentry`
* `deposits.reverse_deposittxn`
* `loans.writeoff_loan`

Define custom perms in `Meta.permissions`.

---

## 6) Enforcement Locations (Non-Negotiable)

### 6.1 Views: Use Mixins / Decorators

* CBVs: `LoginRequiredMixin`, `PermissionRequiredMixin`
* FBVs: `@login_required`, `@permission_required`

### 6.2 Services: Validate Again

Even if view checks, services must validate:

* tenant scope
* role permission
* maker-checker constraints

> Treat services as the last line of defense.

---

## 7) Branch/Tenant Filtering Rules

### 7.1 Tenant Filter (Always)

All queries must filter by `tenant=request.tenant`.

### 7.2 Branch Filter (Usually)

If user is not HO:

* restrict to `branch=user.profile.branch`

### 7.3 Assigned Portfolio (Optional)

Loan officers may see only:

* `assigned_to=user` or
* `portfolio_team=user.team`

This is enforced in selectors.

---

## 8) Admin Site RBAC

### Rule

Django admin access is restricted to:

* System Admin
* Auditor (read-only)
* Compliance (read-only + logs)

Do not give Admin access to tellers by default.

If admin is used operationally:

* restrict models visible per group
* use `has_add_permission/has_change_permission/has_delete_permission`
* log all admin changes to audit log

---

## 9) Audit Log Requirements (Banking Grade)

Audit logs must be created for:

* approvals
* postings
* reversals
* write-offs
* restructuring approvals
* user role changes
* master data changes (COA, product settings)

Audit log fields:

* tenant
* branch (if applicable)
* actor user
* action type
* object type/id
* old/new values (for sensitive changes)
* timestamp
* remarks/reason

---

## 10) UI Rules for Permission Handling

* Hide buttons the user cannot use (for UX)
* But **never rely on hidden buttons** as security
* Unauthorized attempts must return 403 and be logged

---

## 11) Implementation Checklist

Before feature is complete:

* [ ] Roles defined as groups
* [ ] Permissions mapped to groups
* [ ] Views enforce permission checks
* [ ] Services enforce permission + maker-checker
* [ ] Tenant + branch scoping enforced in selectors
* [ ] Audit logs recorded for critical actions
* [ ] Tests added:

  * permission tests
  * maker-checker test
  * tenant isolation test

---

## 12) Minimal Default Roles for MVP

If you want the smallest workable set:

1. **System Admin**
2. **Branch Manager**
3. **Teller**
4. **Loan Officer**
5. **Bookkeeper**
6. **GL Poster**
7. **Compliance**
8. **Auditor (Read-only)**

---

## 13) Common RBAC Mistakes to Avoid

❌ Give “staff” full access by default
❌ Let maker approve their own transaction
❌ Allow cross-branch visibility unintentionally
❌ Store permissions only in UI logic
❌ Allow deletion of financial records
❌ No audit trail for changes

---

## Final Principle

For banking systems:

> Every write should be attributable.
> Every approval should be separated.
> Every view should be scoped.

RBAC is not just access control — it’s a control framework.


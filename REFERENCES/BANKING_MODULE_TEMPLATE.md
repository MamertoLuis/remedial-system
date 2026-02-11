# BANKING_MODULE_TEMPLATE.md — Rural Bank System Modules (Django Standard)

> This is the canonical blueprint for building banking modules in this codebase.
> Follow `AGENTS.md`, `UI_COMPONENTS.md`, `CODE_PATTERNS.md`, and `FEATURE_PLAYBOOK.md`.

This document defines:

1. the **domain apps** to create
2. the **core entities** per app
3. the **standard workflows**
4. the **minimum screens** (templates)
5. the **reporting outputs**

---

## 0) Non-Negotiable Principles

* Source of truth is **PostgreSQL**
* All input through **Forms**
* CRUD uses **CBVs**
* Workflows use **FBVs + services**
* All queries live in **selectors**
* All business rules live in **services**
* Admin is a first-class operational tool (backoffice)

---

## 1) Domain Apps (Recommended)

Create these apps under `apps/` as the system grows:

### Foundation

* `core` — shared utilities, dashboard home, navigation, common mixins
* `accounts` — user roles, permissions, branches, user profiles

### Banking Domains

* `customers` — CIF-style customer records, KYC docs
* `deposits` — savings/current/time deposit (accounts + transactions)
* `loans` — loan accounts + schedules + postings + statuses
* `collateral` — real estate/chattel collateral registry
* `gl` — chart of accounts + journal entries + posting rules
* `rmu` — remedial management: delinquency tracking, collections, restructuring
* `ropa` — acquired assets management (ROPA pipeline + disposition)
* `reports` — financial + regulatory + management reports
* `compliance` — KYC/AMLA monitoring lists, audit logs, checklists

> Start lean: `accounts, customers, deposits, loans, gl, reports`. Add `rmu/ropa` when needed.

---

## 2) Cross-Cutting Concepts

These concepts must be consistent across apps:

### Branch / Unit

Every account (deposit/loan) belongs to a `Branch`.

### Ledger Posting

Deposit and loan transactions ultimately generate GL postings.

### Audit Trail

Every create/update/workflow action must have:

* actor (user)
* timestamp
* reference/remarks

---

## 3) Core Entities by Module

### A) accounts app

**Entities**

* `Branch`
* `Role` (optional; or use Django Groups)
* `UserProfile` (links to user + branch + position)

**Minimum Screens**

* Branch list/detail
* User list/detail (admin can handle most)

**Workflows**

* Assign branch to user
* Enable/disable user

---

### B) customers app (CIF-lite)

**Entities**

* `Customer` (individual/corporate)
* `CustomerAddress`
* `CustomerContact`
* `CustomerDocument` (KYC uploads metadata)

**Minimum Screens**

* Customer list + search
* Customer detail (tabs: profile, addresses, docs)
* Create/edit customer

**Workflows**

* Mark KYC complete
* Upload/expire documents (metadata only; storage can be filesystem later)

---

### C) deposits app

**Entities**

* `DepositProduct` (savings/current/TD; settings)
* `DepositAccount` (customer, branch, product, status)
* `DepositTxn` (date, type, amount, reference, posted_by)
* `DepositBalanceSnapshot` (optional; monthly EOM)

**Minimum Screens**

* Deposit accounts list + filter (branch, status)
* Deposit account detail: balance, txn table
* New transaction form (deposit/withdraw/adjust)

**Workflows (services)**

* `open_deposit_account()`
* `post_deposit_txn()` → validates, updates balance, generates GL draft/posting
* `close_deposit_account()` (requires zero balance)

**Key Rules**

* No direct balance edits in views/templates
* Balance changes only via transactions

---

### D) loans app

**Entities**

* `LoanProduct` (rate, term rules, fees)
* `LoanAccount` (customer, branch, principal, net proceeds, status)
* `LoanSchedule` (installments; due dates; amortization)
* `LoanTxn` (release, payment, adjustment, penalty)
* `LoanStatusHistory` (status changes)

**Minimum Screens**

* Loan list + filters (status, branch, PAR buckets)
* Loan detail (summary + schedule + txns + collateral links)
* Create loan (application → approval can be later)
* Post payment screen
* Restructure screen (workflow)

**Workflows (services)**

* `create_loan_account()` (creates schedule)
* `release_loan()` (posts release txn + GL)
* `post_payment()` (allocates payment principal/interest/penalty based on rules)
* `restructure_loan()` (generates new schedule; preserves history)
* `classify_loan()` (Current/EM/Substandard/Doubtful/Loss)
* `place_on_non_accrual()` / `return_to_accrual()`

**Key Rules**

* Payment allocation belongs in services, not templates
* Schedule regeneration must be deterministic and auditable

---

### E) collateral app

**Entities**

* `CollateralItem` (type: real estate / chattel)
* `CollateralValuation` (date, appraised value, appraiser)
* `CollateralLien` (lien details / registry ref)
* Link table:

  * `LoanCollateral` (loan ↔ collateral)

**Minimum Screens**

* Collateral registry list
* Collateral detail (valuation history, linked loans)

**Workflows**

* Attach/detach collateral to loan (with history log)

---

### F) gl app (minimum viable GL)

**Entities**

* `GLAccount` (code, title, normal_balance, parent)
* `JournalEntry` (date, reference, memo, status: Draft/Posted)
* `JournalLine` (account, debit, credit)

**Minimum Screens**

* Chart of accounts list/detail
* Journal entry list + filter (date range, status)
* Journal entry detail (lines, totals)
* Create journal entry (simple)

**Workflows (services)**

* `create_journal_entry()`
* `add_line()`
* `post_journal_entry()` (locks entry; creates audit trail)

**Key Rules**

* Posting is a workflow action; once posted, it’s immutable (except reversal)

---

### G) rmu app (Remedial Management)

**Entities**

* `DelinquencyCase` (loan, bucket, assigned_to, status)
* `CollectionAction` (call, visit, demand letter served, agreement)
* `PromiseToPay` (date, amount, status)
* `RestructuringProposal` (terms summary, approval fields)

**Minimum Screens**

* RMU dashboard (PAR buckets, top delinquent)
* Case list by bucket/collector
* Case detail timeline (actions + PTP + notes)

**Workflows**

* Assign case to collector
* Log collection action (form)
* Generate demand letter (template-only, print)
* Recommend restructure (proposal workflow)

---

### H) ropa app (Acquired Assets)

**Entities**

* `RopaAsset` (source loan/case, acquisition date, cost, status)
* `RopaExpense` (taxes, maintenance)
* `RopaDisposition` (sale, buyer, proceeds, date)

**Minimum Screens**

* ROPA registry list (status: held/for sale/sold)
* ROPA detail (expenses timeline + disposition)

**Workflows**

* Move asset into ROPA (from foreclosure)
* Record expense
* Record sale and proceeds

---

### I) reports app

Reports should be selector-driven, read-only.

**Report Categories**

* Portfolio Quality: PAR, past due %, aging
* Collections: monthly collection vs target
* Deposits: growth, dormancy, large withdrawals list
* GL: trial balance, income statement, balance sheet
* Compliance: KYC due/expired, AML watchlist hits (basic)

**Minimum Screens**

* Report index page
* Each report page:

  * filters (branch, date range)
  * results table
  * export CSV (optional)

---

### J) compliance app

**Entities**

* `KycChecklistItem` / `KycStatus`
* `AmlaWatchlistName` (optional manual list)
* `AmlaMatchLog`
* `AuditLog` (generic, cross-app)

**Minimum Screens**

* KYC due list
* AML matches log
* Audit log view (filter by user/date/module)

---

## 4) Standard Screens Per Module

Every module should have (minimum):

* List page (`<entity>_list.html`)
* Detail page (`<entity>_detail.html`)
* Create/Edit form page (`<entity>_form.html`)
* HTMX partials for tables (optional but recommended)

All pages must use the standard page pattern:

* Title
* Action bar
* Card container
* Table/form inside card

---

## 5) Standard Workflow Actions

Use these consistent workflow endpoints (FBV + services):

* Approve / Reject
* Post / Unpost (usually only post; unpost = reversal)
* Close / Reopen (if allowed)
* Restructure
* Assign (RMU)
* Serve notice (RMU)
* Move to ROPA (ROPA)

**Rule:** workflow actions must write to:

* status history table OR audit log table

---

## 6) Status & Classification Standards

### Loan status (example)

* Applied
* Approved
* Released
* Active
* Past Due
* Non-Accrual
* Restructured
* Closed
* Written Off

### Delinquency buckets

* 1–30
* 31–90
* 91–180
* 181–365
* 366+

Store bucket as a computed field updated by service job or on transaction posting.

---

## 7) Posting & Accounting Strategy (Practical)

Start with this pragmatic approach:

1. Deposit/loan services produce **JournalEntry (Draft)**
2. GL module posts JE (approval step)
3. Reports read posted journal entries for financial statements

This avoids premature complexity while keeping auditability.

---

## 8) “Minimum Viable Banking System” Build Order

Recommended sequence:

1. `accounts` (Branch + users)
2. `customers` (CIF-lite)
3. `gl` (COA + basic JE posting)
4. `deposits` (accounts + txns + GL draft)
5. `loans` (accounts + schedule + payments + GL draft)
6. `reports` (portfolio + trial balance)
7. `rmu` (delinquency + collection logs)
8. `ropa` (asset registry)

---

## 9) Definition of Done for Any Banking Module

A module is “done” only if:

* [ ] CRUD exists (list/detail/create/edit)
* [ ] Admin configured (search, filter)
* [ ] Workflows use services
* [ ] Reports exist for key output
* [ ] Audit trail or status history exists
* [ ] UI follows UI_COMPONENTS.md

---

## 10) What the AI Must NOT Do

* Don’t invent accounting rules inside templates
* Don’t update balances directly
* Don’t add DRF unless explicitly required
* Don’t add Celery/Redis early
* Don’t build deep nested URLs
* Don’t bypass forms

---

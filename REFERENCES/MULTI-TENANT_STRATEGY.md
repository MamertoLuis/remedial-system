# MULTI-TENANT_STRATEGY.md — Django Multi-Tenant Architecture (Pragmatic)

> This project may support multiple tenants (e.g., multiple rural banks, cooperatives, branches-as-tenants, or business units) within one deployment.
>
> This document defines the **approved multi-tenant strategy**, the **data isolation model**, and the **coding rules** to prevent tenant leakage.

This is written for both developers and AI agents. Follow strictly.

---

## 0) Recommended Tenant Model (Default)

### ✅ Default: **Single Database + Shared Schema + Tenant FK**

We use **one PostgreSQL database** and a shared schema.
Every tenant-owned row includes a required `tenant_id` foreign key.

**Why this is the default**

* Simple to operate for small teams
* Easy backups
* Easy reporting and cross-tenant admin (if allowed)
* Works with standard Django ORM

---

## 1) Tenancy Definitions

### Tenant

A “tenant” is the top-level customer entity.

Examples:

* A rural bank (Bank A, Bank B)
* A cooperative
* A microfinance institution
* A business unit (if SaaS)

### Branch vs Tenant

A **branch is not a tenant** unless explicitly configured.
Branches belong to a tenant:

```
Tenant → Branch → Accounts/Loans/Deposits
```

---

## 2) Core Tenancy Tables

### `tenancy` app (or `core` if you prefer)

#### `Tenant`

* name
* code (unique)
* status (active/suspended)
* created_at, updated_at

#### `TenantDomain` (optional)

* tenant
* domain (e.g., bankA.example.com)
* is_primary

#### `TenantSetting` (optional)

* tenant
* key, value (JSON)

---

## 3) Data Ownership Rule (Non-Negotiable)

### Tenant-owned models MUST include:

```python
tenant = models.ForeignKey("tenancy.Tenant", on_delete=models.PROTECT)
```

This applies to:

* customers
* deposits
* loans
* collateral
* GL journals
* RMU cases
* ROPA assets
* reports metadata

Only “global” reference tables may be tenantless (rare).

---

## 4) Where Tenant Comes From

### Approved tenant resolution methods (choose one)

#### Option A — Subdomain (Recommended for SaaS)

* `tenantcode.example.com`
* Middleware resolves tenant by host

#### Option B — URL prefix (Simple internal hosting)

* `/t/<tenantcode>/loans/`
* Middleware resolves tenant from URL

#### Option C — Single-tenant deployments (No tenancy needed)

* If each bank has its own install, tenancy can be disabled

**Default assumption in this repo:** Option A or B.

---

## 5) Tenant Resolution Middleware (Required)

Tenant must be resolved early and stored on request:

```
request.tenant
```

If tenant cannot be resolved:

* return 404 (not found) or
* show “Invalid tenant” page (never default to another tenant)

---

## 6) Tenant Isolation Enforcement (Hard Rule)

We enforce tenant isolation in three layers:

### Layer 1: Middleware sets request.tenant

No request proceeds without a tenant.

### Layer 2: Query filtering (Selectors only)

All tenant-owned queries must filter by tenant.

✅ Good:

```python
def active_loans(tenant):
    return Loan.objects.filter(tenant=tenant, status=Loan.Status.ACTIVE)
```

❌ Bad:

```python
Loan.objects.filter(status="A")  # tenant leak risk
```

### Layer 3: Service validation (Workflow safety)

All services must validate tenant ownership before actions.

---

## 7) The “Tenant-Aware Selector” Rule

**All reads go through selectors** and selectors accept `tenant`:

```python
# apps/loans/selectors.py
def loan_by_id(tenant, pk):
    return Loan.objects.get(tenant=tenant, pk=pk)
```

Views never call ORM directly (except trivial CBV CRUD which must also be tenant-scoped).

---

## 8) Tenant-Scoped CBVs (CRUD)

For CBVs, always override `get_queryset()`:

```python
class LoanListView(ListView):
    model = Loan

    def get_queryset(self):
        return Loan.objects.filter(tenant=self.request.tenant)
```

For CreateView, set tenant in `form_valid()`:

```python
def form_valid(self, form):
    obj = form.save(commit=False)
    obj.tenant = self.request.tenant
    obj.save()
    return super().form_valid(form)
```

---

## 9) Tenant-Aware Forms

Forms must **never allow tenant selection** in user-facing forms.

Tenant is assigned in view/service, not user input.

---

## 10) Permissions & Roles (Multi-tenant)

### Rule

Users belong to a tenant and may have branch assignment.

Recommended:

* `UserProfile.tenant`
* `UserProfile.branch` (optional)

Authorization checks:

* user tenant must match request.tenant
* optional branch filtering for non-HO users

---

## 11) Reporting: Cross-Tenant vs Tenant-Only

Reports default to tenant-only.

Cross-tenant reporting is restricted to “Platform Admin” role and must use explicit code paths.

---

## 12) Migration Strategy (Single Tenant → Multi Tenant)

If you start single-tenant first, you can migrate later:

1. Add `Tenant` model
2. Add `tenant` FK to tenant-owned models (nullable temporarily)
3. Create default tenant
4. Backfill tenant_id for all rows
5. Make tenant FK non-null
6. Add middleware enforcement
7. Update selectors/services

---

## 13) Operational Considerations

### Backups

Single DB backups cover all tenants.

### Exports

All exports must be tenant-scoped unless platform admin.

### Audit Logs

Audit logs should store:

* tenant
* user
* action
* object id/type
* timestamp

---

## 14) Optional: Stronger Isolation (When Needed)

### Option 1 — Separate schema per tenant

Better isolation, more complexity.

### Option 2 — Separate database per tenant

Highest isolation, highest operational cost.

**This project does NOT use these unless explicitly instructed.**

---

## 15) Testing Rules (Mandatory)

Tests must include tenant isolation tests:

* cannot access objects from another tenant
* services reject cross-tenant operations
* CBV querysets are tenant filtered

---

## 16) AI Must Never Do

❌ Query tenant-owned models without filtering by tenant
❌ Allow user input to choose tenant
❌ Default to “first tenant” if tenant not resolved
❌ Build cross-tenant reporting without explicit permission layer

---

## 17) Definition of Done (Multi Tenant Feature)

A multi-tenant feature is done only if:

* [ ] tenant_id exists on all tenant-owned models
* [ ] middleware sets request.tenant
* [ ] selectors filter by tenant
* [ ] CBVs override get_queryset
* [ ] services validate tenant ownership
* [ ] tests cover tenant isolation


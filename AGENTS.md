# AGENTS.md — Django Development Constitution (Server-Rendered + Controlled)

This repository is built for **Django server-rendered development** with **HTMX**, strong **banking controls**, and **AI-governed engineering**.

Any AI agent or developer MUST follow this document as the highest authority.

---

## 0) Non-Negotiable Architecture

### We build with:
- Django Templates (server-rendered)
- HTMX for interactivity (partial updates)
- Django ORM + Forms + Admin
- CBVs for CRUD, FBVs for workflows
- Services/Selectors pattern
- Whitenoise for static files
- PostgreSQL as database

### We avoid unless explicitly approved:
- SPA frameworks (React/Vue)
- DRF as default (APIs only when necessary)
- Celery/Redis early
- Heavy frontend build pipelines

---

## 1) Primary Patterns (Must Follow)

### 1.1 Services & Selectors (Mandatory)
- **selectors.py**: all DB reads/queries
- **services.py**: all business rules, validations, state transitions
- Views orchestrate only

### 1.2 Views
- CRUD pages → **CBVs**
- Workflows/actions/HTMX endpoints → **FBVs**
- Views must remain thin and predictable

### 1.3 Forms
- ALL input must go through Django Forms / ModelForms
- Never parse `request.POST` manually
- No business logic in templates

### 1.4 URLs
- Resource-oriented nouns (not verbs)
- Flat structure, consistent naming
- No hardcoded URLs in templates

### 1.5 Admin
- Register models early
- Use admin for internal operations where appropriate

---

## 2) AI Execution Model (How the AI Must Behave)

AI must operate in explicit modes (do not mix roles silently):

- **Planner Mode**: clarify objective, classify feature, define scope, risks
- **Architect Mode**: validate app placement, multi-tenant, RBAC, maker-checker
- **Implementer Mode**: write code using canonical patterns
- **Reviewer Mode**: run review checklist before declaring completion
- **Auditor Mode**: required for financial logic, approvals, postings, reversals
- **Security Reviewer Mode**: required for auth/permissions/endpoints
- **Performance Analyst Mode**: required for reports/dashboards/large datasets
- **Change Manager Mode**: required for deploy/rollback/release procedures

Reference: **AI_EXECUTION_MODELS.md**

---

## 3) Mandatory Development Artifacts (No Silent Work)

For every non-trivial task, the agent MUST leave artifacts:

### 3.1 Required outputs (choose one location)
- A feature note file in `docs/dev/FEATURE_<slug>.md`, OR
- Append to `DEV_NOTES.md`, OR
- Add to module-specific notes

### 3.2 Artifact content (required sections)
- **Feature Plan**
- **TODO list** (checkboxes)
- **Completed tasks**
- **Open questions**
- **Risk notes** (security/financial/tenant/performance)

Reference: **AI_PROCESS_DISCIPLINE.md** (or equivalent section if embedded elsewhere)

---

## 4) Mandatory Pause / Clarification Rules

The agent MUST pause and ask structured questions BEFORE coding if any of these apply:

### 4.1 Business ambiguity
- unclear accounting treatment
- unclear interest/payment allocation rules
- unclear approval authority
- undefined workflow steps/status transitions

### 4.2 High-risk / critical changes
- GL posting logic
- payment allocation logic
- write-offs / charge-offs
- reversals and corrections
- compliance/regulatory reporting logic
- cross-tenant reporting or data access

### 4.3 Architectural ambiguity
- whether to create a new app
- whether maker–checker applies
- tenant vs branch scoping

When pausing, ask **specific questions** (numbered) and propose safe defaults if needed.

---

## 5) Document System: Categories, When to Use, and Precedence

### 5.1 Authority Hierarchy (Conflict Resolution)
If documents conflict, precedence is:

1. **AGENTS.md** (this file)
1.1 **GEMINI.md** (supplement)
2. **MULTI-TENANT_STRATEGY.md**
3. **SECURITY_HARDENING_GUIDE.md**
4. **ROLE_BASED_ACCESS_CONTROL_BLUEPRINT.md**
5. **MAKER_CHECKER_MODEL_GUIDE.md**
6. **AI_DEVELOPMENT_PLANNING_GUIDE.md**
7. **AI_REVIEW_CHECKLIST.md**
8. **FEATURE_PLAYBOOK.md**
9. **CODE_PATTERNS.md**
10. **UI_COMPONENTS.md**
11. **BANKING_MODULE_TEMPLATE.md**
12. **PERFORMANCE_OPTIMIZATION_GUIDE.md**
13. **STATIC_FILES.md**
14. **PROJECT_BOOTSTRAP.md**
15. **UBUNTU_DEPLOYMENT_CHECKLIST.md**
16. **CHANGE_MANAGEMENT_PLAYBOOK.md** (applies specifically to deployment/release process)

If still unclear: pause and ask.

---

### 5.2 Category Index + Usage Rules

#### A) Architecture & Governance (Always Applicable)
- **AI_DEVELOPMENT_PLANNING_GUIDE.md**
  - Use when: any new feature request, scope definition, risk scoring
- **FEATURE_PLAYBOOK.md**
  - Use when: selecting CRUD vs workflow vs report patterns
- **CODE_PATTERNS.md**
  - Use when: writing models/services/selectors/views/forms
- **UI_COMPONENTS.md**
  - Use when: creating templates/partials and page layout
- **AI_REVIEW_CHECKLIST.md**
  - Use when: before marking work “done” (mandatory)
- **CHANGE_MANAGEMENT_PLAYBOOK.md**
  - Use when: preparing a release, migration, rollback, hotfix

#### B) Banking Domain Blueprint
- **BANKING_MODULE_TEMPLATE.md**
  - Use when: adding modules (loans/deposits/gl/rmu/ropa/reports), planning MVP roadmap

#### C) Control Framework (Permissions + Approvals)
- **ROLE_BASED_ACCESS_CONTROL_BLUEPRINT.md**
  - Use when: adding endpoints, role restrictions, admin access rules, dashboards by role
- **MAKER_CHECKER_MODEL_GUIDE.md**
  - Use when: approvals/postings/reversals/write-offs/restructuring/financial mutation

#### D) Multi-Tenancy (If enabled)
- **MULTI-TENANT_STRATEGY.md**
  - Use when: adding models, writing selectors, CBV querysets, reports, exports, audit logs

#### E) Security & Operations
- **SECURITY_HARDENING_GUIDE.md**
  - Use when: auth changes, permissions, sensitive endpoints, production readiness
- **UBUNTU_DEPLOYMENT_CHECKLIST.md**
  - Use when: deploying on Ubuntu, configuring Gunicorn/Postgres/Firewall
- **PROJECT_BOOTSTRAP.md**
  - Use when: starting a new environment or re-initializing project structure
- **STATIC_FILES.md**
  - Use when: adding/modifying CSS/JS/images and production static handling
- **PERFORMANCE_OPTIMIZATION_GUIDE.md**
  - Use when: reports/dashboards, slow pages, large tables, query tuning

---

## 6) “Consultation Matrix” (What to Read Before Doing X)

| Task | Must Consult |
|---|---|
| New feature planning | AI_DEVELOPMENT_PLANNING_GUIDE.md, FEATURE_PLAYBOOK.md |
| Create/modify models | CODE_PATTERNS.md (+ MULTI-TENANT_STRATEGY.md if multi-tenant) |
| Add any workflow endpoint | FEATURE_PLAYBOOK.md, RBAC blueprint |
| Financial mutation (posting/allocation/reversal) | MAKER_CHECKER_MODEL_GUIDE.md, RBAC blueprint, AI_REVIEW_CHECKLIST.md |
| Add report/dashboard | PERFORMANCE_OPTIMIZATION_GUIDE.md, UI_COMPONENTS.md |
| Modify permissions/roles | ROLE_BASED_ACCESS_CONTROL_BLUEPRINT.md |
| Add templates/partials | UI_COMPONENTS.md |
| Add static assets | STATIC_FILES.md |
| Pre-deploy or release | UBUNTU_DEPLOYMENT_CHECKLIST.md, SECURITY_HARDENING_GUIDE.md, CHANGE_MANAGEMENT_PLAYBOOK.md |

---

## 7) Definition of Done (Must Pass)

Before declaring completion, the agent MUST:

1. Run **AI_REVIEW_CHECKLIST.md**
2. Update development artifacts (plan/TODO/completed/open questions)
3. Confirm tenant safety (if multi-tenant)
4. Confirm permissions + audit logs for sensitive actions
5. Confirm pagination for lists and filters for reports
6. Confirm no business logic in views/templates

---

## 8) Coding Standards (Short Rules)

- No “clever” abstractions; prefer explicit code
- No duplication across apps; share in `core` only when truly cross-cutting
- No deletion of financial records; prefer reversal/versioning/status changes
- Posted/approved items become immutable (corrections via reversal or new version)
- All risky actions must record: who/when/why (audit log)

---

## 9) Optional: Repository Conventions (Recommended)

### 9.1 Docs structure
- `docs/` contains reference standards
- `docs/dev/` contains feature notes and decision logs
- `docs/runbooks/` contains deployment and ops notes

### 9.2 Feature note naming
`docs/dev/FEATURE_<yyyymmdd>_<short_slug>.md`

---

## 10) Final Instruction to AI Agents

Do not jump to code.

Always:
1) Plan → 2) Architect review → 3) Implement → 4) Review → 5) Document

If a feature impacts money, approvals, or posting:
- Engage Auditor Mode
- Enforce maker-checker + RBAC
- Log everything

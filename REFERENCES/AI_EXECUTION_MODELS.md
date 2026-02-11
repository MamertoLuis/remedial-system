# AI_EXECUTION_MODELS.md

## Structured AI Role Framework for Controlled Software Development

---

# 0️⃣ Purpose

This document defines the **execution modes** AI agents must operate under when working on this banking system.

Instead of behaving as a single monolithic “assistant,” AI must assume distinct roles:

* Planner
* Architect
* Implementer
* Reviewer
* Auditor
* Performance Analyst
* Security Reviewer

Each role has different responsibilities and constraints.

AI must not mix roles without explicitly transitioning.

---

# 1️⃣ Core Execution Philosophy

For this banking system:

> AI is not a coder.
> AI is a controlled software organization.

Each task must pass through structured roles.

---

# 2️⃣ AI Role Definitions

---

## 🧠 1. Planner Mode

### Purpose

Convert business request into structured feature plan.

### Responsibilities

* Clarify objective
* Identify feature type
* Map domain impact
* Identify risk level
* Produce structured plan (see AI_DEVELOPMENT_PLANNING_GUIDE.md)

### Constraints

* No code generation
* No premature optimization
* Must ask clarifying questions if ambiguous

### When Activated

* New feature request
* Architectural change
* Financial logic modification
* Compliance-impacting change

---

## 🏗 2. Architect Mode

### Purpose

Ensure architectural alignment.

### Responsibilities

* Validate app placement
* Validate multi-tenant impact
* Validate RBAC implications
* Validate maker-checker need
* Validate model integrity

### Must Consult

* AGENTS.md
* MULTI-TENANT_STRATEGY.md
* ROLE_BASED_ACCESS_CONTROL_BLUEPRINT.md
* MAKER_CHECKER_MODEL_GUIDE.md

### Constraints

* Cannot invent new frameworks
* Must minimize scope

### When Activated

* New module
* Cross-domain feature
* Schema changes
* Workflow addition

---

## 🧑‍💻 3. Implementer Mode

### Purpose

Generate code following approved plan.

### Responsibilities

* Follow CODE_PATTERNS.md
* Follow UI_COMPONENTS.md
* Keep views thin
* Use services
* Add indexes where required
* Leave TODO artifacts

### Constraints

* No structural changes without plan
* No direct balance mutation
* No bypassing services

### When Activated

* After plan approval

---

## 🔍 4. Reviewer Mode

### Purpose

Self-audit generated code.

### Responsibilities

Run:

* AI_REVIEW_CHECKLIST.md

Validate:

* Security
* Tenant isolation
* Financial integrity
* Permission enforcement
* Performance
* Audit logging

### Constraints

* Must reject own output if failing checklist
* Must flag high-risk changes

### When Activated

* After implementation
* Before completion declaration

---

## 🏦 5. Auditor Mode

### Purpose

Evaluate compliance & control integrity.

### Responsibilities

* Check maker-checker enforcement
* Verify audit trail completeness
* Validate separation of duties
* Ensure no silent data mutation

### Trigger Conditions

* Financial feature
* GL change
* Loan allocation logic
* Reversal logic
* Write-off logic

---

## ⚡ 6. Performance Analyst Mode

### Purpose

Evaluate system performance impact.

### Responsibilities

* Check query efficiency
* Validate pagination
* Review indexes
* Ensure reports require filters
* Evaluate database load

### Must Consult

* PERFORMANCE_OPTIMIZATION_GUIDE.md

### Trigger Conditions

* Large dataset feature
* Report creation
* Dashboard aggregation
* N+1 suspicion

---

## 🔐 7. Security Reviewer Mode

### Purpose

Validate security controls.

### Responsibilities

* Verify permission enforcement
* Check CSRF usage
* Validate no secrets exposed
* Ensure no tenant leak
* Review logging of sensitive actions

### Must Consult

* SECURITY_HARDENING_GUIDE.md
* RBAC Blueprint

### Trigger Conditions

* Authentication change
* Authorization change
* New endpoint
* Deployment prep

---

# 3️⃣ Execution Flow Model

For standard feature:

```
Planner → Architect → Implementer → Reviewer
```

For financial workflow:

```
Planner → Architect → Implementer → Reviewer → Auditor
```

For performance-heavy feature:

```
Planner → Architect → Implementer → Reviewer → Performance Analyst
```

For deployment:

```
Architect → Security Reviewer → Deployment Checklist
```

---

# 4️⃣ Mode Transition Rule

AI must explicitly declare:

```
Switching to Planner Mode.
```

```
Switching to Implementer Mode.
```

This prevents mixed reasoning.

---

# 5️⃣ Forbidden Behavior

AI must never:

❌ Skip planning
❌ Mix planning and implementation without clarity
❌ Approve its own risky financial logic
❌ Modify GL logic without Auditor Mode
❌ Add dependency without Architect review
❌ Implement cross-tenant logic without Multi-Tenant review

---

# 6️⃣ High-Risk Escalation Protocol

If feature involves:

* GL posting modification
* Payment allocation change
* Loan provisioning logic
* Regulatory reporting
* Data deletion
* Cross-tenant reporting

AI must:

1. Enter Planner Mode
2. Enter Architect Mode
3. Explicitly state risk
4. Require confirmation
5. Only then implement

---

# 7️⃣ AI Self-Governance Declaration

Before completion, AI must declare:

```
Execution Modes Applied:
- Planner: ✔
- Architect: ✔
- Implementer: ✔
- Reviewer: ✔
- Auditor: ✔ (if applicable)
- Performance Analyst: ✔ (if applicable)
- Security Reviewer: ✔ (if applicable)

All relevant governance documents consulted.
No architectural violations detected.
```

---

# 8️⃣ Multi-Agent Simulation (Optional Advanced)

For critical features, AI may simulate:

* Planner output
* Architect critique
* Implementer draft
* Reviewer critique
* Auditor critique

Before finalizing.

This increases safety for financial systems.

---

# 9️⃣ Execution Model Summary

| Mode        | Focus                         |
| ----------- | ----------------------------- |
| Planner     | What are we building?         |
| Architect   | Where and how should it live? |
| Implementer | Write compliant code          |
| Reviewer    | Validate correctness          |
| Auditor     | Validate financial control    |
| Performance | Validate scalability          |
| Security    | Validate protection           |

---

# 🔟 Final Philosophy

For this banking system:

> Every feature must survive
> Planning scrutiny
> Architectural scrutiny
> Control scrutiny
> Performance scrutiny
> Security scrutiny

AI is not fast — AI is controlled.

---

You now have:

* Governance framework
* Review framework
* Execution model framework



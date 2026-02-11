
# USER_PRD_TEMPLATE.md

## Product Requirements Document (For AI-Governed Django System)

---

# 0️⃣ Document Purpose

This PRD defines:

* What problem we are solving
* Who it is for
* What must happen
* What must NOT happen
* Risk & control implications

This document is written by the **user/business owner**, not the AI.

The AI will use this PRD as input for:

* Planner Mode
* Architect Mode
* Risk Classification
* Implementation

---

# 1️⃣ Basic Information

**Feature Name:**
**Requested By:**
**Date:**
**Target Release:**
**Priority:** (Low / Medium / High / Critical)

---

# 2️⃣ Business Objective

Describe the business goal.

* What operational problem does this solve?
* What inefficiency does this remove?
* What regulatory requirement does this address?

---

# 3️⃣ Background Context

Provide context:

* Current workflow (how it works today)
* Pain points
* Manual steps involved
* Risks in current process

---

# 4️⃣ Users & Roles Impacted

Who will use this feature?

| Role            | Action |
| --------------- | ------ |
| Teller          |        |
| Loan Officer    |        |
| Branch Manager  |        |
| Credit Approver |        |
| Bookkeeper      |        |
| GL Poster       |        |
| Compliance      |        |
| Auditor         |        |

Specify:

* Is this branch-specific?
* Is this Head Office only?
* Is this multi-tenant sensitive?

---

# 5️⃣ Functional Requirements

Describe what the system must do.

Use numbered requirements.

Example:

1. The system must allow Loan Officers to create a restructuring proposal.
2. The proposal must require approval by Branch Manager.
3. Maker cannot approve own proposal.
4. Approved proposal must generate new amortization schedule.
5. Old schedule must remain archived.

Be specific.

---

# 6️⃣ Workflow Requirements

If applicable, describe lifecycle:

Example:

Draft → Submitted → Approved → Executed → Closed

For each transition, specify:

* Who can trigger it?
* Is maker-checker required?
* Is rejection allowed?
* Is resubmission allowed?

---

# 7️⃣ Financial Impact

Does this feature affect:

* Loan principal?
* Interest computation?
* Penalties?
* GL posting?
* Deposit balances?
* Write-offs?
* Provisions?

If yes:

* Describe expected accounting treatment.
* Identify affected GL accounts (if known).
* Specify if backdating allowed.

---

# 8️⃣ Permission & Control Requirements

* Who can view?
* Who can create?
* Who can approve?
* Who can execute/post?
* Who can reverse?
* Who can delete (if any)?

Is maker–checker required? (Yes / No)

Is audit logging required? (Yes / No — default Yes for financial)

---

# 9️⃣ Reporting Requirements

* Should this appear in dashboard?
* Should this affect PAR?
* Should this affect financial statements?
* Should this have export (CSV/PDF)?

Are filters required (date, branch, tenant)?

---

# 🔟 Data Requirements

Specify:

* New data fields required
* Mandatory vs optional fields
* Validation rules
* File uploads needed?

---

# 1️⃣1️⃣ Compliance & Regulatory Impact

Does this affect:

* BSP reporting?
* AMLA monitoring?
* KYC tracking?
* Loan classification?
* Provisioning rules?

If yes, describe.

---

# 1️⃣2️⃣ Performance Expectations

* Estimated number of records?
* Expected daily volume?
* Should be real-time?
* Acceptable page load time?

---

# 1️⃣3️⃣ Security Considerations

* Sensitive data involved?
* Requires encryption?
* Requires restricted visibility?
* Should be logged for audit?

---

# 1️⃣4️⃣ Edge Cases

Describe potential edge cases:

* What if already approved?
* What if reversed?
* What if partially executed?
* What if user loses permission mid-process?

---

# 1️⃣5️⃣ Success Criteria

How do we know this feature works?

* Clear measurable outcome
* Reduced manual steps?
* Reduced processing time?
* Audit compliance achieved?

---

# 1️⃣6️⃣ Non-Goals

Clearly state what this feature will NOT do.

Example:

* Does not automatically adjust provisioning
* Does not modify historical GL entries
* Does not allow deletion of approved records

---

# 1️⃣7️⃣ Open Questions

List unresolved items for clarification.

---

# 1️⃣8️⃣ Risk Assessment (Business View)

Rate risk:

* Low
* Medium
* High
* Critical

Describe why.

---

# 1️⃣9️⃣ Change Management Considerations

* Data migration required?
* Training required?
* Backward compatibility needed?
* Rollback complexity?

---

# 2️⃣0️⃣ Approval Sign-Off

**Business Owner:**
**Risk Officer (if applicable):**
**IT/Architect:**

---

# 📌 How AI Uses This PRD

When PRD is submitted, AI must:

1. Enter Planner Mode
2. Extract:

   * Feature type
   * Domain app
   * Risk level
3. Identify:

   * Multi-tenant impact
   * RBAC implications
   * Maker-checker requirement
   * Financial mutation
4. Produce structured implementation plan
5. Pause for clarification if ambiguity exists

---

# Final Principle

A good PRD prevents:

* Ambiguous financial logic
* Silent control violations
* Role confusion
* Unintended accounting effects

For a banking system:

> Clarity before coding.

---



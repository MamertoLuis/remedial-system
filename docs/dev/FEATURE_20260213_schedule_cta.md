# Feature Plan: Surface compromise schedule actions

## 📌 Feature Plan

**Feature Name:** Schedule item access from compromise detail
**Type:** UI enhancement + data join
**Domain App:** remedial
**Risk Level:** Low

### Scope
- Teach the compromise detail page to show existing schedule items with statuses and expose the “Create Schedule Item” workflow via a direct CTA.  
- Prefetch schedule items (and their payments) when loading the compromise so the template can render without extra queries.
- Keep the page layout aligned with the existing card-focused design.

### Models Impact
- None; `CompromiseScheduleItem` already exists but we will prefetch it in the detail view.

### Services Impact
- None.

### Permission Impact
- None; reuse the existing tenant-filtered detail view.

### Audit Impact
- None.

### Performance Impact
- Prefetching `schedule_items` and `schedule_items__payments` avoids additional per-item queries, aligning with existing pagination/list patterns.

## TODO – Schedule CTA rollout
- [x] Update `CompromiseDetailView.get_queryset()` to prefetch schedule items and payments for the loaded `CompromiseAgreement`.
- [x] Extend `templates/remedial/compromise_detail.html` with a schedule card that lists `schedule_items` and their key fields plus a “Create Schedule Item” button linking to `scheduleitem-create?compromise_id=...`.
- [x] Ensure the template renders schedule rows even when none exist (show a placeholder state).

## ✅ Completed
- Prefetched `schedule_items__payments` in `CompromiseDetailView.get_queryset()` to avoid per-row queries when the card renders.
- Added a payment schedule card with a “Create Schedule Item” CTA on `templates/remedial/compromise_detail.html`, including a table of existing installments and a friendly empty state.
- Created `templates/remedial/scheduleitem_list.html` so `/remedial/schedule-items/` renders its own list table with links to view/edit, complying with the CTA and list-route contract.
- Added `templates/remedial/scheduleitem_detail.html` that surfaces each installment’s core data, reminder history, and applied payments along with quick edit/record-payment actions.
- Ensured `CompromisePaymentCreateView` wires the `compromise_id` query param into the saved record so payments are always linked to the parent compromise and avoid the NOT NULL error.
- Added `templates/remedial/compromisepayment_list.html` so `/remedial/payments/` renders a proper table/pagination view aligned with the rest of the UI.
- Added `templates/remedial/compromisepayment_detail.html` so `/remedial/payments/<pk>/` shows detailed metadata, links back to the compromise, and exposes the edit action.

## ❓ Open Questions
- None.

## ⚠ Risk Notes
- Low: only presentation logic changes plus safe prefetching; tenant isolation unaffected.

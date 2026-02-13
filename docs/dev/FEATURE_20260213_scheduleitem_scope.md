# Feature Plan: Scope schedule items list by compromise

## 📌 Feature Plan
**Feature Name:** Scope schedule items list to parent compromise
**Type:** Bug fix / UX alignment
**Domain App:** remedial
**Risk Level:** Low

### Scope
- Teach `/remedial/schedule-items/` to require a `compromise_id` context and only render schedule items belonging to that compromise, mirroring the existing CTA contract from the compromise detail card.
- Surface the parent compromise metadata (agreement number, account label) in the list card so users understand the scope of the page.
- Keep the create/edit/detail workflows aware of the current compromise so redirects and breadcrumbs continue to come back to the scoped list.

### Models Impact
- None: no new models or schema changes required.

### Services Impact
- None: no new business services invoked.

### Permission Impact
- None: tenant isolation is already enforced via existing tenant filters.

### Audit Impact
- None: no new actions are recorded or modified.

### Performance Impact
- Neutral: list still paginated, only adds a tiny extra lookup for the parent compromise.

## TODO – Schedule item list scope
- [x] Update `CompromiseScheduleItemListView` to load the parent compromise via `?compromise_id=` and limit the queryset to that foreign key.
- [x] Surface the parent compromise/account info in `scheduleitem_list.html` and pass the query param along to the CTA/breadcrumb links.
- [x] Keep create/update success redirects keyed to the parent compromise so the user lands back on the scoped list.
- [x] Update any related breadcrumb links (detail view) that pointed to the unscoped list.

## ✅ Completed
- Scoped the schedule item list view to require `compromise_id`, added the parent compromise/account context, and raised a `404` when the parameter is missing.
- Taught the compromise card, list template, and breadcrumb navigation to carry the `compromise_id` parameter so the view stays scoped during create/edit/detail flows.
- Routed the create/update success URLs back to the scoped list so users land on the same compromise’s installments after saving changes.

## ❓ Open Questions
- None.

## ⚠ Risk Notes
- Low: only presentation-level filtering + navigation updates; tenant guarding already in place.

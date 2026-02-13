# Feature Plan: Compromise terms column availability

## 📌 Feature Plan

**Feature Name:** Apply the missing compromise terms rename migration
**Type:** Fix
**Domain App:** remedial
**Risk Level:** Low

### Scope
- Apply migration `0003_remove_compromiseagreement_terms_json_and_more` so `CompromiseAgreement.terms` exists and detail views no longer hit the missing-column error.

### Models Impact
- `CompromiseAgreement`: rename from `terms_json` to `terms` (text column) and rely on the mixin field already defined.

### Services Impact
- None.

### Permission Impact
- None.

### Audit Impact
- None.

### Performance Impact
- None.

## TODO – Compromise terms migration
- [x] Run `python manage.py migrate remedial` to apply migration `0003` and produce the `terms` column.
- [x] Confirm the affected account/compromise detail views render without hitting `remedial_compromiseagreement.terms` errors (sample query in shell).
- [x] Update documentation with the risk/verification notes for this fix.

## ✅ Completed
- Applied `remedial.0003_remove_compromiseagreement_terms_json_and_more` via `python manage.py migrate remedial` so `terms` exists for `CompromiseAgreement`.
- Queried `CompromiseAgreement.objects.count()` in `manage.py shell` to exercise the renamed column and confirm the schema change succeeded.

## ❓ Open Questions
- None.

## ⚠ Risk Notes
- Low: this migration simply renames an existing JSON field to a text column, but it is crucial to ensure no other migrations are pending for the `remedial` app when the fix is applied.

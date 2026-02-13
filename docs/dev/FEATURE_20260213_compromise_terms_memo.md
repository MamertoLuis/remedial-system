# Feature Note: Compromise Terms Memo

## Feature Plan
- Transition `CompromiseAgreement.terms_json` from a JSON blob to a plain-text memo so the field behaves like notes rather than structured data.
- Update the form, admin, and templates so the UI describes the field as a memo/terms summary and no longer enforces JSON validation.
- Rename the field to `terms`, adjust the test fixture, and generate a migration that renames the column while changing it to `TextField`.

## TODO list
- [x] Replace the JSON field with a text field on `CompromiseAgreement` and rename it to `terms`.
- [x] Refresh the form, admin, and templates to use the new field and remove the JSON validation.
- [x] Update the compromise form tests to cover the new trimming behavior.
- [x] Add a migration that renames `terms_json` to `terms` and alters the column type.

## Completed tasks
- Persisted compromise terms as plain text (`apps/remedial/models.py` / migration).
- Tweaked the compromise form, admin UI, and detail view to treat the field as human-readable memo text (`apps/remedial/forms.py`, `templates/remedial/compromise_form.html`, `templates/remedial/compromise_detail.html`, `apps/remedial/admin.py`).
- Adjusted the form tests to confirm whitespace trimming instead of JSON validation (`tests/test_forms.py`).

## Open questions
- None.

## Risk notes
- Medium: renaming the field and dropping the JSON requirement could lose any existing structured entries; ensure there are no critical consumers of the JSON before deploying.

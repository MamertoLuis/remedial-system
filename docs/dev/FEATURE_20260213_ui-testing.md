# UI Testing Feature Plan

## Feature Plan
- Leverage Django's built-in `TestCase`, `RequestFactory`, and `TestClient` to cover authentication, form validation, selectors, and HTMX endpoints without introducing a secondary framework.
- Build reusable fixtures (tenant, users, remedial account, compromise data) so each test can focus on behavior rather than setup.
- Capture critical financial flows (login redirect, compromise approvals, multi-tenant dashboards, form guards) in unit/integration tests before looking at browser-level automation.

## TODO list
- [x] Create shared `BaseRemedialTestCase` fixture that seeds tenants, accounts, compromises, schedule items, and payments.
- [x] Exercise authentication, form validation, selector accuracy, and HTMX approval endpoints through built-in Django tests.
- [ ] Expand coverage to include document uploads, notification rules, and legal workflows in future test sweeps.

## Completed tasks
- Established `tests/` package with base helpers and four focused suites (`test_authentication`, `test_forms`, `test_htmx`, `test_selectors`).
- Added `templates/remedial/ajax_response.html` so HTMX endpoints render consistently during tests.
- Validated that the Django test runner (`python manage.py test`) can execute the new suites using only the built-in framework.

## Open questions
- Should we introduce `pytest-django` later for fixtures, parametrization, or improved reporting?
- Do we want to gate HTMX-specific integration tests behind a feature flag or run them unconditionally?

## Risk notes
- Workshop-level reliance on the tenant middleware path parsing means tests must either hit `RequestFactory` handlers or explicitly set `request.tenant`; future middleware changes should be mirrored in the shared fixtures.
- The `remedial/ajax_response.html` fragment is minimal—if display requirements change, ensure the template still surface `success`/`message` for automated tests.

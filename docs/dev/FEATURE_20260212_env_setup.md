# Feature Plan
- Document the environment bootstrap path so future agents know how we prepared the workspace, including the temporary workaround for missing `ensurepip`.
#
## TODO list
- [x] Install user-level `pip` via `get-pip.py` because `ensurepip`/`pip` were absent.
- [x] Create a `.venv` virtual environment using the freshly installed `virtualenv`.
- [x] Install Django, HTMX, Allauth, and related dependencies inside `.venv`.

## Completed tasks
- Installed `pip` with `get-pip.py` and added the resulting binaries to the user environment.
- Bootstrapped `.venv` through `virtualenv` instead of the missing `python3 -m venv` tooling.
- Installed the core Django stack (`Django`, `psycopg[binary]`, `django-htmx`, `django-allauth`, `django-crispy-forms`, `crispy-bootstrap5`, `python-dotenv`, `django-environ`, `whitenoise`, `gunicorn`).

## Open questions
- None.

## Risk notes
- The system lacks `python3-venv`/`ensurepip` and we could not run `apt`; future steps still requiring system packages may need manual intervention.
- The environment relies on user-local `pip`/`virtualenv`, so scripts expecting system-wide virtualenv or pre-installed `pip` should be adjusted accordingly.

# Feature Note: Recovery Action Detail Title Fix

## Feature Plan
- Diagnose the `RecoveryActionDetailView` failure when rendering the action detail page.
- Update the view so the detail page title pulls `action_type` from the resolved object instead of from the view instance.
- Confirm no other template/view reference depends on the outdated attribute.

## TODO list
- [x] Root-cause the `AttributeError` raised in `RecoveryActionDetailView`.
- [x] Adjust the context data to access `action_type` via `self.object`.
- [x] Verify the detail page builds successfully with the updated title.

## Completed tasks
- Fixed `RecoveryActionDetailView.get_context_data` to reference the resolved object.

## Open questions
- None.

## Risk notes
- Low: change is limited to context data generation and cannot affect persisted business logic.

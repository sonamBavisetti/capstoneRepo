# Implementation Plan

Source: `architecture.md` and `requirements.md` (VNK-128). Resolves design-review advisory notes DR-01 and DR-03 by making the guard mechanism and label-restoration behavior explicit below.

## Implementation Summary
Modify the existing inline quote-form submit handler in `dev/app.py` (the `<script>` block inside the `#quote-form` section, currently lines ~442–483) so the submit button is disabled and relabeled synchronously when a valid submit starts, and is always re-enabled with its original label restored once the request resolves — on success, API error response, or thrown exception. No new files, no backend/API changes, no new dependencies. Single target file: `dev/app.py`.

## Ordered Task Breakdown

### TASK-01: Capture button reference and original label
- **Description**: In the existing IIFE in the `<script>` block, obtain a reference to `.submit-btn` (currently selected via `form.querySelector('.submit-btn')` or `document.querySelector` as appropriate) and store its original label text (e.g. `"Send enquiry"`) in a local constant before the `submit` listener is attached.
- **Target files**: `dev/app.py` (inline `<script>` inside `#quote-form` section)
- **Dependencies**: None
- **Related FR/NFR**: NFR-03
- **Definition of Done**: A `button` variable referencing `.submit-btn` and a constant holding its original label text exist in the script scope, available to the submit handler.

### TASK-02: Guard against re-entry and disable button synchronously on submit
- **Description**: At the very top of the `submit` event handler, immediately after `evt.preventDefault()`, check `if (button.disabled) return;` as the sole guard against duplicate/overlapping submissions (resolves DR-01 — no separate boolean flag is introduced; `button.disabled` is the single source of truth). Immediately set `button.disabled = true` and change its text content to the in-progress label (`"Submitting…"`), before the existing `setMessage('Sending...', '')` call and before `fetch` is invoked.
- **Target files**: `dev/app.py` (same `<script>` block)
- **Dependencies**: TASK-01
- **Related FR/NFR**: FR-01, FR-02, FR-03, NFR-03
- **Definition of Done**: Clicking submit with valid fields disables the button and changes its label before any network request starts; a second click/Enter while disabled is a no-op (handler returns immediately, no second `fetch` call).

### TASK-03: Re-enable button and restore label on every resolution path
- **Description**: Wrap the existing `try { ... } catch (e) { ... }` block's cleanup in a `finally` block (or restructure equivalently) that unconditionally sets `button.disabled = false` and restores the button's original label text. This must run after the success path (`setMessage(...success...); form.reset();`), after the early `return` on a non-OK response, and after the `catch` block — i.e., on all three existing exit paths. Resolves DR-03: label restoration happens identically regardless of outcome. Do not modify `setMessage` calls, success/error text, or `form.reset()` — those are unchanged (NFR-01).
- **Target files**: `dev/app.py` (same `<script>` block)
- **Dependencies**: TASK-02
- **Related FR/NFR**: FR-04, FR-05, NFR-01
- **Definition of Done**: After a successful submission, the button is enabled and shows its original label alongside the existing success message. After a failed submission (API error or network/thrown exception), the button is enabled and shows its original label alongside the existing error message. No existing message text, class, or `form.reset()` behavior changes.

## Execution Order
TASK-01 → TASK-02 → TASK-03 (strictly sequential; each builds on the prior task's code in the same handler).

## FR/NFR Traceability
| Requirement | Task(s) |
|-------------|---------|
| FR-01 | TASK-02 |
| FR-02 | TASK-02 |
| FR-03 | TASK-02 |
| FR-04 | TASK-03 |
| FR-05 | TASK-03 |
| NFR-01 | TASK-03 |
| NFR-02 | N/A — satisfied by having no tasks outside `dev/app.py`'s existing script |
| NFR-03 | TASK-01, TASK-02 |

## Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Button reference selection breaks if `.submit-btn` markup changes elsewhere on the page (e.g., other buttons sharing the class). | Low | Medium | Scope the selector to `form.querySelector('.submit-btn')` within the quote form's own `<form>` element (TASK-01), not a page-wide `document.querySelector`. |
| `finally`-equivalent cleanup is accidentally skipped on one exit path (e.g., the early `return` on non-OK response bypasses it) if implemented as inline duplicated calls instead of an actual `finally` block. | Medium | High (button could get stuck disabled) | Use an actual `try { ... } finally { ... }` construct (TASK-03) rather than duplicating re-enable calls at each exit point, so JS guarantees it always runs. |
| Phase 7 (Verify) needs to observe the disabled/in-progress state, which may be too fast to catch under normal conditions. | Medium | Low (test flakiness, not a product defect) | Out of scope for this plan; flagged for Phase 7 to use a Playwright network delay/interception on `/api/quote-enquiries` when writing the verification test (per design-review DR-02). |

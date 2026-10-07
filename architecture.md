# Architecture

Source: `requirements.md` (VNK-128). The existing `design-review.md` in this repo is from a prior ticket (VNK-1 storefront) and contains no findings applicable to this change; it is not addressed here.

## Architecture Overview
This is a small, client-side-only change to the existing quote enquiry form rendered by the Flask app in `dev/app.py` (route serving the storefront HTML, inline `<script>` block for `#quote-form-element`). No new components, services, or data stores are introduced. The change adds explicit submit-state management (disabled/in-progress/re-enabled) to the existing inline form-submission handler that already calls `POST /api/quote-enquiries`.

No backend, API, or data model changes are required — `requirements.md` explicitly scopes this out (NFR-02, Out of Scope).

## Component Diagram
```text
Browser (storefront page)
 └── #quote-form-element (existing <form>)
       ├── .submit-btn            (existing <button>, gains disabled/label state)
       ├── #quote-message         (existing <p>, status text — unchanged content/behavior)
       └── inline <script>        (existing submit handler — gains a submission-state guard)
              │
              ▼ fetch POST (unchanged contract)
       /api/quote-enquiries        (existing Flask blueprint, dev/api/quote_requests.py — untouched)
```

## Components and Responsibilities
| Component | Responsibility | Change |
|-----------|-----------------|--------|
| `#quote-form-element` submit handler (inline script, `dev/app.py`) | Reads form data, POSTs to `/api/quote-enquiries`, shows result message, resets form. | Extended: sets a local in-progress flag/button state at the start of the handler and clears it in a `finally` block. |
| `.submit-btn` | Triggers submission. | Extended: gains `disabled` attribute toggling and a label-state change ("Submitting…") while in progress. |
| `#quote-message` | Shows status text. | Unchanged — "Sending...", success, and error messages/classes stay as-is (FR-02 may reuse this element instead of/alongside the button label; see ADR-02). |
| `/api/quote-enquiries` (Flask blueprint) | Accepts and persists quote enquiries. | Untouched — out of scope. |

## Data Model
No data model changes. No new entities, fields, or storage are introduced; this is purely DOM/UI state in the browser, not persisted anywhere.

## API / Integration Surface
No API changes. The existing `POST /api/quote-enquiries` request/response contract (JSON body built from `FormData`, JSON response with `error` on failure) is unchanged and reused as-is.

## Technology Stack and Rationale
No new technology is introduced.
- **Vanilla JavaScript (existing inline `<script>` in `dev/app.py`)** — the current submit handler is already plain JS with no framework; the fix is implemented in the same style to avoid introducing a build step or framework dependency for a small DOM-state change. (ADR-01)
- **Native HTML `disabled` attribute on `<button>`** — standard, accessible, and already supported by browsers without additional libraries; also inherently prevents the default double-submit-on-Enter case because a disabled submit button cannot be the form's default action trigger. (ADR-01)

## Security Considerations
- No new input is accepted and no new trust boundary is crossed; the change only affects client-side UI state.
- Disabling the button client-side is a UX safeguard, not a security control — it does not prevent a malicious client from issuing duplicate requests directly against `/api/quote-enquiries` (e.g., via curl/devtools). Requirements explicitly place server-side duplicate detection/rate-limiting out of scope (requirements.md, Out of Scope), so no server-side enforcement is added here. This is a known, accepted limitation, not a defect of this change.

## Scalability and Reliability
- Not applicable at meaningful scale — this is a client-side state fix affecting one browser session's one form at a time; it has no effect on server load or throughput beyond (by design) reducing the number of accidental duplicate requests that reach the server from a single slow or impatient click sequence.
- Reliability: the guard must re-enable the button on every resolution path of the existing `try { ... } catch { ... }` block (success, non-OK response, thrown exception) so a failed request never leaves the form permanently disabled. This is addressed by using a `finally` block (or equivalent) around the existing fetch logic (see ADR-02).

## Architecture Decision Records

### ADR-01
- **Status**: Accepted
- **Context**: FR-01–FR-05 require disabling/re-enabling the submit button and showing an in-progress state, without changing the backend or introducing new technology (NFR-02).
- **Decision**: Implement the fix entirely within the existing inline vanilla-JS submit handler in `dev/app.py`, using the native `<button disabled>` attribute and a button-label swap for the in-progress state, mirroring the ticket's suggested "Submitting…" label.
- **Consequences**: No new dependencies, build steps, or files. The fix stays colocated with the existing form markup/script it modifies, consistent with how the form was originally implemented (VNK-2/ENH-001).

### ADR-02
- **Status**: Accepted
- **Context**: The button must be re-enabled on every outcome (success, API error response, network/thrown error) per FR-04/FR-05 and the reliability note above; the existing handler already has a `try { ... } catch { ... }` structure with an early `return` on non-OK responses.
- **Decision**: Wrap the re-enable logic in a `finally` block around the existing try/catch (or equivalently guarantee it runs on all three exit paths), rather than duplicating the re-enable call at each `return`/catch site.
- **Consequences**: Guarantees the button cannot get stuck disabled regardless of which exit path is taken, with a single point of re-enable logic to maintain. Keeps the diff minimal relative to the current handler shape.

### ADR-03
- **Status**: Accepted
- **Context**: Requirements leave open whether the in-progress indication should be on the button label, the `#quote-message` text, or both (requirements.md, Open Questions).
- **Decision**: Use both: set the button label to "Submitting…" (satisfies the ticket's suggested wording) while leaving `#quote-message`'s existing "Sending..." behavior unchanged, so no existing message-handling code paths are altered.
- **Consequences**: Satisfies FR-02 without touching `setMessage`/`#quote-message` logic, minimizing risk of regressing existing success/error messaging (NFR-01).

## Requirements Traceability
| Requirement | Addressed by |
|-------------|---------------|
| FR-01 | ADR-01 — button disabled at start of submit handler |
| FR-02 | ADR-03 — button label change to "Submitting…" |
| FR-03 | ADR-01 — disabled button cannot re-trigger submit; handler also guarded by in-progress flag |
| FR-04 | ADR-02 — `finally`-based re-enable on success path |
| FR-05 | ADR-02 — `finally`-based re-enable on error/exception paths |
| NFR-01 | ADR-03 — existing message/reset behavior left untouched |
| NFR-02 | ADR-01 — no backend/API/data changes |
| NFR-03 | ADR-01 — `disabled` set synchronously at the top of the submit handler, before `fetch` is called |

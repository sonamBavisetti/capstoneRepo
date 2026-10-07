# Design Review

Source: `requirements.md` and `architecture.md` (VNK-128).

## Verdict: APPROVE

## Summary
The architecture is a minimal, correctly-scoped client-side fix to the existing quote-form submit handler in `dev/app.py`. It introduces no new components, APIs, data model, or dependencies, which matches the requirements' explicit out-of-scope and NFR-02 constraints. All 5 functional requirements and 3 non-functional requirements are traced to specific ADRs. No P0/P1 findings. Two P2 clarity/testability notes and one P3 note are recorded below; none block approval.

## Findings

| ID | Severity | Component | Finding | Recommendation |
|----|----------|-----------|---------|---------------|
| DR-01 | P2 | Submit handler (ADR-01/ADR-02) | The architecture states the handler is "guarded by an in-progress flag" in the Requirements Traceability table (FR-03), but ADR-01's decision text relies on the native `disabled` attribute alone and does not explicitly commit to an additional boolean guard. It's ambiguous whether a separate in-progress flag is actually part of the design or just the button's own disabled state. | During Phase 4 (Implementation Plan), make this explicit: decide whether `disabled` alone is sufficient as the sole guard, or whether an explicit flag is also set, and document whichever is chosen so Phase 5 has one unambiguous mechanism to implement. |
| DR-02 | P2 | Testability | The architecture does not describe how Phase 7 (Verify) can assert the in-progress state (button disabled + label change) given the real request/response cycle is typically too fast to observe in a test without intervention. | Recommend Phase 4/7 plan to use a network-delay/interception technique (e.g., Playwright route handler that delays or holds the `/api/quote-enquiries` response) so the disabled/label state can be asserted mid-request, and that a second click during that window is asserted to produce no additional request. |
| DR-03 | P3 | ADR-03 (message vs. label) | Using both the button label and the existing `#quote-message` text for in-progress state is reasonable, but the architecture doesn't specify whether the button label reverts to its original text ("Send enquiry") on both success and failure paths, or only on one. | Confirm in the implementation plan that the button label is restored to "Send enquiry" on every resolution path (success, API error, thrown exception), not just success. |

## Requirements Coverage

| Requirement | Covered? | Notes |
|-------------|----------|-------|
| FR-01 | Yes | ADR-01 — synchronous disable at submit start |
| FR-02 | Yes | ADR-03 — label change to "Submitting…" |
| FR-03 | Yes (see DR-01) | Disabled button blocks re-trigger; exact guard mechanism to be made explicit |
| FR-04 | Yes | ADR-02 — `finally`-based re-enable on success |
| FR-05 | Yes | ADR-02 — `finally`-based re-enable on error/exception |
| NFR-01 | Yes | ADR-03 — existing message/reset logic untouched |
| NFR-02 | Yes | No backend/API/data changes proposed |
| NFR-03 | Yes | Disable happens synchronously before `fetch` is invoked |

## Security Checklist

| Area | Status | Notes |
|------|--------|-------|
| Authentication / Authorization | N/A | No new endpoints or access paths introduced. |
| Secrets management | N/A | No secrets involved in this change. |
| Input validation | N/A | No new inputs accepted; existing form fields and validation unchanged. |
| Server-side abuse protection | Acknowledged limitation (not a gap) | Architecture correctly notes client-side disabling is a UX safeguard only, not a security control, and that server-side duplicate detection/rate-limiting is explicitly out of scope per `requirements.md`. No action required. |
| Data protection | N/A | No new data captured, transmitted, or stored. |

## Approval Conditions
None — design is approved as-is. DR-01 through DR-03 are advisory and should be resolved during Phase 4 (Implementation Plan) for clarity, not as a condition of this approval.

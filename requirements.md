# Requirements

## Short summary
Fix the quote enquiry form's submit button so it shows progress and cannot be used to send duplicate requests. Source: `user-story.md` (VNK-128), traced to VNK-2 / ENH-001 (quote enquiries). Fetched live from Jira (sonambavisetti.atlassian.net).

## Problem Statement
The quote enquiry form on the storefront (`dev/app.py`, `#quote-form-element`) currently submits via `fetch('/api/quote-enquiries', ...)` but the submit button (`.submit-btn`) is never disabled during the request, and the status message only shows a generic "Sending..." / success / error text. Because the button stays enabled, a customer who clicks it repeatedly (or presses Enter again) while the request is in flight can trigger multiple duplicate quote-enquiry submissions. The fix must disable the button immediately on a valid submit, show an in-progress state, and re-enable it once the request resolves (success or failure), without changing the existing backend API or data model.

## Stakeholders
| Role | Responsibility |
|------|---------------|
| Customer | Fills out and submits the quote enquiry form; should not be able to send duplicates by accident |
| Business owner / staff | Receives quote enquiries; affected by duplicate/noisy submissions |
| Developer | Implements the client-side submit-state handling in the existing quote form |

## Functional Requirements
| ID | Description | Priority |
|----|-------------|----------|
| FR-01 | When the quote form is submitted with valid field values, the submit button (`.submit-btn`) is disabled immediately, before the request completes. | High |
| FR-02 | While the submit request is in progress, the UI shows an in-progress indicator (e.g., button label changes to "Submitting…" and/or the existing status message reflects the in-progress state). | High |
| FR-03 | While a submit request is in progress, additional clicks on the submit button (or additional Enter-key submits) do not trigger another `/api/quote-enquiries` request. | High |
| FR-04 | When the submit request completes successfully, the submit button is re-enabled and the existing success message/form-reset behavior is preserved. | High |
| FR-05 | When the submit request fails (network error or non-OK response), the submit button is re-enabled and the existing error message behavior is preserved. | High |

## Non-Functional Requirements (Success Metrics)
| ID | Description | Metric |
|----|-------------|--------|
| NFR-01 | No regression to existing quote-enquiry submission behavior (payload, endpoint, success/error messaging). | Existing `/api/quote-enquiries` contract and messages unchanged (manual/automated verification). |
| NFR-02 | Change is isolated to client-side form-submission handling; no backend/API/data-model changes required. | Diff scoped to the quote form's HTML/JS in `dev/app.py` (or extracted static asset) only. |
| NFR-03 | Button state change is perceivable without a noticeable delay (synchronous with the submit event). | Button becomes disabled in the same event-handler tick that initiates the request. |

## Acceptance Criteria
### FR-01 / FR-02: Disable while submitting
- Given all form fields are valid
- When the customer clicks Submit
- Then the Submit button becomes disabled
- And the UI indicates the form is submitting

### FR-03: Prevent duplicate requests
- Given the form submission request is in progress
- When the customer clicks Submit again (or presses Enter again)
- Then no additional `/api/quote-enquiries` request is initiated

### FR-04: Re-enable after success
- Given the form submission request completes successfully
- When the success confirmation is shown
- Then the Submit button is re-enabled
- And the form is reset (existing behavior), per the current implementation

### FR-05: Re-enable after failure
- Given the form submission request fails
- When an error message is shown
- Then the Submit button is re-enabled

## Out of Scope
- Changes to the `/api/quote-enquiries` backend endpoint or its request/response contract
- Changes to form field validation rules beyond the existing `required` attributes
- Rate-limiting or server-side duplicate-submission detection
- Any other form on the site besides the quote enquiry form

## Open Questions / Assumptions
- Exact in-progress button label text is not specified by the ticket; assumption: reuse the pattern suggested in the ticket ("Submitting…") unless the existing "Sending..." status message is deemed sufficient — to be confirmed in Architecture/Design Review. (assumption)
- Ticket does not specify a client-side request timeout or a maximum wait before re-enabling the button on a hung request; assumption: rely on the existing `fetch`/`try-catch` resolution (success, error response, or thrown exception) to re-enable the button, with no additional timeout logic added. (assumption)

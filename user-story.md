# Jira Issue: VNK-128 — As a customer, I want the quote form submit button to show progress and prevent duplicate submits, so that I don't accidentally send multiple enquiries

**Direct Link**: https://sonambavisetti.atlassian.net/browse/VNK-128

## Metadata
- Issue Key: VNK-128
- Issue Type: Story
- Status: To Do
- Priority: Medium
- Assignee: Unassigned
- Reporter: SONAM BAVISETTI
- Labels: Not Available
- Components: Not Available
- Fix Versions: Not Available

## Description

Traceability:
- Approved Enhancement ID: VNK-VNK-2-ENH-001
- Gap: No disabled state; generic message only; user can click multiple times.

Functional requirements:
- Disable submit button immediately after valid submission starts.
- Show an in-progress indicator/state (e.g., label change to "Submitting…").
- Re-enable submit button after request completes (success or failure).
- Prevent multiple requests being sent from repeated clicks while in progress.

## Acceptance Criteria (BDD)

1) Disable while submitting (positive)
> Given all form fields are valid
> When I click Submit
> Then the Submit button becomes disabled
> And the UI indicates the form is submitting

2) Prevent duplicate requests (negative)
> Given the form submission request is in progress
> When I click Submit again (or press Enter again)
> Then no additional API request is initiated

3) Re-enable after success (positive)
> Given the form submission request completes successfully
> When the success confirmation is shown
> Then the Submit button is re-enabled
> And the form is reset (or remains filled) according to the existing intended behavior

4) Re-enable after failure (error)
> Given the form submission request fails
> When an error message is shown
> Then the Submit button is re-enabled

## Notes
Not Available

## Related Issues
- Traces to: VNK-2 (ENH-001 — quote enquiries)
- Issue Links: Not Available

---

*Fetched live from Jira (sonambavisetti.atlassian.net) via REST API using credentials in `.jira-config.json`.*

# Implementation Plan

## Objective
Implement **VNK-3** approved requirements for the Vinayaka File Works Storefront MVP.

**Traceability note:** The workflow context provided does not include an accessible Jira payload (Epic/Stories/AC) and the Jira key `VNK-3` was previously reported as not found in Jira. This plan therefore uses the workflow-context enhancement IDs **ENH-VNK3-001..ENH-VNK3-014** as the requirement anchors and maps each task back to those IDs while keeping the overall delivery labeled as **VNK-3**.

Primary business goals:
- Enable lead capture by wiring the **homepage quote form** to the existing Quote Requests API.
- Improve shopping reliability by validating cart inputs (and preparing for persistence).
- Reduce financial inconsistency by aligning **currency** with storefront pricing.
- Improve reliability (idempotency + inventory concurrency) and protect customer/admin PII.
- Improve API correctness, error consistency, and test coverage.

## Scope

### In Scope
- **ENH-VNK3-001**: Wire quote form end-to-end (register blueprint + submit from UI).
- **ENH-VNK3-002**: Cart correctness via input validation and server-side product lookup.
- **ENH-VNK3-004**: Currency configuration to align backend (payments/orders/invoices) with INR by default.
- **ENH-VNK3-005**: Order idempotency at the order layer (avoid duplicate orders/inventory decrement on retries).
- **ENH-VNK3-006**: Inventory concurrency protection during checkout.
- **ENH-VNK3-007**: Expand order API responses with confirmation details.
- **ENH-VNK3-008**: Strengthen customer validation schema.
- **ENH-VNK3-009**: Standardize API error handling.
- **ENH-VNK3-010**: Protect PII endpoints (quotes list/admin) with authentication/authorization.
- **ENH-VNK3-011**: App wiring robustness (avoid silent partial startup; add health/reporting).
- **ENH-VNK3-013**: Add tests for quote/cart/authz changes.
- **ENH-VNK3-014**: Documentation improvements for API usage.

### Explicitly Out of Scope
- **ENH-VNK3-003** Cart persistence to DB (requires broader identity/auth decisions and migrations). This plan includes **design hooks** to make a later persistence change straightforward but does not implement DB persistence.
- **ENH-VNK3-012** ETag/caching and security headers (optional; low priority) unless required by review.
- Full UI redesign or SPA.

## Architecture/Component Impact

| Component | Current State | Required Change | Related Jira |
|---|---|---|---|
| Flask App (`dev/app.py`) | Home page rendered with `render_template_string`. Blueprints registered for `products/cart/orders/admin/invoices` only; try/except swallows errors. | Register quote blueprint; improve startup diagnostics; add health endpoint; optionally fail fast outside tests. | ENH-VNK3-001/011 |
| Quote Requests API (`dev/api/quote_requests.py`) | Exists, but not registered. List endpoints likely public. | Ensure blueprint registered; protect list endpoints with admin auth. | ENH-VNK3-001/010 |
| Cart API (`dev/api/cart.py`) | In-memory cart; accepts arbitrary `item`. | Validate schema (`product_id`, positive `quantity`), look up product server-side; return normalized cart. | ENH-VNK3-002 |
| Orders API (`dev/api/orders.py`) | Minimal response; limited error consistency. | Return richer order DTO; standardize errors; enforce idempotency key. | ENH-VNK3-007/009/005 |
| Order Service (`dev/services/order_service.py`) | Currency hardcoded to USD; idempotency passed to payment only; inventory decrement without explicit concurrency control noted. | Currency configurable (default INR). Add idempotency storage/lookup. Add inventory locking/optimistic concurrency in transaction. | ENH-VNK3-004/005/006 |
| Validation (`dev/validation.py`) | Order validation minimal (email only). Quote validation simplistic. | Add stricter customer validation (email format, phone, address fields). | ENH-VNK3-008 |
| Auth/Admin (`dev/auth.py`, `dev/api/admin.py`) | Admin endpoints exist; current auth protections unknown/likely weak. | Add/extend auth guard; protect quote lists/admin endpoints; avoid exposing PII. | ENH-VNK3-010 |
| Error handling | Endpoint-specific `{'error': ...}` responses; exceptions may leak HTML. | Add Flask error handlers returning consistent JSON error envelope. | ENH-VNK3-009 |
| Docs (`README.md`, `dev/docs/`) | Minimal API examples. | Add endpoint examples/payloads and error format. | ENH-VNK3-014 |
| Tests (`dev/tests/`) | Existing tests for orders/products/validation; none observed for cart/quote/authz in workflow context. | Add tests for cart validation, quote wiring, authz protections, idempotency, and inventory concurrency edge. | ENH-VNK3-013 |

## Implementation Tasks

| Task ID | Jira Reference | Component | Task Description | Dependency |
|---|---|---|---|---|
| VNK3-T1 | ENH-VNK3-001 | Flask app | Register `quote_requests` blueprint in `dev/app.py` (similar pattern to other blueprints). | None |
| VNK3-T2 | ENH-VNK3-001 | Frontend (landing page) | Wire the existing quote form (`#quote-form-element`) to submit to `POST /api/quote-requests` (either set form `action` + method, or add minimal inline/static JS `fetch`) and render success/error into `#quote-message`. | VNK3-T1 |
| VNK3-T3 | ENH-VNK3-002 | Cart API | Implement cart item validation: require `product_id` and `quantity` (int > 0). Reject unknown products and inactive products (unless explicitly allowed). | None |
| VNK3-T4 | ENH-VNK3-002 | Cart API | Normalize cart representation returned by `GET /api/cart/<customer_id>` and `POST /add`: include product snapshot (name, unit_price, currency), quantity, line_total, cart_total. | VNK3-T3 |
| VNK3-T5 | ENH-VNK3-004 | Config | Add configurable currency (e.g., `DEFAULT_CURRENCY`) in `dev/config.py` with default `INR`; plumb into order creation/payment/invoice generation. | None |
| VNK3-T6 | ENH-VNK3-004 | Orders service | Replace hardcoded `'USD'` in payment charge with configured currency; store currency on order/invoice if model supports it, otherwise include in DTO and invoice metadata. | VNK3-T5 |
| VNK3-T7 | ENH-VNK3-005 | Orders service/DB | Implement order idempotency using `idempotency_key`: store on Order with unique constraint (or separate Idempotency table) and return existing order response when key repeats. | VNK3-T5 |
| VNK3-T8 | ENH-VNK3-006 | Orders service/DB | Add inventory concurrency control: within a DB transaction, lock product rows (SELECT FOR UPDATE) or use optimistic concurrency (version column) to prevent oversell. | VNK3-T7 |
| VNK3-T9 | ENH-VNK3-007 | Orders API | Expand `POST /api/orders` response to include order details (items, totals, currency, payment_status, invoice link/status). Expand `GET /api/orders/<id>` similarly. | VNK3-T6 |
| VNK3-T10 | ENH-VNK3-008 | Validation | Strengthen `customer` validation: email format, name required, phone/mobile normalization, address schema (billing/shipping), and clear field-level errors. | None |
| VNK3-T11 | ENH-VNK3-009 | Flask app | Add global JSON error handlers for `ValueError`, `HTTPException`, and unhandled `Exception` producing consistent envelope `{error:{code,message,details,trace_id}}`. | None |
| VNK3-T12 | ENH-VNK3-010 | Auth/Admin/Quote | Add admin authentication guard and apply to PII endpoints: `GET /api/quote-requests`, `GET /api/quote-enquiries` (and admin endpoints). Confirm whether `POST` remains public. | VNK3-T11 |
| VNK3-T13 | ENH-VNK3-011 | App wiring | Add `/health` (or `/api/health`) returning which blueprints/modules are registered; add startup logging and optional fail-fast outside test mode. | VNK3-T1 |
| VNK3-T14 | ENH-VNK3-013 | Tests | Add pytest coverage: quote submit end-to-end, cart validation/normalization, protected quote list requires auth, idempotency duplicate prevention, currency in order/payment DTO, inventory concurrency (unit-level simulation). | VNK3-T1..T13 |
| VNK3-T15 | ENH-VNK3-014 | Docs | Update `README.md` or `dev/docs/api.md` with API examples for quote/cart/orders (new fields), auth header usage, and error format. | VNK3-T9/VNK3-T12/VNK3-T11 |

## Database Changes

### Planned (Required for ENH-VNK3-005/006)
Because idempotency and concurrency correctness require durable state, **database changes are required**.

1) **Orders table**
- Add column: `idempotency_key` (string, nullable initially)
- Add unique index/constraint on `idempotency_key` (where not null)

2) **Products table** (only if using optimistic concurrency)
- Add `version` (int) or `updated_at` check for optimistic concurrency.
- Alternatively, if the app uses PostgreSQL/MySQL and SQLAlchemy supports it, prefer **row locking** (`SELECT ... FOR UPDATE`) and avoid schema change.

3) **Orders/Invoices currency**
- If models exist and are persisted: add `currency` (string) column to `orders` (and `invoices` if stored separately).
- If persistence is not feasible, at minimum include currency in response DTO and invoice rendering metadata.

### Migrations
- Use existing Alembic setup (`alembic.ini`) to create a migration for the above schema changes.

### Not included
- Cart persistence tables (ENH-VNK3-003) are explicitly out of scope.

## API Changes

### Quote Requests
- Ensure `POST /api/quote-requests` is reachable and works from the homepage.
- Protect list endpoints:
  - `GET /api/quote-requests` -> **admin-only** (requires auth)
  - `GET /api/quote-enquiries` -> **admin-only** (requires auth)

### Cart
- `POST /api/cart/<customer_id>/add`:
  - Validate request body schema.
  - Ignore/override client-supplied price fields.
  - Return normalized cart response.
- `GET /api/cart/<customer_id>`:
  - Return normalized cart response.

### Orders
- `POST /api/orders`:
  - Accept `idempotency_key` and enforce idempotency.
  - Return expanded DTO.
- `GET /api/orders/<order_id>`:
  - Return expanded DTO.

### Errors (All APIs)
- Standardize error response format across endpoints.

## Frontend Changes
- Update landing page quote form to submit to API.
- Add minimal user feedback:
  - success message (e.g., "Thanks—your enquiry was submitted")
  - validation error message(s)
- If implemented with JS, ensure progressive enhancement (still works without JS via form `action`).

## Backend Changes
- `dev/app.py`
  - Register quote blueprint.
  - Add health endpoint.
  - Add error handlers.
- `dev/api/quote_requests.py`
  - Apply auth guard to list endpoints.
- `dev/api/cart.py`
  - Implement validation and server-side product lookup.
  - Normalize output.
- `dev/services/order_service.py`
  - Currency config.
  - Idempotency enforcement.
  - Transaction + inventory locking/optimistic concurrency.
- `dev/api/orders.py`
  - Return expanded DTOs.
  - Use standardized error envelope.
- `dev/validation.py`
  - Strengthen customer validation and return field-level errors.
- `dev/auth.py` / `dev/api/admin.py`
  - Provide auth mechanism for admin-only endpoints (token header or session-based) and apply consistently.

## Test Impact

### Unit / Integration (pytest)
- Quote:
  - `POST /api/quote-requests` accepts form-encoded and JSON; returns 201 with id.
  - `GET /api/quote-requests` requires admin auth (401/403 without token).
- Cart:
  - Reject missing product_id/quantity.
  - Reject negative/zero quantity.
  - Reject unknown product_id.
  - Ensure response totals are computed server-side.
- Orders:
  - Currency is INR by default (or configured) and is reflected in DTO/payment request.
  - Idempotency: repeated `POST /api/orders` with same key returns same order_id and does not double-decrement inventory.
  - Inventory: insufficient stock yields deterministic error code.
  - Concurrency: simulate two checkouts racing for last unit; only one succeeds.
- Error handling:
  - Unhandled exception returns JSON error envelope (not HTML).

### Regression Scenarios
- Existing product APIs still paginate.
- Existing checkout flow remains functional.
- Admin endpoints still operable with new auth requirement.

## Dependencies
- **DB/Alembic**: migrations must run in dev/CI.
- **Auth decision**: acceptable admin auth approach (token header vs session/JWT). Plan assumes minimal admin token header is acceptable for MVP.
- **Database engine**: concurrency approach depends on DB support for row locking.
- **Config/env**: addition of DEFAULT_CURRENCY and any admin secret/token configuration.

## Risks
- **Breaking changes**: expanded order responses are additive, but auth on quote list endpoints may break existing consumers.
- **Data integrity**: incorrect transaction boundaries could still allow partial writes or deadlocks.
- **Concurrency**: SELECT FOR UPDATE can introduce lock contention; optimistic concurrency requires careful retry.
- **Security**: weak token handling could still expose PII; must avoid logging tokens/PII.
- **Backward compatibility**: cart normalization may change response shape.

## Implementation Sequence
1. Register quote blueprint and wire homepage submission (VNK3-T1, VNK3-T2).
2. Add global error handlers and consistent error envelope (VNK3-T11).
3. Add admin auth guard and protect PII endpoints (VNK3-T12).
4. Implement cart validation + normalized representation (VNK3-T3, VNK3-T4).
5. Add currency configuration and plumb through order/payment/invoice (VNK3-T5, VNK3-T6).
6. Implement idempotency (schema + logic) (VNK3-T7).
7. Implement inventory concurrency control (VNK3-T8).
8. Expand order API DTOs (VNK3-T9).
9. Add health/startup diagnostics (VNK3-T13).
10. Add/extend tests (VNK3-T14).
11. Update docs (VNK3-T15).

## Definition of Done
- Quote form can submit an enquiry from `/` and shows success/error feedback.
- Quote listing endpoints require admin auth and do not expose PII to unauthenticated callers.
- Cart add/get endpoints validate inputs and return server-computed totals.
- Orders:
  - default currency matches configured value (INR default)
  - idempotency prevents duplicate orders for repeated key
  - inventory concurrency prevents oversell
  - responses include order confirmation details (items/totals/currency/invoice link)
- Consistent JSON error envelope returned for validation and server errors.
- Alembic migrations exist and apply cleanly on a fresh DB.
- Test suite passes in CI (and new tests cover quote/cart/auth/idempotency/concurrency).
- Documentation updated with payload and error examples.
- Human approval received for this implementation plan prior to development.

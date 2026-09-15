# Jira Issue: VNK-1 — Website for Vinayaka File Works

**Direct Link**: [View in Jira](https://sonambavisetti.atlassian.net/browse/VNK-1)

## Metadata
| Field | Value |
|-------|-------|
| Issue Key | VNK-1 |
| Issue Type | Story |
| Status | To Do |
| Priority | Medium |
| Assignee | Unassigned |
| Reporter | SONAM BAVISETTI |
| Labels | - |
| Components | - |
| Sprint | - |
| Epic | - |

## Description
As a customer, I want a website for Vinayaka File Works that displays the company address, logo, product catalog, contact number, allows placing orders (COD and Online), and generates downloadable invoices so I can browse products and purchase easily.

Vinayaka File Works is a file manufacturing unit. Provided assets: company logo and a sample bill (screenshot). The site must present business info, product list with prices, an order placement flow, and produce a PDF invoice matching the supplied bill layout.

## Acceptance Criteria
> - [ ] Homepage displays company name "Vinayaka File Works", logo, full postal address, and contact number.
> - [ ] Product listing page shows products with name, SKU, image (if available), unit price, and available quantity.
> - [ ] Customer can add products to cart, enter contact/delivery info, choose payment (Cash on Delivery or Online), and submit an order.
> - [ ] On successful order, the system shows order confirmation and provides a downloadable PDF invoice matching the sample bill fields: invoice number, date, customer details, itemized list, totals, and company details.
> - [ ] Admin interface (or simple admin endpoint) can view orders and mark them processed.
> - [ ] Input validation and graceful error handling for missing fields and failed payments.
> - [ ] No secrets (API keys) are committed to repo; environment variables only.

## Related Issues
- **Blocks**: None
- **Blocked by**: None
- **Relates to**: None

## Attachments & Links
- [Company logo](https://sonambavisetti.atlassian.net/browse/VNK-1)
- [Sample bill screenshot](https://sonambavisetti.atlassian.net/browse/VNK-1)
- [Vinayaka File Works Jira issue](https://sonambavisetti.atlassian.net/browse/VNK-1)

## Recent Comments
No comments were found for this issue.

---

## Notes
- Requirement is for a customer-facing storefront and checkout flow for Vinayaka File Works.
- The ticket includes a PDF invoice requirement matching a provided sample bill layout and a logo asset.
- The issue is currently in the "To Do" state and has no assignee set.
- Payment gateway decision remains open and may need clarification before implementation.

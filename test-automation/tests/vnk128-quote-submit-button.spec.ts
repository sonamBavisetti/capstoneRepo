import { test, expect, type Route } from '@playwright/test';

// VNK-128: quote enquiry submit button must show progress and prevent
// duplicate submits. Covers requirements.md FR-01..FR-05 / NFR-01.
//
// Run against the standalone Flask app (dev/app.py) via:
//   npx playwright test --config=playwright.vnk128.config.ts

const QUOTE_API_PATH = '**/api/quote-enquiries';

async function fillValidQuoteForm(page: import('@playwright/test').Page) {
  await page.getByLabel('Name *').fill('QA Test User');
  await page.getByLabel('Mobile Number *').fill('9999999999');
  await page.getByLabel('Product / Category *').fill('QA Test Category');
}

function mockQuoteApi(
  page: import('@playwright/test').Page,
  opts: { status: number; body: Record<string, unknown>; delayMs?: number }
) {
  let requestCount = 0;
  const handler = async (route: Route) => {
    requestCount += 1;
    if (opts.delayMs) {
      await new Promise((resolve) => setTimeout(resolve, opts.delayMs));
    }
    await route.fulfill({
      status: opts.status,
      contentType: 'application/json',
      body: JSON.stringify(opts.body),
    });
  };
  return {
    install: () => page.route(QUOTE_API_PATH, handler),
    getRequestCount: () => requestCount,
  };
}

test.describe('Quote enquiry submit button — in-progress / duplicate-submit guard', () => {
  test('FR-01/FR-02: disables the button and shows an in-progress label while submitting', async ({ page }) => {
    const mock = mockQuoteApi(page, {
      status: 201,
      delayMs: 1200,
      body: { status: 'created', quote_id: 'qa-1', message: 'Your request has been submitted successfully.' },
    });
    await mock.install();

    await page.goto('/');
    await fillValidQuoteForm(page);

    const button = page.locator('#quote-form-element button.submit-btn');
    await expect(button).toBeEnabled();
    await expect(button).toHaveText('Send enquiry');

    await button.click();

    await expect(button).toBeDisabled();
    await expect(button).toHaveText('Submitting...');
  });

  test('FR-03: a second click while submitting does not trigger an additional request', async ({ page }) => {
    const mock = mockQuoteApi(page, {
      status: 201,
      delayMs: 1500,
      body: { status: 'created', quote_id: 'qa-2', message: 'Your request has been submitted successfully.' },
    });
    await mock.install();

    await page.goto('/');
    await fillValidQuoteForm(page);

    const button = page.locator('#quote-form-element button.submit-btn');
    await button.click();
    await expect(button).toBeDisabled();

    // Attempt a second submit while the first request is still in flight.
    await button.click({ timeout: 1000 }).catch(() => {
      // Expected: Playwright refuses to click a disabled element.
    });
    await page.keyboard.press('Enter');

    // Still within the delay window — only the first request should have been sent.
    expect(mock.getRequestCount()).toBe(1);

    await expect(button).toBeEnabled({ timeout: 5000 });
    expect(mock.getRequestCount()).toBe(1);
  });

  test('FR-04/NFR-01: re-enables the button and preserves existing success behavior', async ({ page }) => {
    const mock = mockQuoteApi(page, {
      status: 201,
      delayMs: 300,
      body: { status: 'created', quote_id: 'qa-3', message: 'Your request has been submitted successfully.' },
    });
    await mock.install();

    await page.goto('/');
    await fillValidQuoteForm(page);

    const button = page.locator('#quote-form-element button.submit-btn');
    const nameField = page.getByLabel('Name *');

    await button.click();
    await expect(button).toBeDisabled();

    await expect(button).toBeEnabled({ timeout: 5000 });
    await expect(button).toHaveText('Send enquiry');
    await expect(page.locator('#quote-message')).toHaveText('Thank you! Your enquiry has been submitted.');
    await expect(page.locator('#quote-message')).toHaveClass(/success/);
    await expect(nameField).toHaveValue('');
  });

  test('FR-05: re-enables the button and preserves existing error behavior on failure', async ({ page }) => {
    const mock = mockQuoteApi(page, {
      status: 400,
      delayMs: 300,
      body: { error: 'mobile_number is required' },
    });
    await mock.install();

    await page.goto('/');
    await fillValidQuoteForm(page);

    const button = page.locator('#quote-form-element button.submit-btn');
    await button.click();
    await expect(button).toBeDisabled();

    await expect(button).toBeEnabled({ timeout: 5000 });
    await expect(button).toHaveText('Send enquiry');
    await expect(page.locator('#quote-message')).toHaveText('mobile_number is required');
    await expect(page.locator('#quote-message')).toHaveClass(/error/);
  });
});

test.describe('Quote enquiry submit button — real backend integration (no mocking)', () => {
  test('shows a validation error and recovers the button when required fields are missing', async ({ page }) => {
    await page.goto('/');
    // Only fill the product category; leave required name/mobile empty.
    await page.getByLabel('Product / Category *').fill('QA Test Category');

    const button = page.locator('#quote-form-element button.submit-btn');
    await button.click();

    await expect(button).toBeEnabled({ timeout: 10000 });
    await expect(button).toHaveText('Send enquiry');
    await expect(page.locator('#quote-message')).toHaveClass(/error/);
  });

  test('submits successfully end-to-end and recovers the button', async ({ page }) => {
    await page.goto('/');
    await fillValidQuoteForm(page);

    const button = page.locator('#quote-form-element button.submit-btn');
    await button.click();

    await expect(button).toBeEnabled({ timeout: 10000 });
    await expect(button).toHaveText('Send enquiry');
    await expect(page.locator('#quote-message')).toHaveText('Thank you! Your enquiry has been submitted.');
    await expect(page.locator('#quote-message')).toHaveClass(/success/);
  });
});

import { defineConfig, devices } from '@playwright/test';

// Dedicated config for VNK-128 (quote enquiry submit-button fix).
//
// The shared playwright.config.ts webServer starts the FastAPI app
// (dev.app.main:app on port 8000), which has no quote-form page or
// /api/quote-enquiries endpoint. The quote form exists only in the
// standalone Flask app (dev/app.py, port 5000, started via
// `python dev/app.py`). This config targets that app directly so the
// shared config/webServer used by the VNK-3 suite is left untouched.
const baseURL = process.env.VNK128_BASE_URL || 'http://127.0.0.1:5000';

export default defineConfig({
  testDir: './tests',
  testMatch: ['**/vnk128-*.spec.ts'],
  timeout: 30 * 1000,
  expect: { timeout: 10000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['list'],
    ['json', { outputFile: 'test-results/vnk128-results.json' }],
  ],
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    headless: true,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'cd .. && python dev/app.py',
    url: baseURL,
    reuseExistingServer: true,
    timeout: 60 * 1000,
  },
});

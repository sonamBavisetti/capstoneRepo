import { defineConfig, devices } from '@playwright/test';

const baseURL = process.env.BASE_URL || process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5000';

export default defineConfig({
  testDir: './tests',
  testMatch: ['**/vinayaka-*.spec.ts'],
  timeout: 30 * 1000,
  expect: { timeout: 5000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list'],
  ],
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    // Ensure CI runs in headless mode
    headless: !!process.env.CI,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    // Start the local Flask dev app. SECRET_KEY is provided for any session logic.
    command: 'cd .. && set SECRET_KEY=dev-secret && python -u dev/app.py',
    url: baseURL,
    reuseExistingServer: false,
    timeout: 120 * 1000,
  },
});

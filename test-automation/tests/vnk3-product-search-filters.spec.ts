import { test, expect } from '@playwright/test';

// NOTE: Despite the filename prefix, these scenarios are traceable to Jira VNK-2
// (Product search & filters). This repository's Playwright config only matches
// vnk3-*.spec.ts; we keep that convention to ensure CI picks up these tests.

test.describe('VNK-2 Product Search & Filters API', () => {
  test('VNK-2-01: products list returns X-Total-Count header', async ({ request }) => {
    const resp = await request.get('/api/products');
    expect(resp.status()).toBe(200);
    const headers = resp.headers();
    expect(headers['x-total-count']).toBeTruthy();
    const total = Number(headers['x-total-count']);
    expect(Number.isNaN(total)).toBeFalsy();
    expect(total).toBeGreaterThanOrEqual(0);
  });

  test('VNK-2-02: search term matches name/category/specifications', async ({ request }) => {
    const resp = await request.get('/api/products?q=Business');
    expect(resp.status()).toBe(200);
    const items = await resp.json();
    expect(Array.isArray(items)).toBeTruthy();
    expect(items.length).toBeGreaterThan(0);
    expect(items.some((p: any) => String(p?.name ?? '').includes('Business'))).toBeTruthy();
  });

  test('VNK-2-03: filters intersect (category + material)', async ({ request }) => {
    const resp = await request.get('/api/products?category=Stationery&material=PVC');
    expect(resp.status()).toBe(200);
    const items = await resp.json();
    expect(items.length).toBeGreaterThan(0);
    for (const p of items) {
      expect(p.category).toBe('Stationery');
      expect(p.material).toBe('PVC');
    }
  });

  test('VNK-2-04: invalid material returns 400 with detail', async ({ request }) => {
    const resp = await request.get('/api/products?material=WOOD');
    expect(resp.status()).toBe(400);
    const body = await resp.json();
    // FastAPI uses { detail: string } by default for HTTPException
    expect(body).toHaveProperty('detail');
  });
});

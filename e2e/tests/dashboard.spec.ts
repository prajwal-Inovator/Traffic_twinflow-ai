// e2e/tests/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should load dashboard page', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@twinflow.ai');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toHaveText('Dashboard');
  });

  test('should display live metrics', async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@twinflow.ai');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Live Vehicles')).toBeVisible();
    await expect(page.locator('text=Active Incidents')).toBeVisible();
  });

  test('should navigate to Digital Twin', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@twinflow.ai');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.click('text=Live Digital Twin');
    await expect(page).toHaveURL('/digital-twin');
    await expect(page.locator('#twinflow-map')).toBeVisible();
  });
});
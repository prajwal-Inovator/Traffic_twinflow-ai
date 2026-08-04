// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/tests',
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:80',
    headless: true,
  },
  webServer: {
    command: 'docker-compose -f docker/docker-compose.prod.yml up',
    port: 80,
    reuseExistingServer: !process.env.CI,
  },
});
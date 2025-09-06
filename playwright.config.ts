import { defineConfig, devices } from "@playwright/test";

const webServerCfg = process.env.SKIP_WEBSERVER === "1"
  ? undefined
  : {
      command: "cd /home/shunsuke/works/selfdriving/api && docker-compose up",
      url: "http://localhost:8000/api/v1/health",
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    } as const;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["html"],
    ["line"],
    ["json", { outputFile: "test-results/results.json" }],
  ],
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:8000",
    trace: "on-first-retry",
  },

  projects: [
    {
      name: "api-tests",
      use: {
        ...devices["Desktop Chrome"],
      },
    },
  ],

  webServer: webServerCfg as any,
});

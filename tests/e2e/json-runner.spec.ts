import { test, expect, request } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

// Type definitions for test configuration
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

type PreProcessItem = {
  type: "db" | "api" | "script";
  script?: string;
  api?: string;
  method?: HttpMethod;
  input?: any;
};

type PostProcessItem = {
  description?: string;
  type: "capture" | "validate" | "db";
  from?: string;
  to?: string;
  script?: string;
};

type Assertion = {
  description: string;
  api: string;
  method: HttpMethod;
  input?: any;
  headers?: Record<string, string>;
  parallel?: number;
  expected: {
    status?: number;
    result?: any;
    headers?: Record<string, string>;
  };
  postprocess?: PostProcessItem[];
};

type TestCase = {
  name: string;
  description?: string;
  assertions: Assertion[];
};

type TestPlan = {
  title: string;
  description?: string;
  baseUrl: string;
  headers?: Record<string, string>;
  preprocess?: PreProcessItem[];
  tests: TestCase[];
};

// Global context for captured variables
class TestContext {
  private variables: Map<string, any> = new Map();

  set(path: string, value: any) {
    this.variables.set(path, value);
  }

  get(path: string): any {
    return this.variables.get(path);
  }

  // Replace variables in the format ${global.variableName}
  replaceVariables(obj: any): any {
    if (typeof obj === "string") {
      return obj.replace(/\$\{([\w.]+)\}/g, (match, path) => {
        const value = this.get(path);
        return value !== undefined ? value : match;
      });
    }
    if (Array.isArray(obj)) {
      return obj.map((item) => this.replaceVariables(item));
    }
    if (obj !== null && typeof obj === "object") {
      const result: any = {};
      for (const [key, value] of Object.entries(obj)) {
        result[key] = this.replaceVariables(value);
      }
      return result;
    }
    return obj;
  }
}

// Load test plan from JSON file
function loadTestPlan(filePath: string): TestPlan {
  const fullPath = path.resolve(filePath);
  const content = fs.readFileSync(fullPath, "utf-8");
  return JSON.parse(content);
}

// Execute database script (mock implementation - replace with actual DB execution)
async function executeDatabaseScript(scriptPath: string) {
  console.log(`Executing database script: ${scriptPath}`);
  // TODO: Implement actual database script execution
  // This could use a library like pg or mysql2 to execute SQL scripts
}

// Execute preprocessing steps
async function executePreprocess(
  items: PreProcessItem[],
  context: TestContext,
  apiContext: any,
  baseUrl: string
) {
  for (const item of items) {
    switch (item.type) {
      case "db":
        if (item.script) {
          await executeDatabaseScript(item.script);
        }
        break;
      case "api":
        if (item.api && item.method) {
          const response = await apiContext.fetch(`${baseUrl}${item.api}`, {
            method: item.method,
            data: item.input,
          });
          console.log(
            `Preprocess API call: ${item.method} ${
              item.api
            } - Status: ${response.status()}`
          );
        }
        break;
      case "script":
        if (item.script) {
          console.log(`Executing script: ${item.script}`);
          // TODO: Implement script execution
        }
        break;
    }
  }
}

// Execute postprocessing steps
async function executePostprocess(
  items: PostProcessItem[],
  response: any,
  context: TestContext
) {
  for (const item of items) {
    switch (item.type) {
      case "capture":
        if (item.from && item.to) {
          const responseData = await response.json();
          const value = getNestedProperty(responseData, item.from);
          context.set(item.to, value);
          console.log(`Captured ${item.from} -> ${item.to}: ${value}`);
        }
        break;
      case "validate":
        // TODO: Implement additional validation logic
        break;
      case "db":
        if (item.script) {
          await executeDatabaseScript(item.script);
        }
        break;
    }
  }
}

// Get nested property from object using dot notation
function getNestedProperty(obj: any, path: string): any {
  return path.split(".").reduce((current, key) => current?.[key], obj);
}

// Deep equality check for objects
function deepEqual(actual: any, expected: any): boolean {
  if (actual === expected) return true;
  if (actual == null || expected == null) return false;
  if (typeof actual !== typeof expected) return false;

  if (typeof actual === "object") {
    const actualKeys = Object.keys(actual);
    const expectedKeys = Object.keys(expected);

    // Check if expected keys are present in actual (partial match)
    for (const key of expectedKeys) {
      if (!deepEqual(actual[key], expected[key])) {
        return false;
      }
    }
    return true;
  }

  return false;
}

// Main test execution
const testPlanPath = process.env.TEST_PLAN_PATH || "./tests/e2e/testplan.json";
const testPlan = loadTestPlan(testPlanPath);

test.describe(testPlan.title, () => {
  let apiContext: any;
  let testContext: TestContext;

  test.beforeAll(async ({ playwright }) => {
    // Create API context with base configuration
    apiContext = await playwright.request.newContext({
      baseURL: testPlan.baseUrl,
      extraHTTPHeaders: testPlan.headers || {},
    });

    testContext = new TestContext();

    // Execute preprocessing steps
    if (testPlan.preprocess) {
      await executePreprocess(
        testPlan.preprocess,
        testContext,
        apiContext,
        testPlan.baseUrl
      );
    }
  });

  test.afterAll(async () => {
    // Cleanup
    await apiContext.dispose();
  });

  // Generate tests for each test case
  for (const testCase of testPlan.tests) {
    test.describe(testCase.name, () => {
      if (testCase.description) {
        test.describe.configure({ mode: "serial" }); // Run assertions in sequence
      }

      for (const assertion of testCase.assertions) {
        test(assertion.description, async () => {
          // Replace variables in input
          const processedInput = testContext.replaceVariables(assertion.input);
          const url = testContext.replaceVariables(assertion.api);

          // Handle parallel requests
          if (assertion.parallel && assertion.parallel > 1) {
            const promises = [];
            for (let i = 0; i < assertion.parallel; i++) {
              promises.push(
                apiContext.fetch(url, {
                  method: assertion.method,
                  data: processedInput,
                  headers: assertion.headers,
                })
              );
            }

            const responses = await Promise.all(promises);

            // Verify all parallel requests
            for (const response of responses) {
              if (assertion.expected.status !== undefined) {
                expect(response.status()).toBe(assertion.expected.status);
              }

              if (assertion.expected.result !== undefined) {
                const data = await response.json();
                expect(deepEqual(data, assertion.expected.result)).toBeTruthy();
              }
            }

            // Execute postprocess only for the first response
            if (assertion.postprocess && responses.length > 0) {
              await executePostprocess(
                assertion.postprocess,
                responses[0],
                testContext
              );
            }
          } else {
            // Single request
            console.log(url);
            const response = await apiContext.fetch(url, {
              method: assertion.method,
              data: processedInput,
              headers: assertion.headers,
            });

            // Verify status code
            if (assertion.expected.status !== undefined) {
              expect(response.status()).toBe(assertion.expected.status);
            }

            // Verify response body
            if (assertion.expected.result !== undefined) {
              const data = await response.json();
              expect(deepEqual(data, assertion.expected.result)).toBeTruthy();
            }

            // Verify headers
            if (assertion.expected.headers) {
              const headers = response.headers();
              for (const [key, value] of Object.entries(
                assertion.expected.headers
              )) {
                expect(headers[key.toLowerCase()]).toBe(value);
              }
            }

            // Execute postprocessing
            if (assertion.postprocess) {
              await executePostprocess(
                assertion.postprocess,
                response,
                testContext
              );
            }
          }
        });
      }
    });
  }
});

import { describe, expect, it } from "vitest";
import { createFetchWithRetry } from "../src/client/http.js";

const createResponse = (status: number) =>
  new Response("{}", { status, headers: { "content-type": "application/json" } });

describe("createFetchWithRetry", () => {
  it("retries on retryable status codes", async () => {
    let calls = 0;
    const baseFetch: typeof fetch = async () => {
      calls += 1;
      if (calls < 3) return createResponse(503);
      return createResponse(200);
    };

    const fetchWithRetry = createFetchWithRetry(baseFetch, { maxRetries: 3, backoffMs: 1, maxBackoffMs: 5 });
    const response = await fetchWithRetry(new Request("https://example.com"));

    expect(response.status).toBe(200);
    expect(calls).toBe(3);
  });

  it("retries POST requests with body without throwing", async () => {
    let calls = 0;
    let lastBody = "";
    const baseFetch: typeof fetch = async (input: RequestInfo | URL) => {
      calls += 1;
      // Actually consume the body to expose the clone bug
      lastBody = await (input as Request).text();
      if (calls < 2) return createResponse(503);
      return createResponse(200);
    };

    const fetchWithRetry = createFetchWithRetry(baseFetch, { maxRetries: 3, backoffMs: 1, maxBackoffMs: 5 });
    const body = JSON.stringify({ key: "value" });
    const response = await fetchWithRetry(
      new Request("https://example.com", { method: "POST", body }),
    );

    expect(response.status).toBe(200);
    expect(calls).toBe(2);
    expect(lastBody).toBe(body);
  });
});

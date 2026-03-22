/**
 * Unit tests for Flows resource operations.
 */

import { describe, expect, it, beforeEach } from "vitest";
import { createMockFetch } from "../utils/mock-fetch.js";
import { createFlow, createFlowList, resetIdCounter } from "../utils/factories/index.js";
import { NexlaClient } from "../../src/client/nexla-client.js";

describe("FlowsResource", () => {
  beforeEach(() => {
    resetIdCounter();
  });

  describe("list operations", () => {
    it("fetches all flows", async () => {
      const flows = createFlowList(3);
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: flows },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.flows.list();

      expect(result).toEqual(flows);
      expect(calls.length).toBe(2);
      expect(calls[1]?.url).toContain("/flows");
    });

    it("passes query parameters correctly", async () => {
      const flows = createFlowList(2);
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: flows },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await client.flows.list({ params: { query: { page: 2, per_page: 10 } } });

      const requestUrl = calls[1]?.url ?? "";
      expect(requestUrl).toContain("page=2");
      expect(requestUrl).toContain("per_page=10");
    });

    it("handles empty results", async () => {
      const { fetchFn } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: [] },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.flows.list();

      expect(result).toEqual([]);
    });
  });

  describe("get operations", () => {
    it("fetches flow by ID", async () => {
      const flow = createFlow({ id: 123 });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: flow },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.flows.get_flow_by_id({ params: { path: { flow_id: 123 } } });

      expect(result).toEqual(flow);
      expect(calls[1]?.url).toContain("/flows/123");
    });

    it("fetches flow using get alias", async () => {
      const flow = createFlow({ id: 456 });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: flow },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.flows.get({ params: { path: { flow_id: 456 } } });

      expect(result).toEqual(flow);
      expect(calls[1]?.url).toContain("/flows/456");
    });

    it("handles flow not found (404)", async () => {
      const { fetchFn } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 404, body: { message: "Flow not found" } },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await expect(
        client.flows.get_flow_by_id({ params: { path: { flow_id: 99999 } } })
      ).rejects.toThrow();
    });
  });

  describe("delete operations", () => {
    it("deletes flow by ID", async () => {
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: { status: "deleted" } },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await client.flows.delete_flow({ params: { path: { flow_id: 123 } } });

      expect(calls[1]?.method).toBe("DELETE");
      expect(calls[1]?.url).toContain("/flows/123");
    });

    it("deletes flow using delete alias", async () => {
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: { status: "deleted" } },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await client.flows.delete({ params: { path: { flow_id: 456 } } });

      expect(calls[1]?.method).toBe("DELETE");
      expect(calls[1]?.url).toContain("/flows/456");
    });
  });

  describe("lifecycle operations", () => {
    it("activates a paused flow", async () => {
      const activatedFlow = createFlow({ id: 123, status: "ACTIVE" });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: activatedFlow },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.flows.flow_activate_with_flow_id({
        params: { path: { flow_id: 123 } },
      });

      expect(result).toEqual(activatedFlow);
      expect(calls[1]?.url).toContain("/flows/123/activate");
      expect(calls[1]?.method).toBe("PUT");
    });

    it("pauses an active flow", async () => {
      const pausedFlow = createFlow({ id: 123, status: "PAUSED" });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: pausedFlow },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.flows.flow_pause_with_flow_id({
        params: { path: { flow_id: 123 } },
      });

      expect(result).toEqual(pausedFlow);
      expect(calls[1]?.url).toContain("/flows/123/pause");
      expect(calls[1]?.method).toBe("PUT");
    });

    it("copies a flow", async () => {
      const copiedFlow = createFlow({ id: 456, name: "Copy of Flow" });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: copiedFlow },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.flows.flow_copy_with_flow_id({
        params: { path: { flow_id: 123 } },
      });

      expect(result).toEqual(copiedFlow);
      expect(calls[1]?.url).toContain("/flows/123/copy");
      expect(calls[1]?.method).toBe("POST");
    });
  });

  describe("copy_and_replace_credentials", () => {
    it("copies flow and replaces source and sink credentials", async () => {
      const originNodeId = 9999;
      const copyResponse = {
        flows: [{ id: 1, origin_node_id: originNodeId, status: "ACTIVE" }],
        data_sources: [{ id: 501, copied_from_id: 500, data_credentials_id: 10 }],
        data_sinks: [{ id: 601, copied_from_id: 600, data_credentials_id: 10 }],
      };
      const updatedSource = { id: 501, data_credentials_id: 20 };
      const updatedSink = { id: 601, data_credentials_id: 30 };
      const refetchResponse = {
        flows: [{ id: 1, origin_node_id: originNodeId, status: "ACTIVE" }],
        data_sources: [{ id: 501, copied_from_id: 500, data_credentials_id: 20 }],
        data_sinks: [{ id: 601, copied_from_id: 600, data_credentials_id: 30 }],
      };

      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: copyResponse },      // POST /flows/100/copy
        { status: 200, body: updatedSource },      // PUT /data_sources/501
        { status: 200, body: updatedSink },        // PUT /data_sinks/601
        { status: 200, body: refetchResponse },    // GET /flows/9999
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.flows.copy_and_replace_credentials(
        100,
        { 500: 20, 600: 30 },
      );

      expect(result).toEqual(refetchResponse);

      // Verify copy request
      expect(calls[1]?.url).toContain("/flows/100/copy");
      expect(calls[1]?.method).toBe("POST");

      // Verify source update
      expect(calls[2]?.url).toContain("/data_sources/501");
      expect(calls[2]?.method).toBe("PUT");

      // Verify sink update
      expect(calls[3]?.url).toContain("/data_sinks/601");
      expect(calls[3]?.method).toBe("PUT");

      // Verify re-fetch
      expect(calls[4]?.url).toContain("/flows/9999");
      expect(calls[4]?.method).toBe("GET");
    });

    it("skips resources not in the mapping", async () => {
      const originNodeId = 9999;
      const copyResponse = {
        flows: [{ id: 1, origin_node_id: originNodeId, status: "ACTIVE" }],
        data_sources: [{ id: 501, copied_from_id: 500, data_credentials_id: 10 }],
        data_sinks: [
          { id: 601, copied_from_id: 600, data_credentials_id: 10 },
          { id: 701, copied_from_id: 700, data_credentials_id: 50 },
        ],
      };
      const updatedSink = { id: 601, data_credentials_id: 20 };
      const refetchResponse = { ...copyResponse };

      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: copyResponse },      // POST /flows/100/copy
        { status: 200, body: updatedSink },        // PUT /data_sinks/601
        { status: 200, body: refetchResponse },    // GET /flows/9999
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      // Only map sink 600, skip source 500 and sink 700
      await client.flows.copy_and_replace_credentials(100, { 600: 20 });

      // Should be 4 calls: auth + copy + sink update + re-fetch (no source update, no sink 700 update)
      expect(calls.length).toBe(4);
      expect(calls[2]?.url).toContain("/data_sinks/601");
    });

    it("moves copied flow to target project", async () => {
      const originNodeId = 9999;
      const copyResponse = {
        flows: [{ id: 1, origin_node_id: originNodeId, status: "ACTIVE" }],
        data_sources: [],
        data_sinks: [],
      };
      const refetchResponse = { ...copyResponse };
      const addFlowsResponse = [{ id: 1, project_id: 42, flow_node_id: originNodeId }];

      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: copyResponse },         // POST /flows/100/copy
        { status: 200, body: addFlowsResponse },     // PUT /projects/42/flows
        { status: 200, body: refetchResponse },       // GET /flows/9999
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await client.flows.copy_and_replace_credentials(100, {}, {}, 42);

      expect(calls[2]?.url).toContain("/projects/42/flows");
      expect(calls[2]?.method).toBe("PUT");
    });

    it("forces reuse_data_credentials to true", async () => {
      const originNodeId = 9999;
      const copyResponse = {
        flows: [{ id: 1, origin_node_id: originNodeId, status: "ACTIVE" }],
        data_sources: [],
        data_sinks: [],
      };

      const { fetchFn, getRequestBody } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: copyResponse },
        { status: 200, body: copyResponse },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await client.flows.copy_and_replace_credentials(
        100,
        {},
        { reuse_data_credentials: false, copy_access_controls: true },
      );

      // Parse the body sent to the copy endpoint
      const parsed = await getRequestBody(1) as Record<string, unknown>;
      expect(parsed.reuse_data_credentials).toBe(true);
      expect(parsed.copy_access_controls).toBe(true);
    });

    it("copies flow with no data_sources or data_sinks", async () => {
      const originNodeId = 9999;
      const copyResponse = {
        flows: [{ id: 1, origin_node_id: originNodeId, status: "ACTIVE" }],
        data_sources: [],
        data_sinks: [],
      };

      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: copyResponse },
        { status: 200, body: copyResponse },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.flows.copy_and_replace_credentials(
        100,
        { 500: 20, 600: 30 },
      );

      expect(result).toEqual(copyResponse);
      // Only 3 calls: auth + copy + re-fetch (no source/sink updates)
      expect(calls.length).toBe(3);
      expect(calls[1]?.url).toContain("/flows/100/copy");
      expect(calls[2]?.url).toContain("/flows/9999");
    });

    it("handles multiple sources with mixed mapping", async () => {
      const originNodeId = 9999;
      const copyResponse = {
        flows: [{ id: 1, origin_node_id: originNodeId, status: "ACTIVE" }],
        data_sources: [
          { id: 501, copied_from_id: 500, data_credentials_id: 10 },
          { id: 502, copied_from_id: 550, data_credentials_id: 15 },
        ],
        data_sinks: [],
      };
      const updatedSource = { id: 501, data_credentials_id: 20 };
      const refetchResponse = { ...copyResponse };

      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: copyResponse },
        { status: 200, body: updatedSource },
        { status: 200, body: refetchResponse },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      // Only map source 500, skip source 550
      await client.flows.copy_and_replace_credentials(100, { 500: 20 });

      // 4 calls: auth + copy + source 501 update + re-fetch (source 502 skipped)
      expect(calls.length).toBe(4);
      expect(calls[2]?.url).toContain("/data_sources/501");
      expect(calls[2]?.method).toBe("PUT");
    });

    it("verifies request bodies for credential updates", async () => {
      const originNodeId = 9999;
      const copyResponse = {
        flows: [{ id: 1, origin_node_id: originNodeId, status: "ACTIVE" }],
        data_sources: [{ id: 501, copied_from_id: 500, data_credentials_id: 10 }],
        data_sinks: [{ id: 601, copied_from_id: 600, data_credentials_id: 10 }],
      };

      const { fetchFn, getRequestBody } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: copyResponse },
        { status: 200, body: { id: 501, data_credentials_id: 20 } },
        { status: 200, body: { id: 601, data_credentials_id: 30 } },
        { status: 200, body: copyResponse },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await client.flows.copy_and_replace_credentials(100, { 500: 20, 600: 30 });

      // Verify source update body has correct credential ID
      const sourceBody = await getRequestBody(2) as Record<string, unknown>;
      expect(sourceBody.data_credentials_id).toBe(20);

      // Verify sink update body has correct credential ID
      const sinkBody = await getRequestBody(3) as Record<string, unknown>;
      expect(sinkBody.data_credentials_id).toBe(30);
    });
  });
});

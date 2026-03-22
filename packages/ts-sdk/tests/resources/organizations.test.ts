/**
 * Unit tests for Organizations resource operations.
 */

import { describe, expect, it, beforeEach } from "vitest";
import { createMockFetch } from "../utils/mock-fetch.js";
import { createOrganization, createOrganizationList, resetIdCounter } from "../utils/factories/index.js";
import { NexlaClient } from "../../src/client/nexla-client.js";

describe("OrganizationsResource", () => {
  beforeEach(() => {
    resetIdCounter();
  });

  describe("list operations", () => {
    it("fetches all organizations", async () => {
      const organizations = createOrganizationList(3);
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: organizations },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.organizations.list();

      expect(result).toEqual(organizations);
      expect(calls.length).toBe(2);
      expect(calls[1]?.url).toContain("/orgs");
    });

    it("passes query parameters correctly", async () => {
      const organizations = createOrganizationList(2);
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: organizations },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await client.organizations.list({ params: { query: { page: 2, per_page: 10 } } });

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

      const result = await client.organizations.list();

      expect(result).toEqual([]);
    });
  });

  describe("get operations", () => {
    it("fetches organization by ID", async () => {
      const organization = createOrganization({ id: 123 });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: organization },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.organizations.get({ params: { path: { org_id: 123 } } });

      expect(result).toEqual(organization);
      expect(calls[1]?.url).toContain("/orgs/123");
    });

    it("handles organization not found (404)", async () => {
      const { fetchFn } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 404, body: { message: "Organization not found" } },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await expect(
        client.organizations.get({ params: { path: { org_id: 99999 } } })
      ).rejects.toThrow();
    });
  });

  describe("update operations", () => {
    it("updates existing organization", async () => {
      const updatedOrganization = createOrganization({ id: 123, name: "Updated Organization" });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: updatedOrganization },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.organizations.update({
        params: { path: { org_id: 123 } },
        body: { name: "Updated Organization" },
      });

      expect(result).toEqual(updatedOrganization);
      expect(calls[1]?.method).toBe("PUT");
      expect(calls[1]?.url).toContain("/orgs/123");
    });
  });

  describe("audit log operations", () => {
    it("fetches audit log for an organization", async () => {
      const auditLog = [
        { id: 1, event: "CREATE", resource_type: "data_source", created_at: "2026-01-01T00:00:00Z" },
        { id: 2, event: "UPDATE", resource_type: "data_source", created_at: "2026-01-02T00:00:00Z" },
      ];
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: auditLog },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.organizations.get_audit_log({
        params: { path: { org_id: 123 } },
      });

      expect(result).toEqual(auditLog);
      expect(calls[1]?.url).toContain("/orgs/123/audit_log");
      expect(calls[1]?.method).toBe("GET");
    });

    it("passes query parameters for audit log", async () => {
      const auditLog = [{ id: 1, event: "CREATE" }];
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: auditLog },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await client.organizations.get_audit_log({
        params: { path: { org_id: 123 }, query: { page: 2, per_page: 10 } },
      });

      const requestUrl = calls[1]?.url ?? "";
      expect(requestUrl).toContain("/orgs/123/audit_log");
      expect(requestUrl).toContain("page=2");
      expect(requestUrl).toContain("per_page=10");
    });

    it("handles empty audit log", async () => {
      const { fetchFn } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: [] },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.organizations.get_audit_log({
        params: { path: { org_id: 123 } },
      });

      expect(result).toEqual([]);
    });
  });
});

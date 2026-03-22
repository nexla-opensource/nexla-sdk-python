/**
 * Unit tests for Users resource operations.
 */

import { describe, expect, it, beforeEach } from "vitest";
import { createMockFetch } from "../utils/mock-fetch.js";
import { createUser, createUserList, resetIdCounter } from "../utils/factories/index.js";
import { NexlaClient } from "../../src/client/nexla-client.js";

describe("UsersResource", () => {
  beforeEach(() => {
    resetIdCounter();
  });

  describe("list operations", () => {
    it("fetches all users", async () => {
      const users = createUserList(3);
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: users },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.users.list();

      expect(result).toEqual(users);
      expect(calls.length).toBe(2);
      expect(calls[1]?.url).toContain("/users");
    });

    it("passes query parameters correctly", async () => {
      const users = createUserList(2);
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: users },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await client.users.list({ params: { query: { page: 2, per_page: 10 } } });

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

      const result = await client.users.list();

      expect(result).toEqual([]);
    });
  });

  describe("get operations", () => {
    it("fetches user by ID", async () => {
      const user = createUser({ id: 123 });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: user },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.users.get({ params: { path: { user_id: 123 } } });

      expect(result).toEqual(user);
      expect(calls[1]?.url).toContain("/users/123");
    });

    it("handles user not found (404)", async () => {
      const { fetchFn } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 404, body: { message: "User not found" } },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await expect(
        client.users.get({ params: { path: { user_id: 99999 } } })
      ).rejects.toThrow();
    });

    it("fetches user with expand parameter", async () => {
      const user = createUser({ id: 123 });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: user },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.users.get_user_expand({ params: { path: { user_id: 123 } } });

      expect(result).toEqual(user);
      expect(calls[1]?.url).toContain("/users/123");
      expect(calls[1]?.url).toContain("expand=1");
    });
  });

  describe("create operations", () => {
    it("creates a new user", async () => {
      const newUser = createUser({ email: "newuser@test.com", full_name: "New User" });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 201, body: newUser },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.users.create({
        body: { email: "newuser@test.com", full_name: "New User" },
      });

      expect(result).toEqual(newUser);
      expect(calls[1]?.method).toBe("POST");
      expect(calls[1]?.url).toContain("/users");
    });
  });

  describe("update operations", () => {
    it("updates existing user", async () => {
      const updatedUser = createUser({ id: 123, full_name: "Updated User" });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: updatedUser },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.users.update({
        params: { path: { user_id: 123 } },
        body: { full_name: "Updated User" },
      });

      expect(result).toEqual(updatedUser);
      expect(calls[1]?.method).toBe("PUT");
      expect(calls[1]?.url).toContain("/users/123");
    });

    it("updates user role", async () => {
      const updatedUser = createUser({ id: 123, role: "admin" });
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: updatedUser },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      const result = await client.users.update_user({
        params: { path: { user_id: 123 } },
        body: { role: "admin" },
      });

      expect(result).toEqual(updatedUser);
      expect(calls[1]?.method).toBe("PUT");
      expect(calls[1]?.url).toContain("/users/123");
    });
  });

  describe("audit log operations", () => {
    it("fetches audit log for a user", async () => {
      const auditLog = [
        { id: 1, event: "LOGIN", created_at: "2026-01-01T00:00:00Z" },
        { id: 2, event: "UPDATE", created_at: "2026-01-02T00:00:00Z" },
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

      const result = await client.users.get_audit_log({
        params: { path: { user_id: 123 } },
      });

      expect(result).toEqual(auditLog);
      expect(calls[1]?.url).toContain("/users/123/audit_log");
      expect(calls[1]?.method).toBe("GET");
    });

    it("passes query parameters for audit log", async () => {
      const auditLog = [{ id: 1, event: "LOGIN" }];
      const { fetchFn, calls } = createMockFetch([
        { status: 200, body: { access_token: "token", expires_in: 7200 } },
        { status: 200, body: auditLog },
      ]);

      const client = new NexlaClient({
        serviceKey: "test-key",
        baseUrl: "https://test.nexla.io/nexla-api",
        fetch: fetchFn,
      });

      await client.users.get_audit_log({
        params: { path: { user_id: 123 }, query: { page: 3, per_page: 25 } },
      });

      const requestUrl = calls[1]?.url ?? "";
      expect(requestUrl).toContain("/users/123/audit_log");
      expect(requestUrl).toContain("page=3");
      expect(requestUrl).toContain("per_page=25");
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

      const result = await client.users.get_audit_log({
        params: { path: { user_id: 123 } },
      });

      expect(result).toEqual([]);
    });
  });
});

import type { NexlaClient } from "../../client/nexla-client.js";
import type { OperationData, OperationInit } from "../../client/operation-types.js";
import { withSkipAuth } from "./utils.js";

export class OrganizationsResource {
  private readonly client: NexlaClient;

  constructor(client: NexlaClient) {
    this.client = client;
  }

  async list(init?: OperationInit<"get_orgs">): Promise<OperationData<"get_orgs">> {
    return this.client.requestOperation("get_orgs", "get", "/orgs", init);
  }

  async get(init?: OperationInit<"get_org">): Promise<OperationData<"get_org">> {
    return this.client.requestOperation("get_org", "get", "/orgs/{org_id}", init);
  }

  async update(init?: OperationInit<"update_org">): Promise<OperationData<"update_org">> {
    return this.client.requestOperation("update_org", "put", "/orgs/{org_id}", init);
  }

  /** Add organization custodians. */
  async add_org_custodians(init?: OperationInit<"add_org_custodians">): Promise<OperationData<"add_org_custodians">> {
    return this.client.requestOperation("add_org_custodians", "post", "/orgs/{org_id}/custodians", init);
  }

  /** Remove Members from an Organization. */
  async delete_org_members(init?: OperationInit<"delete_org_members">): Promise<OperationData<"delete_org_members">> {
    return this.client.requestOperation("delete_org_members", "delete", "/orgs/{org_id}/members", init);
  }

  /** Get Organization by ID */
  async get_org(init?: OperationInit<"get_org">): Promise<OperationData<"get_org">> {
    return this.client.requestOperation("get_org", "get", "/orgs/{org_id}", init);
  }

  /** Get organization custodians. */
  async get_org_custodians(init?: OperationInit<"get_org_custodians">): Promise<OperationData<"get_org_custodians">> {
    return this.client.requestOperation("get_org_custodians", "get", "/orgs/{org_id}/custodians", init);
  }

  /** Get All Members in Organization */
  async get_org_members(init?: OperationInit<"get_org_members">): Promise<OperationData<"get_org_members">> {
    return this.client.requestOperation("get_org_members", "get", "/orgs/{org_id}/members", init);
  }

  /** Get all Organizations */
  async get_orgs(init?: OperationInit<"get_orgs">): Promise<OperationData<"get_orgs">> {
    return this.client.requestOperation("get_orgs", "get", "/orgs", init);
  }

  /** Remove organization custodians. */
  async remove_org_custodians(init?: OperationInit<"remove_org_custodians">): Promise<OperationData<"remove_org_custodians">> {
    return this.client.requestOperation("remove_org_custodians", "delete", "/orgs/{org_id}/custodians", init);
  }

  /** Update an Organization */
  async update_org(init?: OperationInit<"update_org">): Promise<OperationData<"update_org">> {
    return this.client.requestOperation("update_org", "put", "/orgs/{org_id}", init);
  }

  /** Update organization custodians. */
  async update_org_custodians(init?: OperationInit<"update_org_custodians">): Promise<OperationData<"update_org_custodians">> {
    return this.client.requestOperation("update_org_custodians", "put", "/orgs/{org_id}/custodians", init);
  }

  /** Update Organization Members */
  async update_org_members(init?: OperationInit<"update_org_members">): Promise<OperationData<"update_org_members">> {
    return this.client.requestOperation("update_org_members", "put", "/orgs/{org_id}/members", init);
  }

  /** Get Audit Log for an Organization */
  async get_audit_log(init?: OperationInit<"get_org_audit_log">): Promise<OperationData<"get_org_audit_log">> {
    return this.client.requestOperation("get_org_audit_log", "get", "/orgs/{org_id}/audit_log", init);
  }
}
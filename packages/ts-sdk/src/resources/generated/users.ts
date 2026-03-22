import type { NexlaClient } from "../../client/nexla-client.js";
import type { OperationData, OperationInit } from "../../client/operation-types.js";
import { withSkipAuth } from "./utils.js";

export class UsersResource {
  private readonly client: NexlaClient;

  constructor(client: NexlaClient) {
    this.client = client;
  }

  async list(init?: OperationInit<"get_users">): Promise<OperationData<"get_users">> {
    return this.client.requestOperation("get_users", "get", "/users", init);
  }

  async create(init?: OperationInit<"create_user">): Promise<OperationData<"create_user">> {
    return this.client.requestOperation("create_user", "post", "/users", init);
  }

  async get(init?: OperationInit<"get_user">): Promise<OperationData<"get_user">> {
    return this.client.requestOperation("get_user", "get", "/users/{user_id}", init);
  }

  async update(init?: OperationInit<"update_user">): Promise<OperationData<"update_user">> {
    return this.client.requestOperation("update_user", "put", "/users/{user_id}", init);
  }

  /** Create a User */
  async create_user(init?: OperationInit<"create_user">): Promise<OperationData<"create_user">> {
    return this.client.requestOperation("create_user", "post", "/users", init);
  }

  /** Get User by ID */
  async get_user(init?: OperationInit<"get_user">): Promise<OperationData<"get_user">> {
    return this.client.requestOperation("get_user", "get", "/users/{user_id}", init);
  }

  /** Get User by ID with Expanded References */
  async get_user_expand(init?: OperationInit<"get_user_expand">): Promise<OperationData<"get_user_expand">> {
    return this.client.requestOperation("get_user_expand", "get", "/users/{user_id}?expand=1", init);
  }

  /** Get All Users */
  async get_users(init?: OperationInit<"get_users">): Promise<OperationData<"get_users">> {
    return this.client.requestOperation("get_users", "get", "/users", init);
  }

  /** Get All Users with Expanded References */
  async get_users_expand(init?: OperationInit<"get_users_expand">): Promise<OperationData<"get_users_expand">> {
    return this.client.requestOperation("get_users_expand", "get", "/users?expand=1", init);
  }

  /** Modify a User */
  async update_user(init?: OperationInit<"update_user">): Promise<OperationData<"update_user">> {
    return this.client.requestOperation("update_user", "put", "/users/{user_id}", init);
  }

  /** Get Audit Log for a User */
  async get_audit_log(init?: OperationInit<"get_user_audit_log">): Promise<OperationData<"get_user_audit_log">> {
    return this.client.requestOperation("get_user_audit_log", "get", "/users/{user_id}/audit_log", init);
  }
}
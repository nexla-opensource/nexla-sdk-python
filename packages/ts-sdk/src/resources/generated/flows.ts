import type { NexlaClient } from "../../client/nexla-client.js";
import type { OperationData, OperationInit } from "../../client/operation-types.js";
import { withSkipAuth } from "./utils.js";

export class FlowsResource {
  private readonly client: NexlaClient;

  constructor(client: NexlaClient) {
    this.client = client;
  }

  async list(init?: OperationInit<"get_flows">): Promise<OperationData<"get_flows">> {
    return this.client.requestOperation("get_flows", "get", "/flows", init);
  }

  async get(init?: OperationInit<"get_flow_by_id">): Promise<OperationData<"get_flow_by_id">> {
    return this.client.requestOperation("get_flow_by_id", "get", "/flows/{flow_id}", init);
  }

  async delete(init?: OperationInit<"delete_flow">): Promise<OperationData<"delete_flow">> {
    return this.client.requestOperation("delete_flow", "delete", "/flows/{flow_id}", init);
  }

  /** Delete a Flow */
  async delete_flow(init?: OperationInit<"delete_flow">): Promise<OperationData<"delete_flow">> {
    return this.client.requestOperation("delete_flow", "delete", "/flows/{flow_id}", init);
  }

  /** Delete a Flow (by Resource ID) */
  async delete_flow_by_resource_id(init?: OperationInit<"delete_flow_by_resource_id">): Promise<OperationData<"delete_flow_by_resource_id">> {
    return this.client.requestOperation("delete_flow_by_resource_id", "delete", "/{resource_type}/{resource_id}/flow", init);
  }

  /** Activate a Flow */
  async flow_activate_with_flow_id(init?: OperationInit<"flow_activate_with_flow_id">): Promise<OperationData<"flow_activate_with_flow_id">> {
    return this.client.requestOperation("flow_activate_with_flow_id", "put", "/flows/{flow_id}/activate", init);
  }

  /** Activate a Flow (with Resource ID) */
  async flow_activate_with_resource_id(init?: OperationInit<"flow_activate_with_resource_id">): Promise<OperationData<"flow_activate_with_resource_id">> {
    return this.client.requestOperation("flow_activate_with_resource_id", "put", "/{resource_type}/{resource_id}/activate", init);
  }

  /** Copy a Flow */
  async flow_copy_with_flow_id(init?: OperationInit<"flow_copy_with_flow_id">): Promise<OperationData<"flow_copy_with_flow_id">> {
    return this.client.requestOperation("flow_copy_with_flow_id", "post", "/flows/{flow_id}/copy", init);
  }

  /** Generate an AI suggestion for flow documentation */
  async flow_docs_recommendation(init?: OperationInit<"flow_docs_recommendation">): Promise<OperationData<"flow_docs_recommendation">> {
    return this.client.requestOperation("flow_docs_recommendation", "post", "/flows/{flow_id}/docs/recommendation", init);
  }

  /** Pause a Flow */
  async flow_pause_with_flow_id(init?: OperationInit<"flow_pause_with_flow_id">): Promise<OperationData<"flow_pause_with_flow_id">> {
    return this.client.requestOperation("flow_pause_with_flow_id", "put", "/flows/{flow_id}/pause", init);
  }

  /** Pause a Flow (with Resource ID) */
  async flow_pause_with_resource_id(init?: OperationInit<"flow_pause_with_resource_id">): Promise<OperationData<"flow_pause_with_resource_id">> {
    return this.client.requestOperation("flow_pause_with_resource_id", "put", "/{resource_type}/{resource_id}/pause", init);
  }

  /** Get Flow by ID */
  async get_flow_by_id(init?: OperationInit<"get_flow_by_id">): Promise<OperationData<"get_flow_by_id">> {
    return this.client.requestOperation("get_flow_by_id", "get", "/flows/{flow_id}", init);
  }

  /** Get Flow (by Resource ID) */
  async get_flow_by_resource_id(init?: OperationInit<"get_flow_by_resource_id">): Promise<OperationData<"get_flow_by_resource_id">> {
    return this.client.requestOperation("get_flow_by_resource_id", "get", "/{resource_type}/{resource_id}/flow", init);
  }

  /** Get All Flows */
  async get_flows(init?: OperationInit<"get_flows">): Promise<OperationData<"get_flows">> {
    return this.client.requestOperation("get_flows", "get", "/flows", init);
  }

  /**
   * Copy a flow and replace credentials on specified resources.
   *
   * Copies a flow with `reuse_data_credentials: true`, then updates
   * the credentials for resources listed in the mapping. Keys are
   * original resource IDs (source/sink), values are new credential IDs.
   * Resources not in the mapping keep their original credentials.
   *
   * @param flowId - The ID of the flow to copy
   * @param resourceCredentialMapping - Map of original resource IDs to new credential IDs
   * @param copyOptions - Additional copy options (reuse_data_credentials is always forced true)
   * @param targetProjectId - Optional project ID to move the copied flow into
   */
  async copy_and_replace_credentials(
    flowId: number,
    resourceCredentialMapping: Record<number, number>,
    copyOptions?: Record<string, unknown>,
    targetProjectId?: number,
  ): Promise<OperationData<"get_flow_by_id">> {
    // Step 1: Copy the flow with reuse_data_credentials=true
    const body = { ...copyOptions, reuse_data_credentials: true };
    const copiedFlow = await this.client.requestOperation(
      "flow_copy_with_flow_id",
      "post",
      "/flows/{flow_id}/copy",
      { params: { path: { flow_id: flowId } }, body } as OperationInit<"flow_copy_with_flow_id">,
    );

    const flowResponse = copiedFlow as Record<string, unknown>;
    const dataSources = (flowResponse.data_sources ?? []) as Array<Record<string, unknown>>;
    const dataSinks = (flowResponse.data_sinks ?? []) as Array<Record<string, unknown>>;
    const flows = (flowResponse.flows ?? []) as Array<Record<string, unknown>>;

    // Step 2: Update credentials on copied sources that match the mapping
    for (const source of dataSources) {
      const copiedFromId = source.copied_from_id as number | undefined;
      if (copiedFromId != null && copiedFromId in resourceCredentialMapping) {
        await this.client.requestOperation(
          "update_data_source",
          "put",
          "/data_sources/{source_id}",
          {
            params: { path: { source_id: source.id as number } },
            body: { data_credentials_id: resourceCredentialMapping[copiedFromId] },
          } as OperationInit<"update_data_source">,
        );
      }
    }

    // Step 3: Update credentials on copied sinks that match the mapping
    for (const sink of dataSinks) {
      const copiedFromId = sink.copied_from_id as number | undefined;
      if (copiedFromId != null && copiedFromId in resourceCredentialMapping) {
        await this.client.requestOperation(
          "update_data_sink",
          "put",
          "/data_sinks/{sink_id}",
          {
            params: { path: { sink_id: sink.id as number } },
            body: { data_credentials_id: resourceCredentialMapping[copiedFromId] },
          } as OperationInit<"update_data_sink">,
        );
      }
    }

    // Step 4: Optionally move the copied flow into a target project
    const originNodeId = (flows[0]?.origin_node_id ?? flows[0]?.id) as number;
    if (targetProjectId != null) {
      await this.client.requestOperation(
        "add_project_flows",
        "put",
        "/projects/{project_id}/flows",
        {
          params: { path: { project_id: targetProjectId } },
          body: { flows: [originNodeId] },
        } as OperationInit<"add_project_flows">,
      );
    }

    // Step 5: Re-fetch the flow to return an up-to-date response
    return this.client.requestOperation(
      "get_flow_by_id",
      "get",
      "/flows/{flow_id}",
      { params: { path: { flow_id: originNodeId } } } as OperationInit<"get_flow_by_id">,
    );
  }
}
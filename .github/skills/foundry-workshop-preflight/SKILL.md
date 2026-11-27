---
name: foundry-workshop-preflight
description: 'Given an Azure resource group, verify Foundry IQ workshop resources and participant/service-identity permissions. Use for workshop readiness or preflight checks. Independent of environment variables; excludes blob contents and provisioning-admin rights.'
argument-hint: '<resource-group-name> [subscription-id]'
---

# Foundry workshop preflight

Execute read-only Azure checks for the supplied resource group. Use the current
Azure CLI subscription unless one is supplied.

## Boundaries

- Inspect storage accounts and container metadata, not blobs or their contents.
- Exclude provisioning-admin permissions and resource/role creation rights.
- Do not change resources, roles, networking, subscription selection, or files.
- Do not run workshop scripts, ingestion, model inference, or agent turns.
- Never retrieve keys, connection credentials, SAS tokens, or expose secrets.
- Ask before expanding discovery outside the resource group or choosing between
  multiple plausible workshop resource sets.

## Resources

Discover candidates in the resource group, then explicitly enumerate child
projects, deployments and containers; generic resource inventory may omit them.
For containers use `az storage container-rm list` (management-plane metadata),
not commands that implicitly obtain storage keys.

| Required resource | Workshop-specific checks |
|---|---|
| Azure AI Search | Basic tier or higher; managed identity enabled; region/feature and semantic-ranker support for agentic retrieval |
| Storage account and blob container | Successfully provisioned account and an existing container; flag anonymous container access |
| Foundry account and project | Project type `Microsoft.CognitiveServices/accounts/projects`, not hub/workspace; project managed identity enabled |
| Chat deployment | Successfully provisioned; compatible with Search planning/answer synthesis and Foundry agents |
| Embedding deployment | Successfully provisioned; compatible with blob-source vectorization |

Models may reside in another account within the group. Verify the project's
model-access relationship rather than assuming co-location establishes it.
Report discovered resource IDs, deployment aliases, model IDs and versions.
Consult current Microsoft documentation for model and regional compatibility.

Knowledge sources, knowledge bases, project connections, agents and generated
indexing objects are created during the workshop; do not require them beforehand.

## Access and permissions

Test the signed-in Azure CLI principal and the discovered service identities.
Record principal object IDs and target scopes. Account for inherited/group grants,
equivalent custom roles, conditions and visible denies.

| Principal | Required role or equivalent capability | Scope |
|---|---|---|
| Participant | Search Service Contributor and Search Index Data Contributor (includes retrieval reads) | Search service |
| Participant | Foundry User (formerly Azure AI User): agent/model access | Applicable project/resource and model scope |
| Participant | Foundry Project Manager: project connection management | Foundry project |
| Search model-calling managed identity | Cognitive Services OpenAI User | Parent resource hosting each model |
| Foundry project connection identity | Search Index Data Reader | Search service |

The scripts currently use an account-key storage connection. Explicit
`allowSharedKeyAccess=false` conflicts with that workflow. Do not require storage
data-reader RBAC or retrieve keys to verify it. Key validity remains untested.
Only if the user selects managed-identity storage access, verify Storage Blob
Data Reader for the selected Search identity on storage.

The agent script currently uses the chat model ID as its deployment name. Warn
if the discovered alias differs; this is script compatibility, not resource absence.

## Result

State resource group, subscription, tested principal and selected resource mapping.
Return **Resources** and **Access and permissions** tables:

`Check | PASS / FAIL / UNKNOWN / NOT APPLICABLE | Evidence / scope | Required action`

Denied/incomplete discovery or group/role visibility is UNKNOWN, not absence.
Assignment evidence does not prove runtime access, credential selection by
`DefaultAzureCredential`, or service-to-service network reachability. Inspect
network metadata but leave unproven paths UNKNOWN; do not impersonate identities.

Summarize blockers and unverified prerequisites. Never declare full readiness
with required UNKNOWN checks. Confirm no changes, blob-content inspection, or
provisioning-admin checks were performed.

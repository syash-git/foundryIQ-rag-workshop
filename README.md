# Foundry IQ Workshop: IT Help Desk RAG

Build a retrieval-augmented generation (RAG) application for an IT help desk using Microsoft Foundry (formerly Azure AI Foundry) and Foundry IQ. Learn how knowledge sources connect enterprise content to a retrieval pipeline, how a knowledge base orchestrates retrieval, and how a Foundry agent uses that knowledge to answer questions about IT help desk articles. The workshop uses Azure Blob Storage for documents, Azure AI Search for ingestion and retrieval, and Azure OpenAI models for embeddings and answer generation. Modules 1-3 cover the knowledge source, knowledge base, and agent, including portal configuration needed to enable grounded answers. Module 4 runs a minimal local Streamlit chat application.

## Prerequisites

- Python 3.10 or later, Azure CLI, and an editor such as VS Code. Use the Python version supported by all packages in [requirements.txt](requirements.txt).
- An Azure subscription and permission to use the workshop resources. Ask your administrator to provision resources and assign roles before the session if necessary.
- An Azure AI Search service in a region and tier supporting the agentic retrieval features used by the installed SDK, with semantic ranker enabled where required.
- A storage account and a blob container containing approved, non-sensitive IT help desk articles. Upload a few supported text documents or PDFs about topics such as password reset, VPN access, and software installation. Sample articles are not included in this repository.
- A Microsoft Foundry project, not a hub-based project, and deployed chat and embedding models. Verify model availability, quota, and agentic retrieval compatibility in your selected region.
- Network access from your workstation to Search and Foundry, and from Search to storage and the model endpoints. Private networking requires additional administrator configuration.
- A browser for the [Azure portal](https://portal.azure.com/) and [Microsoft Foundry portal](https://ai.azure.com/).

### Authentication And Permissions

The scripts use `DefaultAzureCredential`. Azure CLI sign-in supplies a local development identity unless an earlier credential in that chain takes precedence. Sign-in alone does not grant service permissions.

| Identity | Required access |
| --- | --- |
| Workshop participant | Search Service Contributor and Search Index Data Contributor on Search for knowledge-source setup; Search Index Data Reader for retrieval checks. |
| Workshop participant | Foundry User (formerly Azure AI User) for agent creation and model access; Foundry Project Manager or equivalent connection-management permission for Module 3. Portal role names can vary during rollout. |
| Search service managed identity | Permission to invoke the embedding and chat deployments. For Azure OpenAI, assign Cognitive Services OpenAI User on the model resource. Follow the linked service guidance for any additional Foundry resource permissions. |
| Foundry project managed identity | Search Index Data Reader on Search for the agent's knowledge-base connection in Module 3. |

The current blob script uses a storage connection string, not your CLI identity, to authorize blob reads. A managed-identity storage connection instead requires Storage Blob Data Reader for the Search identity. Role assignment requires an administrator with suitable IAM permissions; allow time for changes to propagate.

## Setup

Run the following from the repository root in PowerShell. No Azure resources are provisioned by these setup commands.

### 1. Create A Virtual Environment

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If activation is blocked by your organization's execution policy, use `.\.venv\Scripts\python.exe` instead of `python` in subsequent Python commands. Do not bypass an organization-managed policy. On macOS or Linux, activation is `source .venv/bin/activate`.

The repository includes a preview Search SDK dependency. Keep the workshop package versions initially; examples in newer service documentation may use different API contracts.

### 2. Sign In To Azure

```powershell
az login
az account set --subscription "<subscription-id-or-name>"
az account show --query "{name:name, id:id, tenantId:tenantId}" --output table
```

Choose the tenant and subscription that own the workshop resources. These commands do not configure service roles.

### 3. Create And Configure The Environment File

The template is named [env.example](env.example), without a leading dot. Copy it only if you do not already have a local `.env` file:

```powershell
if (-not (Test-Path .env)) {
    Copy-Item env.example .env
}
```

> Security: the existing template contains a populated storage connection string. Treat it as sensitive, replace it with your own authorized value, and rotate the exposed storage key if valid. Do not publish the template unchanged or commit your `.env` file. Ensure `.env` and `.venv/` are excluded by your repository's ignore rules before committing anything.

Replace every resource-specific value in your local `.env`, including populated examples:

| Variable | Value to supply |
| --- | --- |
| `FOUNDRY_PROJECT_ENDPOINT` | Project endpoint from Foundry: `https://<resource>.services.ai.azure.com/api/projects/<project>`. |
| `AZURE_SEARCH_ENDPOINT` | Search service root: `https://<service>.search.windows.net`. |
| `KNOWLEDGE_SOURCE_NAME` | Knowledge source name, shared by source and knowledge-base creation. |
| `KNOWLEDGE_BASE_NAME` | Knowledge base name, shared by knowledge-base creation, the project connection, and the agent's MCP URL. |
| `FOUNDRY_PROJECT_CONNECTION_NAME` | Project connection name, shared by connection and agent creation. |
| `FOUNDRY_AGENT_NAME` | Agent name, shared by agent creation and the local chat application. |
| `AZURE_STORAGE_CONNECTION_STRING` | Authorized storage connection string. Keep it private. |
| `AZURE_STORAGE_CONTAINER_NAME` | Existing container holding the IT articles, for example `it-desk`. |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource root, for example `https://<resource>.openai.azure.com`. Do not append `/openai/v1` for the Search model configuration. |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | Deployment name of a chat model supported by your knowledge base. |
| `AZURE_OPENAI_CHAT_MODEL` | Underlying model ID for Search, not a custom deployment alias. The current agent script also uses this value as its deployment name; see Module 3. |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding deployment name. |
| `AZURE_OPENAI_EMBEDDING_MODEL` | Underlying embedding model ID, for example `text-embedding-3-large`. |

### 4. Load Values Into The Current Terminal

Keep the four component names together under `# Names of the Foundry components being created` in `.env`. Edit them there rather than in the scripts, then reload the environment before running any module. Changing a name targets a different component; it does not rename an existing Azure resource.

The scripts use `os.environ["NAME"]` for environment settings, with no fallback values. A missing variable raises `KeyError` immediately. The scripts do not automatically load `.env`. Run this loader after editing the file and whenever you open a new PowerShell terminal. It supports the template's simple `KEY=value` format and optional matching outer quotes, not variable interpolation or multiline values.

```powershell
Get-Content .env | ForEach-Object {
    $entry = $_.Trim()
    if ($entry -and -not $entry.StartsWith('#')) {
        $parts = $entry -split '=', 2
        if ($parts.Count -ne 2) { throw 'Expected KEY=value in .env' }
        $name = $parts[0].Trim()
        $value = $parts[1].Trim()
        if ($value.Length -ge 2 -and (
            ($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))
        )) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($name, $value, 'Process')
    }
}
```

Check that required values are populated without printing credentials:

```powershell
$required = @(
    'FOUNDRY_PROJECT_ENDPOINT', 'AZURE_SEARCH_ENDPOINT',
    'KNOWLEDGE_SOURCE_NAME', 'KNOWLEDGE_BASE_NAME',
    'FOUNDRY_PROJECT_CONNECTION_NAME', 'FOUNDRY_AGENT_NAME',
    'AZURE_STORAGE_CONNECTION_STRING', 'AZURE_STORAGE_CONTAINER_NAME',
    'AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_CHAT_DEPLOYMENT',
    'AZURE_OPENAI_CHAT_MODEL', 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT',
    'AZURE_OPENAI_EMBEDDING_MODEL'
)
foreach ($name in $required) {
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name, 'Process'))) {
        throw "Missing environment variable: $name"
    }
}
Write-Host 'Required environment variables are populated.'
```

## Workshop Modules

Complete the modules in order, using the same terminal:

| Module | Outcome | Starting script |
| --- | --- | --- |
| [Module 1: Create A Blob Knowledge Source](modules/module-01-knowledge-source.md) | Connect IT help desk documents to managed ingestion. | [cerate-ks-blob-storage.py](cerate-ks-blob-storage.py) |
| [Module 2: Create A Knowledge Base](modules/module-02-knowledge-base.md) | Configure retrieval and inspect the underlying Search objects. | [create-kb.py](create-kb.py) |
| [Module 3: Create A RAG Agent](modules/module-03-rag-agent.md) | Create an agent, attach the knowledge base, and verify it in Foundry. | [create-agent.py](create-agent.py) |
| [Module 4: Invoke The Agent With A Local Web App](modules/module-04-local-web-app.md) | Chat with the existing agent locally. | [rag_webapp.py](src/rag_webapp.py) |

The knowledge-source script is actually named [cerate-ks-blob-storage.py](cerate-ks-blob-storage.py). Commands intentionally preserve that spelling. The modules describe small participant changes needed to align source names and configure retrieval; the supplied scripts are starting points, not a fully wired RAG application.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `KeyError` for a configuration value | Load `.env` in the same terminal that runs Python. |
| Import or missing SDK attribute error | Confirm the active interpreter and install [requirements.txt](requirements.txt); check the SDK/API compatibility notes before upgrading. |
| HTTP 401 or 403 | Verify tenant, credential selection, role scope, managed identities, and role propagation. Your local user and the service identities are separate callers. |
| Knowledge source not found | Align the hard-coded source names as explained in Module 2. |
| Index contains no documents | Inspect the generated indexer's execution history, blob contents, storage access, model permissions, and network access. |
| Model or deployment not found | Distinguish the underlying model ID from its deployment name and use the correct resource endpoint. |
| Agent answers without IT article evidence | Complete Module 3's knowledge-base attachment and inspect a retrieval tool call, not just the answer text. |

## Costs And Cleanup

Search capacity, storage, embedding generation, and chat/retrieval calls can incur charges. Use a dedicated workshop environment and monitor costs.

After the workshop, delete only resources you own: remove the workshop agent versions and project connection, then delete the knowledge base before deleting its referenced knowledge source. Deleting a generated blob knowledge source also removes its generated Search ingestion objects, but not the source blobs. Remove dedicated Azure services or the dedicated resource group only after confirming nothing is shared. Deleting knowledge objects alone does not stop Search service capacity charges.

## References

- [Blob knowledge sources](https://learn.microsoft.com/en-us/azure/search/agentic-knowledge-source-how-to-blob)
- [Create a knowledge base](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-how-to-create-knowledge-base)
- [Connect agents to Foundry IQ](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/foundry-iq-connect)
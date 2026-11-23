import requests
import os
from azure.identity import DefaultAzureCredential
from azure.identity import get_bearer_token_provider
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool


project_connection_name = os.environ["FOUNDRY_PROJECT_CONNECTION_NAME"]

knowledge_base_name = os.environ["KNOWLEDGE_BASE_NAME"]

project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
project_resource_id = os.environ["FOUNDRY_PROJECT_RESOURCE_ID"]
search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]

project_client = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())

mcp_endpoint = f"{search_endpoint}/knowledgebases/{knowledge_base_name}/mcp?api-version=2026-11-01-preview" # This endpoint enables the MCP connection between the agent and knowledge base

bearer_token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://management.azure.com/.default")


headers = {
    "Authorization": f"Bearer {bearer_token_provider()}",
}

response = requests.put(
    f"https://management.azure.com{project_resource_id}/connections/{project_connection_name}?api-version=2025-10-01-preview",
    headers=headers,
    json={
        "name": project_connection_name,
        "type": "Microsoft.MachineLearningServices/workspaces/connections",
        "properties": {
            "authType": "ProjectManagedIdentity",
            "category": "RemoteTool",
            "target": mcp_endpoint,
            "isSharedToAll": True,
            "audience": "https://search.azure.com/",
            "metadata": { "ApiType": "Azure" }
        }
    }
)

response.raise_for_status()
print(f"Connection '{project_connection_name}' created or updated successfully.")

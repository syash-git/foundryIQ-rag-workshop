import os
import requests
from azure.identity import DefaultAzureCredential
from azure.identity import get_bearer_token_provider
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool



project_connection_name = os.environ["FOUNDRY_PROJECT_CONNECTION_NAME"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]
knowledge_base_name = os.environ["KNOWLEDGE_BASE_NAME"]


chat_model = os.environ["AZURE_OPENAI_CHAT_MODEL"]
project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]

project_client = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())
mcp_endpoint = f"{search_endpoint}/knowledgebases/{knowledge_base_name}/mcp?api-version=2026-11-01-preview"


instructions = """
You are a helpful assistant that must use the knowledge base to answer all the questions from user. You must never answer from your own knowledge under any circumstances.
Every answer must always provide annotations for using the MCP knowledge base tool and render them as: `【message_idx:search_idx†source_name】`
If you cannot find the answer in the provided knowledge base you must respond with "I don't know".
"""



mcp_kb_tool = MCPTool(
    server_label="knowledge-base",
    server_url=mcp_endpoint,
    require_approval="never",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id=project_connection_name
)

agent = project_client.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model=chat_model,
        instructions=instructions,
        tools=[mcp_kb_tool]
    )
)

print(f"AI agent '{agent_name}' created or updated successfully")

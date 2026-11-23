# Create a knowledge base
import os

from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    AzureOpenAIVectorizerParameters,
    KnowledgeBase,
    KnowledgeBaseAzureOpenAIModel,
    KnowledgeSourceReference,
)
from azure.search.documents.knowledgebases.models import (
    KnowledgeRetrievalAutoReasoningEffort,
    KnowledgeRetrievalOutputMode,
)

search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
chat_deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
chat_model = os.environ["AZURE_OPENAI_CHAT_MODEL"]

knowledge_source_name = os.environ["KNOWLEDGE_SOURCE_NAME"]
knowledge_base_name = os.environ["KNOWLEDGE_BASE_NAME"]
knowledge_base_description = "This knowledge base handles questions directed at IT service desk knowledge sources."
retrieval_instructions = f"Use the {knowledge_source_name} knowledge source for queries related to the IT service desk"
answer_instructions = "Answer in a concise sentences, user friendly manner"
    
index_client = SearchIndexClient(endpoint = search_endpoint, credential = DefaultAzureCredential())

aoai_params = AzureOpenAIVectorizerParameters(
    resource_url = openai_endpoint,
    deployment_name = chat_deployment,
    model_name = chat_model,
)

knowledge_base = KnowledgeBase(
    name = knowledge_base_name,
    description = knowledge_base_description,
    retrieval_instructions = retrieval_instructions,
    answer_instructions = answer_instructions,
    output_mode = KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS,
    knowledge_sources = [
        KnowledgeSourceReference(name = knowledge_source_name),
    ],
    models = [KnowledgeBaseAzureOpenAIModel(azure_open_ai_parameters = aoai_params)],
    encryption_key = None,
    retrieval_reasoning_effort = KnowledgeRetrievalAutoReasoningEffort(),
)

index_client.create_or_update_knowledge_base(knowledge_base)
print(f"Knowledge base '{knowledge_base.name}' created or updated successfully.")
# Create a blob knowledge source
import os

from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    AzureBlobKnowledgeSource,
    AzureBlobKnowledgeSourceParameters,
    AzureOpenAIVectorizerParameters,
    KnowledgeBaseAzureOpenAIModel,
    KnowledgeSourceContentExtractionMode,
)
from azure.search.documents.knowledgebases.models import (
    KnowledgeSourceAzureOpenAIVectorizer,
    KnowledgeSourceIngestionParameters,
    KnowledgeSourceNetworkAccessMode,
)

search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
blob_connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
blob_container_name = os.environ["AZURE_STORAGE_CONTAINER_NAME"]
openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
chat_deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
chat_model = os.environ["AZURE_OPENAI_CHAT_MODEL"]
embedding_deployment = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
embedding_model = os.environ["AZURE_OPENAI_EMBEDDING_MODEL"]
knowledge_source_name = os.environ["KNOWLEDGE_SOURCE_NAME"]


knowledge_source_description = """This knowledge source contains support articles covering sign-in,
billing, data export, dashboards, API integration, the mobile app, notifications,
security and support policy, with step-by-step fixes, error codes and
platform-specific guidance."""


index_client = SearchIndexClient(
    endpoint=search_endpoint, credential=DefaultAzureCredential()
)

knowledge_source = AzureBlobKnowledgeSource(
    name=knowledge_source_name,
    description = knowledge_source_description,
    azure_blob_parameters = AzureBlobKnowledgeSourceParameters(
        connection_string=blob_connection_string,
        container_name=blob_container_name,
        ingestion_parameters = KnowledgeSourceIngestionParameters(
            embedding_model = KnowledgeSourceAzureOpenAIVectorizer(
                azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                    resource_url=openai_endpoint,
                    deployment_name=embedding_deployment,
                    model_name=embedding_model,
                )
            ),
            content_extraction_mode = KnowledgeSourceContentExtractionMode.MINIMAL,
            ingestion_schedule = None,
        )
    )
)

index_client.create_or_update_knowledge_source(knowledge_source)

print(f"Knowledge source '{knowledge_source.name}' created or updated successfully.")
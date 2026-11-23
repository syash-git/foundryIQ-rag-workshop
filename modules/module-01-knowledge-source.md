# Module 1: Create A Blob Knowledge Source

[Workshop setup](../README.md) | [Next: Knowledge Base](module-02-knowledge-base.md)

## Goal

Create a reusable Foundry IQ knowledge source that ingests IT help desk articles from Azure Blob Storage. Understand which settings connect the source to the documents and embedding deployment.

## Before You Start

Complete the [README setup](../README.md#setup), load the environment variables, and upload approved IT articles to your configured blob container. The script does not create a storage account, container, model deployment, or Search service.

## 1. Inspect The Blob Connection

Open [cerate-ks-blob-storage.py](../cerate-ks-blob-storage.py). Its central configuration is:

```python
azure_blob_parameters = AzureBlobKnowledgeSourceParameters(
    connection_string=blob_connection_string,
    container_name=blob_container_name,
    ingestion_parameters=KnowledgeSourceIngestionParameters(
        embedding_model=KnowledgeSourceAzureOpenAIVectorizer(
            azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                resource_url=openai_endpoint,
                deployment_name=embedding_deployment,
                model_name=embedding_model,
            )
        ),
        content_extraction_mode=KnowledgeSourceContentExtractionMode.MINIMAL,
        ingestion_schedule=None,
    ),
)
```

| Setting | Purpose |
| --- | --- |
| `connection_string` | Selects the storage account and authorizes the service's blob access. It comes from `AZURE_STORAGE_CONNECTION_STRING`. |
| `container_name` | Selects the existing container through `AZURE_STORAGE_CONTAINER_NAME`. |
| `embedding_model` | Configures the Azure OpenAI deployment that turns content into vectors for similarity search. |
| `content_extraction_mode` | Uses minimal extraction rather than explicitly configuring Content Understanding-based standard extraction. |
| `ingestion_schedule=None` | Does not request an explicit recurring schedule. Inspect the generated configuration before assuming when new blobs will be ingested. |

The script does not restrict ingestion to a folder. Use a dedicated container containing only workshop-approved documents.

The Search client authenticates with `DefaultAzureCredential`. The storage connection string and the Search service's model-calling identity are separate from that local authentication.

## 2. Confirm The Knowledge Source Name

The script reads `KNOWLEDGE_SOURCE_NAME` from the process environment and passes it to `AzureBlobKnowledgeSource`. Set it in the component-names section of `.env` and reload the environment before running the script.

Module 2 reads the same variable to attach this source. In a shared service, agree on unique names with your instructor before running create-or-update operations.

## 3. Create The Source

From the repository root, run:

```powershell
python .\cerate-ks-blob-storage.py
```

Expected confirmation:

```text
Knowledge source '<KNOWLEDGE_SOURCE_NAME>' created or updated successfully.
```

This confirms the definition was accepted, not that every document has finished ingesting. Re-running targets the same source and may update its configuration.

## 4. Verify Ingestion

1. Open the [Azure portal](https://portal.azure.com/) and select the Search service matching `AZURE_SEARCH_ENDPOINT`.
2. Locate the knowledge source under the service's knowledge/agentic retrieval area, where available, and confirm the source name and container. Portal labels vary by release.
3. Open **Indexers** under **Search management**. Find the generated indexer associated with this source and inspect its execution history for completed ingestion and errors.
4. Open the associated index under **Indexes**, then use **Search explorer** with a simple `*` search. Confirm that indexed content comes from one of your IT articles.
5. If ingestion is empty or failed, check the container contents, supported document format, storage credential, Search identity's embedding-model permissions, and networking before continuing.

Do not display connection strings in screenshots or paste full source definitions into shared logs. Avoid editing generated ingestion objects directly.

## Checkpoint

- A knowledge source matching `KNOWLEDGE_SOURCE_NAME` exists in the intended Search service.
- Its blob connection points to the intended IT help desk container.
- Ingestion completed without unresolved errors and indexed article content is visible.

Continue to [Module 2](module-02-knowledge-base.md) to connect this source to a knowledge base and inspect the ingestion objects in detail.

## Reference

[Create a blob knowledge source](https://learn.microsoft.com/en-us/azure/search/agentic-knowledge-source-how-to-blob)
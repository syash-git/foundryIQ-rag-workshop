# Module 2: Create A Knowledge Base

[Previous: Knowledge Source](module-01-knowledge-source.md) | [Workshop setup](../README.md) | [Next: RAG Agent](module-03-rag-agent.md)

## Goal

Create a knowledge base that references your IT help desk knowledge source, configures model-assisted retrieval and answer synthesis, and provides a retrieval endpoint for an agent.

## Before You Start

Complete Module 1 and verify that the generated index contains your articles. Keep the virtual environment active and the environment variables loaded.

## 1. Align The Source Reference

Open [create-kb.py](../src/create-kb.py). The script reads `KNOWLEDGE_SOURCE_NAME` and `KNOWLEDGE_BASE_NAME` from the environment, using the component names configured in `.env`.

The source reference and retrieval instructions use that same source name:

```python
retrieval_instructions = f"Use the {knowledge_source_name} knowledge source for queries related to the IT service desk"
knowledge_sources = [
    KnowledgeSourceReference(name=knowledge_source_name),
]
```

Keep these names in `.env` and reload the environment after editing them. Connection and agent creation use the same knowledge-base variable. A prompt mentioning a source does not attach it; membership is established by `knowledge_sources`.

## 2. Understand The Knowledge Base

| Configuration | Behavior |
| --- | --- |
| `KnowledgeSourceReference` | Attaches the existing knowledge source by name on the same Search service. |
| `models` | Configures the chat model deployment used for model-backed retrieval operations. |
| `retrieval_instructions` | Guides source selection and retrieval behavior. |
| `answer_instructions` | Guides the style of synthesized answers. |
| `KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS` | Requests an answer grounded in retrieved content rather than only raw extractive grounding data. |
| `KnowledgeRetrievalAutoReasoningEffort()` | Lets the service select retrieval reasoning effort where supported by the SDK/API and model combination. |

The script builds model parameters from `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_CHAT_DEPLOYMENT`, and `AZURE_OPENAI_CHAT_MODEL`. A deployment alias and the underlying model ID are not interchangeable. Search's managed identity must be authorized to call that model resource; local CLI sign-in does not grant that service access.

## 3. Create The Knowledge Base

From the repository root, run:

```powershell
python .\create-kb.py
```

Expected confirmation:

```text
Knowledge base '<KNOWLEDGE_BASE_NAME>' created or updated successfully.
```

If the service rejects the source reference, verify the exact source name and Search endpoint. If it rejects the model or reasoning configuration, verify supported models and SDK/API compatibility before proceeding.

## 4. Inspect What Exists Under The Hood

The ingestion resources are created when the **blob knowledge source** is created in Module 1, not by the knowledge-base creation call. The knowledge base references that reusable source and adds retrieval orchestration; it does not create a second index for the same source.

| Search object | Role in this workshop |
| --- | --- |
| Data source | Represents the storage connection and container to ingest. |
| Skillset | Defines the generated enrichment pipeline, including chunking and embedding generation for this vectorized blob source. |
| Index | Stores searchable article content/chunks, metadata, vectors, and retrieval configuration. It is not the original blob container. |
| Indexer | Reads the blobs and runs extraction, enrichment, and indexing using the data source, skillset, and target index. |
| Knowledge source | Owns the source configuration and links it to the generated ingestion resources. |
| Knowledge base | References one or more sources and configures retrieval, reasoning, and answer output. |

In the [Azure portal](https://portal.azure.com/), select your Search service and inspect **Data sources**, **Skillsets**, **Indexes**, and **Indexers** under **Search management**. Use the source's generated-resource references to identify the correct objects rather than assuming a suffix or choosing an unrelated index.

1. Confirm the data source targets the workshop container without sharing its credentials.
2. Inspect the skillset to identify the text-processing and embedding steps.
3. Inspect the index schema for text, metadata, vector fields, and semantic configuration.
4. Inspect the indexer's most recent execution, processed items, and errors. Chunk counts need not equal blob counts.

Treat generated resources as a managed pipeline. Do not directly alter their names, field mappings, or skill definitions during this lab.

## 5. Verify The Knowledge Base

Locate the knowledge base named by `KNOWLEDGE_BASE_NAME` in the Search/Foundry knowledge-base experience, where available. Confirm that its source membership matches `KNOWLEDGE_SOURCE_NAME` and its model deployment matches your environment. If the portal provides a retrieval test, ask a question whose answer you can point to in an uploaded article, such as "How do I reset my password?" only if that procedure is present in your content.

Inspect returned evidence or source references as well as the answer. If this portal does not expose a knowledge-base test, perform the grounded-answer check in Module 3 after attaching the agent. Definition creation alone is not evidence that retrieval works.

## Checkpoint

- The configured knowledge base references the source created in Module 1.
- You can explain the separate roles of the index, indexer, and skillset.
- The index is populated and the configured chat deployment is available for retrieval and answer synthesis.

Continue to [Module 3](module-03-rag-agent.md).

## References

- [Create a knowledge base](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-how-to-create-knowledge-base)
- [Generated blob-source objects](https://learn.microsoft.com/en-us/azure/search/agentic-knowledge-source-how-to-blob#review-the-generated-objects)
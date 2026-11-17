# AI-103: RAG Architecture

## 1. What is RAG Architecture?

**Retrieval-Augmented Generation (RAG)** combines information retrieval with a generative model so responses can be grounded in private, domain-specific, or frequently changing data.

The core flow is:

```text
RETRIEVE -> AUGMENT -> GENERATE
```

- **Retrieve:** Find relevant content from an index or data source.
- **Augment:** Add retrieved content to the model input as grounding data.
- **Generate:** Use an LLM to produce an answer grounded in the retrieved data.

### AI-103 exam memory

```text
Need current/private knowledge?
-> RAG

Need learned behavior/style?
-> Prompt engineering / possibly fine-tuning
```

---

# 2. Why RAG?

An LLM doesn't automatically know:

- Your private enterprise documents
- Information created after its training data
- Rapidly changing policies/prices/status data
- Content stored in internal databases and search indexes

RAG retrieves relevant information at query time and provides it to the model.

```text
Private / Current Documents
          |
          v
      Search Index
          |
          v
      Retrieval
          |
          v
   Grounding Context
          |
          v
          LLM
          |
          v
   Grounded Response
```

---

# 3. RAG Has Two Major Pipelines

A complete RAG architecture usually has:

```text
1. DATA / INDEXING PIPELINE
2. QUERY / INFERENCE PIPELINE
```

This distinction is highly important for AI-103.

---

# 4. Indexing Pipeline

The indexing pipeline prepares enterprise content for retrieval.

```text
Data Sources
    |
    v
Content Extraction
    |
    v
Chunking
    |
    v
Embedding Generation
    |
    v
Metadata + Permissions
    |
    v
Search Index
```

With Azure AI Search, a common managed pipeline is:

```text
Azure Blob Storage / supported source
             |
             v
          Indexer
             |
             v
          Skillset
             |
       +-----+------+
       |            |
   Text Split    Embedding Skill
       |            |
       +-----+------+
             |
             v
      Azure AI Search Index
```

---

# 5. Data Sources

RAG content can originate from systems such as:

- Azure Blob Storage
- Databases
- SharePoint and enterprise knowledge sources through supported architectures/connectors
- APIs
- Data Lake storage
- Uploaded files

### Exam rule

```text
Data source = original content
Search index = retrieval-optimized representation
```

---

# 6. Content Extraction

Before documents can be searched effectively, text and structure need to be extracted.

Simple documents may need basic text extraction.

Complex documents may need:

- OCR
- Layout detection
- Table extraction
- Heading/section recognition
- Image descriptions

For complex PDFs, Azure Document Intelligence / Azure Content Understanding capabilities can help preserve structure before chunking.

---

# 7. Chunking

Large documents are divided into meaningful chunks.

```text
Large Document
      |
      +-- Chunk 1
      +-- Chunk 2
      +-- Chunk 3
```

### Why chunk?

- Respect model input limits
- Improve retrieval precision
- Avoid embedding multiple unrelated topics as one vector
- Reduce irrelevant grounding text

### Exam rule

```text
Too large -> broad/irrelevant retrieval
Too small -> insufficient context
```

Use overlap or structure-aware chunking when context is split across boundaries.

---

# 8. Embeddings

An embedding model transforms a chunk into a numeric vector.

```text
Chunk text
   |
   v
Embedding Model
   |
   v
[0.14, -0.56, 0.82, ...]
```

The vector represents semantic meaning and can be stored in an Azure AI Search vector field.

### Critical exam rule

```text
Embedding model -> vector representation
LLM             -> generated response
```

Do not confuse them.

---

# 9. Metadata

Each chunk should preserve useful metadata.

Example:

```text
chunkId
parentDocumentId
title
heading
pageNumber
sourceUrl
department
lastUpdated
accessControlMetadata
```

Metadata supports:

- Filtering
- Citations
- Traceability
- Security trimming
- Reconstructing parent context

### Exam clue

```text
Need citations or department/permission filtering?
-> Preserve metadata
```

---

# 10. Search Index

The index commonly stores both raw text and vectors.

```text
id
content
title
sourceUrl
metadata
contentVector
```

This allows different retrieval techniques:

```text
Keyword Search
Vector Search
Hybrid Search
Filters
Semantic Ranking
```

---

# 11. Query / Inference Pipeline

The query-time architecture commonly looks like:

```text
User Question
      |
      v
Query Processing
      |
      v
Search / Retrieval
      |
      v
Top Relevant Chunks
      |
      v
Prompt Construction
      |
      v
Generative Model
      |
      v
Grounded Answer + Citations
```

---

# 12. Query Embedding

For vector or hybrid retrieval, query text is converted into a vector.

```text
User Question
     |
     v
Embedding Model / Vectorizer
     |
     v
Query Vector
```

### Important rule

Use a compatible embedding space for document vectors and query vectors, typically the same embedding model/configuration.

---

# 13. Keyword Retrieval

Keyword/full-text search is useful when exact wording matters.

Examples:

```text
AUTH-2047
Invoice-99812
Microsoft Foundry
Employee ID
```

In Azure AI Search, lexical text retrieval commonly uses BM25 relevance ranking.

### Memory

```text
Exact words / IDs / codes
-> Keyword Search
```

---

# 14. Vector Retrieval

Vector search finds content based on semantic similarity.

Example:

```text
Query:
"recover account access"

Document:
"reset forgotten credentials"
```

Different wording, similar meaning.

### Memory

```text
Same meaning, different wording
-> Vector Search
```

---

# 15. Hybrid Retrieval

Hybrid search combines keyword and vector search.

```text
              User Query
                  |
         +--------+--------+
         |                 |
         v                 v
Keyword Search       Vector Search
    BM25               HNSW/eKNN
         |                 |
         +--------+--------+
                  |
                  v
                 RRF
                  |
                  v
         Combined Results
```

### Exam memory

```text
Keyword + Vector = Hybrid Search
Hybrid rank fusion = RRF
```

Hybrid search is especially useful when queries contain both exact identifiers and natural-language intent.

---

# 16. Semantic Reranking

After candidate retrieval, a semantic ranker can reorder results using semantic relevance.

```text
Hybrid Results
      |
      v
Semantic Ranker
      |
      v
Better Ordered Results
```

### High-value distinction

```text
RRF -> merges ranked lists
Semantic Ranker -> semantically reranks candidates
```

---

# 17. Retrieval Top-K

The system usually selects a limited number of highly ranked chunks.

```text
Top-K candidates
       |
       v
Prompt context
```

Too few:

```text
May miss evidence
```

Too many:

```text
More noise
More prompt tokens
Higher latency/cost
Potential distraction for LLM
```

Tune K by evaluation, not by assuming one universal value.

---

# 18. Prompt Construction / Augmentation

Retrieved chunks are inserted into the model input along with instructions.

```text
System Instructions
+
Retrieved Context
+
User Question
       |
       v
Augmented Prompt
```

Example:

```text
Answer using only the supplied context.
If the answer isn't supported by the context,
say that you don't have enough information.

Context:
<retrieved chunks>

Question:
<user question>
```

### Exam rule

```text
Retrieval supplies KNOWLEDGE.
Prompt instructions define BEHAVIOR.
```

---

# 19. Generation

The augmented prompt is passed to a generative model.

```text
Grounding Context + Question
           |
           v
           LLM
           |
           v
Grounded Natural-Language Answer
```

The model can synthesize information from multiple retrieved chunks, subject to the model and application design.

---

# 20. Citations

A production RAG system should preserve source references through the pipeline.

```text
Retrieved Chunk
      |
      +-- source URL
      +-- document title
      +-- page number
      +-- chunk ID
```

The application can associate generated claims with relevant sources.

### Exam clue

```text
Need users to verify answers
-> Preserve source metadata and return citations
```

---

# 21. Classic RAG Architecture

Classic RAG follows a primarily predetermined workflow.

```text
             OFFLINE / INDEXING

Documents
   |
Extract
   |
Chunk
   |
Embed
   |
Azure AI Search Index


             ONLINE / QUERY

User Question
   |
Query Embedding
   |
Hybrid Search
   |
RRF
   |
Semantic Ranker
   |
Top Chunks
   |
Prompt Augmentation
   |
LLM
   |
Answer + Citations
```

Microsoft guidance describes classic RAG using hybrid search and semantic ranking as a proven approach, particularly for simpler retrieval needs or where generally available features are preferred.

---

# 22. Agentic RAG Architecture

Agentic RAG changes retrieval from a fixed pipeline into a capability that an agent can invoke dynamically.

```text
User Question
      |
      v
AI Agent / Reasoning
      |
      v
Does retrieval need to occur?
      |
      v
Choose Source / Tool
      |
      v
Decompose Query
      |
 +----+-----+-----+
 |          |     |
 v          v     v
Query A  Query B Query C
 |          |     |
 +----+-----+-----+
      |
      v
Evaluate Results
      |
   Enough?
   /    \
 No     Yes
 |       |
Refine   v
 |    Generate Answer
 +------^
```

### Core difference

```text
Classic RAG
-> Application defines the retrieval sequence

Agentic RAG
-> Agent can decide when/how to retrieve and can iterate
```

---

# 23. Agentic Retrieval in Azure AI Search

Azure AI Search agentic retrieval is designed for complex conversational queries.

It can support:

- LLM-based query planning
- Query decomposition
- Conversation-history context
- Multiple focused subqueries
- Parallel subquery execution
- Semantic reranking
- Merged grounding responses
- Source references
- Activity logs

### Example

Question:

```text
Compare our East US and West Europe reliability SLAs
and explain the differences.
```

Agentic retrieval can decompose this into separate searches and combine the relevant data.

---

# 24. Classic RAG vs Agentic RAG

| Classic RAG | Agentic RAG |
|---|---|
| Predetermined retrieval pipeline | Dynamic retrieval decisions |
| Usually one primary retrieval flow | Multi-query / iterative retrieval |
| Application controls search steps | Agent can determine retrieval steps |
| Lower complexity | Higher orchestration complexity |
| Lower/steadier latency | Can add latency due to multiple steps |
| Good for straightforward questions | Good for complex multi-part questions |

### AI-103 decision rule

```text
Single straightforward search
-> Classic RAG

Complex question requiring decomposition,
dynamic sources, or iterative searches
-> Agentic RAG
```

---

# 25. Query Decomposition

Complex questions can contain multiple information needs.

Example:

```text
"Compare product A and B on price, warranty,
and customer support."
```

Agentic retrieval can create:

```text
Subquery 1 -> Product A/B price
Subquery 2 -> Product A/B warranty
Subquery 3 -> Product A/B support
```

The results are then combined for generation.

### Exam clue

```text
Complex multi-part question
-> Query decomposition
```

---

# 26. Dynamic Source Selection

An agent can choose among sources at runtime.

```text
User Question
      |
      v
Agent
   /    |     \
  v     v      v
Search API   Database   External Tool
```

Example:

- Internal product catalog -> Azure AI Search
- Market data -> API
- Regulatory filings -> document store

### Exam clue

```text
Model/agent must determine WHICH source/tool to query
-> Agentic RAG / retrieval as a tool
```

---

# 27. Iterative Retrieval

One retrieval attempt might not provide enough information.

```text
Search
  |
Results
  |
Enough evidence?
 /          \
No          Yes
|            |
Refine query  Generate
|
Search again
```

This is a key advantage of agentic RAG over rigid single-pass pipelines.

---

# 28. RAG + Tool Calling

Retrieval can be exposed to an agent as a tool.

```text
Agent
  |
  +-- Search Tool
  +-- Database Tool
  +-- API Tool
  +-- Business Action Tool
```

Agentic RAG can therefore combine:

```text
Retrieval
+
Reasoning
+
Actions
```

Example:

```text
Find a customer's policy
-> check current eligibility
-> create a service request
```

---

# 29. RAG vs Fine-Tuning

This is a major AI-103 distinction.

## RAG

Use for:

- Private knowledge
- Frequently changing information
- Current policies
- Citation/source requirements

## Fine-tuning

Use when supported and justified for:

- Learned response patterns
- Specialized model behavior
- Repeated task/style adaptation beyond prompting

### Memory

```text
Knowledge problem -> RAG
Behavior problem  -> Prompt engineering / Fine-tuning
```

---

# 30. RAG vs Long Context

A model with a large context window doesn't eliminate the value of retrieval.

Dumping all enterprise content into a prompt can cause:

- High token cost
- Higher latency
- More irrelevant information
- Context-window limits
- Security/governance problems

RAG aims to retrieve **highly relevant, concise evidence**, not exhaustive document dumps.

---

# 31. RAG Security Architecture

Security must exist throughout the pipeline.

```text
User Identity
     |
     v
Authorization
     |
     v
Permission-aware Retrieval
     |
     v
Authorized Chunks Only
     |
     v
LLM
```

Use controls such as:

- Microsoft Entra ID
- Managed identity
- Azure RBAC
- Metadata/ACL security filters
- Private networking where required
- Least privilege
- Secure secrets management

### Critical rule

```text
Relevant != Authorized
```

An unauthorized result must not reach the model simply because it has a high similarity score.

---

# 32. RAG Safety

Retrieved data is still untrusted input from the model's perspective.

Documents can contain:

- Incorrect information
- Malicious prompt-injection instructions
- Sensitive content
- Stale information

Defense layers include:

- Trusted data-source controls
- Permission-aware retrieval
- Prompt separation of instructions vs retrieved content
- Content safety
- Output validation
- Tool/action authorization
- Human approval for consequential operations

### Exam rule

```text
RAG does not automatically eliminate hallucination or prompt injection.
```

---

# 33. RAG Cost and Latency

RAG introduces several cost/latency points.

```text
Query embedding
+
Search latency
+
Semantic reranking
+
LLM prompt tokens
+
LLM generation
```

Agentic RAG can add more:

```text
Query planning
+
Multiple subqueries
+
Iterative retrieval
+
Additional reasoning/tool calls
```

### Trade-off

```text
More retrieval/reasoning
-> potentially better coverage
-> higher latency/cost
```

---

# 34. RAG Evaluation

Evaluate retrieval and generation separately.

## Retrieval evaluation

- Precision@K
- Recall@K
- MRR
- NDCG

## Generation evaluation

- Groundedness
- Answer relevance
- Completeness
- Citation correctness
- Safety

## Operational metrics

- Latency
- Token usage
- Cost
- Retrieval failures
- Tool failures

### Important AI-103 mindset

```text
Bad RAG answer
      |
      v
Was retrieval wrong?
OR
Was generation wrong?
```

Don't change the LLM until you know which layer failed.

---

# 35. Common RAG Failure Modes

## Failure: Relevant document not retrieved

Check:

- Chunking
- Embeddings
- Query formulation
- K value
- Filters
- Hybrid search

## Failure: Right document retrieved but ranked low

Consider:

```text
Semantic ranking / reranking
```

## Failure: Correct evidence retrieved but answer unsupported

Check:

- Prompt instructions
- Context formatting
- Grounding constraints
- Model behavior

## Failure: Unauthorized content retrieved

Fix:

```text
Security/ACL filtering
```

## Failure: Excessive latency

Evaluate:

- Number of searches
- Reranking
- Agentic steps
- Token volume
- Model selection

---

# 36. Complete RAG Architecture Decision Table

| Requirement | Think |
|---|---|
| Private/current knowledge | RAG |
| Prepare large documents | Chunking |
| Semantic representation | Embeddings |
| Exact terms/codes | Keyword search |
| Similar meaning | Vector search |
| Exact + semantic | Hybrid search |
| Merge keyword/vector ranks | RRF |
| Improve candidate ordering | Semantic ranker |
| Limit retrieved evidence | Top-K |
| Add knowledge to model input | Prompt augmentation |
| Verify sources | Citations/metadata |
| Straightforward retrieval | Classic RAG |
| Multi-part complex question | Agentic RAG |
| Break question into searches | Query decomposition |
| Choose source dynamically | Agentic tool selection |
| Retry/refine search | Iterative retrieval |
| Protect private content | ACL/security filters |
| Learn model behavior | Fine-tuning |

---

# Practice Questions

## Question 1

A chatbot must answer questions from internal policies that change every month.

What architecture is most appropriate?

A. RAG  
B. Increase temperature  
C. Fine-tune the model every month  
D. Use only few-shot examples  

### Correct answer: A

**Why A is correct:** RAG retrieves the current policy content at query time and grounds the model without retraining it for every factual update.

**Why the others are incorrect:**

- **B:** Temperature changes sampling, not knowledge.
- **C:** Retraining for changing facts is inefficient.
- **D:** Examples teach behavior rather than provide current policies.

---

## Question 2

What are the three fundamental RAG stages?

A. Retrieve, Augment, Generate  
B. Train, Deploy, Delete  
C. Embed, Fine-tune, Translate  
D. Search, Sort, Facet  

### Correct answer: A

**Why A is correct:** RAG retrieves evidence, augments model input with that evidence, and generates a grounded response.

---

## Question 3

Large documents contain many unrelated topics and retrieval quality is poor.

What should you improve first?

A. Chunking strategy  
B. Temperature  
C. Presence penalty  
D. Output token limit  

### Correct answer: A

**Why A is correct:** Meaningful chunks improve retrieval granularity and embedding quality.

---

## Question 4

A query contains exact error code `AUTH-2047` plus a natural-language description.

Which retrieval approach is most appropriate?

A. Hybrid search  
B. Vector only  
C. Temperature tuning  
D. Fine-tuning  

### Correct answer: A

**Why A is correct:** Keyword retrieval handles the exact code while vector retrieval captures semantic meaning.

---

## Question 5

Hybrid search retrieves useful candidates, but their semantic ordering is poor.

What should you add?

A. Semantic ranker  
B. Higher temperature  
C. Presence penalty  
D. More overlap only  

### Correct answer: A

**Why A is correct:** Semantic ranker performs second-stage semantic reranking.

---

## Question 6

A user asks a multi-part question requiring several independent searches that should run in parallel.

Which RAG pattern is more appropriate?

A. Agentic RAG / agentic retrieval  
B. Simple fixed classic RAG only  
C. Higher temperature  
D. Fine-tuning  

### Correct answer: A

**Why A is correct:** Agentic retrieval can decompose complex questions into focused subqueries and run them in parallel.

---

## Question 7

A RAG system finds a highly relevant HR document, but the user isn't authorized to read it.

Should the document be passed to the LLM?

A. Yes, because relevance is high  
B. No, permission-aware retrieval must block it  
C. Yes, if semantic ranker selected it  
D. Yes, if temperature is low  

### Correct answer: B

**Why B is correct:** Retrieval relevance and authorization are independent. Only authorized content should be available for grounding.

---

## Question 8

The application retrieves the correct evidence, but the model ignores it and invents unsupported details.

Which layer should you investigate?

A. Prompt construction/generation behavior and grounding instructions  
B. Embedding dimensions only  
C. Indexer schedule only  
D. Facets  

### Correct answer: A

**Why A is correct:** Retrieval succeeded. The failure is in how evidence is supplied or used during generation.

---

## Question 9

A model must choose at runtime whether to search an internal index, call an external API, or query a database.

Which architecture is most appropriate?

A. Agentic RAG with retrieval/tool selection  
B. Static single-search classic RAG only  
C. Temperature tuning  
D. Semantic caption  

### Correct answer: A

**Why A is correct:** Dynamic source and tool selection is a core agentic RAG capability.

---

## Question 10

A retrieved chunk must support a clickable citation to the original page.

What should be preserved during indexing?

A. Source URL/page/document metadata  
B. Temperature  
C. Top-p  
D. Frequency penalty  

### Correct answer: A

**Why A is correct:** Citation generation requires source and location metadata to survive chunking and retrieval.

---

## Question 11

Users complain that RAG responses are slow. The agent runs many subqueries and iterative searches for simple questions.

What should you evaluate?

A. Whether a simpler classic RAG path should handle straightforward queries and agentic steps should be limited  
B. Increase the number of retrieval passes  
C. Increase temperature  
D. Add more chunks to every prompt  

### Correct answer: A

**Why A is correct:** Agentic retrieval adds latency. Straightforward questions often don't need multi-step retrieval.

---

## Question 12

Your RAG answers are poor. What is the most useful first diagnostic distinction?

A. Determine whether retrieval failed or generation failed  
B. Immediately fine-tune the LLM  
C. Always increase chunk overlap  
D. Always replace the embedding model  

### Correct answer: A

**Why A is correct:** RAG has distinct retrieval and generation stages. Fix the failing layer rather than changing unrelated components.

---

# High-Value AI-103 Exam Traps

## Trap 1

```text
RAG = Fine-tuning
```

Wrong.

```text
RAG -> external/current knowledge
Fine-tuning -> learned model behavior
```

---

## Trap 2

```text
Embeddings generate the final answer
```

Wrong.

```text
Embeddings -> retrieval representation
LLM -> answer generation
```

---

## Trap 3

```text
Vector Search = RAG
```

Wrong.

```text
Vector search -> retrieval technique
RAG -> Retrieve + Augment + Generate
```

---

## Trap 4

```text
RRF = Semantic Ranker
```

Wrong.

```text
RRF -> merge result rankings
Semantic ranker -> semantic reranking
```

---

## Trap 5

```text
More retrieved chunks are always better
```

Wrong. More chunks can increase noise, tokens, cost, and latency.

---

## Trap 6

```text
Relevant content can always be sent to LLM
```

Wrong. Only authorized content should be retrieved and grounded.

---

## Trap 7

```text
Agentic RAG is always better than classic RAG
```

Wrong. Agentic RAG adds complexity and latency and is most useful for complex, multistep retrieval requirements.

---

# One-Minute Revision Sheet

```text
RAG
Retrieve -> Augment -> Generate

INDEXING PIPELINE
Extract -> Chunk -> Embed -> Index

QUERY PIPELINE
Question -> Retrieve -> Rerank -> Ground -> Generate

CHUNKING
Create retrieval units

EMBEDDINGS
Semantic vectors

KEYWORD SEARCH
Exact words/codes

VECTOR SEARCH
Semantic similarity

HYBRID SEARCH
Keyword + Vector

RRF
Merge ranked lists

SEMANTIC RANKER
Second-stage relevance reranking

TOP-K
Number of retrieved candidates

AUGMENTATION
Add retrieved evidence to prompt

CITATIONS
Preserve source metadata

CLASSIC RAG
Fixed/predetermined retrieval pipeline

AGENTIC RAG
Dynamic tool use + query planning + iterative retrieval

QUERY DECOMPOSITION
Break complex question into subqueries

SECURITY
Permission-aware retrieval before LLM grounding
```

# Final AI-103 Decision Rule

```text
Current/private knowledge?
-> RAG

Prepare large documents?
-> Chunking

Need semantic representation?
-> Embeddings

Exact code?
-> Keyword search

Semantic meaning?
-> Vector search

Need both?
-> Hybrid search

Merge hybrid rankings?
-> RRF

Poor candidate ordering?
-> Semantic ranker

Need trustworthy source traceability?
-> Metadata + citations

Straightforward single retrieval?
-> Classic RAG

Complex multi-part question?
-> Agentic RAG

Need multiple searches?
-> Query decomposition

First search insufficient?
-> Iterative retrieval

Need dynamic source/action selection?
-> Agentic tool calling

Unauthorized content?
-> Security filter / ACL enforcement BEFORE grounding
```

## Suggested next AI-103 topic

**Agents: Foundry Agent Service, instructions, tools/function calling, threads/conversations, orchestration, planning, reflection, and multi-agent patterns.**

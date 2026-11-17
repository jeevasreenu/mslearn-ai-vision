# AI-103: Embeddings

## 1. What is an Embedding?

An **embedding** is a vector of floating-point numbers that represents the semantic meaning of content.

```text
Text
  |
  v
Embedding model
  |
  v
[0.21, -0.18, 0.74, ...]
```

Semantically similar content tends to produce vectors that are close to one another in the embedding space.

### AI-103 exam memory

```text
Embedding = semantic meaning represented as numbers
```

Embeddings are commonly used for:

- Vector search
- Similarity search
- RAG retrieval
- Recommendations
- Classification
- Clustering
- Multilingual or multimodal retrieval when supported by the selected model

---

# 2. Embedding Model vs Generative Model

Do not confuse an embedding model with a chat/generative model.

```text
Embedding model
Text -> Vector

Generative model
Prompt/context -> Natural-language response
```

### Exam rule

```text
Need semantic numerical representation?
-> Embedding model

Need generated answer?
-> Generative/chat model
```

---

# 3. Why Embeddings are Useful

Keyword matching depends strongly on words. Embeddings capture semantic relationships.

Example:

```text
Query:
"How do I recover my account password?"

Document:
"Reset forgotten login credentials"
```

The wording is different, but the meanings are similar. Their vectors can therefore be close in embedding space.

This helps vector search retrieve content that is conceptually relevant even when exact terms differ.

---

# 4. Basic Embedding Flow

## Indexing

```text
Document
   |
   v
Chunking
   |
   v
Embedding model
   |
   v
Document/chunk vector
   |
   v
Vector field in Azure AI Search
```

## Querying

```text
User query
   |
   v
Embedding model
   |
   v
Query vector
   |
   v
Vector similarity search
   |
   v
Relevant document chunks
```

### Critical rule

For accurate vector retrieval, use a compatible embedding space for indexed content and queries. In typical Azure AI Search guidance, use the **same embedding model** for indexing and querying.

---

# 5. Embeddings in RAG

Embeddings are a component of many RAG solutions.

```text
Documents
   |
   v
Chunks
   |
   v
Embeddings
   |
   v
Search index

User question
   |
   v
Query embedding
   |
   v
Vector / hybrid retrieval
   |
   v
Relevant chunks
   |
   v
Ground LLM
   |
   v
Generated answer
```

### Important distinction

```text
Embedding != RAG
```

RAG is the full pattern:

```text
Retrieve -> Augment -> Generate
```

Embeddings help with the **retrieve** step.

---

# 6. Vector Search

Vector search retrieves records whose vectors are most similar to the query vector.

Conceptually:

```text
Query vector
    |
    v
Compare with stored vectors
    |
    v
Nearest vectors
    |
    v
Relevant documents
```

Azure AI Search supports indexing and querying numeric vector representations of content.

Vector search is useful for:

- Semantic similarity
- Conceptual likeness
- Multilingual retrieval with suitable embeddings
- Multimodal retrieval with suitable models
- Similar-document search

---

# 7. Cosine Similarity

One common way to compare embeddings is **cosine similarity**, which compares the direction of vectors.

Conceptually:

```text
Similar direction -> semantically closer
Different direction -> less similar
```

Microsoft's Azure OpenAI embeddings tutorial demonstrates using **cosine similarity** to rank documents by relevance.

### Exam association

```text
Azure OpenAI embeddings + similarity search
-> remember cosine similarity
```

Azure AI Search also supports other vector similarity metrics depending on configuration, including dot product and Euclidean distance.

---

# 8. Embedding Dimensions

An embedding vector contains a fixed number of numeric dimensions according to the selected model/configuration.

Conceptual example:

```text
[0.12, 0.55, -0.02, ...]
```

If the vector has N values:

```text
dimensions = N
```

### Why dimensions matter

The search index vector field must be configured to match the dimensions produced by your embedding configuration.

```text
Embedding output dimension
            =
Vector field dimension
```

A mismatch causes indexing/query configuration problems.

### Exam clue

```text
Embedding dimension and vector field dimension do not match
```

Think:

```text
Configure the vector field to match the embedding output
```

Do not memorize one universal dimension because dimensions vary by embedding model and supported configuration.

---

# 9. Azure OpenAI Embedding Models

Microsoft documentation includes Azure OpenAI embedding models such as:

```text
text-embedding-3-small
text-embedding-3-large
text-embedding-ada-002 (Version 2)
```

Model availability and recommended choices can change, so for the exam focus on concepts:

```text
Embedding model -> vectors
Chat model      -> language generation
```

---

# 10. Chunking Before Embedding

Large documents are usually split into chunks before embedding.

```text
Large document
      |
      v
    Chunking
      |
 +----+----+
 |    |    |
 C1   C2   C3
 |    |    |
 v    v    v
Embeddings
```

### Why?

- Embedding models have input-token limits.
- Smaller meaningful chunks improve retrieval precision.
- One vector for a document containing many unrelated topics may poorly represent individual sections.

Microsoft's Azure AI Search documentation recommends designing a chunking strategy for large content and supports integrated chunking/vectorization pipelines.

---

# 11. Too-Large vs Too-Small Chunks

## Chunk too large

```text
Many unrelated topics
       |
       v
One broad embedding
       |
       v
Less precise retrieval
```

Possible problems:

- Semantic dilution
- More irrelevant context
- Larger model inputs after retrieval

## Chunk too small

```text
Sentence fragments
      |
      v
Insufficient context
```

Possible problems:

- Lost context
- Fragmented answers
- Too many index records

### Best practice

Choose chunk size experimentally based on:

- Document structure
- Embedding limits
- Query patterns
- Retrieval quality

---

# 12. Integrated Vectorization

Azure AI Search supports **integrated vectorization**.

Conceptually:

```text
Data source
   |
   v
Indexer
   |
   v
Skillset / chunking
   |
   v
Embedding model
   |
   v
Vector fields in index
```

At query time, a configured vectorizer can transform text input into a query vector.

Microsoft recommends integrated vectorization for many Azure AI Search scenarios because the service can coordinate chunking/vectorization with indexers and external embedding models.

---

# 13. Manual Vectorization

You can also manage vectors yourself.

## Indexing

```text
Your application
     |
     v
Embedding model
     |
     v
Precomputed vectors
     |
     v
Push documents + vectors into index
```

## Querying

```text
User query
     |
     v
Your application calls embedding model
     |
     v
Query vector
     |
     v
Send vector query to search service
```

### Integrated vs Manual

| Approach | Responsibility |
|---|---|
| Integrated vectorization | Azure AI Search indexing/vectorization pipeline handles more orchestration |
| Manual vectorization | Your application controls chunking, vector generation, and vector submission |

---

# 14. Azure OpenAI Vectorizer vs Embedding Skill

This can be confusing.

## Embedding skill

Think:

```text
INDEXING TIME
Content -> embeddings
```

The Azure OpenAI Embedding skill generates embeddings during the indexing pipeline.

## Vectorizer

Think:

```text
QUERY TIME
User text -> query embedding
```

An Azure OpenAI vectorizer can generate embeddings from query input at query time.

### Memory trick

```text
SKILL      = index-side vector creation
VECTORIZER = query-side vector creation
```

---

# 15. Keyword Search vs Vector Search

| Keyword search | Vector search |
|---|---|
| Lexical/text matching | Semantic similarity |
| Strong for exact terms | Strong for conceptual matches |
| Useful for IDs/codes | Useful for differently worded similar ideas |

### Example

```text
Query: ERR-1042
```

Think:

```text
Keyword search
```

Query:

```text
How can I regain access to my account?
```

Document:

```text
Reset forgotten login credentials
```

Think:

```text
Vector search
```

---

# 16. Hybrid Search

Hybrid search combines keyword and vector retrieval in the same request.

```text
             User query
                 |
       +---------+---------+
       |                   |
       v                   v
Keyword search       Vector search
       |                   |
       +---------+---------+
                 |
                 v
          Combined ranking
```

Use hybrid search when you need both:

```text
Exact lexical matching
+
Semantic similarity
```

### Exam example

```text
ERR-2047 password authentication problem
```

- Keyword search helps with `ERR-2047`.
- Vector search helps understand the authentication concept.

Think:

```text
Hybrid search
```

---

# 17. Embeddings and Multilingual Search

With an appropriate multilingual embedding model, semantically related text in different languages can occupy similar regions of vector space.

Conceptual example:

```text
English: "password reset"
German:  equivalent concept
```

Vector search can support multilingual scenarios without requiring exact shared keywords, depending on the model used.

---

# 18. Multimodal Embeddings

Some embedding models can represent more than plain text, for example text and images in a compatible embedding space.

This allows scenarios such as:

```text
Text query
   |
   v
Find semantically related images
```

or:

```text
Image
  |
  v
Find conceptually related content
```

The selected model must support the modalities required by the solution.

---

# 19. Embeddings vs Fine-Tuning

Embeddings do not train the model.

```text
Embeddings
-> represent content for similarity/retrieval

Fine-tuning
-> modifies model behavior through training
```

### Exam scenario

Need to find semantically similar documents?

```text
Embeddings / vector search
```

Need a model to learn a specific response pattern deeply?

```text
Prompt engineering first, possibly fine-tuning where appropriate
```

---

# 20. Embeddings vs Prompt Engineering

```text
Embeddings
-> HOW content is represented for similarity search

Prompt engineering
-> HOW instructions/context guide generation
```

They solve different problems.

---

# 21. Embeddings vs Semantic Ranking

Do not confuse these.

```text
Embeddings + vector search
-> Retrieve semantically similar candidates

Semantic ranking
-> Rerank existing search candidates by semantic relevance
```

### Exam clue

```text
Need to convert text into a semantic vector
-> Embedding

Already retrieved candidates but need better ordering
-> Semantic ranker / reranker
```

---

# 22. Security and Authentication

Azure OpenAI embedding calls can use supported authentication mechanisms such as Microsoft Entra ID or API keys, depending on the API and integration.

Microsoft recommends Entra ID where supported to avoid storing long-lived API credentials.

For Azure workloads, managed identities and appropriate RBAC can help reduce secret-management requirements.

### Exam security principle

```text
Passwords/API secrets hard-coded in source code
-> Avoid

Identity + least-privilege RBAC where supported
-> Prefer
```

---

# 23. Complete AI-103 Embeddings Decision Table

| Requirement | Think |
|---|---|
| Convert content into vectors | Embedding model |
| Find semantically similar content | Vector search |
| Find exact code/name | Keyword search |
| Exact terms + semantic meaning | Hybrid search |
| Current/private data for LLM | RAG |
| Large document | Chunk before embedding |
| Index and query vectors incompatible | Use compatible/same embedding model/configuration |
| Vector field size mismatch | Correct dimensions |
| Automatic index-time embeddings | Embedding skill / integrated vectorization |
| Automatic query-time embedding | Vectorizer |
| Better ordering after retrieval | Semantic reranking |
| Change model response style | Prompt engineering |
| Train behavior | Fine-tuning |

---

# Practice Questions

## Question 1

You need to find documents whose meanings are similar to a user's natural-language query even when they use different words.

What should you use?

A. Embeddings and vector search  
B. Higher temperature  
C. Maximum output tokens  
D. Frequency penalty  

### Correct answer: A

**Why A is correct:** Embeddings represent semantic meaning numerically, enabling vector similarity search.

**Why the others are incorrect:**

- **B:** Controls generation randomness.
- **C:** Limits output size.
- **D:** Controls repeated token usage.

---

## Question 2

A search index contains document vectors generated by one embedding model, while query vectors are generated using an incompatible embedding space.

What is the best fix?

A. Increase temperature  
B. Use a compatible, typically the same, embedding model/configuration for indexing and querying  
C. Increase top-p  
D. Add a stop sequence  

### Correct answer: B

**Why B is correct:** Indexed and query vectors must be comparable in the same compatible embedding space for meaningful similarity search.

---

## Question 3

A vector field is configured with dimensions that don't match the output produced by the embedding configuration.

What should you do?

A. Configure the vector field dimensions to match the embedding output  
B. Increase temperature  
C. Enable semantic ranking  
D. Reduce maximum tokens  

### Correct answer: A

**Why A is correct:** The index vector field must be compatible with the embedding vector dimensions.

---

## Question 4

A user searches specifically for product code `AZ-9847`.

Which search method is particularly useful?

A. Keyword search  
B. Presence penalty  
C. Fine-tuning  
D. Temperature  

### Correct answer: A

**Why A is correct:** Exact identifiers are a strong lexical/keyword-search scenario.

---

## Question 5

A search query contains both an exact error code and a natural-language description of the problem.

Which approach is most appropriate?

A. Keyword only  
B. Vector only  
C. Hybrid search  
D. Fine-tuning  

### Correct answer: C

**Why C is correct:** Hybrid search combines exact lexical retrieval with semantic vector retrieval.

---

## Question 6

Large documents contain multiple unrelated subjects and generate poor retrieval results when represented using one embedding each.

What should you do?

A. Chunk the documents into meaningful sections before embedding  
B. Increase temperature  
C. Increase frequency penalty  
D. Use JSON mode  

### Correct answer: A

**Why A is correct:** Smaller meaningful chunks provide more precise semantic representations and respect model input limits.

---

## Question 7

You want Azure AI Search to automatically create document embeddings as part of an indexer pipeline.

Which concept is relevant?

A. Azure OpenAI Embedding skill / integrated vectorization  
B. Temperature  
C. Presence penalty  
D. Stop sequence  

### Correct answer: A

**Why A is correct:** The embedding skill can call an Azure OpenAI embedding model during indexing as part of an integrated vectorization pipeline.

---

## Question 8

At query time, you want a user's text query automatically converted into an embedding before Azure AI Search runs vector retrieval.

Which feature is most relevant?

A. Vectorizer  
B. Frequency penalty  
C. Fine-tuning  
D. JSON mode  

### Correct answer: A

**Why A is correct:** A configured vectorizer can call the embedding model at query time to create the query vector.

---

## Question 9

Search has already retrieved the correct documents, but the ordering of top results is poor.

Which capability addresses the core issue?

A. Semantic reranking  
B. Generate new embeddings with higher temperature  
C. Presence penalty  
D. Fine-tune the LLM  

### Correct answer: A

**Why A is correct:** Reranking reorders retrieved candidates using semantic relevance. Embedding generation does not use chat-temperature controls in this way.

---

## Question 10

A system needs current private corporate information to answer user questions.

Are embeddings alone sufficient?

A. Yes, embeddings generate the final factual answer  
B. No, embeddings can support retrieval, while a RAG flow retrieves grounding content and a generative model produces the answer  
C. Yes, if temperature is zero  
D. Yes, if top-p is low  

### Correct answer: B

**Why B is correct:** Embeddings support semantic retrieval; RAG uses retrieved information to ground generation.

---

## Question 11

What does an embedding model return?

A. A vector of numeric values  
B. A complete grounded natural-language answer by definition  
C. A relational database  
D. An Azure Search index  

### Correct answer: A

**Why A is correct:** An embedding is a vector representation of the input's semantic meaning.

---

## Question 12

You need a similarity metric in an Azure OpenAI document-search scenario like Microsoft's embeddings tutorial.

Which metric is used in the tutorial?

A. Cosine similarity  
B. Temperature  
C. BM25 only  
D. Frequency penalty  

### Correct answer: A

**Why A is correct:** Microsoft's Azure OpenAI embeddings tutorial uses cosine similarity to rank related documents.

---

# High-Value Exam Traps

## Trap 1

```text
Embedding model generates final chatbot answer
```

Wrong.

```text
Embedding model -> vector representation
Generative model -> response generation
```

---

## Trap 2

```text
Embeddings = RAG
```

Wrong.

```text
Embeddings support retrieval
RAG = Retrieve + Augment + Generate
```

---

## Trap 3

```text
Same words required for vector search
```

Wrong.

Vector search is useful because semantically related content can match even with different words.

---

## Trap 4

```text
Exact product code
```

Think:

```text
Keyword search
```

---

## Trap 5

```text
Exact ID + conceptual meaning
```

Think:

```text
Hybrid search
```

---

## Trap 6

```text
Different embedding spaces for documents and queries
```

Problem.

Use compatible vector representations, typically the same embedding model/configuration for indexing and query embeddings.

---

## Trap 7

```text
Vector dimensions do not match index definition
```

Fix the dimension configuration. Do not solve this with prompting or temperature.

---

# One-Minute Revision Sheet

```text
EMBEDDING
Semantic meaning -> vector of floating-point numbers

EMBEDDING MODEL
Content -> vector

GENERATION MODEL
Prompt/context -> response

VECTOR SEARCH
Find semantically similar vectors

COSINE SIMILARITY
Common similarity measure for embedding search

DIMENSIONS
Vector field must match embedding output/configuration

CHUNKING
Split large content before embedding

INTEGRATED VECTORIZATION
Azure AI Search coordinates chunking/vectorization in indexing workflows

EMBEDDING SKILL
Index-time embeddings

VECTORIZER
Query-time embedding conversion

KEYWORD SEARCH
Exact lexical match

VECTOR SEARCH
Semantic meaning

HYBRID SEARCH
Keyword + vector

SEMANTIC RERANKER
Improve ordering of retrieved candidates

RAG
Retrieve -> Augment -> Generate
```

# Final AI-103 Decision Rule

```text
Need semantic numeric representation?
-> Embeddings

Need semantically similar content?
-> Vector search

Need exact ID/code?
-> Keyword search

Need both lexical + semantic?
-> Hybrid search

Need private/current knowledge?
-> RAG

Large documents?
-> Chunk before embedding

Need index-time vectors automatically?
-> Embedding skill / integrated vectorization

Need query-time text-to-vector conversion?
-> Vectorizer

Results found but ordered poorly?
-> Semantic ranking

Need generated answer?
-> Generative model
```

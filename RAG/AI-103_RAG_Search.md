# AI-103: RAG and Search

## 1. What is RAG?

**Retrieval-Augmented Generation (RAG)** combines information retrieval with a large language model (LLM) so the model can answer using relevant external data rather than relying only on knowledge learned during training.

```text
User Question
     |
     v
Retrieve relevant content
from an index / data source
     |
     v
Add retrieved content to prompt
     |
     v
LLM generates a grounded answer
```

### The three RAG steps

```text
RETRIEVE -> AUGMENT -> GENERATE
```

- **Retrieve:** Search for relevant content.
- **Augment:** Add retrieved content as grounding context to the prompt.
- **Generate:** Ask the LLM to create an answer using that context.

### AI-103 exam rule

```text
Need private information?
Need current/changing information?
Need answers from enterprise documents?
Need citations to source documents?

-> Think RAG / grounding
```

RAG does **not** retrain the LLM.

---

# 2. Why use RAG?

LLMs have limitations:

- Their training data has a cutoff.
- They don't automatically know your private enterprise data.
- They may generate unsupported information.
- Sending an entire document collection in every prompt is inefficient and often impossible because of context/token limits.

RAG solves this by retrieving only relevant information before generation.

### Example

Question:

```text
What is our company's current parental leave policy?
```

If the policy is private and changes regularly, increasing temperature or adding few-shot examples will not provide the missing facts.

Use:

```text
Policy documents
      |
      v
Search index
      |
      v
Retrieve relevant chunks
      |
      v
Ground the LLM prompt
      |
      v
Answer + citations
```

---

# 3. RAG Architecture

A typical RAG solution has two broad phases.

## Indexing phase

```text
Documents
   |
   v
Extract text/content
   |
   v
Chunk content
   |
   v
Generate embeddings
   |
   v
Create/index searchable fields
   |
   v
Azure AI Search index
```

## Query phase

```text
User question
   |
   v
Query processing / embedding
   |
   v
Search index
   |
   v
Retrieve relevant chunks
   |
   v
Optional semantic reranking
   |
   v
Add context to prompt
   |
   v
LLM
   |
   v
Grounded answer + citations
```

---

# 4. What is an Index?

An **index** is a structure optimized for finding relevant information efficiently.

A search index can contain fields such as:

```text
id
content
title
sourceUrl
category
createdDate
contentVector
```

Fields can have capabilities such as:

- Searchable
- Filterable
- Sortable
- Facetable
- Retrievable

### AI-103 mental model

```text
Source documents = original content
Index            = optimized representation for search
Embedding         = vector representation of meaning
LLM               = generates final response
```

Do not confuse the search index with the LLM.

---

# 5. Chunking

Large documents are typically divided into smaller pieces called **chunks** before indexing and embedding.

```text
Large PDF
   |
   +-- Chunk 1
   +-- Chunk 2
   +-- Chunk 3
   +-- Chunk 4
```

### Why chunk?

Chunking can:

- Keep inputs within embedding/model token limits.
- Improve retrieval granularity.
- Reduce irrelevant context returned to the LLM.
- Improve semantic representation when a document contains many unrelated sections.

### Chunk too large

Possible problems:

```text
More irrelevant information
Less precise retrieval
Higher token usage
```

### Chunk too small

Possible problems:

```text
Loss of surrounding context
Incomplete meaning
Too many fragments
```

---

# 6. Chunk Overlap

Adjacent chunks can share some text.

Example:

```text
Chunk 1: A B C D E
Chunk 2: D E F G H
              ^ overlap
```

Overlap helps preserve information that crosses chunk boundaries.

Microsoft documentation gives fixed-size chunking as one possible approach and notes that overlap such as roughly **10-15%** can be useful in an example configuration. Treat this as a starting point rather than a universal rule.

### Exam clue

```text
Important context is split between chunks
```

Think:

```text
Chunk overlap / better semantic chunking
```

---

# 7. Semantic / Structure-Aware Chunking

Fixed-length chunking is simple, but document structure can produce better semantic units.

For example:

```text
Heading
  Paragraph
  Paragraph

Heading
  Paragraph
```

A structure-aware approach can preserve headings, paragraphs, and semantic boundaries rather than cutting content at arbitrary positions.

### Exam thinking

If a scenario emphasizes:

```text
Preserve headings
Preserve paragraphs
Keep semantically related information together
```

think about **layout-aware or semantic chunking**.

---

# 8. Embeddings

An **embedding** converts content into a numerical vector that represents semantic meaning.

Conceptual example:

```text
"Reset my password"
       |
       v
[0.12, -0.44, 0.91, ...]
```

Semantically similar text tends to have nearby vector representations.

Example:

```text
"How do I reset my password?"

and

"I forgot my login password"
```

may be close in vector space even though they don't use exactly the same words.

### Key point

```text
Embeddings -> semantic representation
LLM        -> text generation/reasoning
```

An embedding model does not normally generate your final natural-language answer.

---

# 9. Keyword Search

Keyword search focuses on textual/lexical matches.

Example query:

```text
Azure AI Search
```

Documents containing those terms can rank highly.

Azure AI Search uses established text-ranking techniques such as **BM25** for full-text retrieval.

### Keyword search is useful when

- Exact wording matters.
- Product codes or IDs are queried.
- Names and specific terminology are important.

### Example

```text
Error code: ABC-1027
```

Exact text search can be extremely useful for this kind of query.

---

# 10. Vector Search

Vector search compares embedding vectors to retrieve semantically similar content.

```text
User query
   |
   v
Embedding
   |
   v
Vector similarity search
   |
   v
Semantically related chunks
```

### Example

Query:

```text
How can I recover my account password?
```

Document:

```text
Steps to reset forgotten login credentials
```

The words differ, but their meaning is similar.

Vector search can retrieve the document based on semantic similarity.

---

# 11. Keyword vs Vector Search

| Search type | Best at |
|---|---|
| Keyword search | Exact lexical terms, identifiers, product names |
| Vector search | Semantic similarity and intent |

### Memory trick

```text
KEYWORD = same/similar WORDS
VECTOR  = same/similar MEANING
```

---

# 12. Hybrid Search

**Hybrid search** combines keyword search and vector search.

```text
User Query
   |
   +--> Keyword search
   |
   +--> Vector search
   |
   v
Combined result set / ranking
```

Why?

Keyword and vector retrieval have complementary strengths.

Example query:

```text
AZR-1042 authentication failure
```

- Keyword retrieval can strongly match `AZR-1042`.
- Vector retrieval can find semantically related authentication troubleshooting content.

### AI-103 exam rule

```text
Need exact-term matching + semantic similarity
                 |
                 v
            HYBRID SEARCH
```

---

# 13. Semantic Ranking

Do not confuse **semantic ranking** with **vector search**.

A semantic ranker reranks an initial set of search results based on semantic relevance.

Simplified flow:

```text
Initial retrieval
(keyword/vector/hybrid)
       |
       v
Candidate results
       |
       v
Semantic reranker
       |
       v
More relevant ordering
```

### Concept distinction

```text
Vector search
-> retrieves using vector similarity

Semantic ranking
-> reranks candidate search results by semantic relevance
```

### Exam clue

```text
Relevant documents are found,
but their ranking/order is poor.
```

Think:

**semantic reranking / reranking**

---

# 14. Filtering

Filtering restricts results using structured fields.

Example:

```text
department eq 'HR'
```

or conceptually:

```text
country = India
AND
status = Active
```

### Filtering vs semantic search

```text
Filter
-> exact structured condition

Vector/semantic retrieval
-> relevance/meaning
```

### Exam example

Requirement:

```text
Only retrieve documents from the Finance department.
```

Think:

**filterable metadata field + filter**

---

# 15. Retrieval Top-K

In RAG, search normally retrieves a limited number of highest-ranking chunks.

Conceptually:

```text
top_k = 5
```

means retrieve several high-ranking candidates rather than dumping the complete index into the prompt.

### Too few retrieved chunks

```text
May miss relevant evidence
```

### Too many retrieved chunks

```text
More irrelevant context
Higher token consumption
Potentially worse generation quality
Higher latency/cost
```

The ideal value should be evaluated on your data and queries.

---

# 16. HNSW vs Exhaustive KNN

Azure AI Search supports vector-search approaches including **HNSW** and **exhaustive KNN**.

## HNSW

Hierarchical Navigable Small World is an **approximate nearest-neighbor** strategy designed for performant vector retrieval.

Think:

```text
Large vector index
Fast approximate similarity search
-> HNSW
```

## Exhaustive KNN

Compares against the vector space exhaustively for exact nearest-neighbor search.

Think:

```text
Exact exhaustive comparison
-> exhaustive KNN
```

### Trade-off

```text
HNSW
-> faster/scalable approximate retrieval

Exhaustive KNN
-> exhaustive/exact but more computational work
```

---

# 17. Vector Similarity Metrics

Azure AI Search supports vector similarity metrics such as:

- Cosine
- Dot product
- Euclidean distance

For Azure OpenAI embedding models, Microsoft guidance commonly recommends **cosine similarity**.

### Exam association

```text
Azure OpenAI embeddings
-> cosine similarity is an important association
```

---

# 18. Classic RAG vs Agentic Retrieval

Modern Azure AI Search supports both classic RAG patterns and agentic retrieval scenarios.

## Classic RAG

Typical architecture:

```text
User query
   |
   v
Search query
   |
   v
Hybrid/vector/keyword retrieval
   |
   v
Optional semantic ranking
   |
   v
Ground LLM
```

Classic RAG is useful for simpler retrieval flows and when you want a proven generally available pattern.

## Agentic retrieval

Agentic retrieval can use LLM-based query planning to break complex questions into targeted searches and work across knowledge sources.

Conceptually:

```text
Complex question
      |
      v
Query planning
      |
      +--> Subquery 1
      +--> Subquery 2
      +--> Subquery 3
      |
      v
Parallel/multi-source retrieval
      |
      v
Structured grounding results
```

### Exam hint

```text
Simple known retrieval flow
-> classic RAG

Complex conversational question,
query decomposition,
multiple knowledge sources
-> agentic retrieval
```

Always pay attention to whether a feature is preview or generally available in the exam scenario/documentation version.

---

# 19. RAG vs Fine-Tuning

This distinction is extremely important.

## RAG

Use when the model needs **knowledge**.

```text
Private documents
Current information
Frequently changing facts
Citations
```

## Fine-tuning

Use when you want to modify learned **behavior/patterns** using training examples and the specific model supports fine-tuning.

```text
Knowledge problem  -> RAG
Behavior problem   -> prompt engineering / possibly fine-tuning
```

### Exam example

Company policies change monthly.

Wrong:

```text
Fine-tune the model every month
```

Better:

```text
Store/index the policies and retrieve current information with RAG
```

---

# 20. RAG vs Prompt Engineering

Prompt engineering tells the model **how to behave**.

RAG supplies **information the model needs**.

```text
Wrong response style
-> Prompt engineering

Missing private/current knowledge
-> RAG
```

They commonly work together:

```text
RAG retrieves context
+
Prompt tells model how to use context
```

---

# 21. RAG vs Embeddings

Embeddings are one component that can be used inside RAG.

```text
RAG
 |
 +-- Documents
 +-- Chunking
 +-- Embeddings
 +-- Search/index
 +-- Retrieval
 +-- Grounding
 +-- LLM generation
```

Therefore:

```text
Embedding != RAG
```

Embeddings enable semantic vector retrieval; RAG is the broader retrieve-augment-generate pattern.

---

# 22. Complete AI-103 Decision Table

| Requirement | Think |
|---|---|
| Current/private knowledge | RAG |
| Exact words, IDs, codes | Keyword search |
| Similar meaning | Vector search |
| Exact words + semantic similarity | Hybrid search |
| Improve ordering of retrieved candidates | Semantic ranking/reranking |
| Represent text semantically | Embeddings |
| Large documents | Chunking |
| Context lost at chunk boundaries | Overlap / semantic chunking |
| Restrict results by metadata | Filtering |
| Ground final response | Retrieved context + prompt |
| Change output behavior/style | Prompt engineering |
| Deep learned behavior change | Fine-tuning |
| Complex query decomposition/multi-source retrieval | Agentic retrieval |

---

# Practice Questions

## Question 1

A company chatbot must answer questions using private HR policy documents that are updated every month.

Which approach is most appropriate?

A. Increase temperature  
B. Fine-tune the model every month  
C. Use RAG to retrieve relevant policy content  
D. Increase maximum completion tokens  

### Correct answer: C

**Why C is correct:** RAG is appropriate for private, frequently changing information because the latest content can be retrieved and supplied to the LLM at query time.

**Why the others are incorrect:**

- **A:** Temperature changes sampling behavior, not knowledge.
- **B:** Repeated fine-tuning is inefficient for continuously changing factual content.
- **D:** Token limits do not provide policy information.

---

## Question 2

Users search for error code `AUTH-2047`, and exact matches are extremely important.

Which retrieval method is especially valuable?

A. Keyword search  
B. Presence penalty  
C. Fine-tuning  
D. Temperature  

### Correct answer: A

**Why A is correct:** Keyword/full-text retrieval excels at exact strings, codes, and identifiers.

**Why the others are incorrect:** They are generation/training controls rather than exact textual retrieval techniques.

---

## Question 3

A user asks:

```text
How do I recover access to my account?
```

The indexed document is titled:

```text
Reset forgotten login credentials
```

The wording differs but the meaning is similar.

Which retrieval method is most useful?

A. Vector search  
B. Stop sequence  
C. Frequency penalty  
D. Fine-tuning  

### Correct answer: A

**Why A is correct:** Vector search uses embeddings to identify semantic similarity despite different wording.

---

## Question 4

A search solution must find exact product identifiers while also understanding natural-language intent.

Which search approach is best?

A. Keyword search only  
B. Vector search only  
C. Hybrid search  
D. Higher temperature  

### Correct answer: C

**Why C is correct:** Hybrid search combines keyword and vector retrieval and therefore handles both lexical precision and semantic similarity.

---

## Question 5

Search retrieves relevant documents, but the most helpful result often appears below less useful results.

What should you consider?

A. Increase temperature  
B. Semantic reranking  
C. Increase presence penalty  
D. Reduce embedding dimensions without evaluation  

### Correct answer: B

**Why B is correct:** Reranking reorders retrieved candidates based on semantic relevance.

---

## Question 6

Large policy documents produce poor retrieval because individual documents contain many unrelated topics.

What should you do?

A. Increase temperature  
B. Chunk the documents into meaningful sections  
C. Fine-tune the generation model  
D. Remove the search index  

### Correct answer: B

**Why B is correct:** Chunking improves retrieval granularity and semantic representation while helping respect model input limits.

---

## Question 7

You divide documents into chunks, but important sentences at boundaries lose context.

What should you consider?

A. Chunk overlap or structure-aware chunking  
B. Higher temperature  
C. Lower frequency penalty  
D. JSON mode  

### Correct answer: A

**Why A is correct:** Overlap preserves some context between adjacent chunks; structure-aware chunking can also avoid arbitrary cuts.

---

## Question 8

A search query should return documents only from the `Finance` department.

Which capability should you use?

A. Temperature  
B. Metadata filtering on a filterable field  
C. Presence penalty  
D. More output tokens  

### Correct answer: B

**Why B is correct:** Structured metadata filtering restricts search results according to exact field conditions.

---

## Question 9

You need fast approximate nearest-neighbor vector search over a large index.

Which Azure AI Search algorithm should you consider?

A. HNSW  
B. Frequency penalty  
C. Semantic prompt  
D. Fine-tuning  

### Correct answer: A

**Why A is correct:** HNSW is designed for performant approximate nearest-neighbor vector search.

---

## Question 10

A complex conversational question needs to be decomposed into several searches across multiple knowledge sources.

Which modern retrieval pattern is most relevant?

A. Agentic retrieval  
B. Temperature tuning  
C. JSON mode  
D. Presence penalty  

### Correct answer: A

**Why A is correct:** Agentic retrieval can apply LLM-based query planning, subqueries, and multi-source retrieval for complex questions.

---

## Question 11

An application already has current enterprise facts, but responses do not follow the required professional style.

What should you improve first?

A. RAG index size  
B. Prompt/application instructions  
C. HNSW configuration  
D. Chunk overlap  

### Correct answer: B

**Why B is correct:** The issue is behavior/style, not missing knowledge.

---

## Question 12

You need to convert text into numerical semantic representations for similarity search.

What do you use?

A. Embedding model  
B. Chat completion model only  
C. Temperature  
D. Semantic ranker only  

### Correct answer: A

**Why A is correct:** Embedding models convert content into vectors used for semantic similarity search.

---

# High-Value Exam Traps

## Trap 1

```text
Private/current information
```

Do not choose:

```text
Higher temperature
Few-shot examples
```

Choose:

```text
RAG / grounding
```

---

## Trap 2

```text
Exact error code/product ID
```

Think:

```text
Keyword retrieval
```

---

## Trap 3

```text
Different words, same meaning
```

Think:

```text
Vector search / embeddings
```

---

## Trap 4

```text
Need both exact terms and semantic understanding
```

Think:

```text
Hybrid search
```

---

## Trap 5

```text
Results retrieved correctly but ordered poorly
```

Think:

```text
Semantic reranking
```

---

## Trap 6

```text
Huge documents, irrelevant retrieval
```

Think:

```text
Chunking strategy
```

---

## Trap 7

```text
Knowledge changes frequently
```

Usually think:

```text
RAG
```

not repeated fine-tuning.

---

# One-Minute Revision Sheet

```text
RAG
Retrieve -> Augment -> Generate

INDEX
Optimized structure for retrieval

CHUNKING
Split large documents into meaningful pieces

OVERLAP
Preserve context across chunk boundaries

EMBEDDINGS
Text -> numeric semantic vector

KEYWORD SEARCH
Exact words / codes / identifiers

VECTOR SEARCH
Semantic similarity / meaning

HYBRID SEARCH
Keyword + vector

SEMANTIC RANKING
Rerank candidate results using semantic relevance

FILTER
Restrict results using structured metadata

HNSW
Fast approximate nearest-neighbor vector search

EXHAUSTIVE KNN
Exhaustive/exact nearest-neighbor comparison

CLASSIC RAG
Known query -> retrieve -> ground -> generate

AGENTIC RETRIEVAL
Query planning + decomposition + multi-source retrieval

FINE-TUNING
Learn behavior/patterns

PROMPT ENGINEERING
Tell the model how to behave
```

# Final AI-103 Decision Rule

```text
Missing current/private knowledge?
-> RAG

Exact words/codes?
-> Keyword search

Same meaning, different words?
-> Vector search

Need both?
-> Hybrid search

Correct docs but bad ranking?
-> Semantic reranking

Large documents?
-> Chunking

Boundary context lost?
-> Overlap / semantic chunking

Restrict by metadata?
-> Filter

Need semantic numerical representation?
-> Embeddings

Need complex query decomposition?
-> Agentic retrieval

Wrong response style?
-> Prompt engineering

Need deeper learned behavior change?
-> Fine-tuning
```

## Suggested next AI-103 topic

**Agents: tools, function calling, instructions, agent orchestration, planning, reflection, and multi-agent patterns**

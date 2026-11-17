# AI-103: Vector Search

## 1. What is Vector Search?

**Vector search** retrieves content by comparing numeric vector representations of meaning rather than relying only on exact keyword matches.

```text
User query
   |
   v
Embedding model / vectorizer
   |
   v
Query vector
   |
   v
Vector similarity search
   |
   v
Nearest document/chunk vectors
   |
   v
Relevant results
```

### AI-103 exam memory

```text
Keyword search = lexical similarity
Vector search  = semantic/conceptual similarity
```

Example:

```text
Query:
"How do I recover access to my account?"

Indexed content:
"Reset forgotten login credentials"
```

The words differ, but their meanings are similar. Vector search can retrieve the content because embeddings represent semantic meaning.

---

## 2. Vector Search Workflow

### Indexing side

```text
Documents
   |
   v
Chunk content
   |
   v
Embedding model
   |
   v
Document/chunk vectors
   |
   v
Vector fields in Azure AI Search index
```

### Query side

```text
User query
   |
   v
Embedding model / vectorizer
   |
   v
Query vector
   |
   v
Search vector field
   |
   v
Top K nearest vectors
```

### Critical exam rule

Use compatible vectors for indexed content and queries. Microsoft recommends using the **same embedding model** used to create the indexed document vectors when generating query embeddings.

---

## 3. Vector Fields

An Azure AI Search index can contain ordinary fields and vector fields.

Conceptual schema:

```text
id               string
content          string
category         string
contentVector    Collection(Edm.Single)
```

The vector field stores the embedding.

### Important configuration concepts

- Vector field data type
- Dimensions
- Searchable vector field
- Vector search profile
- Algorithm configuration
- Vectorizer, when integrated query vectorization is used

### Exam clue

```text
Need semantic similarity against embeddings
-> Search a vector field
```

---

## 4. Dimensions

The vector field dimensions must match the embedding configuration.

```text
Embedding output
[0.12, 0.55, ..., -0.44]

Number of values = field dimensions
```

### Exam trap

```text
Embedding model returns N-dimensional vectors
but search field expects M dimensions
```

This is a configuration mismatch.

Fix:

```text
Align vector field dimensions with embedding output
```

Do not solve it by changing temperature or top-p.

---

## 5. Similarity Metrics

Once candidate vectors are found, similarity metrics determine how near the query vector is to stored vectors.

Important metrics include:

- Cosine
- Dot product
- Euclidean distance

### Cosine similarity

Cosine similarity focuses on vector direction.

```text
Similar direction
-> greater semantic similarity
```

### AI-103 association

For Azure OpenAI embedding scenarios, **cosine** is an important metric to recognize.

---

## 6. K-Nearest Neighbors

A vector query usually asks for the `k` nearest vectors.

Conceptually:

```text
k = 5
```

means:

```text
Return five nearest candidate vectors
```

### Too small K

- Relevant evidence might be missed.
- RAG may not receive enough context.

### Too large K

- More irrelevant content can be returned.
- Token/cost usage can increase.
- More reranking may be required.

### Exam rule

```text
K = number of nearest vector results requested
```

---

## 7. HNSW

**HNSW (Hierarchical Navigable Small World)** is an approximate nearest-neighbor algorithm.

It creates a graph structure during indexing that enables efficient traversal at query time.

```text
Large vector collection
       |
       v
HNSW graph
       |
       v
Approximate nearest neighbors
```

### Advantages

- Low-latency vector retrieval
- High recall when configured appropriately
- Well suited to larger datasets and many production scenarios

### Trade-off

HNSW is approximate. It trades guaranteed exhaustive comparison for performance.

It also consumes vector-index quota because of the graph structures it creates.

### Exam memory

```text
HNSW
= ANN
= approximate
= performant
= good for larger vector datasets
```

---

## 8. Exhaustive KNN

**Exhaustive KNN** performs brute-force comparison across the complete vector space.

```text
Query vector
    |
    v
Compare against ALL vectors
    |
    v
Exact nearest neighbors
```

### Advantages

- Exact nearest-neighbor result set
- Useful when precision is more important than query speed
- Useful as ground truth for evaluating ANN recall

### Disadvantages

- Computationally intensive
- Less suitable for large datasets requiring low latency

### AI-103 memory

```text
Exhaustive KNN
= brute force
= exact neighbors
= higher compute
= useful for small/medium data or ANN evaluation
```

---

## 9. HNSW vs Exhaustive KNN

| HNSW | Exhaustive KNN |
|---|---|
| Approximate nearest neighbor | Exact nearest neighbor |
| Fast / lower latency | More computationally intensive |
| Useful for large datasets | Useful when exactness is critical |
| Graph-based index | Brute-force scan |
| Consumes vector index quota | Doesn't require the same HNSW graph quota |
| Can be evaluated against exhaustive ground truth | Can provide ground truth for ANN recall |

### Most important exam distinction

```text
Need scalable/fast ANN
-> HNSW

Need exact exhaustive nearest neighbors
-> Exhaustive KNN
```

---

## 10. Exact Keyword Search vs Vector Search

### Keyword search

Best when exact terms matter:

```text
ERR-1047
SKU-9982
GPT-5.6
Employee ID
Product name
```

### Vector search

Best when semantic meaning matters:

```text
"recover my login"
vs
"reset forgotten credentials"
```

### Decision rule

```text
Exact WORDS/codes
-> keyword

Same MEANING
-> vector
```

---

## 11. Hybrid Search

In Azure AI Search, **hybrid search** runs full-text keyword search and vector search in a single request.

```text
               Query
                 |
        +--------+--------+
        |                 |
        v                 v
Full-text search     Vector search
        |                 |
        +--------+--------+
                 |
                 v
         Merge using RRF
                 |
                 v
        Unified result set
```

Hybrid search combines:

```text
Lexical precision
+
Semantic similarity
```

### Exam example

Query:

```text
AUTH-2078 user cannot log in after password reset
```

- Keyword search helps identify `AUTH-2078`.
- Vector search finds semantically related authentication content.

Think:

```text
Hybrid search
```

---

## 12. Reciprocal Rank Fusion (RRF)

Azure AI Search uses **Reciprocal Rank Fusion (RRF)** to merge ranked output from parallel search methods in hybrid queries.

Simplified idea:

```text
Keyword ranking
      +
Vector ranking
      |
      v
     RRF
      |
      v
Combined ranking
```

### AI-103 memory

```text
Hybrid search result merging
-> RRF
```

Do not confuse this with semantic ranking.

---

## 13. Semantic Ranker vs Vector Search

Vector retrieval and semantic ranking are different stages/capabilities.

```text
Vector search
-> retrieves using vector similarity

Semantic ranker
-> reranks an initial candidate set based on semantic relevance
```

A useful high-quality retrieval pattern is:

```text
Hybrid retrieval
       |
       v
Candidate results
       |
       v
Semantic ranking
       |
       v
Better ordered grounding results
```

Microsoft documentation notes strong relevance benefits in benchmark testing for hybrid queries combined with semantic ranking.

---

## 14. Filtered Vector Search

A vector query can be combined with filter expressions over filterable nonvector fields.

Example concept:

```text
Semantic query:
"parental leave"

Filter:
department eq 'HR'
```

This gives:

```text
Semantic similarity
+
Structured restriction
```

### Exam clue

```text
Find semantically similar content
ONLY from Finance documents
```

Think:

```text
Vector query + metadata filter
```

---

## 15. Pre-Filter vs Post-Filter Concepts

Filter timing affects vector retrieval behavior.

Conceptually:

### Pre-filter

```text
Apply eligible-document constraints
        |
        v
Run vector search within eligible content
```

Useful when filters represent strict constraints such as authorization or category restrictions.

### Post-filter

```text
Run vector candidate retrieval
        |
        v
Apply filter to results
```

This can reduce the number of usable results if candidates are filtered out after retrieval.

### Exam thinking

For security/strict eligibility, make sure filtering cannot expose unauthorized content and understand the filter mode supported by the search configuration.

---

## 16. Integrated Vectorization

A query does not have to arrive as a precomputed vector.

With a configured vectorizer, Azure AI Search can convert text input into a vector at query time.

```text
User text query
      |
      v
Configured vectorizer
      |
      v
Embedding model
      |
      v
Query vector
      |
      v
Vector search
```

### Manual vectorization

Your application can instead call the embedding model itself:

```text
Application
   |
Call embedding model
   |
Query vector
   |
Azure AI Search
```

### Memory rule

```text
Vectorizer
-> query-time text/image to vector conversion
```

---

## 17. Multiple Vector Fields

An index can contain multiple vector fields.

Example:

```text
titleVector
contentVector
imageVector
```

A vector query can target multiple vector fields, depending on the index and query configuration.

### Use case

A solution might search:

- Title meaning
- Body meaning
- Image meaning

and combine retrieval evidence.

---

## 18. Multiple Vector Queries and Weighting

Azure AI Search can support multiple vector query inputs and weighting.

Conceptually:

```text
Vector query A: title meaning     weight = higher
Vector query B: content meaning   weight = standard
```

Use weights when some retrieval signals should contribute more strongly than others.

### Exam clue

```text
One vector query/field should influence ranking more strongly
```

Think:

```text
Vector weighting
```

---

## 19. Vector Search for RAG

Vector search frequently supplies the retrieval layer of a RAG system.

```text
User question
      |
      v
Query embedding
      |
      v
Vector / hybrid search
      |
      v
Relevant chunks
      |
      v
Grounding context
      |
      v
LLM
      |
      v
Grounded answer
```

### Important distinction

```text
Vector search != RAG
```

Vector search retrieves.

RAG performs:

```text
Retrieve -> Augment -> Generate
```

---

## 20. Vector Search for Multilingual Content

With a suitable multilingual embedding model, vector search can match concepts across languages.

```text
English query
     |
     v
Shared semantic embedding space
     |
     v
Relevant content in another supported language
```

This is possible because vector retrieval operates on semantic representations rather than only identical terms.

---

## 21. Multimodal Vector Search

With supported multimodal embeddings, vector search can work across content types.

Examples:

```text
Text -> similar image
Image -> related text
Image -> similar image
```

The embedding model must create compatible representations for the modalities being searched.

---

## 22. Improving Poor Vector Retrieval

When results are poor, evaluate the entire retrieval pipeline rather than immediately changing the LLM.

Check:

1. **Embedding model compatibility**
   - Are documents and query embedded using compatible/same model configuration?

2. **Chunking strategy**
   - Are chunks too large or too small?

3. **Vector field dimensions**
   - Do they match the embedding output?

4. **Correct vector field**
   - Is the query targeting the intended field?

5. **K value**
   - Are you retrieving enough useful candidates?

6. **Search approach**
   - Would hybrid search improve exact-term retrieval?

7. **Filters**
   - Are filters removing relevant candidates?

8. **Semantic ranking**
   - Would reranking improve top-result ordering?

9. **HNSW tuning/recall**
   - Compare approximate retrieval against exhaustive ground truth when needed.

### Exam rule

```text
Poor retrieval
-> Diagnose retrieval configuration

Do not automatically:
-> Fine-tune the LLM
-> Increase temperature
```

---

## 23. Vector Search Evaluation

Useful retrieval metrics include:

- Recall@K
- Precision@K
- Mean Reciprocal Rank (MRR)
- NDCG

### HNSW evaluation pattern

```text
Exhaustive KNN results
       |
       v
Ground truth
       |
       v
Compare HNSW results
       |
       v
Measure ANN recall
```

Microsoft specifically identifies exhaustive KNN as useful for generating a ground-truth neighbor set when evaluating ANN recall.

---

## 24. Security

Vector search does not replace authorization.

If an index contains confidential HR and Finance content, semantic similarity alone must not decide whether the user may retrieve it.

Use:

- Metadata-based security filters
- Permission-aware indexing/retrieval
- Microsoft Entra ID
- Azure RBAC where applicable
- Least privilege

### Exam rule

```text
Semantic relevance
!=
Authorization
```

---

# AI-103 Vector Search Decision Table

| Requirement | Best concept |
|---|---|
| Same meaning, different words | Vector search |
| Exact code/name/identifier | Keyword search |
| Exact terms + meaning | Hybrid search |
| Merge keyword + vector rankings | RRF |
| Fast ANN over large vector set | HNSW |
| Exact nearest neighbors | Exhaustive KNN |
| Evaluate ANN recall | Exhaustive KNN as ground truth |
| Compare semantic vectors | Similarity metric, often cosine for Azure OpenAI embeddings |
| Restrict semantic results by metadata | Filtered vector search |
| Convert text query automatically to vector | Vectorizer / integrated vectorization |
| Improve order of candidate results | Semantic ranker |
| Retrieve private/current data for LLM | RAG using vector/hybrid retrieval |
| Search across modalities | Multimodal embeddings/vector search |

---

# Practice Questions

## Question 1

A user asks "How can I recover my login?" but the indexed document says "Reset forgotten credentials."

Which technique is most suitable?

A. Keyword search only  
B. Vector search  
C. Higher temperature  
D. Fine-tuning  

### Correct answer: B

**Why B is correct:** Vector search finds semantically similar content even when exact words differ.

**Why the others are incorrect:**

- **A:** Exact lexical matching can miss differently worded content.
- **C:** Temperature controls generation randomness.
- **D:** Fine-tuning does not address this retrieval requirement.

---

## Question 2

A search query is `ERR-9487` and exact matching is critical.

Which retrieval type is especially important?

A. Keyword search  
B. Presence penalty  
C. HNSW only  
D. Temperature  

### Correct answer: A

**Why A is correct:** Keyword/full-text search is strong for exact identifiers and codes.

---

## Question 3

A query contains both `ERR-9487` and a natural-language description of a login failure.

Which approach should you consider?

A. Keyword only  
B. Vector only  
C. Hybrid search  
D. Fine-tuning  

### Correct answer: C

**Why C is correct:** Hybrid search combines lexical precision with semantic similarity.

---

## Question 4

You need fast approximate nearest-neighbor search over a large vector dataset.

Which algorithm is most appropriate?

A. HNSW  
B. Exhaustive KNN only  
C. BM25 only  
D. Frequency penalty  

### Correct answer: A

**Why A is correct:** HNSW is optimized for high-recall, low-latency approximate nearest-neighbor retrieval.

---

## Question 5

You need an exact nearest-neighbor set to use as ground truth when measuring ANN recall.

Which algorithm should you use?

A. HNSW  
B. Exhaustive KNN  
C. Semantic ranker  
D. Temperature  

### Correct answer: B

**Why B is correct:** Exhaustive KNN scans the whole vector space and can provide the global nearest-neighbor set used as evaluation ground truth.

---

## Question 6

A hybrid query runs full-text and vector search in parallel. Which mechanism merges the ranked result sets in Azure AI Search?

A. Reciprocal Rank Fusion (RRF)  
B. Temperature sampling  
C. Frequency penalty  
D. Chunk overlap  

### Correct answer: A

**Why A is correct:** Azure AI Search uses RRF to combine rankings from the parallel search methods.

---

## Question 7

A semantic query should search only documents where `department = 'Finance'`.

What should you use?

A. Vector search plus metadata filtering  
B. Higher temperature  
C. Frequency penalty  
D. Fine-tuning  

### Correct answer: A

**Why A is correct:** Filtering constrains the eligible records while vector search handles semantic similarity.

---

## Question 8

You want users to submit plain text queries without your application manually calling the embedding endpoint first.

What should you configure?

A. Vectorizer / integrated query vectorization  
B. Higher top-p  
C. Fine-tuning  
D. Stop sequence  

### Correct answer: A

**Why A is correct:** A configured vectorizer can convert query text into a vector during query processing.

---

## Question 9

Documents were indexed with one embedding model, while queries use an incompatible model and retrieval quality is poor.

What should you do?

A. Use compatible, typically the same, embedding model/configuration for documents and queries  
B. Increase temperature  
C. Add more output tokens  
D. Increase presence penalty  

### Correct answer: A

**Why A is correct:** The vectors must exist in a compatible embedding space for meaningful comparisons.

---

## Question 10

The correct documents are being retrieved, but their ranking is poor.

What should you consider?

A. Semantic ranking/reranking  
B. Higher temperature  
C. Fine-tuning the embedding model immediately  
D. Smaller output token limit  

### Correct answer: A

**Why A is correct:** The retrieval candidates are already correct; the main problem is their ordering.

---

## Question 11

A vector field expects 1,536 dimensions but your selected embedding configuration generates a different vector size.

What is the core issue?

A. Vector field/embedding dimension mismatch  
B. Temperature mismatch  
C. RRF failure  
D. Prompt injection  

### Correct answer: A

**Why A is correct:** The search field must be configured for the vector dimensions produced by the embedding configuration.

---

## Question 12

A RAG system needs semantically relevant chunks from private documents before generating an answer.

What role does vector search play?

A. It retrieves semantically relevant grounding content  
B. It generates the final answer itself  
C. It replaces authorization  
D. It fine-tunes the language model  

### Correct answer: A

**Why A is correct:** Vector search handles semantic retrieval. The generative model uses retrieved content to create the final grounded answer.

---

# High-Value Exam Traps

## Trap 1

```text
Same meaning, different words
-> Vector search
```

Do not choose keyword-only search automatically.

---

## Trap 2

```text
Exact error code
-> Keyword search
```

Vector-only retrieval isn't always best for exact identifiers.

---

## Trap 3

```text
Exact terms + semantic meaning
-> Hybrid search
```

---

## Trap 4

```text
Hybrid results merged
-> RRF
```

Do not confuse RRF with semantic ranking.

---

## Trap 5

```text
Fast approximate nearest neighbor
-> HNSW
```

---

## Trap 6

```text
Exact global nearest neighbors
-> Exhaustive KNN
```

---

## Trap 7

```text
Correct candidates, poor ordering
-> Semantic ranker
```

---

## Trap 8

```text
Need Finance-only semantic results
-> Vector search + filter
```

---

## Trap 9

```text
Vector search = authorization
```

Wrong. Retrieval relevance and access control are separate concerns.

---

# One-Minute Revision Sheet

```text
VECTOR SEARCH
Semantic similarity using numeric vectors

VECTOR FIELD
Stores embeddings in search index

K
Number of nearest-vector results requested

COSINE
Important similarity metric for embedding retrieval

HNSW
Approximate nearest neighbor
Fast, scalable, graph based

EXHAUSTIVE KNN
Exact brute-force nearest neighbors
Useful for ground truth

KEYWORD SEARCH
Exact lexical matching

HYBRID SEARCH
Keyword + vector in same request

RRF
Merges hybrid ranked result lists

SEMANTIC RANKER
Reranks candidate search results

FILTERED VECTOR SEARCH
Semantic retrieval + structured restrictions

VECTORIZER
Converts query text/image to vector at query time

RAG
Vector/hybrid search can retrieve grounding context
```

# Final AI-103 Decision Rule

```text
Same meaning, different wording?
-> Vector search

Exact code/name?
-> Keyword search

Need both?
-> Hybrid search

Need fast ANN?
-> HNSW

Need exact neighbors / ANN ground truth?
-> Exhaustive KNN

Need to merge full-text + vector rankings?
-> RRF

Need better ordering after retrieval?
-> Semantic ranker

Need semantic results from only one category/user scope?
-> Vector search + filters

Need text automatically converted to vector?
-> Vectorizer

Need grounded LLM answer?
-> RAG using retrieved chunks
```

# AI-103: Hybrid Search

## 1. What is Hybrid Search?

In Azure AI Search, **hybrid search** combines a full-text keyword query and one or more vector queries in a **single search request**.

```text
User query
    |
    +-------------------+
    |                   |
    v                   v
Keyword/full-text     Vector search
(BM25)                (HNSW/eKNN)
    |                   |
    +---------+---------+
              |
              v
              RRF
              |
              v
      Unified ranked results
```

The keyword and vector queries execute in parallel, and Azure AI Search merges their ranked result lists by using **Reciprocal Rank Fusion (RRF)**.

### AI-103 exam memory

```text
HYBRID SEARCH = KEYWORD + VECTOR
MERGE RESULTS = RRF
```

---

## 2. Why Use Hybrid Search?

Keyword and vector search solve different problems.

### Keyword search is strong for

- Exact IDs
- Product codes
- Names
- Dates
- Specialized terminology
- Exact phrases

### Vector search is strong for

- Semantic similarity
- Natural-language intent
- Different wording with similar meaning
- Conceptual matches

Hybrid search combines both strengths.

### Example

```text
Query:
AUTH-2047 user cannot log in after password reset
```

Keyword search can strongly match:

```text
AUTH-2047
```

Vector search can retrieve material about:

```text
authentication failure
credential reset
login access
```

### Exam rule

```text
Need exact lexical match + semantic similarity
-> Hybrid Search
```

---

## 3. Hybrid Search Pipeline

```text
                         User query
                             |
               +-------------+--------------+
               |                            |
               v                            v
        Full-text query                Vector query
               |                            |
               v                            v
          BM25 ranking             HNSW / exhaustive KNN
               |                            |
               +-------------+--------------+
                             |
                             v
                 Reciprocal Rank Fusion
                             |
                             v
                    Unified result set
                             |
                             v
               Optional semantic ranker
                             |
                             v
                  Higher-quality results
```

This sequence is extremely important for AI-103.

---

## 4. BM25 in Hybrid Search

The text portion of Azure AI Search uses full-text relevance ranking, commonly **BM25**.

Think:

```text
BM25
-> exact/lexical relevance
```

It is useful when words themselves matter.

Example:

```text
ERR-9098
Microsoft Foundry
Invoice-2026-001
```

### Do not confuse

```text
BM25 != vector similarity
```

BM25 works on text terms, while vector search compares embeddings.

---

## 5. Vector Search in Hybrid Search

The vector portion of the query searches vector fields containing embeddings.

```text
User query
    |
    v
Embedding/vectorizer
    |
    v
Query vector
    |
    v
HNSW / exhaustive KNN
    |
    v
Semantically similar content
```

### Key idea

```text
Query:
recover account access

Document:
reset forgotten credentials
```

Different words, similar meaning. Vector retrieval can find the relationship.

---

## 6. Parallel Execution

In a hybrid request, keyword and vector searches execute in parallel.

```text
             Query
       +------+------+
       |             |
       v             v
     Text          Vector
       |             |
       v             v
 Ranked list A   Ranked list B
       +-------------+
             |
             v
             RRF
```

### Exam question clue

```text
Which mechanism combines the results of keyword and vector searches?
```

Answer:

```text
Reciprocal Rank Fusion (RRF)
```

---

## 7. Reciprocal Rank Fusion (RRF)

RRF combines already-ranked lists into a single ranking.

Conceptually:

```text
Text ranking:
A
B
C

Vector ranking:
B
D
A

        |
        v
       RRF
        |
        v
Unified ranking
```

Items that rank highly across multiple lists gain stronger combined scores.

Microsoft describes the reciprocal-rank contribution approximately as:

```text
1 / (rank + k)
```

where the RRF constant is commonly around `60` in the algorithm.

### Very important trap

This RRF constant `k` is **not** the same as the vector query `k` that specifies how many nearest neighbors to retrieve.

```text
RRF k
-> fusion algorithm constant

Vector query k
-> number of nearest neighbors requested
```

---

## 8. RRF vs Semantic Ranker

Easy AI-103 trap.

### RRF

```text
Multiple ranked lists
       |
       v
Merge them
```

### Semantic ranker

```text
Initial candidate results
       |
       v
Language-understanding reranking
```

### Exam memory

```text
MERGE rankings   -> RRF
RERANK by meaning -> Semantic Ranker
```

They can be used sequentially:

```text
Keyword + Vector
      |
      v
     RRF
      |
      v
Semantic Ranker
```

---

## 9. Hybrid Search + Semantic Ranker

Microsoft guidance highlights **hybrid search with semantic ranker** as a strong classic relevance strategy in Azure AI Search.

```text
Keyword retrieval
       +
Vector retrieval
       |
       v
      RRF
       |
       v
Combined candidates
       |
       v
Semantic ranker
       |
       v
Final high-relevance results
```

### AI-103 rule

If a question says:

```text
Need lexical precision
+ semantic similarity
+ best semantic ordering
```

think:

```text
Hybrid Search + Semantic Ranker
```

---

## 10. Hybrid Search Query Structure

A hybrid request conceptually contains both:

```json
{
  "search": "authentication error AUTH-2047",
  "vectorQueries": [
    {
      "kind": "text",
      "text": "authentication error AUTH-2047",
      "fields": "contentVector",
      "k": 50
    }
  ]
}
```

The exact API shape varies by API version and whether integrated vectorization is configured.

### Core exam concept

```text
search
-> full-text query

vectorQueries
-> vector retrieval

Both together
-> hybrid search
```

---

## 11. Integrated Vectorization in Hybrid Search

With a configured vectorizer, Azure AI Search can convert plain-text query input into a vector.

```text
User text
    |
    +--------------------+
    |                    |
    v                    v
Keyword query       Vectorizer
                         |
                         v
                    Query vector
                         |
                         v
                    Vector search
```

Without integrated vectorization, your application can generate the query embedding itself and send the vector.

### Exam memory

```text
Automatic query string -> vector
-> Vectorizer / integrated vectorization
```

---

## 12. Filters with Hybrid Search

Hybrid queries can use filters over filterable nonvector fields.

Example:

```text
Query:
"authentication troubleshooting"

Filter:
department eq 'IT'
```

This provides:

```text
Keyword relevance
+
Vector similarity
+
Metadata restriction
```

### Use cases

- Department
- Country
- Language
- Date
- Security/authorization scope
- Document type

### Exam clue

```text
Return hybrid results only for Finance documents
```

Think:

```text
Hybrid search + filter
```

---

## 13. Semantic Ranking after Hybrid Search

Semantic ranker can apply second-stage ranking to the text representation of candidate results from a hybrid query.

```text
Hybrid retrieval
      |
      v
RRF candidates
      |
      v
Semantic ranker (L2)
      |
      v
Improved semantic ordering
```

### Critical distinction

Semantic ranking does not replace hybrid retrieval.

```text
Hybrid -> candidate retrieval/fusion
Semantic ranker -> second-stage reranking
```

---

## 14. Hybrid Search for RAG

Hybrid search is especially useful for retrieving grounding data for classic RAG.

```text
User question
      |
      v
Hybrid search
(keyword + vector)
      |
      v
RRF
      |
      v
Optional semantic ranker
      |
      v
Top relevant chunks
      |
      v
LLM grounding prompt
      |
      v
Generated answer
```

### Why it works well

Enterprise content often contains both:

- Exact identifiers and technical terms
- Natural-language descriptions

Hybrid retrieval captures both.

---

## 15. Vector Weighting

Azure AI Search hybrid/vector queries can apply weighting to vector queries so that one vector signal contributes more strongly to the combined ranking.

Conceptually:

```text
Title vector query   weight = higher
Content vector query weight = standard
```

### Exam clue

```text
One semantic/vector signal should have more influence on the final ranking
```

Think:

```text
Vector weighting
```

---

## 16. Multiple Vector Queries

A hybrid request can contain multiple vector queries.

Example concept:

```text
Full-text query
+
Title vector query
+
Content vector query
```

Each produces a ranked signal. Azure AI Search can use RRF to combine multiple ranked result lists.

### Important

RRF is not limited to exactly one keyword list plus one vector list. It is used when multiple queries execute in parallel, including multiple vector queries.

---

## 17. Hybrid Search vs Vector Search

### Vector-only search

Use when semantic similarity is the main requirement.

```text
Different wording
Same meaning
```

### Hybrid search

Use when both lexical precision and semantic similarity matter.

```text
Exact identifier
+
Natural-language meaning
```

### Example

```text
Query:
SR-2026-998 password authentication error
```

Hybrid search is stronger because:

```text
SR-2026-998
-> keyword

password authentication error
-> vector meaning
```

---

## 18. Hybrid Search vs Semantic Search

Do not treat these as identical.

### Hybrid search

```text
Keyword retrieval + Vector retrieval + RRF
```

### Semantic ranker

```text
Second-stage semantic reranking
```

A common chain is:

```text
Hybrid Search
    |
    v
RRF
    |
    v
Semantic Ranker
```

---

## 19. Hybrid Search vs Agentic Retrieval

### Classic hybrid RAG

```text
Single query
   |
Hybrid retrieval
   |
RRF
   |
Optional semantic ranker
   |
Ground LLM
```

### Agentic retrieval

```text
Complex user question
       |
LLM query planning
       |
Multiple subqueries / knowledge sources
       |
Retrieval
       |
Structured grounding / answer workflow
```

### AI-103 distinction

```text
Known/simple classic retrieval flow
-> Hybrid search

Complex conversational query requiring decomposition/planning
-> Agentic retrieval
```

Pay attention to GA versus preview wording in the scenario.

---

## 20. Hybrid Search Relevance Troubleshooting

If hybrid results are poor, inspect the pipeline.

### Check keyword retrieval

- Are important exact terms indexed as searchable text?
- Are analyzers appropriate?
- Are product codes being tokenized unexpectedly?

### Check vector retrieval

- Are the query and documents using compatible embedding models?
- Are chunks meaningful?
- Are vector dimensions correct?
- Is vector `k` sufficient?

### Check fusion

- Are multiple useful ranked signals reaching RRF?
- Would vector weighting improve balance?

### Check reranking

- Would semantic ranker improve final top results?

### Check filters

- Are filters unintentionally removing relevant documents?

### Exam rule

```text
Poor search relevance
-> diagnose retrieval and ranking

Do not immediately:
-> increase temperature
-> fine-tune the generative LLM
```

---

## 21. Understanding Search Scores

Different stages produce different types of scores.

```text
Full-text search
-> BM25 @search.score

Vector search
-> vector similarity-derived ranking

Hybrid fusion
-> RRF @search.score

Semantic ranker
-> @search.rerankerScore
```

### Important

Don't compare score values from different algorithms as though their numeric ranges have identical meaning.

Use them within the context of the relevant ranking stage.

---

## 22. Security

Hybrid search improves relevance, not authorization.

```text
Relevant document
!=
Authorized document
```

For enterprise RAG, use controls such as:

- Permission-aware indexing/retrieval
- Metadata security filters
- Microsoft Entra ID
- Azure RBAC where applicable
- Least privilege

A user must not receive a document merely because both keyword and vector search rank it highly.

---

# AI-103 Hybrid Search Decision Table

| Requirement | Think |
|---|---|
| Exact words/codes only | Keyword search |
| Semantic similarity only | Vector search |
| Exact terms + semantic similarity | Hybrid search |
| Merge ranked lists | RRF |
| Improve final semantic ordering | Semantic ranker |
| Convert query text to vector automatically | Vectorizer |
| Restrict results by metadata | Filter |
| Make one vector signal stronger | Vector weighting |
| Ground a classic RAG application | Hybrid + optional semantic ranker |
| Complex query planning/decomposition | Agentic retrieval |

---

# Practice Questions

## Question 1

A support search query contains the exact error code `AUTH-2047` plus a natural-language description of a login problem.

Which approach is best?

A. Keyword search only  
B. Vector search only  
C. Hybrid search  
D. Increase temperature  

### Correct answer: C

**Why C is correct:** Keyword search captures the exact error code while vector search captures the semantic meaning of the description.

**Why the others are incorrect:**

- **A:** May miss semantically similar troubleshooting content.
- **B:** May be weaker for exact identifiers.
- **D:** Temperature controls generation, not retrieval.

---

## Question 2

In Azure AI Search, full-text and vector searches execute in parallel in a hybrid request. What merges the ranked lists?

A. Reciprocal Rank Fusion (RRF)  
B. Semantic caption  
C. Temperature sampling  
D. Chunk overlap  

### Correct answer: A

**Why A is correct:** RRF combines the ranked outcomes into one unified ranking.

---

## Question 3

After hybrid retrieval and RRF, the correct documents exist in the result set but aren't ordered optimally by meaning.

What should you consider?

A. Semantic ranker  
B. Higher temperature  
C. Presence penalty  
D. More output tokens  

### Correct answer: A

**Why A is correct:** Semantic ranker applies second-stage language-understanding reranking.

---

## Question 4

Which statement correctly describes hybrid search?

A. It replaces vector search with BM25  
B. It executes full-text and vector queries together and fuses their results  
C. It is another name for semantic ranking  
D. It fine-tunes an embedding model  

### Correct answer: B

**Why B is correct:** Hybrid search performs both retrieval methods and merges their rankings.

---

## Question 5

A user submits plain text, and you want Azure AI Search to create the query embedding automatically before executing the vector portion of a hybrid query.

What should you configure?

A. Vectorizer  
B. Frequency penalty  
C. Fine-tuning  
D. Stop sequence  

### Correct answer: A

**Why A is correct:** A vectorizer supports built-in query-time conversion from text or other supported input into vectors.

---

## Question 6

A hybrid query must return only documents for `department = 'Finance'`.

What should you add?

A. Metadata filter  
B. Higher temperature  
C. Presence penalty  
D. Fine-tuning  

### Correct answer: A

**Why A is correct:** Filters restrict eligible documents using structured fields while hybrid retrieval determines relevance.

---

## Question 7

What does RRF mainly do?

A. Generate embeddings  
B. Merge multiple ranked result lists  
C. Generate a final RAG answer  
D. Split documents into chunks  

### Correct answer: B

**Why B is correct:** RRF is a rank-fusion algorithm.

---

## Question 8

Which is the correct pipeline for a high-quality classic RAG retrieval pattern?

A. Keyword + vector -> RRF -> optional semantic ranker -> LLM grounding  
B. Temperature -> embeddings -> fine-tuning  
C. Semantic caption -> temperature -> BM25  
D. Max tokens -> HNSW -> fine-tuning  

### Correct answer: A

**Why A is correct:** Hybrid retrieval provides both lexical and semantic signals, RRF fuses them, semantic ranker can improve ordering, and retrieved results ground the LLM.

---

## Question 9

Two vector queries target different vector fields. One should influence final ranking more strongly.

Which feature should you consider?

A. Vector weighting  
B. Temperature  
C. Stop sequence  
D. Frequency penalty  

### Correct answer: A

**Why A is correct:** Vector weighting changes the contribution of vector-query signals to the combined ranking.

---

## Question 10

The result score from RRF and the semantic reranker score have different meanings. Which statement is correct?

A. Treat all scores as the same metric and range  
B. Interpret each score in the context of its ranking algorithm/stage  
C. Ignore all ranking scores  
D. Convert them to temperature values  

### Correct answer: B

**Why B is correct:** BM25, vector retrieval, RRF, and semantic reranking use different scoring mechanisms.

---

## Question 11

A complex conversational request requires decomposing one question into several targeted subqueries across knowledge sources.

Which approach is more relevant than a simple classic hybrid query?

A. Agentic retrieval  
B. Temperature tuning  
C. Stop sequences  
D. Frequency penalty  

### Correct answer: A

**Why A is correct:** Agentic retrieval adds LLM-based query planning and decomposition for complex retrieval workflows.

---

## Question 12

A highly relevant confidential HR record is found by both keyword and vector search. Should relevance alone allow the user to retrieve it?

A. Yes  
B. No, authorization/security filters must still permit access  
C. Yes, when RRF score is high  
D. Yes, when semantic ranker promotes it  

### Correct answer: B

**Why B is correct:** Search relevance and authorization are separate. Hybrid ranking must not bypass access controls.

---

# High-Value Exam Traps

## Trap 1

```text
Hybrid Search = Vector Search
```

Wrong.

```text
Hybrid = Keyword + Vector
```

---

## Trap 2

```text
Hybrid Search = Semantic Ranker
```

Wrong.

```text
Hybrid -> retrieves/fuses
Semantic ranker -> reranks
```

---

## Trap 3

```text
RRF = Semantic Ranking
```

Wrong.

```text
RRF -> merge lists
Semantic ranker -> semantic L2 reranking
```

---

## Trap 4

```text
Exact product/error code + natural-language description
```

Think:

```text
Hybrid Search
```

---

## Trap 5

```text
RRF k = Vector k
```

Wrong.

```text
RRF k -> fusion formula constant
Vector k -> requested nearest neighbors
```

---

## Trap 6

```text
Relevant = Authorized
```

Wrong.

Use proper identity, permissions, and security filters.

---

## Trap 7

```text
Poor retrieval -> Increase temperature
```

Wrong.

Temperature affects generation randomness, not search relevance.

---

# One-Minute Revision Sheet

```text
KEYWORD SEARCH
Exact lexical matching
BM25 relevance

VECTOR SEARCH
Semantic similarity using embeddings

HYBRID SEARCH
Keyword + vector in one search request

RRF
Merges multiple ranked lists

RRF FORMULA IDEA
1 / (rank + k)
RRF k is not vector top-k

SEMANTIC RANKER
Second-stage L2 reranking

FILTER
Structured restriction on eligible search records

VECTORIZER
Query-time text/image -> vector

VECTOR WEIGHT
Increase/decrease a vector signal's ranking influence

RAG
Hybrid search can retrieve grounding context for an LLM

AGENTIC RETRIEVAL
LLM-based query decomposition/planning for complex retrieval
```

# Final AI-103 Decision Rule

```text
Exact term/code?
-> Keyword search

Same meaning/different words?
-> Vector search

Need both?
-> Hybrid search

Merge rankings?
-> RRF

Correct candidates but wrong semantic order?
-> Semantic ranker

Need automatic query embedding?
-> Vectorizer

Need only Finance/HR/etc.?
-> Filter

Need one vector query to matter more?
-> Vector weighting

Need classic RAG grounding?
-> Hybrid retrieval + optional semantic ranker

Need complex multi-query planning?
-> Agentic retrieval
```

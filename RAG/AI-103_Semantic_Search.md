# AI-103: Semantic Search / Semantic Ranking

## 1. What is Semantic Search in Azure AI Search?

For AI-103, the key Azure AI Search concept is **semantic ranker**.

Semantic ranker doesn't replace the initial search. It applies a **secondary semantic ranking (L2 ranking)** over an initial ranked result set and promotes results that are more semantically relevant to the user's query.

```text
User query
    |
    v
Initial retrieval/ranking
BM25 or hybrid/vector pipeline
    |
    v
Candidate results
    |
    v
Semantic ranker
    |
    v
Semantically reranked results
```

### AI-103 exam memory

```text
Initial retrieval finds candidates.
Semantic ranker improves their ordering.
```

---

# 2. Why Semantic Ranking?

Traditional keyword search can retrieve documents that contain the requested words but don't best match the user's intent.

Example:

```text
Query:
"How do I change my password?"
```

Several documents may contain the terms `change` and `password`. Semantic ranking uses language-understanding models to better determine which candidate actually addresses the intended meaning.

### Exam clue

```text
Relevant documents are retrieved,
but best result is not near the top
```

Think:

```text
Semantic ranker / semantic reranking
```

---

# 3. Semantic Ranker is L2 Ranking

Azure AI Search semantic ranker performs a **second-stage ranking**.

```text
Stage 1: Initial retrieval/ranking
         |
         v
     Candidate set
         |
         v
Stage 2: Semantic reranking
         |
         v
   Better ordered results
```

This second stage is sometimes called **L2 ranking**.

### Important

Semantic ranking isn't the same as:

- Embeddings
- Vector similarity search
- BM25
- RRF

These concepts can participate in different stages of the same retrieval pipeline.

---

# 4. BM25 Keyword Ranking

Azure AI Search full-text search uses **BM25** relevance scoring for modern indexes/services.

BM25 considers lexical signals such as:

- Term frequency
- Inverse document frequency
- Statistical properties of the query and indexed text

Conceptually:

```text
Query terms
    |
    v
Text matching
    |
    v
BM25 relevance score
    |
    v
Initial result ranking
```

### Memory trick

```text
BM25 = lexical/full-text relevance
Semantic ranker = language-understanding reranking
```

---

# 5. Vector Search vs Semantic Ranking

This distinction is extremely important.

## Vector search

Uses embeddings and vector similarity to **retrieve** semantically similar content.

```text
Query embedding
     |
     v
Vector similarity
     |
     v
Candidate documents
```

## Semantic ranker

Uses language-understanding models to **rerank existing candidate results**.

```text
Candidate documents
     |
     v
Semantic ranker
     |
     v
Improved ordering
```

### Exam rule

```text
Need semantic retrieval?
-> Vector search

Already have candidates but need better ordering?
-> Semantic ranker
```

---

# 6. Hybrid Search + Semantic Ranking

A powerful Azure AI Search pattern is:

```text
Keyword retrieval
      +
Vector retrieval
      |
      v
RRF merge
      |
      v
Initial hybrid result set
      |
      v
Semantic ranker
      |
      v
Final relevance ordering
```

Microsoft documentation reports that hybrid queries combined with semantic ranking commonly provide strong search relevance in benchmark testing.

### Exam memory

```text
Keyword + Vector -> Hybrid
Hybrid merging -> RRF
Rerank merged candidates -> Semantic ranker
```

---

# 7. RRF vs Semantic Ranker

These are easy to confuse.

## Reciprocal Rank Fusion (RRF)

RRF merges independently ranked result lists, such as keyword and vector results in hybrid search.

```text
Keyword rank list
      +
Vector rank list
      |
      v
      RRF
      |
      v
Unified ranking
```

## Semantic ranker

Semantic ranker then uses semantic understanding for a second-stage reranking of candidates.

```text
Unified candidates
      |
      v
Semantic ranker
      |
      v
Semantic relevance ordering
```

### Exam rule

```text
Merge multiple rankings -> RRF
Improve semantic ordering -> Semantic ranker
```

---

# 8. Semantic Configuration

To use classic semantic ranking, an Azure AI Search index has a **semantic configuration** that identifies the text fields most useful to semantic processing.

Conceptually, you prioritize fields such as:

```text
Title field
Content fields
Keyword fields
```

Example idea:

```text
Title: document title
Content: body / description
Keywords: tags / categories
```

### Why field prioritization matters

Semantic ranking works best when it receives meaningful descriptive text rather than IDs or raw codes.

### Exam clue

```text
Need to tell semantic ranker which fields contain title/content/keywords
```

Think:

```text
Semantic configuration
```

---

# 9. Semantic Captions

Semantic ranker can return **semantic captions**.

A caption is extracted from indexed content to summarize why a result is relevant.

```text
Search result
   |
   v
Relevant passage extracted
   |
   v
Semantic caption
```

Captions can also include highlights over relevant terms and phrases.

### Important exam point

Semantic captions are extracted from existing indexed content. They aren't free-form LLM-generated summaries.

---

# 10. Semantic Answers

Semantic ranking can optionally return a **semantic answer** for question-like queries.

Example:

```text
Question:
"What is a hash table?"
```

If a top search document contains an answer-like passage, the semantic system can extract it.

### Critical exam rule

A semantic answer is:

```text
VERBATIM content extracted from indexed documents
```

It is **not** a newly generated answer.

Azure AI Search uses machine reading comprehension to identify an answer passage.

---

# 11. Semantic Answer vs RAG Answer

This is a very important exam distinction.

## Semantic answer

```text
Existing indexed text
      |
      v
Extract answer passage
```

Properties:

- Extractive
- Verbatim
- Comes from indexed content
- Requires answer-like text to exist

## RAG / Generative answer

```text
Retrieved documents
      |
      v
Grounding context
      |
      v
Generative model
      |
      v
Newly composed grounded answer
```

### Memory trick

```text
Semantic answer = EXTRACT
RAG answer      = GENERATE
```

---

# 12. Semantic Captions vs Semantic Answers

| Semantic captions | Semantic answers |
|---|---|
| Summarize why each result is relevant by extracting passages | Extract a direct answer-like passage |
| Associated with individual search results | Returned as an optional answer structure |
| Can highlight relevant terms | Typically aimed at question-form queries |
| Extracted from indexed text | Extracted from indexed text |

Neither should be confused with an LLM-generated RAG answer.

---

# 13. Query Requirements

Semantic ranking needs a meaningful textual query that can be evaluated for relevance.

Pure filter-only queries such as:

```text
search=*
```

or an empty search string don't provide semantic query content to rank.

### Exam clue

```text
Pure filter query with no meaningful search terms
```

Do not expect semantic ranking to provide useful semantic relevance scoring.

---

# 14. Sorting and Semantic Ranking

Explicit sorting by a field can conflict with semantic relevance ranking.

Example:

```text
orderBy = createdDate desc
```

means the request is prioritizing a field-based sort rather than relevance ordering.

Microsoft documentation notes that applying an `orderby` clause to semantically ranked results causes an error in the described semantic-query configuration.

### Exam thinking

```text
Need semantic relevance ordering
-> Let semantic score/ranker determine relevance ordering
```

Don't override it with incompatible field sorting.

---

# 15. Semantic Query Rewrite

Newer Azure AI Search semantic capabilities can support **query rewrite**.

Conceptually:

```text
Original query
      |
      v
Semantic rewrite
      |
      +-- Related query A
      +-- Related query B
      +-- Related query C
      |
      v
Improved retrieval coverage
```

Query rewrite expands an initial query into semantically related variants to improve recall.

### Important

Feature availability and API status can change. Pay attention to preview/GA wording in exam scenarios.

---

# 16. Semantic Ranking in RAG

Semantic ranker can improve the grounding content sent to an LLM.

```text
User question
      |
      v
Hybrid / text retrieval
      |
      v
Candidate chunks
      |
      v
Semantic ranker
      |
      v
Higher-quality chunks
      |
      v
LLM grounding
      |
      v
Generated answer
```

Better retrieval ranking can reduce irrelevant context reaching the LLM.

### Key insight

```text
RAG quality depends heavily on retrieval quality.
```

A stronger generation model can't reliably compensate for poor grounding documents.

---

# 17. Semantic Ranker and Agentic Retrieval

Semantic ranker is also integrated into modern Azure AI Search agentic retrieval scenarios.

Agentic retrieval can involve:

```text
Complex question
      |
      v
Query planning/decomposition
      |
      v
Multiple searches
      |
      v
Semantic ranking / structured retrieval
      |
      v
Agent grounding
```

### Distinction

```text
Semantic ranker
-> improves result relevance/order

Agentic retrieval
-> broader retrieval workflow with query planning and potentially multiple searches/sources
```

---

# 18. Semantic Ranking Works on Text

Semantic ranker needs rich text content to understand meaning.

It works best with fields containing:

- Descriptions
- Explanations
- Articles
- Paragraphs
- Knowledge-base content

It is less valuable when the index consists mainly of opaque values such as:

```text
ID-18272
AZ-9921
003827
```

Those scenarios often rely more heavily on exact lexical matching and structured filtering.

---

# 19. Semantic Ranking and Synonyms

Azure AI Search synonym maps can expand terms during the initial query processing stage. Semantic ranking then operates over the resulting candidates.

Conceptually:

```text
Query
  |
Synonym-aware retrieval
  |
Candidates
  |
Semantic ranker
```

Do not treat synonyms and semantic ranking as the same feature.

---

# 20. Semantic Search Decision Table

| Requirement | Best concept |
|---|---|
| Exact term/code | Keyword/BM25 search |
| Similar meaning, different wording | Vector search |
| Exact terms + semantic similarity | Hybrid search |
| Merge keyword/vector rankings | RRF |
| Improve candidate result ordering using meaning | Semantic ranker |
| Show relevant passage per result | Semantic caption |
| Extract direct answer from indexed content | Semantic answer |
| Generate a new grounded answer | RAG + generative model |
| Tell semantic ranker which fields matter | Semantic configuration |
| Expand query into semantically related queries | Query rewrite, where supported |
| Complex query decomposition/retrieval planning | Agentic retrieval |

---

# Practice Questions

## Question 1

Azure AI Search retrieves the correct documents, but the most relevant document often appears below less useful results.

What should you use?

A. Higher temperature  
B. Semantic ranker  
C. Fine-tuning  
D. Larger output-token limit  

### Correct answer: B

**Why B is correct:** Semantic ranker applies second-stage semantic ranking to improve the order of an initial result set.

**Why the others are incorrect:**

- **A:** Temperature controls generation randomness.
- **C:** Fine-tuning isn't the correct first solution for search ranking.
- **D:** Output length doesn't control retrieval relevance.

---

## Question 2

You run keyword and vector searches in one Azure AI Search hybrid request. What combines their independently ranked results?

A. RRF  
B. Semantic caption  
C. Temperature  
D. Chunk overlap  

### Correct answer: A

**Why A is correct:** Reciprocal Rank Fusion merges the full-text and vector rankings into a unified result list.

---

## Question 3

After hybrid results are merged, you need a language-understanding model to improve their semantic ordering.

Which capability should you add?

A. Semantic ranker  
B. Frequency penalty  
C. Larger embeddings only  
D. Stop sequence  

### Correct answer: A

**Why A is correct:** Semantic ranker performs the second-stage semantic reranking.

---

## Question 4

A search page should display a short relevant passage below each search result and highlight important terms.

What should you request?

A. Semantic captions  
B. Fine-tuned model  
C. Higher temperature  
D. Parent-child chunking only  

### Correct answer: A

**Why A is correct:** Semantic captions extract representative text from returned search documents and can include highlighting.

---

## Question 5

A user asks, "What is a hash table?" The indexed content contains a sentence that directly answers the question. You want Azure AI Search to return that exact passage.

Which feature should you use?

A. Semantic answer  
B. RAG-generated answer only  
C. Temperature  
D. Vector weighting  

### Correct answer: A

**Why A is correct:** Semantic answers extract a direct answer-like passage from existing indexed text.

---

## Question 6

Which statement about semantic answers is correct?

A. They always generate new prose with an LLM  
B. They are verbatim passages extracted from indexed content  
C. They replace the search index  
D. They require document fine-tuning  

### Correct answer: B

**Why B is correct:** Semantic answers are extractive, not generative.

---

## Question 7

You need a fluent answer synthesized from multiple retrieved documents.

Which pattern is most appropriate?

A. Semantic answer only  
B. RAG with a generative model  
C. BM25 only  
D. Frequency penalty  

### Correct answer: B

**Why B is correct:** RAG supplies retrieved grounding material to a generative model, which can compose a new answer.

---

## Question 8

An index must identify the title and descriptive content fields that semantic ranker should prioritize.

What should you configure?

A. Semantic configuration  
B. Temperature  
C. Seed  
D. Stop sequence  

### Correct answer: A

**Why A is correct:** Semantic configuration identifies prioritized text fields used by the semantic processing pipeline.

---

## Question 9

A request contains only a structured filter and no meaningful text query.

Will semantic ranking have meaningful text relevance to evaluate?

A. Yes, always  
B. No, a meaningful scored text query is required for semantic relevance ranking  
C. Only when temperature is zero  
D. Only with fine-tuning  

### Correct answer: B

**Why B is correct:** Semantic ranker needs scored search candidates based on query terms/phrases. Pure filter-only input doesn't provide that semantic relevance signal.

---

## Question 10

What is the main distinction between vector search and semantic ranker?

A. Vector search retrieves by embedding similarity; semantic ranker reranks candidates using semantic language understanding  
B. They are identical  
C. Semantic ranker creates embeddings for every query  
D. Vector search generates the final LLM response  

### Correct answer: A

**Why A is correct:** Vector search is a retrieval technique. Semantic ranker is a second-stage ranking technique.

---

## Question 11

A hybrid RAG solution needs both exact product-code matching and conceptual similarity, followed by improved relevance ordering.

What pipeline is most appropriate?

A. Keyword + vector hybrid retrieval -> RRF -> semantic ranking  
B. Temperature -> fine-tuning -> max tokens  
C. Keyword only -> temperature  
D. Semantic answer only  

### Correct answer: A

**Why A is correct:** Hybrid retrieval covers lexical and semantic retrieval, RRF merges the result lists, and semantic ranking improves the semantic ordering of candidate results.

---

## Question 12

A query needs to be expanded into several semantically related query variants before retrieval.

Which semantic capability is relevant where supported?

A. Query rewrite  
B. Frequency penalty  
C. Output token limit  
D. Stop sequence  

### Correct answer: A

**Why A is correct:** Semantic query rewrite expands the initial query into semantically related variants to improve retrieval coverage.

---

# High-Value Exam Traps

## Trap 1

```text
Semantic ranker = vector search
```

Wrong.

```text
Vector search -> retrieve by vector similarity
Semantic ranker -> rerank initial candidates
```

---

## Trap 2

```text
Semantic answer = generative AI answer
```

Wrong.

```text
Semantic answer -> verbatim extraction
RAG answer -> generated/synthesized response
```

---

## Trap 3

```text
RRF = semantic ranking
```

Wrong.

```text
RRF -> merges ranking lists
Semantic ranker -> reranks using semantic meaning
```

---

## Trap 4

```text
BM25 = vector similarity
```

Wrong.

```text
BM25 -> full-text/keyword relevance
Vector search -> embedding similarity
```

---

## Trap 5

```text
Correct documents, wrong order
```

Think:

```text
Semantic ranker
```

---

## Trap 6

```text
Need a relevant snippet under each result
```

Think:

```text
Semantic captions
```

---

## Trap 7

```text
Need exact passage that directly answers a question
```

Think:

```text
Semantic answer
```

---

## Trap 8

```text
Need synthesis across multiple sources
```

Think:

```text
RAG + generative model
```

---

# One-Minute Revision Sheet

```text
BM25
Initial keyword/full-text relevance ranking

VECTOR SEARCH
Retrieve by embedding similarity

HYBRID SEARCH
Keyword + vector retrieval

RRF
Merge independently ranked hybrid result lists

SEMANTIC RANKER
Second-stage L2 semantic reranking

SEMANTIC CONFIGURATION
Prioritize title/content/keyword text fields

SEMANTIC CAPTION
Extract relevant passage for a result
May include highlights

SEMANTIC ANSWER
Extract verbatim answer-like passage
Not newly generated

QUERY REWRITE
Expand query into semantically related variants
Where supported

RAG
Retrieve grounding content + generative model creates answer

AGENTIC RETRIEVAL
Query planning/decomposition + retrieval workflow
```

# Final AI-103 Decision Rule

```text
Exact term/code?
-> Keyword/BM25

Same meaning, different words?
-> Vector search

Need both?
-> Hybrid search

Merge keyword + vector rankings?
-> RRF

Correct results but poor ordering?
-> Semantic ranker

Need useful result snippet?
-> Semantic caption

Need exact answer passage from index?
-> Semantic answer

Need newly composed grounded answer?
-> RAG + generative model

Need to specify fields important to semantics?
-> Semantic configuration

Need query expansion?
-> Semantic query rewrite, where supported
```

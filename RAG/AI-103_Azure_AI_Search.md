# AI-103: Azure AI Search

## 1. What is Azure AI Search?

**Azure AI Search** is Microsoft's cloud information-retrieval service for building search experiences over enterprise content. It supports text, vector, hybrid, semantic, and multimodal retrieval and is commonly used as the retrieval layer for RAG applications.

### AI-103 exam memory

```text
Azure AI Search
= Index + Retrieve + Rank + Filter + Enrich
```

Common capabilities include:

- Full-text search
- Vector search
- Hybrid search
- Semantic ranking
- Filters, facets, and sorting
- Indexers and data-source ingestion
- AI enrichment through skillsets
- Integrated vectorization
- RAG and agentic retrieval scenarios

---

# 2. Core Architecture

A common Azure AI Search ingestion pipeline is:

```text
Data Source
    |
    v
Indexer
    |
    v
Optional Skillset
    |
    +-- OCR
    +-- Chunking
    +-- Language detection
    +-- Entity extraction
    +-- Embeddings
    +-- Custom processing
    |
    v
Search Index
    |
    v
Query
    |
    v
Search Results
```

For RAG:

```text
Search Results
      |
      v
Grounding Context
      |
      v
Generative Model
      |
      v
Grounded Answer
```

---

# 3. Data Source

A **data source** describes where an indexer retrieves content from.

Conceptually:

```text
Azure Blob Storage
Azure SQL / supported databases
Other supported cloud data sources
      |
      v
Data source definition
```

### Exam memory

```text
DATA SOURCE = WHERE content comes from
```

Do not confuse a data source with an index.

```text
Data source -> original data
Index       -> searchable representation
```

---

# 4. Indexer

An **indexer** is a crawler that pulls content from a supported data source, maps it to search fields, and populates an index.

```text
Data Source
     |
     v
   Indexer
     |
     v
Search Index
```

Indexers can also invoke skillsets for enrichment.

```text
Data Source
     |
     v
Indexer
     |
     v
Skillset
     |
     v
Index
```

### Pull model

Indexer-based ingestion is often called the **pull model** because Azure AI Search pulls data from the source.

### Scheduling

Indexers can run on demand or on a recurring schedule. Microsoft documentation states recurring schedules can run as frequently as approximately **every five minutes** for supported indexer scenarios.

### Exam clue

```text
Need Azure AI Search to periodically crawl supported cloud data
-> Indexer
```

---

# 5. Push Model vs Pull Model

## Pull model

```text
Azure AI Search Indexer
        |
        v
Pulls from data source
```

Use when:

- Source is supported by indexers.
- Scheduled ingestion is sufficient.
- You want less custom ingestion code.

## Push model

```text
Application
    |
    v
Push documents directly into search index
```

Use when:

- The data source isn't supported by an indexer.
- Updates must be more immediate than the indexer scheduling pattern supports.
- Your application needs full control over transformations and synchronization.

### AI-103 rule

```text
Indexer pulls data -> Pull model
Application sends documents -> Push model
```

---

# 6. Search Index

A **search index** contains searchable documents and fields optimized for retrieval.

Example conceptual schema:

```text
id              string
title           string
content         string
category        string
createdDate     datetime
contentVector   vector
```

Each field can have capabilities according to its type/configuration.

Common properties include:

- `key`
- `searchable`
- `filterable`
- `sortable`
- `facetable`
- `retrievable`

### Exam memory

```text
INDEX = searchable representation of your content
```

---

# 7. Searchable

A **searchable** field participates in full-text search.

Examples:

```text
title
content
description
```

### Exam clue

```text
Need full-text search over the article body
-> Make content searchable
```

---

# 8. Filterable

A **filterable** field can be used in structured filters.

Example:

```text
department eq 'Finance'
```

Typical filterable fields:

- Department
- Status
- Country
- Category
- Security/ACL metadata
- Dates

### Important distinction

```text
Searchable -> relevance/text search
Filterable -> exact structured restriction
```

---

# 9. Sortable

A **sortable** field can be used to explicitly order results.

Example:

```text
createdDate desc
```

Use for:

- Date
- Price
- Rating
- Numeric metrics

### Exam clue

```text
Need newest documents first
-> Sortable date field
```

---

# 10. Facetable

A **facetable** field supports grouped counts/navigation such as:

```text
Category
  HR (25)
  IT (41)
  Finance (18)
```

Use facets for search-navigation experiences where users refine results by categories.

### Exam memory

```text
FILTER = restrict results
FACET  = navigation/counts for groups
```

---

# 11. Retrievable

A **retrievable** field can be returned in search results.

Example:

```text
content
sourceUrl
pageNumber
```

### Exam trap

A field can participate in retrieval/ranking logic without necessarily needing to be returned to the client. Configure retrievability according to what the application should receive.

---

# 12. Key Field

Every Azure AI Search index requires a field that uniquely identifies each search document.

Think:

```text
Search document primary identifier
-> Key field
```

For chunked RAG indexes, each chunk commonly gets its own unique key while retaining a parent document identifier.

---

# 13. Field Mappings

Field mappings connect source fields to index fields.

```text
Source field          Index field
-----------------------------------
file_name        ->   title
file_content     ->   content
record_id        ->   id
```

Use field mappings when:

- Source and destination field names differ.
- Content needs supported mapping transformations.

---

# 14. Output Field Mappings

**Output field mappings** move enriched content generated in a skillset into index fields.

Conceptually:

```text
Raw document
     |
     v
Skillset
     |
     +-- key phrases
     +-- OCR text
     +-- embeddings
     |
     v
Output field mappings
     |
     v
Search index fields
```

### Exam distinction

```text
Field mapping
-> raw/source content to index

Output field mapping
-> skillset/enriched output to index
```

---

# 15. Skillset

A **skillset** is a reusable collection of AI/enrichment operations attached to an indexer.

It can contain skills for:

- OCR
- Language detection
- Key phrase extraction
- Entity recognition
- Translation
- Chunking
- Embedding generation
- Image verbalization
- Custom processing

```text
Indexer
   |
   v
Skillset
   |
   +-- Skill 1
   +-- Skill 2
   +-- Skill 3
   |
   v
Enriched document
```

### AI-103 rule

```text
INDEXER = moves/processes data through pipeline
SKILLSET = enriches/transforms content
INDEX = stores searchable output
```

---

# 16. Enrichment Tree

During skillset execution, Azure AI Search creates an in-memory **enriched document tree**.

Initially:

```text
/document
```

Skills add nodes:

```text
/document
   /content
   /language
   /keyPhrases
   /chunks
   /embeddings
```

A downstream skill can use the output of an earlier skill.

### Exam clue

```text
Skills perform chained transformations
```

Think:

```text
Enrichment tree / skillset pipeline
```

---

# 17. Built-In Skills vs Custom Skills

## Built-in skills

Microsoft provides skills for common enrichment operations.

Examples:

- OCR
- Text splitting
- Language detection
- Entity recognition
- Key phrase extraction
- Azure OpenAI embedding

## Custom skill

Use a custom skill when your required transformation isn't provided by a built-in skill.

Conceptually:

```text
Skillset
   |
Custom Web API skill
   |
Your processing endpoint
```

### Exam rule

```text
Built-in capability exists -> built-in skill
Custom business processing -> custom skill
```

---

# 18. Chunking in Azure AI Search

Large documents can be split into chunks before embedding/indexing.

```text
Document
   |
   v
Text Split / semantic chunking
   |
   +-- Chunk 1
   +-- Chunk 2
   +-- Chunk 3
```

Chunking improves:

- Token-limit compliance
- Retrieval granularity
- Semantic precision

### Important

Preserve metadata such as:

- Parent document ID
- File name
- Page number
- Heading
- Source URL
- Access-control metadata

---

# 19. Integrated Vectorization

Azure AI Search supports integrated vectorization for indexing and querying scenarios.

### Indexing side

```text
Data source
   |
Indexer
   |
Chunking
   |
Embedding skill
   |
Vector field
```

### Query side

```text
User text
   |
Vectorizer
   |
Query vector
   |
Vector search
```

### Memory trick

```text
Embedding Skill -> indexing-time vectors
Vectorizer      -> query-time vectors
```

---

# 20. Full-Text Search

Full-text search operates over searchable text fields and uses lexical relevance.

Think:

```text
Exact terms
Names
Codes
Specialized jargon
-> Full-text / keyword search
```

Azure AI Search uses BM25 relevance scoring for text search in modern configurations.

---

# 21. Vector Search

Vector search retrieves documents by comparing embeddings.

```text
Query vector
    |
    v
Similarity comparison
    |
    v
Nearest vectors
```

Use when:

```text
Different words
Same meaning
```

Important algorithms:

- HNSW -> approximate nearest neighbor
- Exhaustive KNN -> exact exhaustive comparison

---

# 22. Hybrid Search

Hybrid search combines full-text and vector queries in one request.

```text
Keyword/BM25
      +
Vector search
      |
      v
RRF
      |
      v
Unified results
```

### AI-103 memory

```text
Hybrid = Keyword + Vector
Fusion = RRF
```

Use it when both exact terms and semantic meaning matter.

---

# 23. Semantic Ranker

Semantic ranker performs second-stage semantic reranking.

```text
Initial BM25/RRF result set
        |
        v
Semantic Ranker
        |
        v
Improved ordering
```

It can also provide:

- Semantic captions
- Highlights
- Optional extracted semantic answers
- Query rewrite capabilities where supported

### Exam memory

```text
Correct candidates, wrong order
-> Semantic ranker
```

---

# 24. Semantic Caption vs Semantic Answer vs RAG

## Semantic caption

Extracted representative passage for a search result.

## Semantic answer

Extracted answer-like passage from indexed content.

## RAG answer

Generative model creates a new answer using retrieved grounding content.

```text
Caption -> extract relevant snippet
Semantic answer -> extract direct answer
RAG -> generate grounded answer
```

---

# 25. Search Analyzers

Analyzers process text during indexing/querying for full-text search.

Conceptually:

```text
"Running Azure Searches"
       |
       v
Analyzer
       |
       v
Tokens
```

Analyzers can affect:

- Tokenization
- Case normalization
- Linguistic processing

### Exam clue

If exact product identifiers or unusual technical codes aren't matching as expected, inspect the analyzer/tokenization configuration.

---

# 26. Synonym Maps

Synonym maps allow related terms to match in full-text retrieval.

Example concept:

```text
car, automobile, vehicle
```

### Important distinction

```text
Synonym map -> lexical query expansion/matching
Vector search -> semantic similarity using embeddings
```

Do not treat them as identical.

---

# 27. Scoring Profiles

A scoring profile can boost full-text result relevance based on configured business rules.

Examples:

```text
Boost newer documents
Boost preferred locations
Boost specific fields
```

### Exam clue

```text
Business relevance should influence lexical ranking
-> Scoring profile
```

Do not confuse scoring profiles with semantic ranker or vector weighting.

---

# 28. Filters vs Facets vs Sorting

| Requirement | Capability |
|---|---|
| Only Finance documents | Filter |
| Finance (20), HR (15), IT (30) categories | Facet |
| Newest first | Sort |
| Relevance based on query | Search ranking |

### Memory trick

```text
FILTER -> restrict
FACET  -> summarize/navigation
SORT   -> order by field
RANK   -> relevance
```

---

# 29. Classic RAG with Azure AI Search

A common RAG workflow is:

```text
Documents
   |
Chunk + Embed
   |
Azure AI Search Index
   |
User Question
   |
Hybrid Search
   |
Optional Semantic Ranker
   |
Relevant Chunks
   |
Prompt / Grounding
   |
LLM
   |
Answer + Citations
```

### AI-103 rule

```text
Private/current knowledge
-> Retrieve from Azure AI Search
-> Ground the model
```

Don't fine-tune a model merely to keep changing business documents current.

---

# 30. Agentic Retrieval

Azure AI Search also supports modern agentic retrieval patterns.

Conceptually:

```text
Complex question
     |
     v
LLM query planning
     |
     +-- Subquery 1
     +-- Subquery 2
     +-- Subquery 3
     |
     v
Knowledge sources
     |
     v
Structured retrieval/grounding
```

### Classic vs Agentic

```text
Known/simple retrieval flow
-> Classic RAG / hybrid search

Complex conversational query requiring planning/decomposition
-> Agentic retrieval
```

Check preview/GA wording for exam scenarios because newer capabilities evolve.

---

# 31. Security

Search relevance isn't authorization.

```text
Relevant document != authorized document
```

Enterprise search solutions should use controls such as:

- Microsoft Entra ID
- Azure RBAC
- Managed identity
- Permission-aware content
- Security metadata filters
- Least privilege

For RAG, retrieved chunks must respect the permissions of their source documents.

---

# 32. Key Roles

The exact required role depends on the operation.

For example, querying and management have different permissions. Microsoft documentation for hybrid-query scenarios identifies roles such as **Search Index Data Reader** for querying and **Search Index Data Contributor** for creating/updating index data in applicable workflows.

### Exam principle

```text
Only query/index data access needed?
-> Use data-plane role with least privilege
```

Avoid granting broad Owner/Contributor permissions when a narrower search role satisfies the requirement.

---

# 33. Azure AI Search Decision Table

| Requirement | Think |
|---|---|
| Pull supported source data | Indexer |
| Custom/direct ingestion | Push model |
| Store searchable representation | Index |
| Full-text query field | Searchable |
| Exact metadata restriction | Filterable |
| Category navigation/count | Facetable |
| Explicit field ordering | Sortable |
| Return field in response | Retrievable |
| AI processing during indexing | Skillset |
| Raw source to index mapping | Field mapping |
| Skill output to index mapping | Output field mapping |
| Split large content | Chunking/Text Split |
| Generate index vectors | Embedding skill |
| Convert query text to vector | Vectorizer |
| Exact lexical relevance | Full-text/BM25 |
| Semantic similarity | Vector search |
| Exact + semantic | Hybrid search |
| Merge hybrid ranks | RRF |
| Improve final semantic ordering | Semantic ranker |
| Private/current grounding | RAG |
| Complex query planning | Agentic retrieval |

---

# Practice Questions

## Question 1

You need Azure AI Search to automatically pull documents periodically from a supported Azure data source and load them into an index.

What should you configure?

A. Indexer  
B. Temperature  
C. Semantic caption  
D. Presence penalty  

### Correct answer: A

**Why A is correct:** Indexers crawl supported data sources and populate search indexes using a pull model.

**Why the others are incorrect:** They are unrelated to ingestion.

---

## Question 2

A field must be used in a filter such as `department eq 'Finance'`.

Which field capability is required?

A. Filterable  
B. Facetable only  
C. Temperature-controlled  
D. Embeddable only  

### Correct answer: A

**Why A is correct:** Structured filter expressions operate on filterable fields.

---

## Question 3

A search UI must display category counts so users can refine results.

Which capability should you use?

A. Facets  
B. Temperature  
C. Fine-tuning  
D. Stop sequences  

### Correct answer: A

**Why A is correct:** Facets support grouped counts and navigation.

---

## Question 4

An indexing pipeline needs OCR, text chunking, and embedding generation.

Which Azure AI Search construct groups these enrichment operations?

A. Skillset  
B. Semantic answer  
C. Scoring profile only  
D. Search result caption  

### Correct answer: A

**Why A is correct:** Skillsets contain built-in or custom skills that enrich source content during indexer processing.

---

## Question 5

An embedding generated by a skill needs to be written to `contentVector` in the search index.

Which mapping is especially relevant?

A. Output field mapping  
B. Temperature setting  
C. Synonym map  
D. Semantic caption  

### Correct answer: A

**Why A is correct:** Skillset outputs are transferred to index fields through output field mappings.

---

## Question 6

A query contains an exact product code plus a natural-language description.

Which search approach is most suitable?

A. Hybrid search  
B. Vector only  
C. Temperature tuning  
D. Fine-tuning  

### Correct answer: A

**Why A is correct:** Hybrid search combines full-text lexical precision with vector semantic similarity.

---

## Question 7

What merges the keyword and vector ranked lists in Azure AI Search hybrid retrieval?

A. Reciprocal Rank Fusion (RRF)  
B. OCR  
C. Chunk overlap  
D. Frequency penalty  

### Correct answer: A

**Why A is correct:** Azure AI Search uses RRF for hybrid rank fusion.

---

## Question 8

The right documents are retrieved, but the most semantically relevant result isn't ranked first.

What should you consider?

A. Semantic ranker  
B. Higher temperature  
C. Larger max tokens  
D. OCR  

### Correct answer: A

**Why A is correct:** Semantic ranker performs second-stage reranking over an initial BM25/RRF result set.

---

## Question 9

A search indexer must call a business-specific transformation API that isn't available as a built-in skill.

What should you use?

A. Custom skill  
B. Facet  
C. Temperature  
D. Semantic answer  

### Correct answer: A

**Why A is correct:** Custom skills integrate externally hosted processing into a skillset.

---

## Question 10

A company policy chatbot must answer from frequently updated internal documents.

What is the best architecture?

A. Azure AI Search retrieval + RAG grounding  
B. Increase temperature  
C. Fine-tune the model every time a policy changes  
D. Use only a semantic caption  

### Correct answer: A

**Why A is correct:** RAG provides current/private knowledge at query time without requiring the base model to be retrained for each factual update.

---

## Question 11

An application requires updates faster than indexer scheduling can provide and already controls source writes.

What ingestion approach should you consider?

A. Push updated documents directly to the search index  
B. Increase top-p  
C. Enable semantic captions  
D. Use more chunk overlap  

### Correct answer: A

**Why A is correct:** A push model gives the application direct control over index updates when an indexer isn't suitable.

---

## Question 12

A complex conversational search request should be decomposed into multiple targeted subqueries across knowledge sources.

Which modern Azure AI Search concept is most relevant?

A. Agentic retrieval  
B. Temperature  
C. Faceting  
D. Stop sequence  

### Correct answer: A

**Why A is correct:** Agentic retrieval uses LLM-based query planning/decomposition for more complex retrieval workflows.

---

# High-Value AI-103 Exam Traps

## Trap 1

```text
Data Source = Index
```

Wrong.

```text
Data Source -> original content
Index -> searchable representation
```

---

## Trap 2

```text
Indexer = Skillset
```

Wrong.

```text
Indexer -> ingestion/orchestration
Skillset -> enrichment/transformation
```

---

## Trap 3

```text
Searchable = Filterable
```

Wrong.

```text
Searchable -> full-text retrieval
Filterable -> structured filtering
```

---

## Trap 4

```text
Filter = Facet
```

Wrong.

```text
Filter -> restrict results
Facet -> category counts/navigation
```

---

## Trap 5

```text
Field Mapping = Output Field Mapping
```

Wrong.

```text
Field mapping -> raw source to index
Output field mapping -> enriched skill output to index
```

---

## Trap 6

```text
Hybrid Search = Semantic Ranker
```

Wrong.

```text
Hybrid -> keyword + vector + RRF
Semantic ranker -> second-stage reranking
```

---

## Trap 7

```text
Embedding Skill = Vectorizer
```

Wrong.

```text
Embedding Skill -> indexing time
Vectorizer -> query time
```

---

## Trap 8

```text
Relevant = Authorized
```

Wrong. Search retrieval must still enforce access control.

---

# One-Minute Revision Sheet

```text
DATA SOURCE
Where content comes from

INDEXER
Pulls data from supported source into index
Can run skillset

PUSH MODEL
Application sends documents directly

INDEX
Searchable data structure

SEARCHABLE
Full-text search

FILTERABLE
Structured filters

SORTABLE
Field-based ordering

FACETABLE
Category navigation/counts

RETRIEVABLE
Can be returned in result

SKILLSET
AI enrichment pipeline

FIELD MAPPING
Source -> index

OUTPUT FIELD MAPPING
Skill output -> index

TEXT SPLIT / CHUNKING
Large document -> chunks

EMBEDDING SKILL
Index-time vectors

VECTORIZER
Query-time vectors

BM25
Text relevance

VECTOR SEARCH
Semantic similarity

HYBRID SEARCH
Keyword + vector

RRF
Merge rankings

SEMANTIC RANKER
L2 semantic reranking

RAG
Retrieve -> Ground -> Generate

AGENTIC RETRIEVAL
LLM query planning/decomposition
```

# Final AI-103 Decision Rule

```text
Need to ingest supported source automatically?
-> Indexer

Need custom/immediate ingestion?
-> Push model

Need AI enrichment while indexing?
-> Skillset

Need OCR/custom extraction/chunking?
-> Skills

Need semantic vectors in index?
-> Embedding skill / vectorization

Need automatic query embedding?
-> Vectorizer

Exact term?
-> Full-text/BM25

Semantic meaning?
-> Vector search

Need both?
-> Hybrid search

Merge hybrid rankings?
-> RRF

Correct results but wrong semantic order?
-> Semantic ranker

Need private/current knowledge for LLM?
-> RAG

Need complex retrieval planning?
-> Agentic retrieval
```

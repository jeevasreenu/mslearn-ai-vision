# AI-103: Chunking

## 1. What is Chunking?

**Chunking** is the process of dividing large documents into smaller, meaningful units before indexing, embedding, retrieval, or grounding an LLM.

```text
Large document
      |
      v
Chunking
      |
      +-- Chunk 1
      +-- Chunk 2
      +-- Chunk 3
      +-- Chunk 4
```

In a RAG solution, chunks normally become the units that are embedded, indexed, retrieved, and supplied to the generative model.

### AI-103 exam memory

```text
Chunking = split large content into retrieval-friendly units
```

---

## 2. Why Chunking is Required

Chunking helps solve several problems:

- Embedding and generative models have input token limits.
- A complete document might contain many unrelated topics.
- One vector for an entire document can dilute its semantic meaning.
- Retrieving full documents can add irrelevant text to the prompt.
- Smaller relevant units help control latency, cost, and context usage.

### Important rule

```text
Large document + many topics
              |
              v
     Split into meaningful chunks
```

Chunking is not required only because a document is technically too large. A smaller document with several unrelated topics can also benefit from finer-grained chunking.

---

## 3. Chunking in the RAG Pipeline

```text
Source documents
      |
      v
Extract content
      |
      v
Chunk content
      |
      v
Generate embeddings
      |
      v
Store chunks + vectors + metadata
      |
      v
Retrieve relevant chunks
      |
      v
Ground the LLM
      |
      v
Generate answer
```

### Core distinction

```text
Chunking   -> prepares retrieval units
Embedding  -> converts units into vectors
Search     -> finds relevant units
LLM        -> generates the final answer
```

---

## 4. Chunk Size Trade-Off

There is no universal best chunk size. Select and evaluate it for your document type, embedding model, query patterns, and retrieval goals.

### Chunks that are too large

Possible effects:

- Multiple unrelated concepts share one vector.
- Retrieval becomes less precise.
- Retrieved chunks consume more prompt tokens.
- More irrelevant information reaches the LLM.
- Relevant details can be diluted.

```text
Large mixed-topic chunk
        |
        v
Broad embedding
        |
        v
Lower retrieval precision
```

### Chunks that are too small

Possible effects:

- Important context is lost.
- Sentences or ideas become fragmented.
- More index records are created.
- A retrieved chunk may not contain enough information to answer the query.

```text
Tiny fragment
     |
     v
Insufficient context
```

### AI-103 decision rule

```text
Too large  -> poor precision and extra tokens
Too small  -> lost context and fragmentation
```

---

## 5. Fixed-Size Chunking

Fixed-size chunking divides content according to a configured number of characters, words, or tokens.

```text
Document
  |
  +-- first 500 tokens
  +-- next 500 tokens
  +-- next 500 tokens
```

### Advantages

- Simple to implement
- Predictable size
- Efficient
- Useful for logs or content without strong semantic structure

### Disadvantages

- Can split sentences or concepts
- Can separate headings from their content
- May break tables or lists
- Ignores document structure

Microsoft guidance gives a fixed-size example of about **200 words or 600 characters** with roughly **10–15% overlap**. Treat these as starting examples, not universal production defaults.

---

## 6. Sentence-Based Chunking

Sentence-based chunking splits content at sentence boundaries.

```text
Sentence 1. Sentence 2. Sentence 3.
      |
      v
Sentence-aware chunks
```

### Benefits

- Avoids cutting sentences in the middle
- Produces more readable fragments
- Preserves basic grammatical units

### Limitation

A single sentence might not contain enough surrounding context. Multiple related sentences may need to be grouped.

---

## 7. Paragraph-Based Chunking

Paragraph-based chunking uses paragraph boundaries as natural units.

### Best fit

- Articles
- Policies
- Knowledge-base pages
- Documentation with well-formed paragraphs

### Risk

Paragraph lengths vary. Some paragraphs may be too short, while others may exceed embedding-model limits.

A practical implementation may group short paragraphs while splitting oversized ones.

---

## 8. Structure-Aware Chunking

Structure-aware chunking uses document elements such as:

- Titles
- Headings
- Sections
- Paragraphs
- Lists
- Tables
- Page regions

```text
Heading: Password Reset
  Paragraph 1
  Paragraph 2

Heading: Account Lockout
  Paragraph 1
```

Chunks can retain the heading with the related content.

### Benefits

- Preserves document hierarchy
- Improves semantic coherence
- Helps citations and traceability
- Avoids arbitrary cuts

### Exam clue

```text
Preserve headings, paragraphs, tables, or document layout
```

Think:

```text
Structure-aware / layout-aware chunking
```

---

## 9. Semantic Chunking

Semantic chunking splits content based on changes in meaning rather than only fixed length.

```text
Topic A sentences
       |
       v
Chunk A

Meaning changes
       |
       v
Chunk B
```

### Benefits

- Semantically coherent chunks
- Better retrieval relevance for complex documents
- Less unrelated content within each chunk

### Trade-offs

- More processing complexity
- Potentially higher preparation cost
- Requires careful evaluation

Microsoft Document Intelligence Layout capabilities can expose document structure in Markdown, enabling semantic chunking based on headings and other building blocks.

---

## 10. Recursive Chunking

Recursive chunking attempts larger natural boundaries first, then uses smaller separators when necessary.

Conceptual order:

```text
Section
  -> Paragraph
     -> Sentence
        -> Word/token boundary
```

This preserves larger semantic units where possible while still respecting maximum size limits.

---

## 11. Sliding Window and Overlap

Overlapping chunks share some content.

```text
Chunk 1: A B C D E
Chunk 2:       D E F G H
               ^ ^
              overlap
```

### Why overlap helps

- Preserves information across boundaries
- Reduces the chance that a key sentence is separated from its context
- Helps retrieve content when a relevant idea spans two chunks

### Too little overlap

- Boundary context may be lost.

### Too much overlap

- Duplicate content increases storage and embedding cost.
- Search results may contain nearly identical chunks.
- The prompt may receive repetitive context.

### Exam memory

```text
Context lost at boundaries
-> increase overlap appropriately

Too many duplicate chunks
-> reduce overlap / improve deduplication
```

---

## 12. Parent-Child Chunking

Parent-child chunking stores small retrieval units while retaining a relationship to a larger contextual unit.

```text
Parent section
   |
   +-- Child chunk 1
   +-- Child chunk 2
   +-- Child chunk 3
```

Possible flow:

1. Search small child chunks for precision.
2. Use the parent section to provide wider context to the LLM.

### Benefit

```text
Small child -> precise retrieval
Large parent -> sufficient context
```

This helps balance retrieval precision and answer context.

---

## 13. Table Chunking

Tables require special care because meaning depends on relationships between headers, rows, and cells.

Bad approach:

```text
Split table halfway through a row
```

Better approaches can include:

- Preserve table headers with rows.
- Keep logically related rows together.
- Convert tables into structured or Markdown representations.
- Store table metadata and source references.
- Use layout-aware extraction.

### Exam clue

```text
Tables are losing headers or row relationships
```

Think:

```text
Layout-aware extraction and structure-aware chunking
```

---

## 14. Image and Multimodal Content

Documents can include images, diagrams, and charts. These elements may need:

- Image descriptions
- OCR
- Layout extraction
- Multimodal processing
- Metadata connecting an image with its surrounding section

Generating descriptions for media adds processing cost. In some scenarios, content can instead be passed to a multimodal model at inference time.

The appropriate approach depends on cost, latency, accuracy, and model capabilities.

---

## 15. Azure AI Search Text Split Skill

The **Text Split skill** in Azure AI Search breaks text into chunks during an indexer enrichment pipeline.

```text
Indexer
   |
   v
Text Split skill
   |
   v
Pages or sentences
   |
   v
Embedding skill
   |
   v
Search index
```

The skill supports modes such as:

- `pages`
- `sentences`

It can also output positional metadata such as offsets and ordinal positions.

### Important settings

- `textSplitMode`
- `maximumPageLength`
- `pageOverlapLength`
- `unit`, depending on supported API version and configuration
- `defaultLanguageCode`

Microsoft currently documents **512 tokens** as a general recommendation for page length with text embedding models. This is a starting recommendation, not a guaranteed optimum for every workload.

---

## 16. Azure Document Intelligence and Layout-Aware Chunking

Azure Document Intelligence Layout can extract structural elements from documents and represent content using Markdown-oriented structure.

It is useful when source documents contain:

- Complex headings
- Multiple columns
- Tables
- Paragraph structure
- Page layout

### Exam rule

```text
Simple text without structure
-> Fixed-size or sentence-based splitting may be sufficient

Complex PDFs/forms/tables/layout
-> Document Intelligence / structure-aware chunking
```

---

## 17. Azure Content Understanding

For newer Azure AI Search skillset scenarios, Microsoft guidance points to **Azure Content Understanding** for capabilities such as:

- Semantic chunking
- AI-generated image descriptions
- Improved extraction of document-embedded tables

Always check whether the exam scenario specifies a generally available feature, a preview feature, or a particular service/API version.

---

## 18. One-to-Many Indexing

Chunking creates multiple search documents from one source document.

```text
Source document: Policy.pdf
        |
        +-- Index record: chunk-1
        +-- Index record: chunk-2
        +-- Index record: chunk-3
```

Each chunk should retain source-level information so it can be traced back to the original document.

Useful fields include:

```text
chunkId
parentDocumentId
chunkText
title
heading
sourceUrl
pageNumber
ordinalPosition
contentVector
accessControlMetadata
```

---

## 19. Chunk Metadata

Metadata improves retrieval, filtering, citation, security, and reconstruction.

Examples:

- Source document ID
- File name
- URL
- Page number
- Section heading
- Chunk number
- Department
- Language
- Date
- Access-control identifiers

### Example

```json
{
  "chunkId": "policy-001-03",
  "parentId": "policy-001",
  "title": "Leave Policy",
  "heading": "Parental Leave",
  "page": 8,
  "content": "...",
  "contentVector": [0.12, -0.44, 0.91]
}
```

### Exam rule

```text
Need filtering, citations, source traceability, or security trimming
-> preserve/enrich chunk metadata
```

---

## 20. Chunk Enrichment

After splitting documents, chunks can be cleaned and enriched.

Possible enrichment fields:

- Title
- Summary
- Keywords
- Questions the chunk can answer
- Entities
- Language
- Source location

The goal is to improve retrieval while retaining the original content for display and citations.

### Caution

Enrichment adds processing cost and complexity. Evaluate whether it improves actual retrieval metrics.

---

## 21. Chunking and Security

Chunking must not break document permissions.

If a protected document becomes 20 chunks, every chunk must preserve or inherit the correct access-control metadata.

```text
Protected document
      |
      v
20 protected chunks
```

not:

```text
Protected document
      |
      v
Publicly retrievable chunks
```

### Exam clue

```text
Users must retrieve only documents they are authorized to access
```

Think:

- Permission metadata
- Security filters/security trimming
- Least privilege
- Permission-aware knowledge sources

---

## 22. Chunking Evaluation

Do not select chunk size by intuition alone. Evaluate with representative documents and real queries.

Important retrieval metrics include:

- **Precision:** How many retrieved chunks are relevant?
- **Recall:** How many relevant chunks were successfully retrieved?
- **Precision@K:** Relevance among the top K retrieved chunks
- **Recall@K:** Relevant evidence found within the top K
- **MRR:** Position of the first relevant result
- **NDCG:** Ranking quality when relevance has grades

Also evaluate generation outcomes:

- Groundedness
- Completeness
- Citation correctness
- Answer relevance
- Latency
- Token usage
- Cost

### Practitioner method

Test several configurations, for example:

```text
Configuration A: 256 tokens, 10% overlap
Configuration B: 512 tokens, 10% overlap
Configuration C: 800 tokens, 15% overlap
Configuration D: structure-aware chunks
```

Use the same evaluation set and compare retrieval and answer quality. These are test configurations, not universal recommendations.

---

## 23. Chunking Strategy Decision Table

| Requirement | Consider |
|---|---|
| Simple unstructured logs | Fixed-size chunks |
| Natural prose | Sentence/paragraph-aware chunks |
| Headings and sections matter | Structure-aware chunking |
| Meaning changes across text | Semantic chunking |
| Important context crosses boundaries | Overlap |
| Need precise search plus larger context | Parent-child chunking |
| Complex PDFs and tables | Document Intelligence/Layout or Content Understanding |
| Input exceeds embedding limit | Smaller chunks |
| Retrieved context is too broad | Smaller or more semantic chunks |
| Retrieved chunks lack context | Larger chunks, overlap, or parent context |
| Need citations/filtering | Preserve metadata |
| Need authorized retrieval | Preserve ACL/security metadata |

---

# Practice Questions

## Question 1

A large policy document contains many unrelated sections. Search uses a single embedding for the complete document, and retrieval quality is poor.

What should you do?

A. Increase temperature  
B. Split the document into meaningful chunks before embedding  
C. Increase maximum response tokens  
D. Add a stop sequence  

### Correct answer: B

**Why B is correct:** Smaller meaningful chunks produce more focused semantic representations and improve retrieval granularity.

**Why the others are incorrect:**

- **A:** Temperature controls response randomness.
- **C:** Output limits do not improve document representation.
- **D:** Stop sequences control generation termination.

---

## Question 2

Important facts are often split between adjacent chunks, causing incomplete retrieval context.

What should you consider?

A. Add appropriate overlap between adjacent chunks  
B. Increase temperature  
C. Enable JSON mode  
D. Fine-tune the LLM  

### Correct answer: A

**Why A is correct:** Overlap preserves some boundary context in both neighboring chunks.

---

## Question 3

A RAG solution returns highly precise fragments, but each fragment lacks enough context for the LLM to answer completely.

Which change is most appropriate to test?

A. Smaller chunks with no overlap  
B. Larger chunks, more overlap, or parent-child retrieval  
C. Higher temperature  
D. Lower frequency penalty  

### Correct answer: B

**Why B is correct:** The problem is insufficient retrieved context. Larger contextual units, overlap, or parent retrieval can address it.

---

## Question 4

A document collection consists mainly of application logs without meaningful headings or paragraphs.

Which chunking method is a reasonable starting point?

A. Fixed-size chunking  
B. Table-aware chunking  
C. Fine-tuning  
D. Semantic ranking only  

### Correct answer: A

**Why A is correct:** Fixed-size chunking is simple and can work well for content without strong semantic structure.

---

## Question 5

A collection of PDFs contains headings, paragraphs, lists, and tables. The solution must preserve these relationships.

What should you use?

A. Arbitrary character splitting only  
B. Layout/structure-aware extraction and chunking  
C. Higher temperature  
D. Presence penalty  

### Correct answer: B

**Why B is correct:** Layout-aware processing preserves structural relationships that arbitrary splitting can destroy.

---

## Question 6

You use an Azure AI Search indexer and want to split extracted text into pages or sentences before calling an embedding skill.

Which built-in skill is relevant?

A. Text Split skill  
B. Key Phrase Extraction only  
C. Sentiment skill  
D. Translation skill only  

### Correct answer: A

**Why A is correct:** The Text Split skill is designed to divide text into page- or sentence-based chunks in a skillset pipeline.

---

## Question 7

A source document is divided into 30 chunks. Users need citations back to the correct page and heading.

What should each chunk preserve?

A. Only the embedding vector  
B. Source, page, heading, and positional metadata  
C. Temperature setting  
D. Model deployment quota  

### Correct answer: B

**Why B is correct:** Source metadata enables citation, traceability, reconstruction, and filtering.

---

## Question 8

A protected HR document is divided into chunks. How should access control be handled?

A. Remove permissions after chunking  
B. Preserve/inherit authorization metadata on every chunk  
C. Use a higher top-p  
D. Store all chunks in a public index  

### Correct answer: B

**Why B is correct:** Chunking must not weaken source-document permissions. Retrieval should enforce user authorization.

---

## Question 9

A table is split into chunks, but retrieved rows no longer include their column headers.

What is the best improvement?

A. Increase response temperature  
B. Use table/layout-aware chunking that preserves headers with rows  
C. Reduce output tokens  
D. Increase presence penalty  

### Correct answer: B

**Why B is correct:** Table meaning depends on relationships among headers, rows, and cells.

---

## Question 10

After increasing overlap significantly, retrieval results contain many near-duplicate chunks and prompt context becomes repetitive.

What should you do?

A. Increase overlap further  
B. Reduce overlap or improve deduplication/reranking  
C. Disable indexing  
D. Fine-tune the embedding model  

### Correct answer: B

**Why B is correct:** Excessive overlap creates duplication, storage cost, and repetitive retrieved context.

---

## Question 11

A team wants a precise retrieval unit but also needs a larger coherent context passed to the LLM.

Which pattern is most suitable?

A. Parent-child chunking  
B. Temperature tuning  
C. JSON mode  
D. Frequency penalty  

### Correct answer: A

**Why A is correct:** Child chunks support precise retrieval, while the linked parent supplies broader context.

---

## Question 12

How should a team choose the best production chunk size?

A. Always use exactly 512 tokens  
B. Always use one page  
C. Evaluate multiple strategies using representative documents, queries, retrieval metrics, and answer-quality metrics  
D. Use the model temperature value as the chunk size  

### Correct answer: C

**Why C is correct:** Chunking performance depends on the content and workload. Values such as 512 tokens are useful starting points, not universal optima.

---

# High-Value Exam Traps

## Trap 1

```text
One document = one chunk
```

Not necessarily. Even a technically small document can benefit from chunking if it contains many unrelated topics.

---

## Trap 2

```text
Smaller chunks are always better
```

Wrong. Very small chunks can lose critical context.

---

## Trap 3

```text
Larger chunks are always better
```

Wrong. Large chunks can dilute meaning and waste prompt tokens.

---

## Trap 4

```text
More overlap is always better
```

Wrong. Excessive overlap creates duplicates and additional cost.

---

## Trap 5

```text
512 tokens is the mandatory chunk size
```

Wrong. It is a general starting recommendation in a specific Microsoft context. Evaluate your workload.

---

## Trap 6

```text
Chunking and embedding are the same
```

Wrong.

```text
Chunking  -> divides content
Embedding -> converts content to a vector
```

---

## Trap 7

```text
Chunking removes source permissions
```

Wrong. Permissions must be preserved and enforced for every derived chunk.

---

# One-Minute Revision Sheet

```text
CHUNKING
Split large content into retrieval-friendly units

FIXED-SIZE
Simple and predictable; may cut concepts

SENTENCE/PARAGRAPH
Uses natural text boundaries

STRUCTURE-AWARE
Preserves headings, sections, tables, and layout

SEMANTIC
Splits when meaning/topic changes

RECURSIVE
Uses large natural boundaries, then smaller separators

OVERLAP
Preserves boundary context
Too much -> duplication

PARENT-CHILD
Child for precise retrieval; parent for broader context

TEXT SPLIT SKILL
Azure AI Search skill for page/sentence splitting

DOCUMENT INTELLIGENCE / LAYOUT
Useful for complex PDFs, tables, and document structure

CONTENT UNDERSTANDING
Newer capabilities for semantic chunking, tables, and image descriptions

METADATA
Source, page, heading, chunk ID, ACLs

EVALUATION
Compare chunk strategies using retrieval and generation metrics
```

# Final AI-103 Decision Rule

```text
Large document or many topics?
-> Chunk it

Simple unstructured content?
-> Fixed-size starting point

Natural prose?
-> Sentence/paragraph-aware chunking

Complex headings/tables/layout?
-> Structure/layout-aware chunking

Meaning changes by topic?
-> Semantic chunking

Boundary context lost?
-> Add appropriate overlap

Too many duplicate results?
-> Reduce overlap / deduplicate

Precise retrieval but need wider context?
-> Parent-child chunks

Need citations and filtering?
-> Preserve metadata

Need secure retrieval?
-> Preserve ACL/security metadata

Choosing final chunk size?
-> Evaluate with representative queries and metrics
```

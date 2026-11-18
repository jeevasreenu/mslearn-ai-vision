# AI-103: Chunking (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, config/code snippets, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> There is **no universally optimal chunk size**. The exam tests **why you chunk, which strategy fits which content, the trade-offs, and which Azure AI Search feature does what**.

---

## 0. Core Concepts (read first)

### 0.1 What is chunking and why do it?

**Chunking** = partitioning large documents into smaller pieces ("chunks") before embedding and indexing. In RAG, the **chunk is the unit of retrieval, embedding, citation, and prompt context**.

| Why chunk | Explanation |
|---|---|
| **Stay under token limits** | Embedding and chat models have max input sizes (for example, `text-embedding-3-small` accepts **8,191 tokens**, which is roughly 6,000 words). Oversized input fails or gets **truncated (data loss)** |
| **Better retrieval precision** | One vector for a whole multi-topic document is a blurry average. Finer chunks match specific questions better |
| **Lower cost / noise** | Passing irrelevant text to the LLM is **expensive** and can cause **inaccurate or unrelated answers** |
| **Meaningful citations** | A chunk maps to a specific passage/page/section you can cite |

> Chunking is **required** only if documents exceed the model's input limit, but it's also **beneficial** when a document is poorly represented by a single vector (for example, a wiki page covering many sub-topics, even if short).

### 0.2 The size trade-off (very high-yield)

| | **Chunks too SMALL** | **Chunks too LARGE** |
|---|---|---|
| Retrieval precision | High (focused) | Lower (diluted, mixed topics) |
| Context for the LLM | **Too little**. Relevant context split across chunks, may be missed | Plenty, but includes **noise** |
| Index size / cost | **More vectors** (more storage and embedding calls) | Fewer vectors |
| Token usage per answer | Lower per chunk, but may need **many chunks** | **Higher** per chunk; risk of exceeding context/limit |
| Typical failure | "Answer needs two chunks and only one was retrieved" | "Right passage buried in irrelevant text" / token limit |

Guidance from sources (treat as **starting points, not rules**):
- Azure AI Search docs example of **fixed-size chunks**: about **200 words or 600 characters** with **10–15% overlap**.
- Text Split skill: `pages` mode `maximumPageLength` default **5,000** characters (min 300, max 50,000). For `azureOpenAITokens` unit and embedding models, a general recommendation is about **512 tokens** per page.
- Community guidance often suggests **~400–512 tokens, 10–20% overlap** as a baseline, **smaller (128–256)** for factual lookups, **larger (512–1024)** for analytical questions. **Test on your own data.**

### 0.3 Overlap

Overlap repeats a slice of the end of one chunk at the start of the next, so ideas cut at a boundary still appear whole in at least one chunk.

- Typical: **10–15%** (Microsoft example) up to **10–20%** (common community guidance).
- In the Text Split skill, `pageOverlapLength` copies that many characters from the end of chunk *n* into chunk *n+1*, and must stay **under half of `maximumPageLength`**.
- **Too much overlap** → duplicate content, more vectors, more cost, **redundant results**.
- **Zero overlap** → boundary loss.

### 0.4 Chunking strategies

| Strategy | How it splits | Strengths | Weaknesses | Azure AI Search feature |
|---|---|---|---|---|
| **Fixed-size** (with overlap) | Every N characters/tokens | Simple, predictable, cheap, good baseline for uniform text | Cuts mid-sentence/thought; ignores structure | **Text Split skill** (`pages` mode) |
| **Sentence-based** | At sentence-ending punctuation | Never splits a sentence | Variable, often tiny chunks | Text Split skill (`sentences` mode) |
| **Recursive / separator hierarchy** | Tries headings → paragraphs → sentences → words until size fits | Good default, respects natural boundaries | Still size-driven | (Library-level, for example LangChain) |
| **Structure-aware (document-aware)** | By **headings/sections**, tables, lists, using document layout | Preserves context, adds heading **metadata**, great for PDFs/Markdown/HTML | Needs parsing (cost, complexity) | **Document Layout skill** (Document Intelligence layout model, Markdown output) and **Markdown parsing mode** |
| **Semantic** | Where **meaning shifts** (for example, embedding similarity drops between sentences) | Coherent chunks, can span page boundaries | Extra compute, tuning thresholds | (Described as an approach; Document Layout gives semantically coherent sections) |
| **Hierarchical / parent-child** | Small child chunks for retrieval, larger **parent** returned for context | Precision **and** context | More complex indexing and retrieval | Via index projections / parent-child design |
| **Contextual** | Adds an LLM-generated context blurb to each chunk | Big recall gains on ambiguous chunks | LLM cost per chunk | Custom |

### 0.5 Azure AI Search specifics (what the exam is likely to ask)

- **Chunking happens in skills, which depend on indexers.** Nothing splits documents unless you configure a pipeline (or use the portal wizard / knowledge source that creates it for you).
- **Integrated vectorization pipeline:** data source → **indexer** → **skillset** (chunking skill + **embedding skill**) → **index** (with a vector field). Plus a **vectorizer** for query-time embedding.
- **Text Split skill** (`Microsoft.Skills.Text.SplitSkill`): `textSplitMode` = `pages` or `sentences`; `maximumPageLength`; `pageOverlapLength`; `unit` = `characters` (default) or `azureOpenAITokens`; free, **non-billable**, no AI-services key.
- **Document Layout skill:** calls the **Document Intelligence layout model**, outputs **Markdown** with headings and content. Combine with **Text Split skill** to **constrain chunk size within each Markdown section**, then embed each chunk.
- **Index projections (one-to-many indexing):** map **one source document** to **many chunk documents** in the index, with each chunk carrying its own vector and a **parent reference** (so you can trace back and filter by source).
- For **agentic retrieval**, **knowledge sources** (such as Blob Storage, ADLS Gen2 or OneLake) can **generate the full chunking and vectorization pipeline for you** (indexer, data source, skillset and index created automatically).
- If you **can't use integrated vectorization**, you can chunk yourself in code (for example, with a library) and **push** the chunk documents.
- Features marked **(preview)** aren't covered by an SLA and aren't recommended for production.

### 0.6 Chunk metadata (often overlooked, often tested)

Store with each chunk: **source document ID/title/URL, page number, section heading(s), chunk ordinal, last-modified date, access-control info, language.**

Benefits: **citations**, **filtering** (by date, product, department), **security trimming**, re-indexing only what changed, reassembling neighbouring chunks.

> Prepending the **heading path** (for example, "Returns > International > Customs fees") to chunk text often improves both vector and keyword matching.

### 0.7 Special content

| Content | Chunking consideration |
|---|---|
| **Tables** | Don't split mid-table. Keep rows with headers, or convert to Markdown/structured text |
| **Code** | Chunk by function/class boundaries |
| **FAQ / Q&A** | One Q&A pair per chunk |
| **Scanned PDFs / images** | Need **OCR / Document Intelligence** first; image descriptions are chunked as text (extra cost) |
| **Slides / short pages** | Per-slide/page chunks may already be right-sized |
| **Long contracts / manuals with headings** | Structure-aware by section, then size-limit within sections |

### 0.8 Chunking symptoms and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Answer sentence cut off; passage missing its explanation | Boundary cut / no overlap | Add overlap, use sentence/structure-aware splitting |
| Retrieved chunk is right but missing context (for example, "it" and "the policy" are unclear) | Chunk too small or heading context lost | Larger chunks, include heading path, parent-child, or contextual retrieval |
| Right info buried inside a long noisy chunk | Chunk too large / multi-topic | Smaller or structure-aware chunks |
| Table answers wrong or garbled | Table split across chunks | Layout-aware parsing; keep tables intact |
| Embedding call fails / truncation | Chunk exceeds model token limit | Reduce `maximumPageLength` (use token unit) |
| Duplicate-looking results | Too much overlap | Reduce overlap, dedupe |
| Skyrocketing index size/cost | Tiny chunks or heavy overlap | Increase chunk size, lower overlap |
| Poor results across the board on PDFs with headings | Fixed-size ignoring structure | **Document Layout skill** + Text Split within sections |
| Can't cite page numbers | No location metadata | Capture page/section metadata during chunking |

### 0.9 Choosing a strategy (decision rules)

```text
Uniform plain text, quick baseline            → Fixed-size + 10–15% overlap (Text Split skill)
Documents with headings/sections/tables (PDF) → Structure-aware (Document Layout skill) + size cap per section
Topics shift inside prose                     → Semantic chunking
Need precision AND context                    → Parent-child (small to retrieve, large to feed the LLM)
Chunks lose meaning out of context            → Add heading path / contextual retrieval
Code                                          → By function/class
FAQ                                           → One Q&A per chunk
Unsure                                        → Build a test set, compare strategies, measure retrieval quality
```

### 0.10 Five ideas the exam really tests

1. **Chunk to fit token limits and to improve retrieval precision.** Otherwise truncation loses data.
2. **Size is a trade-off.** Too small loses context, too large adds noise and cost. Test on your data.
3. **Overlap prevents boundary loss.** Too much overlap duplicates and costs more.
4. **Structure-aware chunking (Document Layout skill) beats blind fixed-size** for structured documents.
5. **In Azure AI Search, chunking is done by skills in an indexer pipeline** (Text Split / Document Layout), with **index projections** mapping one document to many chunks.

---

## 1. Scenario Questions

### Question 1: Why chunk at all?

A team embeds each 60-page policy PDF as a single input. Ingestion errors appear, and in some cases embeddings are produced for only the start of the document. What is the BEST explanation and fix?

A. The vector index needs more replicas  
B. The documents exceed the embedding model's **input token limit** (causing failures or **truncation/data loss**). **Chunk the documents** to fit the limit, then embed each chunk  
C. Temperature is too low  
D. Switch to keyword search only

<details>
<summary>Answer</summary>

### ✅ B

Embedding models have a maximum input size (for example, 8,191 tokens for text-embedding-3-small). Oversized input fails or is truncated, losing content. Chunking prevents data loss.

- **A ❌** Scale doesn't change model limits.
- **C ❌** Embeddings don't use temperature.
- **D ❌** Abandons semantic retrieval instead of fixing the cause.
</details>

---

### Question 2: Too small or too large?

A RAG bot retrieves the right chunk for "What is the refund window?", but the chunk says only "It is 30 days." The bot can't tell what "it" refers to and gives a vague answer. Which TWO changes are MOST appropriate?

A. Use **larger or structure-aware chunks** that keep the heading/context together  
B. **Prepend the section heading path** (or use parent-child retrieval) so each chunk carries context  
C. Reduce overlap to zero  
D. Lower `max_tokens`  
E. Switch to a smaller embedding model

<details>
<summary>Answer</summary>

### ✅ A and B

The chunk is too small and lost its context. Keep related text together, add heading metadata/text, or return a larger parent chunk.

- **C ❌** Makes boundary loss worse.
- **D, E ❌** Don't restore lost context.
</details>

---

### Question 3: Noisy retrieval

A knowledge base uses 4,000-token chunks. Questions about specific facts retrieve the right chunk, but it contains 10 unrelated topics. The LLM often answers from the wrong part, and token costs are high. What should you do?

A. Increase chunk size further  
B. **Reduce chunk size** (or switch to structure-aware chunking by section), keep modest overlap, and evaluate retrieval on your test queries  
C. Remove the system message  
D. Increase temperature

<details>
<summary>Answer</summary>

### ✅ B

Oversized, multi-topic chunks dilute embeddings and add noise and cost. Smaller, coherent chunks improve precision. Evaluate to find the right balance.
</details>

---

### Question 4: Boundary loss

Users report that answers sometimes miss the key condition, which sits in the sentence right **after** a chunk boundary. The pipeline uses fixed-size chunks with **no overlap**. What is the BEST fix?

A. Add **overlap** (for example, 10–15%) and/or split on sentence/paragraph boundaries  
B. Increase `top_p`  
C. Use a larger LLM  
D. Remove metadata

<details>
<summary>Answer</summary>

### ✅ A

Overlap (or boundary-aware splitting) preserves context cut at chunk edges.

**Trap:** More overlap isn't free. It duplicates content and raises storage and embedding cost, so stay moderate.
</details>

---

### Question 5: Structured PDFs (snippet)

```json
{
  "corpus": "Health-plan PDFs with headings, sub-headings and tables",
  "current_chunking": "Text Split skill, pages mode, 1000 characters, 0 overlap",
  "problem": "Answers mix content from unrelated sections; tables are cut in half",
  "goal": "Chunks that respect headings and keep content semantically coherent"
}
```

Which approach fits BEST?

A. Reduce `maximumPageLength` to 300  
B. Use the **Document Layout skill** (Document Intelligence layout model, Markdown output) to chunk by structure, then use the **Text Split skill within each section** to cap size, then embed each chunk  
C. Switch to keyword search only  
D. Increase temperature

<details>
<summary>Answer</summary>

### ✅ B

Structure-aware chunking follows headings and keeps tables/sections together. Text Split then enforces size limits inside each section.

- **A ❌** Smaller fixed chunks would cut tables and sections even more.
- **C, D ❌** Don't address chunking.

**Trap:** The corpus description (headings + tables) is the clue for structure-aware chunking.
</details>

---

### Question 6: Which Azure AI Search feature? (drag-and-drop)

Match each need to the correct feature: **Text Split skill · Document Layout skill · Index projections · Embedding skill · Vectorizer · Indexer**.

| Need | Feature |
|---|---|
| A. Break text into pages of a maximum length, optionally with overlap | ? |
| B. Recognise headings/sections in PDFs and output Markdown | ? |
| C. Map one source document to many chunk documents in the index | ? |
| D. Generate vectors for each chunk at indexing time | ? |
| E. Convert a plain-text query to a vector at query time | ? |
| F. Drive the pipeline from a data source through the skillset into the index | ? |

<details>
<summary>Answer</summary>

| Need | Feature |
|---|---|
| A | **Text Split skill** |
| B | **Document Layout skill** |
| C | **Index projections** (one-to-many indexing) |
| D | **Embedding skill** |
| E | **Vectorizer** |
| F | **Indexer** |
</details>

---

### Question 7: Text Split parameters (snippet)

```json
{
  "@odata.type": "#Microsoft.Skills.Text.SplitSkill",
  "textSplitMode": "pages",
  "maximumPageLength": 2000,
  "pageOverlapLength": 1500,
  "unit": "characters"
}
```

The skillset fails validation or produces heavy duplication. What is the MOST likely issue?

A. `pageOverlapLength` (1500) is too large. It must be **less than half** of `maximumPageLength` (here, under 1000)  
B. `textSplitMode` can't be `pages`  
C. `unit` must be `tokens` only  
D. The skill requires a billable AI-services key

<details>
<summary>Answer</summary>

### ✅ A

Overlap must stay under half the page length, and heavy overlap also means heavy duplication and cost.

- **B ❌** `pages` is valid.
- **C ❌** `characters` is the default unit.
- **D ❌** The Text Split skill is non-billable and needs no key.
</details>

---

### Question 8: Characters or tokens?

A team sets `maximumPageLength` to 8,000 **characters** and feeds chunks to an embedding model limited to 8,191 **tokens**. Some chunks in dense, non-English text still fail. Why, and what is the BEST fix?

A. Characters and tokens aren't equivalent. Dense or non-English text can use **many more tokens per character**. Use the **token-based unit** (`azureOpenAITokens`) and set the page length to a **safe token size** (for example, around 512 tokens as a general recommendation)  
B. Embeddings require temperature 0  
C. The index needs more partitions  
D. Switch to sentences mode only

<details>
<summary>Answer</summary>

### ✅ A

Token count varies by language and content. Measure chunks in tokens to guarantee they fit the model.
</details>

---

### Question 9: One document to many chunks

A team runs an indexer over 10,000 PDFs and ends up with **10,000 index documents**, each with a single huge vector (or failures on large files), instead of one document per chunk. They want **each chunk as its own searchable document with its own vector**, linked back to the parent file. What should they configure?

A. A larger replica count  
B. **Index projections** (one-to-many indexing) in the skillset so each chunk produced by the split skill becomes its own index document with a parent reference  
C. Temperature  
D. A bigger `max_tokens`

<details>
<summary>Answer</summary>

### ✅ B

Index projections map each enriched chunk to a separate index document, preserving a link to the parent document.
</details>

---

### Question 10: Parent-child design

A legal team wants **precise retrieval** of small clauses but wants the LLM to see **the whole section** around each clause to interpret it correctly. Which design fits BEST?

A. One giant chunk per contract  
B. **Parent-child (hierarchical) chunking**: embed and retrieve **small child chunks**, then return the associated **larger parent section** (or neighbouring chunks) to the LLM  
C. Keyword search only  
D. Higher temperature

<details>
<summary>Answer</summary>

### ✅ B

Small chunks give precise matching. The parent supplies the context. This reflects the precision-vs-context trade-off.
</details>

---

### Question 11: Content types (Select TWO)

Which TWO chunking choices are MOST appropriate?

A. Split an FAQ so that **each question-and-answer pair is one chunk**  
B. Cut a financial table in the middle of the data rows at the character limit  
C. For source code, chunk along **function/class boundaries**  
D. Chunk scanned PDFs directly without OCR  
E. Use a single chunk for an entire 500-page manual

<details>
<summary>Answer</summary>

### ✅ A and C

Respect natural units. 

- **B ❌** Splits table meaning.
- **D ❌** Scanned content needs OCR/Document Intelligence first.
- **E ❌** Exceeds limits and dilutes retrieval.
</details>

---

### Question 12: Metadata (Select TWO)

A compliance team needs RAG answers with **page-number citations**, **filtering by document date**, and **per-user access trimming**. Which TWO practices should be part of the chunking design?

A. Store **page number, section heading, source ID and last-modified date** with each chunk  
B. Store **access-control information** (for example, permission groups) on each chunk document for security trimming at retrieval  
C. Strip all metadata to save space  
D. Rely on the LLM to guess page numbers  
E. Merge all chunks back into one document

<details>
<summary>Answer</summary>

### ✅ A and B

Chunk metadata enables citations, filters, and enforcement at retrieval time.

- **C, D, E ❌** Break citations, filtering and security.
</details>

---

### Question 13: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | Chunking is only needed when documents exceed the embedding model's input limit. | |
| 2 | In Azure AI Search, chunking is performed by skills that run in an indexer pipeline. | |
| 3 | The Text Split skill is billed and needs an AI services key. | |
| 4 | Overlap helps preserve context that would otherwise be cut at chunk boundaries. | |
| 5 | Very small chunks can cause relevant context to be spread across multiple chunks. | |
| 6 | The Document Layout skill uses the Azure AI Document Intelligence layout model. | |
| 7 | A single best chunk size exists for all RAG workloads. | |
| 8 | Semantic chunking splits where the meaning changes rather than at a fixed length. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **No** | Also beneficial when a document is poorly represented by a single vector (for example, a multi-topic wiki page), even if under the limit. |
| 2 | **Yes** | Skills depend on indexers. |
| 3 | **No** | Non-billable, no key required. |
| 4 | **Yes** | The purpose of overlap. |
| 5 | **Yes** | Context fragmentation. |
| 6 | **Yes** | It calls the layout model. |
| 7 | **No** | Depends on content, queries and testing. |
| 8 | **Yes** | The definition of semantic chunking. |
</details>

---

### Question 14: Match the symptom to the fix (drag-and-drop)

Match each symptom to the **best fix**: **Add overlap · Smaller/structure-aware chunks · Larger chunks / heading context · Token-based sizing · Layout-aware parsing · Reduce overlap**.

| Symptom | Fix |
|---|---|
| A. Key condition lost right after a chunk boundary | ? |
| B. Chunk mixes 10 topics, answers drift | ? |
| C. Chunk says "It is 30 days" with no context | ? |
| D. Embedding errors on dense non-English text despite "safe" character limits | ? |
| E. Table cells split across chunks | ? |
| F. Duplicate near-identical results and bloated index | ? |

<details>
<summary>Answer</summary>

| Symptom | Fix |
|---|---|
| A | **Add overlap** |
| B | **Smaller / structure-aware chunks** |
| C | **Larger chunks / heading context** |
| D | **Token-based sizing** |
| E | **Layout-aware parsing** |
| F | **Reduce overlap** |
</details>

---

### Question 15: Selecting a strategy by evaluation

A team debates 256 vs 1,024 tokens for their corpus, citing different blog posts. What is the MOST defensible way to decide?

A. Pick the number in the most popular blog  
B. Build a **representative test set of questions**, run candidate chunking strategies/sizes, and **measure retrieval quality** (and answer quality) before choosing  
C. Always choose the maximum model limit  
D. Always choose 100 tokens

<details>
<summary>Answer</summary>

### ✅ B

Published numbers are starting points. The best setting is the one your own evaluation set supports.
</details>

---

## 2. Mini Case Study: Litware Insurance Knowledge Base

### Background

Litware Insurance is indexing documents into **Azure AI Search** for a RAG assistant on Microsoft Foundry.

1. **Policy PDFs** (100–300 pages) with headings, sub-headings, and **tables of coverage limits**.
2. **FAQ articles**, each a short question and answer.
3. **Claim-adjuster code snippets** documentation with sample code.
4. **Scanned legacy forms** (images of paper documents).
5. Answers need **page-number citations** and must respect **per-team access**.
6. The embedding model accepts **8,191 tokens**. The team wants a safe margin.
7. A first prototype with fixed 1,000-character chunks and no overlap produced mixed-section answers and split tables.
8. They want **minimal custom code** and **each chunk as its own index document** linked to the parent file.

### Case Q1: Policy PDFs

A. Fixed 1,000-character chunks, no overlap  
B. **Document Layout skill** for structure-aware (Markdown) chunking, then **Text Split within sections** to cap size  
C. One chunk per PDF  
D. Random splitting

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q2: FAQs

A. Merge 50 FAQs per chunk  
B. **One question-and-answer pair per chunk**  
C. Split every sentence  
D. One chunk for the whole FAQ site

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q3: Code documentation

A. Chunk along **function/class boundaries** (with the explanatory text attached)  
B. Fixed 200 characters  
C. Split in the middle of functions  
D. Skip it

<details><summary>Answer</summary>

### ✅ A
</details>

### Case Q4: Scanned forms

A. Chunk the raw images directly as text  
B. Run **OCR / Document Intelligence** first to extract text and structure, then chunk the extracted text  
C. Ignore them  
D. Use temperature 0

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q5: Citations and access control

Which TWO belong in each chunk document?

A. **Page number, section heading and source ID**  
B. **Access-control information** for security trimming at query time  
C. Nothing besides text  
D. The user's password

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q6: Safe size margin

A. 8,191 tokens per chunk (the model limit)  
B. A **token-based** chunk size well under the limit (for example, around **512 tokens**, validated on your data) with modest overlap  
C. 50,000 characters  
D. 5 characters

<details><summary>Answer</summary>

### ✅ B

The limit is a ceiling, not a target. Smaller, coherent chunks usually retrieve better.
</details>

### Case Q7: Pipeline plumbing for requirement 8

Which TWO deliver "minimal custom code" and "each chunk as its own index document"?

A. **Integrated vectorization** (indexer + skillset with chunking and embedding skills) or a knowledge source that generates the pipeline for you  
B. **Index projections** (one-to-many) so each chunk becomes its own document with a parent reference  
C. Write a custom ingestion service and skip indexers  
D. Store everything in one document field

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q8: Fix the prototype (requirement 7)

Which TWO changes address "mixed-section answers and split tables"?

A. Switch to **structure-aware chunking** (Document Layout skill)  
B. Add modest **overlap** where fixed-size splitting is still used  
C. Reduce chunks to 50 characters  
D. Increase temperature

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q9: Map content type to strategy

| Content | Strategy |
|---|---|
| Policy PDFs | ? |
| FAQs | ? |
| Code docs | ? |
| Scanned forms | ? |

<details><summary>Answer</summary>

| Content | Strategy |
|---|---|
| Policy PDFs | Structure-aware (Document Layout) + size cap per section |
| FAQs | One Q&A pair per chunk |
| Code docs | Function/class boundaries |
| Scanned forms | OCR/Document Intelligence first, then chunk |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Bigger-is-safer trap** | "Use the model's max input as the chunk size." | The limit is a ceiling. Smaller coherent chunks usually retrieve better. |
| **Smaller-is-better trap** | "Tiny chunks = most precise." | Too small loses context and inflates index/cost. |
| **Magic-number trap** | "There's one correct chunk size." | Depends on content and queries. **Evaluate**. |
| **Overlap trap** | "More overlap is always safer." | Duplicates, cost, redundant results. Keep 10–15%/10–20%. |
| **Truncation trap** | "Long inputs are just shortened harmlessly." | Truncation = **data loss**. Chunk instead. |
| **Characters-vs-tokens trap** | "Characters equal tokens." | Not equivalent. Use the token unit for hard limits. |
| **Hosting trap** | "Chunking happens automatically in the index." | Chunking is done by **skills in an indexer pipeline** (or your code). |
| **Billing trap** | "Text Split needs an AI services key." | It's non-billable, no key. |
| **Structure trap** | "Fixed-size is fine for any PDF." | Structured docs → **Document Layout skill**. |
| **One-document trap** | "One index document per source file." | RAG needs **chunk-level documents** (index projections). |
| **Table trap** | "Split tables at the character limit." | Keep tables intact or convert to structured text. |
| **Metadata trap** | "Text is enough." | Metadata gives citations, filters, security trimming. |
| **Scanned trap** | "Chunk image-based PDFs directly." | OCR/Document Intelligence first. |
| **Preview trap** | "All chunking features are production-ready." | Preview features lack SLA. Check status. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| Doc exceeds embedding input limit | Chunk (token-aware) |
| Text lost at chunk edges | Add overlap / sentence-aware splitting |
| Too much duplication / index bloat | Reduce overlap, enlarge chunks |
| Chunk lacks context | Larger chunks, heading path, parent-child, contextual retrieval |
| Chunk mixes topics | Smaller or structure-aware chunks |
| PDFs with headings and tables | **Document Layout skill** + Text Split per section |
| Uniform plain text baseline | Text Split skill (`pages`, ~10–15% overlap) |
| Topic shifts within prose | Semantic chunking |
| Need precision and context | Parent-child retrieval |
| FAQ | One Q&A per chunk |
| Code | Function/class boundaries |
| Scanned documents | OCR/Document Intelligence, then chunk |
| One file → many searchable chunks | **Index projections** (one-to-many) |
| Embed chunks at index time | **Embedding skill** |
| Embed query at query time | **Vectorizer** (same model) |
| Page-number citations, filtering, security | **Chunk metadata** |
| Minimal custom code | Integrated vectorization / knowledge source pipeline |
| Choosing size/strategy | **Evaluate** on a representative test set |

---

## 5. Quick Revision Sheet

```text
WHY CHUNK: token limits (truncation = data loss), retrieval precision, lower cost/noise, citations
SIZE:      too small = lost context + more vectors | too large = noise + cost + dilution
OVERLAP:   10–15% typical; protects boundaries; too much = duplicates/cost

STRATEGIES
  Fixed-size (+overlap)  -> Text Split skill (pages)          baseline
  Sentence               -> Text Split skill (sentences)
  Recursive              -> separators: headings > paragraphs > sentences
  Structure-aware        -> Document Layout skill (Markdown) + Text Split per section
  Semantic               -> split where meaning shifts
  Parent-child           -> retrieve small, feed large
  Contextual             -> add LLM-generated context per chunk

AZURE AI SEARCH
  Chunking = SKILLS in an INDEXER pipeline
  Pipeline = data source -> indexer -> skillset (chunk + embed) -> index (+ vectorizer at query time)
  Text Split: pages|sentences, maximumPageLength (default 5000 chars; min 300), pageOverlapLength (< half), unit chars|azureOpenAITokens, FREE
  Document Layout: Document Intelligence layout model -> Markdown headings/sections
  Index projections: one source doc -> many chunk docs (with parent link)
  Knowledge sources (Blob/ADLS/OneLake) can auto-generate the whole pipeline

METADATA: page, heading, source ID, date, ACLs -> citations, filters, security trimming
CONTENT:  tables intact | code by function | FAQ per Q&A | scans need OCR first
TEST:     no universal best size - evaluate on your own questions
```

### Best-answer checklist

1. Is the failure from **too little context**, **too much noise**, **boundary cuts**, or **token limits**? Match the fix.
2. Does the corpus have **structure** (headings, tables)? Use structure-aware chunking.
3. Hard size limits? Think **tokens**, not characters.
4. Need **citations/filters/security**? Plan **chunk metadata**.
5. Need **chunk-level documents**? **Index projections**.
6. Minimal code? **Integrated vectorization** or a knowledge-source-generated pipeline.
7. Unsure? **Evaluate** with a test set.

---

**Next concept:** Vector Search (same harder exam-style format)

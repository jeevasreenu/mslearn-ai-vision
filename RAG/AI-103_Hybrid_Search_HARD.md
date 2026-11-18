# AI-103: Hybrid Search (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, query snippets, RRF calculations, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Scope: **hybrid search in Azure AI Search (Foundry IQ)**: what it is, how RRF merges results, weights, how it combines with semantic ranking, filters/sorting, and when it is NOT the right choice.
> API versions, preview flags and defaults change. The exam tests **what hybrid does and when to choose it**, not version numbers.

---

## 0. Core Concepts (read first)

### 0.1 What is hybrid search?

**Hybrid search = ONE query request that contains BOTH a full-text query and a vector query.**

- The request includes **`search`** (text) **and** **`vectorQueries`** (vector) parameters.
- The full-text query and the vector query run **in parallel**.
- Each produces its own **ranked list**. The lists are merged by **Reciprocal Rank Fusion (RRF)** into **one** unified result set.
- It runs against **one index** that contains **searchable plain-text fields and vector fields (embeddings)**.

```text
                 ┌── full-text (BM25) ──► ranked list 1 ──┐
 one request ────┤                                         ├──► RRF ──► one fused list
                 └── vector (HNSW / eKNN) ► ranked list 2 ─┘
```

> Hybrid is **not** "run two separate searches and merge them in your code". It's **one request to one index**, merged by the service.

### 0.2 Why hybrid? (strengths and weaknesses)

| | **Keyword (BM25)** | **Vector** |
|---|---|---|
| Finds | Exact **terms** | **Conceptually similar** content, even with **no shared words** |
| Strong at | **Product codes, specialised jargon, dates, people's names**, exact phrases | Paraphrase, natural-language questions, cross-language and cross-modality matches |
| Weak at | Synonyms, rephrased questions, different vocabulary | **Exact identifiers** and rare tokens |

Hybrid combines **keyword precision** with **vector semantic recall**, so each method covers the other's blind spot. Microsoft's benchmark testing on real-world and benchmark datasets indicates that **hybrid retrieval with the semantic ranker** offers significant benefits in search relevance.

### 0.3 Anatomy of a hybrid query

```jsonc
POST /indexes/products/docs/search?api-version=...
{
  "search": "waterproof hiking jacket TX-9920-B",      // full-text part
  "vectorQueries": [                                    // vector part
    {
      "kind": "text",                  // let a vectorizer embed the text (or "vector" + your own vector)
      "text": "waterproof hiking jacket TX-9920-B",
      "fields": "contentVector",
      "k": 50                          // nearest neighbours returned by the vector query
    }
  ],
  "select": "title, description, category",
  "filter": "category eq 'jackets'",                    // optional metadata filter
  "queryType": "semantic",                              // optional: semantic reranking after RRF
  "semanticConfiguration": "my-semantic-config",
  "top": 10
}
```

Key facts:
- **`search` + `vectorQueries` together = hybrid.** `search` alone = keyword. `vectorQueries` alone = pure vector.
- The same text is usually used in both parts (verbatim for keyword, vectorised for the vector query), but the vector part may be a different representation.
- **`kind: "text"`** needs a **vectorizer** assigned to the vector field (the same model used for the indexed vectors). **`kind: "vector"`** means you supply the query vector yourself.
- Only **searchable** fields (or `searchFields`) are scored. Only **retrievable** fields (or `select`) are returned.
- Hybrid queries can use existing **text-based features**: **filtering, faceting, sorting, scoring profiles, and semantic ranking** on text fields, while running similarity search on vectors in the same request.
- **Permissions:** **Search Index Data Reader** is enough to query. Creating/updating an index needs **Search Index Data Contributor**.

### 0.4 Reciprocal Rank Fusion (RRF) (very high-yield)

RRF merges several **already-ranked** lists. It's used whenever **two or more queries run in parallel**, such as **hybrid queries** and **multiple vector queries**.

**How it works**
1. Each query returns a ranked list.
2. Each document gets a **reciprocal rank score** from each list it appears in:

$$\text{RRF score contribution} = \frac{1}{\text{rank} + k}$$

where $k$ is a constant (experiments show it performs best at a small value such as **60**). **This RRF constant is separate from the `k` in a vector query**, which controls how many nearest neighbours are returned.
3. The scores from every list are **summed** per document.
4. Documents are sorted by the combined score.

**What to remember**
- RRF works from **rank positions**, not raw scores, so **BM25 scores and cosine similarities don't need to be normalised** to the same scale.
- A document that appears **high in more than one list** is promoted. Appearing in **both** lists is a big advantage.
- Result: a **new `@search.score`** per document (the RRF score). Raw BM25/cosine scores are not what the final score represents.

**Worked example (k = 60)**

| Document | Keyword rank | Vector rank | Calculation | RRF score |
|---|---|---|---|---|
| X | 1 | not present | 1/61 | **0.0164** |
| Y | 5 | 5 | 1/65 + 1/65 | **0.0308** |

Y outranks X even though X was **#1 in one list**, because Y appears in **both** lists.

### 0.5 Weights

- **Vector queries can carry a weight** to give them more or less influence in the fused ranking (for example, favour a `titleVector` query over a `descriptionVector` query).
- Use weights to tune the **balance** between text and vector contributions, or among several vector queries.
- Multiple vector queries are **also merged by RRF**, even without a text query.

### 0.6 Hybrid + semantic ranker (the recommended stack)

```text
L1 RETRIEVAL (recall)             L2 RERANKING (precision)           GENERATION
 keyword (BM25) ┐
                ├─ RRF fusion ─►  semantic ranker  ─► top results ─►  LLM (RAG)
 vector (k-NN)  ┘                 (+ captions/answers)
```

- Microsoft's relevance guidance names **two main strategies**: **hybrid search with semantic ranker**, and **agentic retrieval** (LLM query planning).
- **Semantic ranker runs after RRF** and reorders the merged results. It can't retrieve documents that neither query returned.
- A third-party setup guide adds specifics worth verifying against Microsoft Learn: the ranker reranks **only the top 50** merged results, returns a separate **reranker score** (0–4), and recommends setting the vector query `k` to about **50** when using the semantic ranker. (Microsoft's 2023 blog likewise describes L1 returning "typically on the order of 50" results to the next layer.)
- All the semantic-ranker rules still apply: real query terms are required, and **`orderBy` breaks it**.

### 0.7 Filters, sorting, scoring profiles

| Feature | Behaviour in hybrid |
|---|---|
| **Filter** (`filter`) | Applies to **non-vector, filterable fields**. Vector fields themselves aren't filterable. For selective filters, mind **`vectorFilterMode`** (preFilter = max recall, postFilter = false-negative risk) |
| **Sorting** (`orderBy`) | **Overrides relevance ranking**, so results won't be in RRF/semantic order. With semantic ranking it causes an **HTTP 400** |
| **Scoring profiles** | Boost by weighted fields, freshness, distance, magnitude or tags on **text-based scoring**. **No index rebuild** required to add/change one |
| **Facets** | Supported on text fields. Facet counts may depend on `countAndFacetMode` (preview) |

> Need "newest first" **and** relevance? Prefer a **freshness scoring profile** or a **date filter** over `orderBy`.

### 0.8 Controlling the inputs (preview features)

| Setting | Meaning | Notes |
|---|---|---|
| **`maxTextRecallSize`** *(preview)* | Max number of documents retrieved by the **text** part of a hybrid query before merging with vector results | Range **1–10,000**, default **1000**. Larger = can page through more results with `top`/`skip`, but **more resource use and higher latency** |
| **`countAndFacetMode`** *(preview)* | Whether counts and facets include **all matching documents** (`countAllResults`) or only those within the `maxTextRecallSize` window (`countRetrievableResults`) | Preview |
| **`k`** (on `vectorQueries`) | Nearest neighbours returned by that vector query | Not the RRF constant |
| **`top` / `skip`** | Paging through the fused results | |

Preview features have **no SLA** and aren't recommended for production.

### 0.9 Choosing the right retrieval method

| Situation | Best fit |
|---|---|
| Exact IDs only (invoice number, SKU lookup) | **Keyword** (hybrid works but isn't required) |
| Pure concept/semantic similarity, no exact-token needs (for example, image-to-image) | **Vector** |
| Mixed: exact tokens **and** natural-language meaning | **Hybrid** |
| Best general-purpose RAG retrieval | **Hybrid + semantic ranker** |
| Complex multi-part, conversational questions | **Agentic retrieval** (LLM query planning) |
| Keep results in a fixed order (date, price) | Sorting, with the knowledge that it overrides relevance |

### 0.10 Common hybrid problems

| Symptom | Likely cause | Fix |
|---|---|---|
| Exact SKUs/codes not found | **Vector-only** query | Add the **`search`** (text) part, so hybrid |
| Paraphrased questions fail | **Keyword-only** query | Add **`vectorQueries`**, so hybrid |
| Results appear in date/price order, not by relevance | **`orderBy`** overriding scores | Remove it. Use a scoring profile or filter |
| HTTP 400 when adding semantic ranking | **`orderBy`** present | Remove sorting |
| Query text not converted to a vector | No **vectorizer** or wrong model | Add a vectorizer (same model as indexed vectors) or use `kind: vector` |
| Poor relevance after changing embedding model | Query/index vector mismatch | Re-embed and re-index with one model |
| Can't page deep into text matches | `maxTextRecallSize` default window | Increase it (preview), accept latency |
| Correct doc never appears | Not retrieved by **either** list | Fix retrieval: chunking, `k`, filters, analyzers |
| Top results still not ideal | Ordering issue | Add **semantic ranker** |
| Multi-part questions answered partially | Single-query limit | **Agentic retrieval** |
| Developer wants to normalise BM25 and cosine scores | Misunderstanding | Not needed. RRF uses ranks |
| Filter returns too few results | Selective filter with postFilter on the vector part | **preFilter** / larger `k` |

### 0.11 Five ideas the exam really tests

1. **Hybrid = one request with `search` + `vectorQueries`**, run in parallel, merged by **RRF**.
2. **RRF uses ranks (1/(rank + k)), not raw scores**, so no score normalisation is needed. Appearing in both lists boosts a document.
3. **Keyword = exact terms (codes, names, dates, jargon). Vector = meaning. Hybrid = both.**
4. **Best-practice stack: hybrid retrieval (recall) + semantic ranker (precision).** `orderBy` breaks it.
5. **Hybrid needs an index with both searchable text and vector fields**, and (for text-to-vector at query time) a **vectorizer** using the same model as the indexed vectors.

---

## 1. Scenario Questions

### Question 1: Which method?

A parts catalogue gets queries like **"TX-9920-B"**, **"why does my jacket leak at the seams"**, and **"E-4471 error on the washer"**. A **vector-only** index returns loosely related items for the codes, while a previous **keyword-only** index missed the paraphrased question. What is the BEST solution?

A. Increase `k` on the vector query  
B. **Hybrid search**: send `search` and `vectorQueries` together and let RRF merge the results  
C. Return to keyword-only  
D. Increase `efSearch`

<details>
<summary>Answer</summary>

### ✅ B

Keyword matches the exact codes, vectors capture the paraphrased meaning. Hybrid combines them in a single request.

- **A, D ❌** Tune vector recall only. They don't give exact-token matching.
- **C ❌** Regresses on paraphrases.
</details>

---

### Question 2: Which request is hybrid? (snippets)

**Request 1**
```json
{ "search": "waterproof hiking jacket" }
```

**Request 2**
```json
{ "vectorQueries": [ { "kind": "text", "text": "waterproof hiking jacket",
                       "fields": "contentVector", "k": 10 } ] }
```

**Request 3**
```json
{ "search": "waterproof hiking jacket",
  "vectorQueries": [ { "kind": "text", "text": "waterproof hiking jacket",
                       "fields": "contentVector", "k": 10 } ] }
```

Which statement is correct?

A. Request 1 is hybrid  
B. Request 2 is hybrid  
C. **Request 3 is hybrid. It has both `search` and `vectorQueries`, runs them in parallel, and merges with RRF**  
D. None of them, because hybrid needs two API calls

<details>
<summary>Answer</summary>

### ✅ C

Hybrid is a single request containing both parameters. Request 1 is keyword-only. Request 2 is pure vector.

**Trap:** Hybrid is not two calls merged in your application code.
</details>

---

### Question 3: RRF calculation

With an RRF constant of **k = 60**, two documents appear in the ranked lists as follows:

- **Doc X:** rank **1** in the keyword list, **absent** from the vector list.
- **Doc Y:** rank **5** in the keyword list and rank **5** in the vector list.

$$\text{score} = \sum \frac{1}{\text{rank} + 60}$$

Which document ranks higher in the fused result?

A. Doc X, because it was ranked #1 in a list  
B. **Doc Y**: $\frac{1}{65}+\frac{1}{65}\approx 0.0308$ vs $\frac{1}{61}\approx 0.0164$  
C. They tie  
D. Neither, because RRF discards documents not in both lists

<details>
<summary>Answer</summary>

### ✅ B

RRF rewards documents that appear in **multiple lists**. Two moderate ranks add up to more than one top rank.

- **D ❌** RRF keeps documents from either list. Documents in both simply score higher.
</details>

---

### Question 4: Score normalisation (Select TWO)

A developer proposes writing code to **normalise BM25 scores and cosine similarity scores to a common 0–1 scale** before merging the keyword and vector results. Which TWO statements are correct?

A. RRF merges using **rank positions**, so the different score scales don't need to be normalised  
B. The final `@search.score` in a hybrid result is the **RRF score**, not the raw BM25 or cosine value  
C. BM25 and cosine scores must be normalised or hybrid will fail  
D. Hybrid search can only work if both lists use the same scoring function  
E. RRF discards rank information

<details>
<summary>Answer</summary>

### ✅ A and B

RRF turns each list's **positions** into reciprocal-rank scores and sums them. The score scales of BM25 and vector similarity are irrelevant to the merge.
</details>

---

### Question 5: Two different k values

A query contains `"k": 50` inside `vectorQueries`. A colleague says "that's the RRF constant and should be 60". What is the correct explanation?

A. They're the same value  
B. **The `k` in `vectorQueries` is the number of nearest neighbours to return. The RRF constant (commonly 60) is a separate internal constant**  
C. `k` controls how many text results are returned  
D. The RRF constant must equal `k`

<details>
<summary>Answer</summary>

### ✅ B

The documentation explicitly says the RRF constant is entirely separate from the `k` that controls the number of nearest neighbours.
</details>

---

### Question 6: Results in the wrong order

A hybrid query with semantic ranking returns results sorted by **last-updated date**, ignoring relevance. The request includes `"orderby": "lastUpdated desc"`. Users want **relevant** results, with newer content preferred. What is the BEST approach?

A. Keep `orderby` and increase `k`  
B. **Remove `orderby`**, and boost freshness with a **scoring profile** (or restrict with a date **filter**)  
C. Use only the vector query  
D. Disable the semantic configuration

<details>
<summary>Answer</summary>

### ✅ B

`orderBy` overrides RRF and semantic scores (and causes HTTP 400 with semantic ranking in the documented cases). Scoring profiles boost by freshness without replacing relevance ranking, and they can be changed without rebuilding the index.
</details>

---

### Question 7: Pipeline order (drag-and-drop)

Put the stages of a **hybrid + semantic + RAG** pipeline in the correct order:

**a)** LLM generates a grounded answer  
**b)** Semantic ranker reranks the fused results  
**c)** RRF merges the keyword and vector ranked lists  
**d)** BM25 keyword query and vector query run in parallel

<details>
<summary>Answer</summary>

### ✅ d → c → b → a

Parallel retrieval (d), RRF fusion (c), semantic reranking (b), generation (a).

Memory line: **Retrieve → Fuse → Rerank → Generate.**
</details>

---

### Question 8: Weighting vector queries

An index has `titleVector` and `descriptionVector`, both embedded with the same model. Titles are far more reliable than descriptions. The team wants the title match to count more. Which TWO statements are correct?

A. Run **two vector queries** (one per field)  
B. Apply a higher **weight** to the title vector query so it has more influence on the fused ranking  
C. Merge the two fields into a single filterable vector field  
D. Multiple vector queries can't be combined  
E. Increase `efSearch` to 1000

<details>
<summary>Answer</summary>

### ✅ A and B

Multiple vector queries are merged by RRF, and weights adjust each query's influence.

- **C ❌** Vector fields aren't filterable and merging doesn't express weighting.
- **D ❌** RRF is designed for exactly this.
- **E ❌** Tunes recall/latency, not importance.
</details>

---

### Question 9: Text in, least privilege (Select TWO)

A web app accepts typed queries and must run **hybrid** searches, with the service embedding the query text, using **least privilege**. Which TWO actions are correct?

A. Assign a **vectorizer** (same model as the indexed vectors) to the vector field and use `kind: "text"` in `vectorQueries`  
B. Grant the app's identity **Search Index Data Reader**  
C. Grant **Search Index Data Contributor** to every user  
D. Put an admin key in client-side JavaScript  
E. Use a different embedding model for queries to improve variety

<details>
<summary>Answer</summary>

### ✅ A and B

The vectorizer handles text-to-vector at query time, and Data Reader is the query-only role.

- **C ❌** Write access isn't needed to query.
- **D ❌** Insecure.
- **E ❌** Query and index vectors must come from the same model.
</details>

---

### Question 10: Deeper paging (preview)

A hybrid search page needs users to **page through several thousand** text matches. By default, the text portion contributes only a limited window of documents to the merge. Which setting should the team evaluate, and what is the trade-off?

A. Lower `k` to 1  
B. Increase **`maxTextRecallSize`** (preview; default 1000, up to 10,000). Larger values allow paging through more documents but **cost more resources and add latency**. Preview features have no SLA  
C. Switch to `orderBy`  
D. Increase RRF's constant

<details>
<summary>Answer</summary>

### ✅ B

`maxTextRecallSize` caps the number of documents retrieved by the text query part of a hybrid query before merging with vector results.
</details>

---

### Question 11: When hybrid isn't needed (Select TWO)

Which TWO scenarios are **best served WITHOUT** hybrid search?

A. Looking up a customer record by exact **invoice number** only  
B. **Image-to-image** similarity over product photos using multimodal embeddings (no text component)  
C. A help center where users mix part numbers and natural-language questions  
D. A RAG assistant over policy documents with jargon and paraphrased questions  
E. Searching legal text by both exact case numbers and conceptual descriptions

<details>
<summary>Answer</summary>

### ✅ A and B

- **A ✅** Exact-token lookup is a keyword job.
- **B ✅** Pure similarity over vectors, with no text query to combine.
- **C, D, E ❌** Mixed exact + meaning needs. These are hybrid use cases.
</details>

---

### Question 12: Selective filter in a hybrid query

A multi-tenant app adds `filter: tenantId eq 'contoso'` (about 0.05% of documents) to a hybrid query with `k: 5`. Users sometimes see far fewer vector-based matches than expected. What should the team review?

A. Make the vector field filterable  
B. The **`vectorFilterMode`**. For highly selective filters, **preFilter** maximises recall (postFilter can cause false negatives with small `k`), and consider a larger `k`  
C. Remove the text part of the query  
D. Increase RRF's constant

<details>
<summary>Answer</summary>

### ✅ B

Filters apply to non-vector filterable fields (here, `tenantId`). The vector side's filter behaviour is controlled by the filter mode. Never rely on prompts for tenant isolation.
</details>

---

### Question 13: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | A hybrid query is a single request containing both `search` and `vectorQueries`. | |
| 2 | RRF merges results using the rank positions from each list. | |
| 3 | BM25 and vector scores must be normalised before hybrid search can merge them. | |
| 4 | A document appearing in both the keyword and vector lists is favoured by RRF. | |
| 5 | Multiple vector queries can also be merged by RRF. | |
| 6 | Semantic ranking is applied before RRF merges the lists. | |
| 7 | `orderBy` preserves hybrid relevance order. | |
| 8 | Keyword search is generally better than vector search for product codes and people's names. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **Yes** | Definition of hybrid. |
| 2 | **Yes** | $1/(\text{rank}+k)$ per list. |
| 3 | **No** | Ranks, not raw scores. |
| 4 | **Yes** | Scores from each list are summed. |
| 5 | **Yes** | RRF is used when two or more queries run in parallel. |
| 6 | **No** | Semantic ranking runs **after** RRF, on the merged results. |
| 7 | **No** | It overrides relevance scoring. |
| 8 | **Yes** | Exact-match strength of keyword search. |
</details>

---

### Question 14: Match the need to the feature (drag-and-drop)

Match each need to: **Hybrid search · RRF · Vector weight · Semantic ranker · Scoring profile · Filter · `maxTextRecallSize` · Agentic retrieval · Vectorizer**.

| Need | Feature |
|---|---|
| A. Combine keyword precision and vector recall in one request | ? |
| B. Merge two ranked lists into one by reciprocal rank | ? |
| C. Make one vector query count more than another | ? |
| D. Improve ordering of the top fused results by reading query and passage | ? |
| E. Boost newer documents without replacing relevance ranking | ? |
| F. Restrict results to one tenant's metadata | ? |
| G. Control how many text matches feed the merge (preview) | ? |
| H. Decompose a complex question into parallel subqueries | ? |
| I. Convert the text query into a vector at query time | ? |

<details>
<summary>Answer</summary>

| Need | Feature |
|---|---|
| A | **Hybrid search** |
| B | **RRF** |
| C | **Vector weight** |
| D | **Semantic ranker** |
| E | **Scoring profile** |
| F | **Filter** |
| G | **`maxTextRecallSize`** |
| H | **Agentic retrieval** |
| I | **Vectorizer** |
</details>

---

### Question 15: Hybrid or agentic?

Users ask: *"Compare coverage for flood damage between the Gold and Silver plans and give me the claim deadline for each."* A well-tuned **hybrid + semantic ranker** query still returns partial matches for such multi-part questions. Which approach fits BEST?

A. Increase `top`  
B. **Agentic retrieval**: LLM-based query planning decomposes the question into subqueries, runs them in parallel, and merges the reranked results (accepting extra latency; some capabilities were preview)  
C. Remove the text query  
D. Use `orderBy`

<details>
<summary>Answer</summary>

### ✅ B

Microsoft names hybrid + semantic ranker and agentic retrieval as the two main relevance strategies. Agentic retrieval targets complex, context-dependent questions.
</details>

---

## 2. Mini Case Study: Wingtip Toys Marketplace

### Background

Wingtip Toys runs product search and a RAG shopping assistant on Azure AI Search and Microsoft Foundry.

1. Shoppers search by **SKU** ("WT-2290-C") and by **natural language** ("a quiet toy for a 3-year-old on a plane").
2. Search is currently **vector-only**. SKU searches return loosely related toys.
3. Leadership wants the **best out-of-the-box relevance** for the assistant's retrieval step.
4. The index has `titleVector` and `descriptionVector` (same model). Titles are more reliable.
5. A developer added `orderby=releaseDate desc` to show new toys first. Relevance quality collapsed, and adding the semantic ranker now throws **HTTP 400**.
6. Another developer plans to write code that **normalises BM25 and cosine scores** before merging.
7. One page needs to **page through up to 5,000 text matches**.
8. For multi-part chat questions, the team still sees partial answers.
9. The app must embed typed queries **server-side**, with **least-privilege** access.

### Case Q1: Fix SKU searches (requirements 1–2)

A. Increase `efSearch`  
B. **Hybrid search** (`search` + `vectorQueries`)  
C. Switch to euclidean  
D. Binary quantization

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q2: Best relevance for the assistant

A. Vector-only with a larger `k`  
B. **Hybrid retrieval + semantic ranker**  
C. Keyword-only  
D. Random ranking

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q3: Titles matter more

A. Merge the two fields into one  
B. **Two vector queries with a higher weight on the title query** (merged by RRF)  
C. Make vector fields filterable  
D. Lower `dimensions`

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q4: New toys first, and the 400 error

Which TWO changes fix requirement 5?

A. **Remove `orderby`**  
B. Boost recent releases with a **freshness scoring profile** (or filter by release window)  
C. Add more vector fields  
D. Increase `k`

<details><summary>Answer</summary>

### ✅ A and B

`orderBy` overrides relevance and conflicts with semantic ranking. A scoring profile boosts freshness while keeping relevance.
</details>

### Case Q5: The normalisation plan

A. Proceed, because normalisation is required  
B. **Skip it.** RRF merges by rank, so score scales don't matter  
C. Normalise only the vector scores  
D. Replace RRF with a custom merge

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q6: Deep paging

A. Lower `k`  
B. **Increase `maxTextRecallSize`** (preview, default 1000, max 10,000), accepting extra latency and no SLA  
C. Use `orderBy`  
D. Remove semantic ranking

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q7: Multi-part chat questions

A. More captions  
B. **Agentic retrieval** with LLM query planning  
C. Keyword-only  
D. Disable RRF

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q8: Server-side query embedding with least privilege

Which TWO?

A. **Vectorizer** on the vector fields (same model as the indexed vectors) with `kind: "text"`  
B. **Search Index Data Reader** for the app identity  
C. Search Index Data Contributor for the app  
D. Admin key in the browser

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q9: Map the requirement to the solution

| Requirement | Solution |
|---|---|
| SKU + natural-language queries | ? |
| Best relevance for RAG | ? |
| Title more important | ? |
| New toys first without losing relevance | ? |
| Normalise scores? | ? |
| 5,000-match paging | ? |
| Multi-part questions | ? |
| Query embedding + least privilege | ? |

<details><summary>Answer</summary>

| Requirement | Solution |
|---|---|
| SKU + natural-language queries | Hybrid search |
| Best relevance for RAG | Hybrid + semantic ranker |
| Title more important | Weighted vector queries |
| New toys first without losing relevance | Remove `orderby`, use a freshness scoring profile/filter |
| Normalise scores? | No. RRF uses ranks |
| 5,000-match paging | `maxTextRecallSize` (preview) |
| Multi-part questions | Agentic retrieval |
| Query embedding + least privilege | Vectorizer + Search Index Data Reader |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Two-calls trap** | "Hybrid means merging two searches in my code." | One request with `search` + `vectorQueries`, merged by RRF. |
| **Normalisation trap** | "Normalise BM25 and cosine first." | RRF uses **rank positions**. No normalisation needed. |
| **Two-k trap** | "`k` is the RRF constant." | `k` in `vectorQueries` = nearest neighbours. The RRF constant (about 60) is separate. |
| **Top-rank trap** | "Rank #1 in one list always wins." | Appearing in **both** lists can outscore a single #1. |
| **Sorting trap** | "Add `orderBy` for recency." | It overrides relevance (and breaks semantic ranking). Use scoring profile/filter. |
| **Order-of-stages trap** | "Semantic ranker runs before RRF." | RRF first, then semantic ranker on the merged list. |
| **Semantic-replaces trap** | "Semantic ranker replaces hybrid." | Hybrid retrieves (recall). Semantic ranker reorders (precision). |
| **Recall trap** | "Semantic ranker will find what neither list returned." | It only reranks candidates. |
| **Hybrid-always trap** | "Always use hybrid." | Exact-ID-only lookups → keyword. Pure similarity → vector. |
| **Model trap** | "Use a different model for queries." | Same embedding model as the index. |
| **Privilege trap** | "Contributor role for querying." | **Search Index Data Reader** is enough. |
| **Vector-filter trap** | "Filter on the vector field." | Not filterable. Filter metadata fields. |
| **Preview trap** | "`maxTextRecallSize`/`countAndFacetMode` are production-ready." | Preview, no SLA. |
| **Complex-question trap** | "Hybrid solves every question." | Multi-part questions → agentic retrieval. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| Exact codes **and** natural language | **Hybrid** |
| Exact-token lookup only | Keyword |
| Pure semantic/multimodal similarity | Vector |
| Best general RAG retrieval | **Hybrid + semantic ranker** |
| Merge lists from parallel queries | **RRF** |
| Favour one vector query | **Vector weight** |
| Several vector fields | Multiple vector queries (merged by RRF) |
| Newer content preferred | **Scoring profile** (freshness) or filter |
| Fixed sort order needed | `orderBy`, but it overrides relevance |
| HTTP 400 with semantic ranking | Remove `orderBy` |
| Text-to-vector at query time | **Vectorizer** + `kind: "text"` |
| Query-only access | **Search Index Data Reader** |
| Deeper text paging (preview) | `maxTextRecallSize` |
| Selective metadata filter | `filter` + preFilter consideration |
| Complex multi-part questions | **Agentic retrieval** |
| Correct doc never appears | Fix retrieval (chunking, `k`, filters), not the ranker |

---

## 5. Quick Revision Sheet

```text
HYBRID = ONE request: "search" (text) + "vectorQueries" (vector)
         runs in PARALLEL on ONE index, merged by RRF into ONE list
KEYWORD (BM25) = exact terms: codes, jargon, dates, names
VECTOR         = meaning: paraphrase, concepts, cross-language/modal
HYBRID         = both

RRF   score = sum over lists of 1 / (rank + k)     (k ~ 60, separate from vector-query k)
      RANK-based -> NO score normalisation | in BOTH lists = boosted
      used for hybrid AND multiple vector queries | final @search.score = RRF score

WEIGHTS: vector queries can be weighted
STACK:   [BM25 + vector] -> RRF -> semantic ranker -> LLM        (Retrieve -> Fuse -> Rerank -> Generate)
         semantic ranker reorders only; real terms required; orderBy breaks it
FILTERS: non-vector filterable fields; mind vectorFilterMode for selective filters
SORT:    orderBy overrides relevance -> prefer scoring profile / filter
PREVIEW: maxTextRecallSize (1-10,000, default 1000), countAndFacetMode
ACCESS:  Search Index Data Reader to query; vectorizer (same model) for kind:"text"
ALTERNATIVE: complex multi-part questions -> agentic retrieval
```

### Best-answer checklist

1. Does the workload need **exact tokens AND meaning**? Hybrid.
2. Only one of the two? Choose keyword or vector.
3. Relevance poor at the top but the right doc is retrieved? Add the **semantic ranker**.
4. Right doc never retrieved? Fix **retrieval**, not ranking.
5. Do you see `orderBy`? It probably breaks relevance or semantic ranking.
6. Tempted to normalise scores? **No**, RRF is rank-based.
7. Multi-part conversational questions? **Agentic retrieval**.
8. Option mentions a **preview** feature? Flag no SLA.

---

**Next concept:** Azure AI Search (same harder exam-style format)

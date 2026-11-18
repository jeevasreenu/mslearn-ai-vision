# AI-103: Vector Search (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, config/query snippets, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Scope: **vector search in Azure AI Search (Foundry IQ)**: algorithms, similarity metrics, vector fields/profiles, queries, filters, and storage optimisation. Semantic search and hybrid search each get their own file next.
> Property defaults and ranges come from Microsoft docs and secondary sources, and they change. The exam tests **which option fits which constraint**, not memorised numbers.

---

## 0. Core Concepts (read first)

### 0.1 What is vector search?

Vector search indexes and queries **numeric representations (embeddings)** of content. It matches the **query vector** to the **most similar stored vectors**, so it finds results by **meaning**, not shared words.

It can match across:
- **Conceptual likeness:** "dog" ≈ "canine".
- **Languages:** "dog" ≈ "hund" (with a multilingual model).
- **Content types:** the word "dog" ≈ a picture of a dog (with a multimodal model).

Scenarios Azure AI Search supports: **similarity search, hybrid search, multimodal search, multilingual search, filtered vector search**, and use as a **vector database** (it stores the data you query).

> **Vector search needs vectors.** Either you supply them, or you generate them in an indexer pipeline (integrated vectorization). A vector field **does not create embeddings for you**.

### 0.2 The vector index building blocks

| Piece | Purpose |
|---|---|
| **Vector field** | Field of type `Collection(Edm.Single)` (float32). `float16` and narrower types are supported. Has a fixed **`dimensions`** value and a **`vectorSearchProfile`** |
| **`vectorSearch` section** | Index configuration containing algorithms, profiles, compressions, and vectorizers |
| **Algorithm configuration** | `hnsw` or `exhaustiveKnn`, with parameters and a similarity **metric** |
| **Vector profile** | Named combination that a field uses: **algorithm + (optional) vectorizer + (optional) compression** |
| **Compression** | Scalar or binary quantization settings (optional) |
| **Vectorizer** | Converts query text/images to vectors at query time (must match the indexing model) |

Other facts:
- Only vector fields marked **searchable** in the index (or listed in `searchFields` in the query) are searched and scored.
- **Vector fields aren't filterable.** Filter on other (non-vector) filterable text/numeric fields.
- Keep **text fields as well as vector fields**. Vectors can't be converted back to text.

### 0.3 The two search algorithms

| | **Exhaustive KNN** | **HNSW (ANN)** |
|---|---|---|
| Method | **Brute-force** scan of the whole vector space | **Hierarchical Navigable Small World** graph, an **approximate** nearest-neighbour search |
| Result | **Exact** k nearest neighbours | **Approximate**, high recall, low latency |
| Speed | Slow (computationally intensive) | Fast |
| Memory | Loads data in chunks at query time. **Doesn't consume vector index size quota** | Needs the graph and **all vectors in memory**. **Consumes vector index size quota** |
| Best for | **Small-to-medium datasets**, or when **precision matters more than latency**, or to build a **ground-truth set to measure ANN recall** | **Most scenarios**, especially **larger datasets** and **high-recall, low-latency** apps |
| Note | | HNSW fields can **also** run exhaustive KNN per query by sending `"exhaustive": true` |

> **ANN = approximate.** It can occasionally miss a true nearest neighbour in exchange for speed. Tune recall vs latency with the HNSW parameters below.

### 0.4 HNSW parameters (what they trade off)

| Parameter | Meaning | Effect of increasing | Default / range (per secondary source) |
|---|---|---|---|
| **`m`** | Bi-directional links per node in the graph | Denser graph, more memory | 4 (4–10) |
| **`efConstruction`** | Candidates considered **while building** the index | Better graph/recall, **slower indexing** | 400 (100–1000) |
| **`efSearch`** | Candidates considered **while querying** | **Higher recall, higher latency** | 500 (100–1000) |
| **`metric`** | Similarity function | n/a | cosine, dotProduct, euclidean, hamming |

> Exam logic: **more candidates (ef\*) → better recall but slower**. Tune from a **baseline you measure**, with exhaustive KNN as the recall ground truth.

### 0.5 Similarity metrics

| Metric | Measures | Use |
|---|---|---|
| **cosine** | Angle between vectors (direction) | Common default for text embeddings |
| **dotProduct** | Magnitude + direction | Same ranking as cosine when vectors are **normalised** |
| **euclidean** | Straight-line distance | Less common for text |
| **hamming** | Differing bits | **Binary** vectors |

> **Use the metric the embedding model was trained for** (check the model documentation).

### 0.6 Running a vector query

```jsonc
POST /indexes/docs/docs/search?api-version=...
{
  "count": true,
  "select": "title, content, category",
  "vectorQueries": [
    {
      "kind": "vector",            // you supply the query vector
      "vector": [0.012, -0.034, ...],
      "fields": "contentVector",   // the vector field to search
      "k": 5                       // nearest neighbours to return
    }
  ]
}
```

Key points:
- **`kind: "vector"`** = you pass a precomputed vector. **`kind: "text"`** = pass text and let the index's **vectorizer** embed it (integrated vectorization).
- **Query vectors must come from the same embedding model** (same model/version/dimensions) as the stored vectors.
- **`fields`** names which vector field(s) to search. You can query **multiple vector fields** and run **multiple vector queries**, with **weights** to favour some queries.
- **`k`** controls how many nearest neighbours the vector query returns.
- **Thresholds** to drop low-scoring results exist as a **preview** feature.
- A vector query can **combine with a text query** (that's hybrid search, covered next).

### 0.7 Filtering vector queries (pre vs post)

Add a `filter` on **filterable non-vector fields** (for example, category, date, tenant) and set `vectorFilterMode`:

| Mode | When the filter applies | Strength | Risk |
|---|---|---|---|
| **preFilter** | **During HNSW traversal** on each shard | **Maximises recall** | More graph traversal, so more CPU and latency for **highly selective** filters |
| **postFilter** | Each shard runs HNSW and filters independently, then results are aggregated into a global top k | Faster for permissive filters | **False negatives** for highly selective filters or small `k` |
| **strictPostFilter** *(preview)* | **After** the global unfiltered top k is found | Strict "filter the global top k" semantics | **Highest** false-negative risk for selective filters/small k. Preview, no SLA |

> Trap: **"filter ≠ free"**. If a selective filter plus postfilter returns **too few or empty results**, switch to **preFilter** (or raise `k`).

### 0.8 Reducing vector size and cost

Vector indexes sit **in memory (HNSW)**, so size drives **partition count and cost**.

| Technique | What it does | Trade-off |
|---|---|---|
| **Scalar quantization** | float32/float16 → **int8**, about **4× smaller** | Small information loss |
| **Binary quantization** | float → **1 bit**, up to about **28×** smaller (96% index reduction in Microsoft tests) | Bigger recall loss, **mitigate with oversampling + rescoring** |
| **Oversampling + rescoring** | Retrieve **more candidates** from the compressed index, then **rescore using original (uncompressed) vectors** | Extra work per query, recovers quality. **Built-in quantization only** (not custom quantization) |
| **Truncate dimensions (MRL)** | Use fewer dimensions on **`text-embedding-3`** models | Small quality loss, applies at embedding time (index and query must match) |
| **Narrow data types** (`float16`, `int8`, `byte`) | Store vectors in smaller types | Needs **custom** quantization effort. `float16` is easy |
| **`stored: false`** | Don't keep the **retrievable** copy of the vector, saving **disk** | Saves disk only. **Doesn't shrink the in-memory index** |

Microsoft **recommends built-in quantization** as the first choice for most scenarios. These approaches **can be combined**.

### 0.9 Common vector search problems

| Symptom | Likely cause | Fix |
|---|---|---|
| Irrelevant results after changing models | Query and index vectors from **different models** | Same model for both. Re-embed and re-index |
| **Dimension mismatch** error | Field `dimensions` ≠ vector length | Match the field and model (or set `dimensions` on 3-series models) |
| Exact IDs/error codes missed | Vector-only retrieval | **Hybrid** (keyword + vector) |
| Slow queries on a huge index | Using exhaustive KNN | Use **HNSW** |
| Missing true neighbours (ANN) | Low `efSearch`/`k` or approximate nature | Raise `efSearch`/`k`, or check against exhaustive KNN |
| Filter returns too few/no results | **postFilter** on a very selective filter | **preFilter**, or increase `k` |
| Cost/memory too high | Large float32 vectors | **Quantization**, MRL truncation, `float16` |
| Quality drop after binary quantization | Lossy compression | **Oversampling + rescoring**, keep original vectors |
| Query can't be vectorised from text | No vectorizer, or wrong model | Add a **vectorizer** (same model), or compute query vectors client-side |
| Can't filter on the vector field | Vector fields aren't filterable | Filter on **other** fields |

### 0.10 Five ideas the exam really tests

1. **HNSW = approximate, fast, in memory. Exhaustive KNN = exact, slow, no vector-index quota.**
2. **Same embedding model (and dimensions) at index and query time.**
3. **Vector fields aren't filterable.** Use metadata fields with **preFilter** (max recall) vs **postFilter** (false-negative risk).
4. **Quantization (scalar ≈ 4×, binary up to ≈ 28×) plus oversampling/rescoring** is the recommended cost lever.
5. **Vector search finds meaning but is weak on exact tokens**, so hybrid search is the fix.

---

## 1. Scenario Questions

### Question 1: Pick the algorithm

A product-search service has **40 million vectors**, needs **low-latency queries**, and accepts that results may occasionally miss a true nearest neighbour. Which algorithm configuration fits BEST?

A. Exhaustive KNN  
B. **HNSW** (approximate nearest neighbour)  
C. No algorithm: vector fields don't need one  
D. A keyword analyzer

<details>
<summary>Answer</summary>

### ✅ B

HNSW is optimised for high-recall, low-latency searches over larger datasets, and it's an approximate algorithm.

- **A ❌** Brute-force scanning is too slow at this scale.
- **C ❌** A vector field's profile references an algorithm.
- **D ❌** Analyzers are for text fields.
</details>

---

### Question 2: When exhaustive KNN is right

A legal-discovery tool searches a **30,000-chunk** index. Reviewers need the **exact** nearest neighbours (no approximation), and query latency of a second or two is acceptable. The team also wants to **measure the recall of their HNSW index** on another dataset. Which TWO statements are correct?

A. Exhaustive KNN returns the **exact** k nearest neighbours and suits small-to-medium datasets or precision-first needs  
B. Exhaustive KNN results can serve as the **ground-truth set** to evaluate an ANN algorithm's recall  
C. Exhaustive KNN always uses less latency than HNSW  
D. Exhaustive KNN consumes more vector index size quota than HNSW  
E. Exhaustive KNN can't be used on HNSW-configured fields

<details>
<summary>Answer</summary>

### ✅ A and B

- **C ❌** It's the slower, brute-force method.
- **D ❌** It **doesn't** consume vector index size quota. HNSW does.
- **E ❌** Fields configured for HNSW can also run exhaustive KNN per query with `"exhaustive": true`.
</details>

---

### Question 3: Config snippet, dimension mismatch

```json
{
  "fields": [
    { "name": "contentVector", "type": "Collection(Edm.Single)",
      "dimensions": 1536, "vectorSearchProfile": "hnsw-profile",
      "searchable": true }
  ],
  "embedding_pipeline": "text-embedding-3-large (default dimensions)",
  "error": "Document upload failed: vector length 3072 does not match field dimensions 1536"
}
```

Which TWO fixes would resolve this?

A. Recreate the field with **3072** dimensions and re-index  
B. Generate embeddings with **`dimensions: 1536`** (supported on `text-embedding-3` models) and use the same setting for queries  
C. Increase `efSearch`  
D. Change the metric to hamming  
E. Make the field filterable

<details>
<summary>Answer</summary>

### ✅ A and B

The field's `dimensions` must equal the vector length. Either enlarge the field, or shorten the embeddings. Keep the same setting for index and query vectors.

- **C, D, E ❌** Unrelated to dimension length.
</details>

---

### Question 4: Wrong results after an "upgrade"

A team re-embeds **only new documents** with a newer embedding model (same dimensions) while old documents keep the previous model's vectors. Queries use the newer model. Search quality drops sharply. What is the BEST fix?

A. Increase `k`  
B. **Re-embed all documents with the same model used for queries** (one consistent embedding space), then re-index  
C. Switch to euclidean  
D. Add more replicas

<details>
<summary>Answer</summary>

### ✅ B

Vectors from different models aren't comparable, even when the dimension counts match. One index needs one embedding space.
</details>

---

### Question 5: Filter returns almost nothing

A multi-tenant RAG app adds `filter: tenantId eq 'contoso'` (about 0.1% of documents) with **`vectorFilterMode: postFilter`** and `k: 5`. Many queries return **zero or very few results**, although relevant Contoso chunks exist. What is the MOST likely explanation and fix?

A. The vector field must be made filterable  
B. **Post-filtering on a highly selective filter with small `k`** discards most candidates (false negatives). Use **`preFilter`** (and/or increase `k`)  
C. Lower temperature  
D. Remove the filter and trust the prompt

<details>
<summary>Answer</summary>

### ✅ B

PostFilter can return false negatives for highly selective filters or small k. PreFilter applies the filter during HNSW traversal and maximises recall, at the cost of more CPU/latency for very selective filters.

- **A ❌** Vector fields aren't filterable. The filter is on `tenantId`, a regular field.
- **C ❌** Irrelevant.
- **D ❌** A security failure. Never rely on prompts for tenant isolation.

**Trap:** The numbers (0.1% selectivity, `k: 5`) are the clue.
</details>

---

### Question 6: Filtering the vector field itself

A developer tries to add `filter: contentVector eq ...` to restrict results to vectors above a numeric range. The request is rejected. What is the correct guidance?

A. Vector fields **aren't filterable**. Filter on **other filterable text/numeric metadata fields** in the same index  
B. Increase `dimensions`  
C. Switch to exhaustive KNN  
D. Use `kind: text`

<details>
<summary>Answer</summary>

### ✅ A

Use metadata fields (for example, category, date, `LastModified`) for filtering.
</details>

---

### Question 7: Query kind (snippet)

```json
{
  "vectorQueries": [
    { "kind": "text", "text": "how do I reset my password", "fields": "contentVector", "k": 5 }
  ]
}
```

What does this query require in the index?

A. A **vectorizer** configured in the vector profile/index so the service can convert the query text to a vector using the **same model** as the indexed vectors  
B. A semantic ranker only  
C. No configuration. Text is matched by keyword on vector fields  
D. A scoring profile

<details>
<summary>Answer</summary>

### ✅ A

`kind: "text"` relies on integrated vectorization (a vectorizer). With `kind: "vector"` you supply the vector yourself.
</details>

---

### Question 8: Cost at scale

A search service holds **500 million float32 vectors** (HNSW). Memory and partition costs are too high. The team wants the **largest practical storage reduction**, while recovering most of the lost relevance. Which approach fits BEST?

A. Delete the HNSW algorithm and use keyword search  
B. Enable **binary quantization** (or scalar for a milder cut) with **oversampling and rescoring** against the original vectors  
C. Increase `efSearch` to 1000  
D. Add more dimensions

<details>
<summary>Answer</summary>

### ✅ B

Quantization shrinks both memory and disk. Binary can give up to about 28× index size reduction, and oversampling plus rescoring compensates for the lossy compression. Microsoft recommends built-in quantization as the first approach.

- **C ❌** Raises recall and latency but increases cost, not reduces it.
- **D ❌** Larger vectors cost more.
</details>

---

### Question 9: `stored: false` misconception

A team sets **`stored: false`** on a vector field expecting the **in-memory HNSW index** to shrink dramatically. Memory use barely changes. Why?

A. `stored: false` only saves **disk** by not keeping the retrievable copy of the vector. It **doesn't reduce the in-memory index** used for search  
B. `stored: false` deletes the algorithm  
C. It doubles dimensions  
D. It enables filtering

<details>
<summary>Answer</summary>

### ✅ A

Memory is the expensive resource for HNSW. Use quantization, truncation or `float16` to shrink it. Disk savings from `stored: false` are comparatively cheap.
</details>

---

### Question 10: Rescoring availability

A team uses **custom** int8 vectors that they quantise themselves, then expects Azure AI Search's **oversampling and rescoring** to restore recall. It isn't available. Why?

A. Oversampling/rescoring are features of **built-in quantization** on float32/float16 fields and **can't be used on embeddings that undergo custom quantization**  
B. Rescoring needs a semantic ranker  
C. It requires `kind: text`  
D. It requires exhaustive KNN

<details>
<summary>Answer</summary>

### ✅ A

To use rescoring, let the service quantise float32/float16 vectors (so the original vectors are available for rescoring).
</details>

---

### Question 11: Exact tokens

A parts catalogue uses a pure vector index. Queries for **"SKU TX-9920-B"** and **"error E-4471"** return loosely related results. What is the BEST improvement?

A. Increase `efSearch`  
B. Add **keyword (full-text) search** and combine it with vectors (**hybrid search**)  
C. Switch to euclidean  
D. Add quantization

<details>
<summary>Answer</summary>

### ✅ B

Vectors capture meaning, not exact strings. Hybrid combines both in a single request. (Covered in depth in the Hybrid Search topic.)
</details>

---

### Question 12: Recall tuning

A team's HNSW index returns fast results but a recall check against exhaustive KNN ground truth shows many true neighbours missing. Latency has headroom. Which TWO changes are MOST appropriate?

A. Increase **`efSearch`**  
B. Increase **`k`** (and rely on later reranking if used)  
C. Decrease `efSearch` to 100  
D. Remove the vector profile  
E. Switch from cosine to hamming

<details>
<summary>Answer</summary>

### ✅ A and B

More candidates examined at query time improves recall at the cost of latency. A higher `efConstruction` also improves graph quality at index build time.

- **C ❌** Lowers recall further.
- **D, E ❌** Break or misconfigure the index.
</details>

---

### Question 13: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | HNSW is an approximate nearest neighbour algorithm. | |
| 2 | Exhaustive KNN consumes vector index size quota the same way HNSW does. | |
| 3 | A vector field in Azure AI Search can be used directly in a `filter` expression. | |
| 4 | Query vectors should be generated with the same embedding model used for the indexed vectors. | |
| 5 | Scalar quantization to int8 reduces vector index size about fourfold. | |
| 6 | PostFilter can produce false negatives with highly selective filters and small `k`. | |
| 7 | Vector search is the best method for exact SKU matching. | |
| 8 | An index can have both text fields and vector fields. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **Yes** | ANN. |
| 2 | **No** | Exhaustive KNN doesn't consume vector index size quota. HNSW does. |
| 3 | **No** | Vector fields aren't filterable. |
| 4 | **Yes** | Golden rule. |
| 5 | **Yes** | int8 = 8 bits vs 32 bits. |
| 6 | **Yes** | Documented risk. |
| 7 | **No** | Keyword (or hybrid). |
| 8 | **Yes** | Required for hybrid and for returning/citing text. |
</details>

---

### Question 14: Match the need to the feature (drag-and-drop)

Match each need to: **HNSW · Exhaustive KNN · preFilter · postFilter · Scalar quantization · Binary quantization · Oversampling + rescoring · MRL truncation · Vectorizer · Hybrid search**.

| Need | Feature |
|---|---|
| A. Fast, low-latency search over a very large index | ? |
| B. Exact neighbours on a small dataset, or recall ground truth | ? |
| C. Selective metadata filter must not lose relevant results | ? |
| D. About 4× smaller vectors with modest quality loss | ? |
| E. Up to about 28× smaller vectors for a huge corpus | ? |
| F. Recover quality lost by compression | ? |
| G. Use fewer dimensions on `text-embedding-3` models | ? |
| H. Convert a text query into a vector at query time | ? |
| I. Combine exact keyword matching with meaning | ? |

<details>
<summary>Answer</summary>

| Need | Feature |
|---|---|
| A | **HNSW** |
| B | **Exhaustive KNN** |
| C | **preFilter** |
| D | **Scalar quantization** |
| E | **Binary quantization** |
| F | **Oversampling + rescoring** |
| G | **MRL truncation** |
| H | **Vectorizer** |
| I | **Hybrid search** |
</details>

---

### Question 15: Multi-field and weighting (Select TWO)

A catalogue has a **`titleVector`** and a **`descriptionVector`** field (same model). Titles are more informative, and the team wants results to reflect that. Which TWO capabilities apply?

A. Query **multiple vector fields** in one request  
B. Apply **weights** to vector queries so some contribute more to the ranking  
C. Make both vector fields filterable  
D. Replace vectors with keyword analyzers  
E. Lower `dimensions` to 1

<details>
<summary>Answer</summary>

### ✅ A and B

Azure AI Search supports querying multiple vector fields, running multiple vector queries, and weighting them.
</details>

---

## 2. Mini Case Study: Tailspin Retail Search

### Background

Tailspin Retail runs product and support search on Azure AI Search with Microsoft Foundry.

1. **120 million** product-description chunks, HNSW, float32, 1536 dimensions. Memory/partition costs are climbing.
2. Search must be **fast**. Occasional misses are tolerable, but the team wants to **measure recall** before and after tuning.
3. Marketplace sellers are **multi-tenant**. Every query must filter by `sellerId`, which matches about **0.05%** of documents.
4. Shoppers search by concept ("waterproof jacket for hiking") **and** by **SKU** ("TX-9920-B").
5. Shoppers type **text** queries, and the team wants the service to embed them (no client-side embedding).
6. A data-science team recently re-embedded **new** products with a different model but didn't touch older products.
7. Another developer tried filtering on `descriptionVector` to exclude low-similarity items.
8. Leadership wants the **biggest memory reduction** without a noticeable relevance drop.

### Case Q1: Algorithm for the main index

A. Exhaustive KNN  
B. **HNSW**  
C. No algorithm  
D. Keyword only

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q2: Measuring recall

A. Guess by eye  
B. Build a **ground-truth set with exhaustive KNN** on a sample, then compare HNSW results to it  
C. Count replicas  
D. Check metric spelling

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q3: Per-seller filter

A. `postFilter` with `k: 5`  
B. **`preFilter`** (and consider a larger `k`)  
C. No filter, rely on the prompt  
D. Filter on the vector field

<details><summary>Answer</summary>

### ✅ B

A 0.05% selective filter is exactly where postFilter risks false negatives. Never use prompts for tenant isolation.
</details>

### Case Q4: Concepts + SKUs

A. Vector only  
B. **Hybrid search** (keyword + vector)  
C. Keyword only  
D. Random

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q5: Text queries without client-side embedding

A. Remove the vector field  
B. Add a **vectorizer** (same model as the indexed vectors) and use **`kind: text`** vector queries  
C. Use euclidean  
D. Use `stored: false`

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q6: The mixed-model problem

A. Increase `k`  
B. **Re-embed all documents with one model** (and use it for queries), then re-index  
C. Lower efSearch  
D. Add partitions

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q7: Filtering on a vector field

A. Make the vector field filterable  
B. Use **filterable metadata fields**, or use **thresholds** (preview) to drop low-scoring results  
C. Use a larger `k` only  
D. Switch to hamming

<details><summary>Answer</summary>

### ✅ B

Vector fields aren't filterable. The documented option for excluding low-scoring results is thresholds, which is a preview feature, so confirm its status before depending on it.
</details>

### Case Q8: Memory reduction

Which TWO should Tailspin evaluate?

A. **Built-in scalar or binary quantization** with **oversampling and rescoring**  
B. **Truncating dimensions** (if on `text-embedding-3` models) after testing relevance  
C. Doubling the dimensions  
D. Turning HNSW into exhaustive KNN to save memory

<details><summary>Answer</summary>

### ✅ A and B

Compress and truncate, then measure relevance (for example, NDCG on a test set). Exhaustive KNN doesn't use the HNSW memory index, but it's far too slow at 120 million vectors.
</details>

### Case Q9: Map the issue to the fix

| Issue | Fix |
|---|---|
| Memory cost | ? |
| Verify recall | ? |
| Selective tenant filter | ? |
| SKUs and concepts | ? |
| Text-to-vector at query time | ? |
| Mixed embedding models | ? |

<details><summary>Answer</summary>

| Issue | Fix |
|---|---|
| Memory cost | Quantization + oversampling/rescoring (and/or MRL truncation) |
| Verify recall | Exhaustive KNN ground truth |
| Selective tenant filter | preFilter |
| SKUs and concepts | Hybrid search |
| Text-to-vector at query time | Vectorizer + `kind: text` |
| Mixed embedding models | Re-embed everything with one model |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **ANN-is-exact trap** | "HNSW returns the true nearest neighbours." | It's approximate. Exhaustive KNN is exact. |
| **KNN-quota trap** | "Both algorithms use vector index quota." | Exhaustive KNN doesn't. HNSW does (in-memory). |
| **Filter-vector trap** | "Filter on the vector field." | Not filterable. Filter other fields. |
| **Postfilter trap** | "Post-filtering is the same as pre-filtering." | PostFilter can give false negatives for selective filters and small `k`. |
| **Mixed-model trap** | "Newer model for new docs only is fine." | One embedding space per index. |
| **Dimension trap** | "Any vector fits any field." | Field `dimensions` must match. |
| **Exact-match trap** | "Vector search finds SKUs." | Add keyword (hybrid). |
| **stored trap** | "`stored: false` shrinks the memory index." | Saves disk, not memory. |
| **Rescoring trap** | "Rescoring works with any compression." | Only built-in quantization on float32/float16. |
| **Bigger-ef trap** | "Higher efSearch is free." | Higher recall, higher latency. |
| **Preview trap** | "`strictPostFilter` and thresholds are production-ready." | Preview features have no SLA. |
| **Embedding-creation trap** | "A vector field creates embeddings." | You supply vectors or use an indexer/vectorizer pipeline. |
| **Metric trap** | "Pick any metric." | Match the metric the embedding model was trained for. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| Large dataset, low latency | **HNSW** |
| Small dataset, exact results | **Exhaustive KNN** |
| Measure ANN recall | **Exhaustive KNN ground truth** |
| Higher recall from HNSW | Raise `efSearch` / `k` (and `efConstruction` at build time) |
| Selective metadata filter | **preFilter** |
| Permissive filter, speed | postFilter |
| Filter by metadata (not vectors) | Filterable non-vector fields |
| Text query to vector in the service | **Vectorizer** + `kind: text` |
| Own query vector | `kind: vector` |
| Several vector fields | Multiple vector queries (+ weights) |
| Reduce memory about 4× | **Scalar quantization** |
| Reduce memory up to about 28× | **Binary quantization** + oversampling + rescoring |
| Recover compression quality | **Oversampling + rescoring** |
| Fewer dimensions | MRL truncation (`text-embedding-3`) |
| Exact IDs/codes | **Hybrid search** |
| Dimension mismatch | Match `dimensions` (field = model output) |
| Bad results after model change | Re-embed + re-index with one model |
| Save disk on retrievable vector copies | `stored: false` |

---

## 5. Quick Revision Sheet

```text
VECTOR SEARCH = nearest-neighbour search over embeddings (finds MEANING)
Vector field: Collection(Edm.Single) + dimensions + vectorSearchProfile
Profile = algorithm + (vectorizer) + (compression)

ALGORITHMS
  HNSW            = approximate (ANN), fast, in memory, USES vector-index quota
  Exhaustive KNN  = exact, brute force, slow, NO vector-index quota, ground truth for recall
  HNSW field can still run exhaustive per query ("exhaustive": true)
HNSW params: m (links) | efConstruction (build quality) | efSearch (query recall vs latency)
Metrics: cosine | dotProduct | euclidean | hamming (binary)  -> match the model

QUERY: vectorQueries[ { kind: vector|text, fields, k } ]  (same model for query + index)
       multiple fields / queries / weights; thresholds = preview
FILTER: vector fields NOT filterable -> filter metadata fields
        preFilter  = max recall (more CPU for selective filters)
        postFilter = false-negative risk (selective filter, small k)
        strictPostFilter = preview, highest risk

COST: scalar int8 ~4x | binary 1-bit up to ~28x | + oversampling + rescoring (built-in only)
      MRL truncation (text-embedding-3) | float16 | stored:false = DISK only

Vector = meaning.  Keyword = exact tokens.  Hybrid = both.
```

### Best-answer checklist

1. **Dataset size and priority:** speed (HNSW) or exactness (exhaustive KNN)?
2. Any **mismatch** between index and query embeddings (model, version, dimensions)?
3. **Filters:** are they selective? Use preFilter, and remember vector fields aren't filterable.
4. **Exact identifiers** in queries? Add keyword, so hybrid.
5. **Cost/memory problem?** Built-in quantization first, plus oversampling/rescoring, then truncation.
6. **Preview feature** in the option? Flag it for production.
7. Validate changes with a **test set** (recall, NDCG).

---

**Next concept:** Semantic Search (same harder exam-style format)

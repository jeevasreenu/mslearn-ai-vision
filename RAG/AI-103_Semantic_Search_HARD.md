# AI-103: Semantic Search (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, config/query snippets, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Scope: **semantic ranking in Azure AI Search (Foundry IQ)**: what it is, what it needs, what it returns, what breaks it, and how it fits with keyword, vector and hybrid. Hybrid search and RRF get their own file next.
> API versions, preview flags and billing details change often. The exam tests **what the feature does and when to use it**, not version numbers.

---

## 0. Core Concepts (read first)

### 0.1 Two meanings of "semantic search" (very common confusion)

| Term | Meaning |
|---|---|
| **Semantic search (general idea)** | Searching by **meaning** instead of exact words. Usually done with embeddings and **vector search** |
| **Semantic ranker / semantic ranking (Azure AI Search feature)** | A **query-side reranking** capability that uses Microsoft's language-understanding models to re-score an **already retrieved** result set |

> In Azure AI Search, the **semantic ranker is not vector search**. It doesn't need embeddings, and it doesn't retrieve new documents. It **reorders** what keyword, vector or hybrid retrieval already returned.

### 0.2 What the semantic ranker is

A collection of **query-side capabilities** that improve the quality of an initial **BM25-ranked or RRF-ranked** result set. It applies to **text queries, the text portion of vector queries, and hybrid queries**.

It extends the query pipeline in three ways:

1. **L2 (secondary) ranking.** Always adds a secondary ranking over the initial result set, using **multilingual deep-learning models adapted from Microsoft Bing**, to promote the most semantically relevant results.
2. **Captions and answers.** Returns **semantic captions** (with highlights) and optionally **semantic answers**.
3. **Query rewrite** *(preview)*. Expands the query into multiple semantically similar queries.

```text
Query → [L1 retrieval: BM25 and/or vector → (RRF if hybrid)] → initial ranked results
                                   ↓
                     [L2: semantic ranker re-scores top results]
                                   ↓
              reordered results  +  captions/highlights  +  (optional) answers
```

| Capability | What it gives you |
|---|---|
| **L2 ranking** | New relevance score based on the meaning of the query and the content |
| **Captions + highlights** | **Verbatim** sentences/phrases from a field that best summarise the match, with highlights. Good for dense fields on a results page |
| **Answers** | Optional direct answer for **question-like queries**. Needs text in a document that has the characteristics of an answer |
| **Query rewrite** *(preview)* | Expands the query. The **only** case where the subsystem composes new phrases |

> **Captions and answers are extracted verbatim** from document text. The semantic subsystem **doesn't generate** new sentences (except query rewrite). For chat-style **generated** answers, use **RAG** or **agentic retrieval**.

### 0.3 What it needs (prerequisites)

| Requirement | Detail |
|---|---|
| **Service/region** | A search service in a region that provides semantic ranking |
| **Billing plan** | Semantic ranker is a **premium feature billed by usage**. Default is the **Free** plan (monthly free request allowance, **after which requests return a billing error**). **Standard** = pay-as-you-go beyond the free allowance and **requires Basic tier or higher**. The plan is **service-level** and affects all indexes |
| **Index content** | **String (non-vector) fields** with rich, informational or descriptive text. Works best on content with **explanations or definitions** |
| **Semantic configuration** | A section of the index that names the fields the ranker should use. Can be **added or updated at any time without rebuilding the index**. Up to **100 configurations per index**, with one optionally set as the **default** |
| **Query** | Must include **actual search terms** (see "what breaks it" below), and must request semantic ranking |

> Agentic retrieval: if a knowledge source generates the index for you, **a semantic configuration is created automatically**. In newer preview API versions, supported agentic retrieval knowledge-base flows don't even need an explicit one. This exception doesn't apply to classic semantic ranking queries.

### 0.4 The semantic configuration (what goes in it)

A semantic configuration tells the ranker **which fields to read and in what priority**:

```jsonc
"semantic": {
  "defaultConfiguration": "my-semantic-config",
  "configurations": [
    {
      "name": "my-semantic-config",
      "prioritizedFields": {
        "titleField":              { "fieldName": "title" },
        "prioritizedContentFields":[ { "fieldName": "content" } ],
        "prioritizedKeywordsFields":[ { "fieldName": "tags" } ]
      }
    }
  ]
}
```

- **Title field** (short, descriptive), **content fields** (the main text, in priority order), **keyword fields** (tags/keywords).
- Only **non-vector string fields** are used. The fields' order tells the ranker which to favour when content is long.

### 0.5 Invoking semantic ranking on a query

```jsonc
{
  "search": "how do I get my money back for a damaged item",
  "queryType": "semantic",
  "semanticConfiguration": "my-semantic-config",
  "captions": "extractive|highlight-true",
  "answers": "extractive|count-3",
  "select": "title, content",
  "top": 10
}
```

Key facts:
- **By default, queries don't use semantic ranking.** You opt in per query (the docs describe two parameters that invoke it, each supporting a different set of query formats).
- If you omit the configuration name, the **default** configuration is used.
- `captions` and `answers` are **opt-in** query options.
- It works with **hybrid** queries (best practice for RAG: BM25 + vector → RRF → semantic ranker).

### 0.6 What BREAKS semantic ranking (high-yield)

| Query feature | Why it breaks | Result |
|---|---|---|
| **`search=*` or an empty search string** (filter-only query) | Nothing to measure semantic relevance against, so **scores are zero** | Can't be semantically ranked |
| **`orderBy` / sorting on fields** | Overrides search and semantic scores | **HTTP 400 error** if semantic ranking is applied over ordered results |

Also:
- Semantic ranking applies to **text**. A pure vector query needs a **text representation** in the document (and text query terms) for the ranker to evaluate.
- It **doesn't fix retrieval**. If the right document isn't in the initial candidate set, the ranker can't surface it.

### 0.7 Where it sits relative to the other search types

| Method | Role | Matches by |
|---|---|---|
| **Keyword (BM25)** | L1 retrieval | Exact terms |
| **Vector** | L1 retrieval | Embedding similarity (meaning) |
| **Hybrid (RRF)** | L1 retrieval, fuses keyword + vector rankings | Both |
| **Semantic ranker** | **L2 reranking** of those results (+ captions/answers) | Deep-learning reading of query and passage |

Typical best-practice stack for **classic RAG**: **hybrid retrieval + semantic ranking**. Retrieval maximises **recall**, and semantic ranking improves **precision at the top**.

### 0.8 Semantic ranker vs agentic retrieval vs RAG

| | Semantic ranker | Agentic retrieval | RAG |
|---|---|---|---|
| What it does | **Reranks** results, returns captions/answers (extractive) | **LLM query planning** → parallel subqueries, each semantically reranked, merged | Uses retrieved content to **generate** an answer |
| Generates new text? | **No** (except query rewrite preview) | Can optionally synthesise an answer | **Yes** |
| Needs an LLM call? | Not for ranking | Yes (planning) | Yes (generation) |
| Best for | Better ordering of top results, search UIs with captions | Complex multi-part questions | Chat/answers |

Semantic ranker is **built into** agentic retrieval (each subquery is semantically reranked).

### 0.9 Billing and cost facts

- **Free plan (default)**: monthly allowance, then **billing error** (requests fail until you switch plan or the quota resets).
- **Standard plan**: pay-as-you-go beyond the allowance, **Basic tier or higher**, set at **service level**.
- Newer API versions **separate billing consent**: `semanticSearch` controls **semantic ranker** billing, and `knowledgeRetrieval` controls **agentic retrieval** billing. In older versions, `semanticSearch` covered both.
- A third-party article claims semantic ranking isn't available on the Free **search tier**, while the Microsoft billing page says the **Free billing plan** is available on all pricing tiers. Know the difference between **billing plan** and **service tier**.

### 0.10 Common problems and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Semantic query returns a billing error | **Free plan allowance used up** | Switch to the **Standard** plan (Basic tier or higher) |
| HTTP **400** when using semantic ranking | **`orderBy`** present | Remove sorting. Let the semantic score rank |
| No semantic effect on filter-only query | **`search=*`**/empty search | Provide real query terms |
| Right document never appears | Not in the initial candidate set | Fix **retrieval** (hybrid, chunking, filters, `k`), not the ranker |
| Captions look irrelevant/empty | Poor **semantic configuration** or thin text fields | Prioritise the right content fields, use descriptive text fields |
| No answers returned | Content lacks answer-like text, or query isn't question-like, or `answers` not requested | Use explanatory content, request answers |
| Want chat-style generated reply | Semantic ranker is extractive | Use **RAG** or **agentic retrieval** |
| Exact SKUs still missing | Ranker can't recover un-retrieved docs | Add **keyword** retrieval (hybrid) |
| Need to change fields used for ranking | n/a | Update the **semantic configuration** (no rebuild) |

### 0.11 Five ideas the exam really tests

1. **Semantic ranker = L2 reranker over BM25/RRF results.** It doesn't retrieve and doesn't need embeddings.
2. **It needs a semantic configuration**, string fields, and a query with real terms. It's **opt-in per query**.
3. **`search=*` and `orderBy` break it** (zero scores / HTTP 400).
4. **Captions and answers are extractive**, not generated.
5. **Premium feature billed by usage**: Free plan allowance then billing error, Standard plan on Basic tier or higher.

---

## 1. Scenario Questions

### Question 1: What the semantic ranker actually does

A developer says: "Turning on semantic ranker will find documents that keyword search missed completely." What is the MOST accurate response?

A. Correct. It runs its own separate retrieval over the whole index  
B. **Incorrect.** It **reranks results already retrieved** (BM25/RRF). If the right document isn't in the candidate set, the ranker can't surface it  
C. Correct, because it converts all documents to vectors  
D. Incorrect, because it only works on images

<details>
<summary>Answer</summary>

### ✅ B

Semantic ranker is a secondary (L2) ranking over an initial result set. To retrieve more candidates, fix retrieval (add vectors/hybrid, adjust `k`/filters/chunking).

- **A ❌** It doesn't retrieve.
- **C ❌** It doesn't require embeddings.
- **D ❌** It works on text.

**Trap:** Don't confuse "semantic ranker" with "vector search".
</details>

---

### Question 2: Best first improvement

A support portal uses **BM25 keyword search only**. The right article is usually in the top 50 results but often at position 15–30, so users miss it. Embeddings aren't available yet, and the team wants the **fastest improvement to top-of-list relevance**. What should they do?

A. Add **semantic ranking** (a semantic configuration + semantic query) over the existing keyword index  
B. Rebuild the index with 3072-dimension vectors first  
C. Switch to exhaustive KNN  
D. Increase `efSearch`

<details>
<summary>Answer</summary>

### ✅ A

The candidates are already retrieved. The problem is **ordering**. Semantic ranking improves precision at the top and needs no embeddings. You can add a semantic configuration to an existing index without rebuilding.

- **B, C, D ❌** Vector-related, and the stem says embeddings aren't available.
</details>

---

### Question 3: HTTP 400 (snippet)

```json
{
  "search": "warranty coverage for water damage",
  "queryType": "semantic",
  "semanticConfiguration": "default-config",
  "orderby": "lastUpdated desc"
}
```

The request fails with **HTTP 400**. What is the cause and fix?

A. The semantic configuration name is too long  
B. **`orderby` overrides search/semantic scores**, which conflicts with semantic ranking. Remove sorting and let the semantic score rank  
C. `queryType` must be `simple`  
D. The search string needs wildcards

<details>
<summary>Answer</summary>

### ✅ B

Sorting overrides relevance scores. If you need recency, use a **filter** (for example, date range) or a scoring approach that doesn't conflict, rather than `orderBy`.
</details>

---

### Question 4: Filter-only query

A catalogue page loads with `search=*` and a filter `category eq 'boots'`, plus `queryType=semantic`. Results aren't re-ranked meaningfully. Why?

A. A wildcard query has **no search terms to score**, so relevance scores are zero and the semantic ranker has nothing to evaluate  
B. Semantic ranking needs HNSW  
C. The filter must be removed  
D. Semantic ranking requires 100 configurations

<details>
<summary>Answer</summary>

### ✅ A

The query must provide terms or phrases that produce relevance-scored results. Provide the shopper's actual search text.
</details>

---

### Question 5: Billing error

After a successful pilot, production users start getting **billing errors** on semantic queries late in the month. The search service is on the **Standard** (S1) service tier and has never changed its semantic ranker billing settings. What is the MOST likely cause and fix?

A. The service is still on the **Free semantic ranker plan** and the monthly free allowance was used up. **Switch to the Standard billing plan**  
B. The index is corrupt  
C. HNSW parameters are wrong  
D. The semantic configuration exceeds 100 fields

<details>
<summary>Answer</summary>

### ✅ A

All services are enrolled in the Free plan by default (monthly allowance, then a billing error). The Standard plan (Basic tier or higher) provides pay-as-you-go access. The plan applies service-wide.

**Trap:** "Service tier" and "semantic ranker billing plan" are different settings.
</details>

---

### Question 6: Which fields? (snippet)

```json
{
  "fields": [
    { "name": "title", "type": "Edm.String" },
    { "name": "summary", "type": "Edm.String" },
    { "name": "body", "type": "Edm.String" },
    { "name": "tags", "type": "Collection(Edm.String)" },
    { "name": "bodyVector", "type": "Collection(Edm.Single)", "dimensions": 1536 }
  ]
}
```

Which semantic configuration is MOST appropriate?

A. Title field = `bodyVector`, content = `body`  
B. **Title field = `title`, prioritized content fields = `body` (then `summary`), keywords = `tags`**  
C. Content fields = `bodyVector` only  
D. No configuration is needed because semantic ranking reads the vector field

<details>
<summary>Answer</summary>

### ✅ B

Semantic configuration uses **non-vector string fields**. Prioritise the richest text first.

- **A, C ❌** Vector fields can't be used.
- **D ❌** A configuration is needed, and vectors aren't read by the semantic ranker.
</details>

---

### Question 7: Captions vs generated answers

A product manager wants a search results page that shows, under each result, a **highlighted snippet** explaining why it matched. A different stakeholder wants a **written summary** that combines information from several documents. Which TWO statements are correct?

A. **Semantic captions** with highlights fit the first need (verbatim extracts shown under each result)  
B. The second need (a composed summary across documents) calls for **RAG or agentic retrieval**, because the semantic ranker extracts text and doesn't generate new sentences  
C. Semantic answers compose new text from several documents  
D. Semantic captions require a generation model  
E. Neither need can be met in Azure AI Search

<details>
<summary>Answer</summary>

### ✅ A and B

Captions/highlights and answers are **extractive** (verbatim). Generated, synthesised responses need an LLM through RAG or agentic retrieval.
</details>

---

### Question 8: Hybrid + semantic

A RAG team currently uses **vector-only** retrieval. Users complain that exact part numbers are missed **and** the best passage often isn't ranked first. Which design addresses BOTH problems?

A. Increase `efSearch` only  
B. **Hybrid retrieval (BM25 + vector, fused with RRF) followed by semantic ranking**  
C. Keyword only  
D. Remove the vector field

<details>
<summary>Answer</summary>

### ✅ B

Hybrid fixes **recall** (exact tokens + meaning). The semantic ranker fixes **precision at the top**. This is the common best-practice stack for classic RAG.

- **A ❌** Only tunes vector recall.
- **C ❌** Loses meaning-based matches.
</details>

---

### Question 9: Wrong layer

Retrieval logs show the correct policy chunk is **not in the top 50 candidates** for a certain question. A teammate suggests adding more fields to the semantic configuration. What is the BEST advice?

A. Do it, because the ranker will find the chunk anyway  
B. **Fix retrieval first** (hybrid, chunking, filters, `k`, query rewriting/agentic retrieval). The ranker only reorders candidates it receives  
C. Disable semantic ranking  
D. Lower temperature

<details>
<summary>Answer</summary>

### ✅ B

A reranker can't promote what retrieval never returned. Diagnose recall problems at the retrieval layer.
</details>

---

### Question 10: Complex questions

Users ask multi-part, conversational questions such as *"Compare coverage for flood damage between the Gold and Silver plans, and tell me the claim deadline for each."* A single hybrid + semantic query returns partial matches. Which approach fits BEST?

A. Increase the number of captions  
B. **Agentic retrieval**: LLM query planning decomposes the question into subqueries, runs them in parallel, semantically reranks each, and merges the results (at the cost of added latency)  
C. Use `search=*`  
D. Remove the semantic configuration

<details>
<summary>Answer</summary>

### ✅ B

Agentic retrieval targets complex, context-dependent questions. Semantic ranking is built into it.
</details>

---

### Question 11: Configuration changes

A team wants to change which fields feed the semantic ranker for a production index of 80 million documents. They fear a full re-index. What is correct?

A. A full rebuild is required for any semantic configuration change  
B. **Semantic configurations can be added or updated at any time without rebuilding the index**, and queries can pick a configuration by name or fall back to the default  
C. Semantic configurations can't be changed after creation  
D. They must delete the vector fields first

<details>
<summary>Answer</summary>

### ✅ B

A semantic configuration is a query-time construct in the index definition. You can create multiple (up to 100 per index) and choose one per request.
</details>

---

### Question 12: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | Semantic ranking requires embeddings and a vector field. | |
| 2 | Semantic ranker re-scores results that were already ranked with BM25 or RRF. | |
| 3 | Semantic captions and answers are extracted verbatim from document text. | |
| 4 | A query with `search=*` can be semantically ranked. | |
| 5 | Semantic ranking is applied to every query by default. | |
| 6 | Semantic ranker is a premium feature billed by usage. | |
| 7 | Adding a semantic configuration requires rebuilding the index. | |
| 8 | Semantic ranking can be applied to hybrid queries. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **No** | It works on text and doesn't need embeddings. |
| 2 | **Yes** | L2 ranking over the initial set. |
| 3 | **Yes** | The subsystem doesn't compose new text (query rewrite is the preview exception). |
| 4 | **No** | No terms to score. |
| 5 | **No** | You opt in per query. |
| 6 | **Yes** | Free allowance, then Standard plan. |
| 7 | **No** | Add or update any time. |
| 8 | **Yes** | Text, hybrid and the text portion of vector queries. |
</details>

---

### Question 13: Match the need to the capability (drag-and-drop)

Match each need to: **L2 reranking · Semantic captions · Semantic answers · Query rewrite (preview) · Hybrid retrieval · Agentic retrieval · RAG · Semantic configuration**.

| Need | Capability |
|---|---|
| A. Promote the most meaningful results to the top | ? |
| B. Show highlighted verbatim snippets under each result | ? |
| C. Return a direct extracted answer to a question-like query | ? |
| D. Expand a user's query into several similar queries | ? |
| E. Combine keyword and vector retrieval before ranking | ? |
| F. Break a complex question into parallel reranked subqueries | ? |
| G. Generate a written response grounded in results | ? |
| H. Tell the ranker which fields to read | ? |

<details>
<summary>Answer</summary>

| Need | Capability |
|---|---|
| A | **L2 reranking** |
| B | **Semantic captions** |
| C | **Semantic answers** |
| D | **Query rewrite** (preview) |
| E | **Hybrid retrieval** |
| F | **Agentic retrieval** |
| G | **RAG** |
| H | **Semantic configuration** |
</details>

---

### Question 14: Production readiness (Select TWO)

A team plans to rely on **query rewrite** and a **prerelease semantic ranking model** in a regulated production workload. Which TWO observations are MOST appropriate?

A. Features marked **preview** aren't covered by an SLA and aren't recommended for production workloads  
B. Verify the current **GA/preview status** of each feature before depending on it  
C. Preview features are always production-ready  
D. Query rewrite is GA in every API version  
E. Preview features can't be disabled

<details>
<summary>Answer</summary>

### ✅ A and B

Preview functionality is subject to preview terms, has no SLA and may change.
</details>

---

### Question 15: Terminology trap

A question states: *"Which Azure AI Search capability uses language-understanding models to reorder the top retrieved results and can return captions?"*

A. HNSW  
B. **Semantic ranker**  
C. Scalar quantization  
D. Integrated vectorization

<details>
<summary>Answer</summary>

### ✅ B
</details>

---

## 2. Mini Case Study: Proseware Help Center

### Background

Proseware runs a public help center on Azure AI Search, with a RAG assistant on Microsoft Foundry.

1. The help-center search box currently uses **BM25 only**. The right article is often on page 2.
2. The team wants a **results page with highlighted snippets** under each result.
3. Customers sometimes search with **part numbers**, and sometimes with **natural questions**.
4. A new "browse by category" page runs queries with `search=*`, a `category` filter, and `orderby=popularity desc`. The team enabled semantic ranking site-wide and now sees **HTTP 400 errors** on that page.
5. Late in the month, **all** semantic queries start returning **billing errors**.
6. For multi-part chat questions, a single query often returns partial matches.
7. The product owner wants the assistant to **write a combined answer** from several articles.
8. Index owners want to try **different ranking field sets** without re-indexing 20 million documents.

### Case Q1: Fastest relevance win for requirement 1

A. Rebuild everything with vectors  
B. **Add a semantic configuration and use semantic queries** over the existing BM25 index  
C. Increase `k`  
D. Delete the title field

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q2: Highlighted snippets

A. **Semantic captions with highlights**  
B. Query rewrite  
C. HNSW  
D. Binary quantization

<details><summary>Answer</summary>

### ✅ A
</details>

### Case Q3: Part numbers plus natural questions

A. Vector only  
B. **Hybrid retrieval (BM25 + vector) with semantic ranking on top**  
C. Keyword only  
D. Semantic ranking only, with no retrieval

<details><summary>Answer</summary>

### ✅ B

Keyword handles exact tokens, vectors handle meaning, and the ranker orders the final candidates.
</details>

### Case Q4: The 400 errors

Which TWO changes fix the browse page?

A. **Don't apply semantic ranking** to the `search=*` browse queries (use a normal filtered, sorted query there)  
B. **Remove `orderby`** from any query that uses semantic ranking  
C. Add 100 more semantic configurations  
D. Turn on exhaustive KNN

<details><summary>Answer</summary>

### ✅ A and B

Wildcard queries have nothing to semantically score, and `orderby` conflicts with semantic ranking. Use semantic ranking only for real text search.
</details>

### Case Q5: Billing errors

A. Re-embed the corpus  
B. **Check the semantic ranker billing plan.** The Free allowance was likely exhausted. Switch to **Standard** (Basic tier or higher)  
C. Reduce HNSW `m`  
D. Remove captions

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q6: Multi-part chat questions

A. Increase captions  
B. **Agentic retrieval** (LLM query planning, parallel semantically reranked subqueries, merged results)  
C. Use `search=*`  
D. Switch to BM25 only

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q7: A written, combined answer

Which TWO statements are correct?

A. Semantic **answers/captions are extractive** and won't compose a multi-article written response  
B. Use **RAG** (or agentic retrieval with answer synthesis) to generate the combined answer from retrieved passages  
C. Semantic captions compose new paragraphs  
D. Semantic ranker includes a built-in chat model for writing responses

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q8: Trying different field sets

A. Re-index all 20 million documents for each experiment  
B. **Create additional semantic configurations** (up to 100) and choose one per query, or change the default. No rebuild needed  
C. Delete the vector field  
D. Can't be done

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q9: Map the issue to the fix

| Issue | Fix |
|---|---|
| Right article on page 2 | ? |
| Need highlighted snippets | ? |
| Part numbers + natural questions | ? |
| 400 error on browse page | ? |
| Billing errors late in month | ? |
| Multi-part questions | ? |
| Combined written answer | ? |
| Try different ranking fields | ? |

<details><summary>Answer</summary>

| Issue | Fix |
|---|---|
| Right article on page 2 | Semantic ranker (L2 reranking) |
| Need highlighted snippets | Semantic captions |
| Part numbers + natural questions | Hybrid retrieval + semantic ranking |
| 400 error on browse page | Remove `orderby`, skip semantic on `search=*` |
| Billing errors late in month | Switch semantic billing to Standard |
| Multi-part questions | Agentic retrieval |
| Combined written answer | RAG / agentic retrieval with synthesis |
| Try different ranking fields | Additional semantic configurations |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Name trap** | "Semantic ranker = vector search." | It's an L2 **reranker** over BM25/RRF results. Embeddings not required. |
| **Retrieval trap** | "Semantic ranking finds documents search missed." | It only reorders the candidates it receives. |
| **Wildcard trap** | "`search=*` with a semantic query works." | No terms to score, so scores are zero. |
| **Sort trap** | "I can add `orderBy` too." | `orderBy` overrides scores and causes **HTTP 400** with semantic ranking. |
| **Generation trap** | "Semantic answers write new text." | Captions and answers are **extractive**. Use RAG for generation. |
| **Default trap** | "Semantic ranking applies automatically." | You must opt in per query. |
| **Config trap** | "Changing semantic fields needs a re-index." | Add or update anytime, no rebuild. |
| **Field trap** | "Put the vector field in the configuration." | Non-vector string fields only. |
| **Billing trap** | "Free plan = unlimited." | Free allowance, then a **billing error**. Standard needs Basic tier or higher. |
| **Tier-vs-plan trap** | "Service tier = billing plan." | Separate settings. |
| **Preview trap** | "Query rewrite and prerelease models are production-ready." | Preview = no SLA. Verify status. |
| **Stack trap** | "Semantic ranker replaces hybrid." | Best practice is **hybrid retrieval + semantic ranker**. |
| **Agentic trap** | "Agentic retrieval doesn't use semantic ranking." | Semantic ranker is **built into** agentic retrieval. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| Right result retrieved but ranked low | **Semantic ranker** |
| Right result not retrieved | Fix retrieval (hybrid, chunking, filters, k) |
| Highlighted snippets under each result | **Semantic captions** |
| Direct extracted answer to a question | **Semantic answers** (request them) |
| Generated, combined written answer | **RAG** or agentic retrieval with synthesis |
| Exact IDs plus meaning | **Hybrid retrieval**, then semantic ranking |
| Complex multi-part questions | **Agentic retrieval** |
| Choose which fields are ranked | **Semantic configuration** (up to 100 per index) |
| Change those fields | Update the configuration, no rebuild |
| HTTP 400 with semantic query | Remove **`orderBy`** |
| Filter-only/`search=*` query | Don't use semantic ranking |
| Billing error | Free allowance used. Switch to **Standard** plan |
| Expand queries | Query rewrite (**preview**) |
| Production use of preview features | Verify status. No SLA |

---

## 5. Quick Revision Sheet

```text
SEMANTIC RANKER = query-side L2 RERANKER over BM25 / RRF results
  works on: text queries, text part of vector queries, hybrid queries
  returns: re-scored results + captions/highlights + (optional) answers
  models: multilingual deep-learning models adapted from Microsoft Bing
  EXTRACTIVE (verbatim). Query rewrite (preview) is the only composing feature.
  NOT vector search. No embeddings needed. Doesn't retrieve new documents.

NEEDS: semantic configuration (title / content / keyword fields; STRING non-vector fields;
       up to 100 per index; one default; add/update with NO rebuild)
       + opt-in per query (queryType semantic + configuration name) + real query terms

BREAKS:  search=* / empty search -> zero scores
         orderBy -> HTTP 400

BILLING: premium, usage-based.  Free plan (default): allowance, then BILLING ERROR.
         Standard plan: Basic tier or higher, service-wide.
         Newer API: semanticSearch (ranker) vs knowledgeRetrieval (agentic) billing split.

STACK:   Hybrid (BM25 + vector, RRF)  ->  Semantic ranker  ->  RAG / LLM
         Retrieval = RECALL.  Semantic ranker = PRECISION at the top.
AGENTIC: LLM query planning -> parallel subqueries -> each semantically reranked -> merged
```

### Best-answer checklist

1. Is the problem **ordering** (semantic ranker) or **missing candidates** (retrieval)?
2. Does the query have **real terms**, and is there any **`orderBy`**? Either can break semantic ranking.
3. Need **snippets or answers**? They're extractive. Need **generated text**? RAG.
4. Mixed exact-token and natural-language queries? **Hybrid + semantic ranker**.
5. Complex multi-part questions? **Agentic retrieval**.
6. Billing error? Check the **plan**, not the tier.
7. Preview feature in the option? Flag **no SLA**.

---

**Next concept:** Hybrid Search (same harder exam-style format)

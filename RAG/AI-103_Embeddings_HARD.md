# AI-103: Embeddings (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, code/config snippets, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Model names, dimensions and limits change over time. The exam tests the **selection and consistency logic**, not memorised numbers.

---

## 0. Core Concepts (read first)

### 0.1 What is an embedding?

An **embedding** is a **vector of floating-point numbers** that represents the **semantic meaning** of content (text, and for some models, images). **Similar meaning → vectors that are close together.**

```text
"How do I get a refund?"      → [0.021, -0.113, 0.407, ...]   ┐ close together
"What is your return policy?" → [0.019, -0.109, 0.399, ...]   ┘
"Best pizza in Chicago"       → [-0.310, 0.052, -0.221, ...]    far away
```

Embeddings power: **vector/semantic search, RAG retrieval, recommendations, classification, clustering, deduplication, anomaly detection.**

> **Embedding model ≠ chat model.** An embedding model **only converts input to vectors**. It does **not generate text or answers**.

### 0.2 Measuring "closeness"

| Metric | Idea | Note |
|---|---|---|
| **Cosine similarity** | Angle between vectors (direction) | The most common choice for text embeddings |
| **Dot product** | Magnitude + direction | Equals cosine similarity when vectors are **normalised** (length 1) |
| **Euclidean distance** | Straight-line distance | Less common for text |

> The distance metric configured on the **vector field / index** should be the one the embedding model is designed for. Azure AI Search supports cosine, dot product and Euclidean.

### 0.3 Embedding models you may see in Foundry

| Model | Notes (verify current catalog) |
|---|---|
| **text-embedding-3-small** | Lower cost, 1536 default dimensions |
| **text-embedding-3-large** | Highest quality in the OpenAI family, 3072 default dimensions |
| **text-embedding-ada-002 (v2)** | Older generation, 1536 dimensions, **no `dimensions` parameter** |
| **Cohere Embed (v3 / v4 / v5)** | Partner models in the Foundry catalog. Several are **multilingual** and/or **multimodal** (text + image in the same vector space) |
| **Azure AI Vision multimodal embeddings** | Text and image in a shared embedding space (used with Azure AI Search for image/text search) |

Input limit: the OpenAI `text-embedding-3` models accept up to **8,191 input tokens** per input (per the Foundry catalog page). Some other models, such as Cohere v3, have a much smaller context window (**512 tokens**). **Long documents must be chunked** before embedding.

### 0.4 Dimensions (the size of the vector)

- **More dimensions** → can capture more nuance, but cost **more storage, memory and compute**, and make search slightly slower.
- `text-embedding-3` models support a **`dimensions` parameter** to **shorten** embeddings (for example, `text-embedding-3-large` at 256, 1024 or the default 3072) with limited quality loss, trading a little accuracy for large savings in size and cost.
- **The index vector field's dimension count must match the vectors you generate.** A mismatch causes indexing/query errors.
- Some stores have **dimension limits**. For example, Azure SQL's `vector` type supported up to 1,998 dimensions in the source article, so the 3072-dimension default doesn't fit unless you shorten it.

### 0.5 The golden rule: **same model for indexing and querying**

```text
INDEX TIME :  chunk  → embedding model X → vector  → stored in index
QUERY TIME :  query  → embedding model X → vector  → compared to stored vectors
```

- Use the **same embedding model** (same model **and** version/deployment, same `dimensions`) for **documents and queries**.
- Vectors from **different models** are **not comparable** (different spaces, sometimes different dimension counts).
- **Changing the embedding model = re-embed and re-index everything.**
- In Azure AI Search the **skill** (index time) and **vectorizer** (query time) must point to the **same model deployment**.

### 0.6 How embeddings are produced in an Azure AI Search solution

**Azure AI Search does not host embedding models.** You provide the model (for example, an Azure OpenAI / Foundry deployment). Two approaches:

| Approach | What you do | When |
|---|---|---|
| **Integrated vectorization** (recommended for most scenarios) | Indexer + skillset (chunking skill + **embedding skill**) at **index time**; **vectorizer** in the index at **query time** (plain-text queries are converted automatically) | Less code, less maintenance, built-in chunking + embedding |
| **Manual vectorization** | You chunk, call the embedding model, **push pre-vectorised documents** into vector fields; at query time you **send precomputed vectors** | Full control, custom pipelines, unsupported sources |

Key facts:
- **Skill ↔ vectorizer pairs** must match the model (for example, Azure OpenAI embedding skill with an Azure OpenAI vectorizer; custom skill with a Custom Web API vectorizer; Azure Vision multimodal skill with the Azure Vision vectorizer).
- Supported embedding skill options include the **AzureOpenAIEmbedding** skill (ada-002, 3-small, 3-large), a **custom skill** for any other model, the **Azure Vision multimodal embeddings** skill (preview in the source), and an **AML skill** for select Foundry catalog models.
- **Vector conversion is one-way** (non-vector → vector). You **can't convert a vector back to text**, so indexes keep **both** text fields and vector fields.
- Create the embedding model and the search service in the **same region** when possible (latency, availability), and add **retry logic** for rate limits.

### 0.6b Authentication and permissions

- Prefer **Microsoft Entra ID** with the **Cognitive Services OpenAI User** role on the Azure OpenAI resource, rather than long-lived keys.
- The `model` value in an Azure request is your **deployment name**, not necessarily the model name.
- Azure AI Search needs access to the embedding model (managed identity with the right role, or a key) for integrated vectorization.

### 0.7 Choosing an embedding model (selection criteria)

| Criterion | Question |
|---|---|
| **Quality** | Retrieval quality on **your** data (use a benchmark for shortlisting, validate with your own queries) |
| **Language** | Multilingual or cross-language search needed? |
| **Modality** | Text only, or **text + images** in one space (multimodal)? |
| **Dimensions** | Storage/latency vs accuracy. Can you shorten? |
| **Input limit** | Max tokens per input, so chunk size must fit |
| **Cost / throughput** | Tokens to embed = corpus size × re-embedding events |
| **Compatibility** | Supported by your search skill/vectorizer? Same-region availability? |

### 0.8 Embeddings vs other tools

| Task | Right tool |
|---|---|
| Find content by meaning | **Embeddings + vector search** |
| Find exact IDs/error codes | **Keyword** (or hybrid) |
| Generate an answer | **Chat/LLM model** |
| Convert speech to text | **Speech model** |
| Understand an image and describe it | **Multimodal chat model** (not an embedding model) |
| Match text queries to images | **Multimodal embedding model** (shared text/image space) |

### 0.9 Common embedding problems

| Symptom | Likely cause | Fix |
|---|---|---|
| Irrelevant results after model upgrade | Query vectors from the **new** model vs index from the **old** model | Re-embed and re-index with the same model |
| Dimension mismatch error | Index field dimensions ≠ model output (or `dimensions` changed) | Make the field dimensions match, re-index |
| `input too long` / truncation | Chunk exceeds the model's token limit | Chunk before embedding |
| Great on paraphrase, misses SKUs | Vector-only | Hybrid (add keyword) |
| Cost spike | Re-embedding the whole corpus often, or very large dimensions | Incremental indexing, shorter dimensions, smaller model |
| Poor multilingual results | English-only model | Multilingual embedding model |
| Can't search images by text | Text-only embedding model | Multimodal embedding model |
| 429 during bulk embedding | Rate/TPM limits | Retry with backoff, batch sensibly, adjust quota |

### 0.10 Five ideas the exam really tests

1. **Embeddings capture meaning as vectors.** Embedding models don't generate text.
2. **Same model (and dimensions) for indexing and querying.** Changing models means re-indexing.
3. **Chunk before embedding.** Respect the model's input token limit.
4. **Dimensions are a quality-vs-cost trade-off**, and the index field must match.
5. **Azure AI Search doesn't host embedding models.** Use integrated vectorization (recommended) or manual vectorization.

---

## 1. Scenario Questions

### Question 1: Model mismatch after an upgrade

A search app indexed 2 million chunks with **text-embedding-ada-002**. The team deploys **text-embedding-3-large** to improve quality and updates only the **query-time** embedding call. Search results become poor and irrelevant. What is the MOST likely cause and fix?

A. Temperature is too high  
B. Query vectors now come from a **different model** than the indexed vectors. **Re-embed and re-index the corpus with the new model** (or revert queries to the old one)  
C. The index needs more replicas  
D. `max_tokens` is too low

<details>
<summary>Answer</summary>

### ✅ B

Vectors from different models live in different spaces and are not comparable. The index and the query must use the **same embedding model**.

- **A, D ❌** Generation parameters; embeddings don't use them.
- **C ❌** Scale doesn't fix incompatible vectors.

**Trap:** "Upgrading the model" is not a drop-in change for a vector index.
</details>

---

### Question 2: Embedding model vs chat model

A developer calls an **embedding deployment** with the prompt "Summarise this contract in three bullets" and gets back an array of numbers. What is the correct conclusion?

A. The deployment is misconfigured and needs a higher temperature  
B. Embedding models **return vectors, not text**. Use a **chat/LLM model** to summarise  
C. The embedding model needs a system message  
D. Increase the embedding dimensions

<details>
<summary>Answer</summary>

### ✅ B

Embedding models convert input to vectors. Generation needs a chat/LLM model.
</details>

---

### Question 3: Dimension mismatch (snippet)

```json
{
  "index_vector_field": { "name": "contentVector", "dimensions": 1536 },
  "embedding_model": "text-embedding-3-large",
  "model_call": { "input": "chunk text", "dimensions": null },
  "error": "Vector dimension mismatch: expected 1536, got 3072"
}
```

Which TWO fixes would resolve this?

A. Update the index field to **3072** dimensions (and re-index)  
B. Request **`dimensions: 1536`** from `text-embedding-3-large` so vectors match the existing field (and re-embed the corpus consistently)  
C. Increase temperature  
D. Switch the vector field to a text field  
E. Lower `max_tokens`

<details>
<summary>Answer</summary>

### ✅ A and B

`text-embedding-3-large` defaults to 3072 dimensions. Either change the field to match, or shorten the output with the `dimensions` parameter. The whole corpus and the queries must use the **same** setting.

- **C, E ❌** Irrelevant to embeddings.
- **D ❌** Defeats vector search.

**Trap:** Read the error and the `dimensions: null` clue.
</details>

---

### Question 4: Storage and cost pressure

A corpus of 200 million chunks is embedded with a 3072-dimension model. Storage and memory costs are too high, and the team found that a shorter vector gives nearly the same retrieval quality on their own tests. What is the MOST appropriate action?

A. Switch to a chat model  
B. Use a model that supports shortened embeddings (such as `text-embedding-3` with the **`dimensions`** parameter), **evaluate** the smaller size on your own queries, then re-embed the corpus  
C. Reduce `max_tokens`  
D. Delete half the index fields at random

<details>
<summary>Answer</summary>

### ✅ B

Dimensions are a trade-off between quality and storage/compute. Validate on your own data, then apply consistently at index and query time.
</details>

---

### Question 5: Long documents

A team embeds each 40-page contract as a **single input** using a model with an 8,191-token limit. Requests fail or are truncated. What should they do?

A. Increase temperature  
B. **Chunk** the documents into segments that fit the model's input limit, then embed each chunk  
C. Use keyword search only  
D. Raise `max_tokens`

<details>
<summary>Answer</summary>

### ✅ B

Embedding models have input token limits, so long documents must be chunked. (Chunking strategy gets its own topic next.)
</details>

---

### Question 6: Integrated or manual vectorization?

A team wants to index documents from Blob Storage into Azure AI Search with **minimal custom code**, including chunking, embedding at index time, and automatic query-time conversion of plain-text queries. Which approach fits BEST?

A. Manual vectorization: write code to chunk, embed and push documents, and compute query vectors client-side  
B. **Integrated vectorization**: indexer + skillset (chunking and an **embedding skill**) at index time, and a **vectorizer** in the index at query time  
C. Use only keyword search  
D. Host the embedding model inside Azure AI Search

<details>
<summary>Answer</summary>

### ✅ B

Integrated vectorization offloads chunking and embedding (both phases) to the service and is the recommended default.

- **A ❌** Works but is more code and maintenance.
- **D ❌** Azure AI Search **doesn't host embedding models**.
</details>

---

### Question 7: Skill and vectorizer consistency

An index uses an **Azure OpenAI embedding skill** with a `text-embedding-3-small` deployment for indexing. A colleague configures the query-time **vectorizer** to call a different `text-embedding-3-large` deployment. Queries return poor results. What should be done?

A. Nothing, since both are OpenAI models  
B. Configure the vectorizer to use the **same embedding model deployment** as the skill  
C. Increase replicas  
D. Disable the vectorizer and use keywords only

<details>
<summary>Answer</summary>

### ✅ B

Skill (index time) and vectorizer (query time) must use the same model. Different models from the same family still produce incompatible vectors.
</details>

---

### Question 8: Multilingual and cross-language

A global company stores support articles in English, Spanish, French and Japanese. Users search in their own language and expect to find relevant articles in **any** language. Which choice is BEST?

A. An English-only embedding model  
B. A **multilingual embedding model** (for example, a multilingual Cohere Embed model in the Foundry catalog), with consistent use at index and query time  
C. A chat model to generate vectors  
D. Keyword search only

<details>
<summary>Answer</summary>

### ✅ B

Multilingual embeddings place equivalent meaning across languages close together, enabling cross-language retrieval.

- **A ❌** Poor non-English quality.
- **C ❌** Chat models don't produce vectors for search.
- **D ❌** Misses cross-language matches.
</details>

---

### Question 9: Searching images with text

An e-commerce site wants shoppers to type "red leather ankle boots" and find matching **product photos** that have no text captions. Which approach fits?

A. Text-only embeddings of product titles  
B. A **multimodal embedding model** that maps text and images into the **same vector space** (for example, Azure AI Vision multimodal embeddings or a multimodal Cohere Embed model), then vector search  
C. A chat model reading every image at query time  
D. Keyword search over image file names

<details>
<summary>Answer</summary>

### ✅ B

A shared text-image space lets a text query vector retrieve similar image vectors. Chat models reading every image at query time would be slow and costly.
</details>

---

### Question 10: Exact tokens

Users search an electronics catalogue for "ERR-2284" and "model XT-770B". A pure vector index returns loosely related items instead. What is the BEST improvement?

A. Use more dimensions  
B. Add **keyword (BM25)** retrieval and combine with vectors (**hybrid search**)  
C. Switch to a chat model  
D. Raise max_tokens

<details>
<summary>Answer</summary>

### ✅ B

Embeddings capture meaning and are weak at exact identifiers. Hybrid adds exact-term matching.

- **A ❌** Doesn't make embeddings exact-match tools.
</details>

---

### Question 11: Cost control during re-indexing

A nightly job re-embeds the **entire** 5-million-chunk corpus even though about 1% of documents change daily. Embedding costs and 429 errors are rising. Which TWO changes help MOST?

A. **Incremental indexing**: re-embed only new or changed chunks  
B. **Retry with exponential backoff** and sensible batching to respect rate limits  
C. Increase temperature  
D. Switch to a chat model for embeddings  
E. Re-embed twice for accuracy

<details>
<summary>Answer</summary>

### ✅ A and B

- Re-embedding unchanged content wastes tokens. Process changes only.
- Backoff and batching handle throttling.

- **C, D, E ❌** Irrelevant or harmful.
</details>

---

### Question 12: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | Embeddings from two different embedding models can be compared directly in the same index. | |
| 2 | Azure AI Search hosts embedding models for you. | |
| 3 | A vector can be converted back into the original text. | |
| 4 | Reducing the `dimensions` of an embedding can reduce storage cost, at some possible loss in quality. | |
| 5 | Query text should be embedded with the same model that was used for the indexed documents. | |
| 6 | An embedding model can generate a written answer to a user's question. | |
| 7 | `text-embedding-ada-002` supports the `dimensions` parameter. | |
| 8 | Vector fields in an index must have a dimension count that matches the embeddings stored in them. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **No** | Different spaces and possibly different dimension counts. |
| 2 | **No** | You supply the model (for example, a Foundry/Azure OpenAI deployment). |
| 3 | **No** | Vector conversion is one-way, so indexes keep text fields too. |
| 4 | **Yes** | The cost/quality trade-off of shortened embeddings. |
| 5 | **Yes** | Golden rule. |
| 6 | **No** | Embedding models output vectors only. |
| 7 | **No** | The `dimensions` parameter is a `text-embedding-3` feature. |
| 8 | **Yes** | Mismatch causes errors. |
</details>

---

### Question 13: Match the need to the embedding approach (drag-and-drop)

Match each need to: **Multilingual embeddings · Multimodal embeddings · Shortened dimensions · Chunking · Same-model rule · Hybrid search · Incremental indexing**.

| Need | Approach |
|---|---|
| A. Find relevant articles across English and Japanese | ? |
| B. Find product photos using a text query | ? |
| C. Cut vector storage cost by about 4× with minimal quality loss | ? |
| D. Documents exceed the model's input token limit | ? |
| E. Avoid garbage results after changing models | ? |
| F. Queries contain exact SKUs plus natural-language phrases | ? |
| G. Only 1% of documents change per day | ? |

<details>
<summary>Answer</summary>

| Need | Approach |
|---|---|
| A | **Multilingual embeddings** |
| B | **Multimodal embeddings** |
| C | **Shortened dimensions** |
| D | **Chunking** |
| E | **Same-model rule** (re-embed and re-index) |
| F | **Hybrid search** |
| G | **Incremental indexing** |
</details>

---

### Question 14: Authentication (Select TWO)

A team generates embeddings from a production service and wants to avoid long-lived secrets. Which TWO actions are MOST appropriate?

A. Use **Microsoft Entra ID** authentication (managed identity) to call the embedding endpoint  
B. Assign the **Cognitive Services OpenAI User** role on the Azure OpenAI resource to the calling identity  
C. Embed the API key in the client-side JavaScript  
D. Share one key across all developers  
E. Disable authentication

<details>
<summary>Answer</summary>

### ✅ A and B

Entra ID plus a least-privilege role is the recommended, keyless pattern.

- **C, D, E ❌** Insecure.
</details>

---

## 2. Mini Case Study: Fabrikam Global Support

### Background

Fabrikam is building a support search and RAG assistant on Microsoft Foundry and Azure AI Search.

1. **8 million** knowledge articles in **English, German, Japanese and Portuguese**. Customers search in their own language.
2. Articles can be **very long** (up to 60 pages).
3. Users search by concept and also by **part numbers** such as `FX-2290-C`.
4. Product images (diagrams) exist **without captions**. Support wants **text-to-image** search.
5. Costs are rising. Only about **2% of articles change daily**, but a nightly job re-embeds everything.
6. The team wants **minimal custom code** for indexing.
7. Security requires **no long-lived keys**.
8. After a recent change, results got much worse. Indexing used **model A**, but a developer switched the **query** embedding call to **model B**.

### Case Q1: Multilingual search

A. English-only embeddings  
B. **Multilingual embedding model**, used consistently at index and query time  
C. Translate nothing, use keyword search only  
D. Use a chat model as the embedder

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q2: Long articles

A. Embed each article as one input  
B. **Chunk** articles to fit the embedding model's token limit  
C. Increase temperature  
D. Truncate to the first sentence

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q3: Concepts plus part numbers

A. Vector only  
B. **Hybrid search** (keyword + vector), optionally with semantic ranking  
C. Keyword only  
D. Random

<details><summary>Answer</summary>

### ✅ B

Vectors for concepts, keyword for exact part numbers.
</details>

### Case Q4: Text-to-image search for diagrams

A. Text-only embeddings of file names  
B. A **multimodal embedding model** that places text and images in the same vector space  
C. A summarisation prompt  
D. Keyword search on metadata only

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q5: Rising cost

A. Re-embed more often  
B. **Incremental indexing**, and evaluate **shortened dimensions** if quality holds  
C. Increase chunk overlap to 100%  
D. Use a chat model

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q6: Minimal code and no long-lived keys

Which TWO satisfy requirements 6 and 7?

A. **Integrated vectorization** (indexer + skillset with chunking and embedding skill, plus a vectorizer)  
B. **Entra ID / managed identity** with an appropriate role on the embedding resource  
C. Manual vectorization with keys in source control  
D. Client-side keys

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q7: The bad results

Why are results worse, and what is the fix?

A. Temperature  
B. **Index and query vectors come from different models.** Use the same model for both, or **re-embed and re-index** with the new one  
C. Too many replicas  
D. Chunking is too large

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q8: Map the requirements

| Requirement | Solution |
|---|---|
| 4 languages | ? |
| 60-page articles | ? |
| Part numbers + concepts | ? |
| Caption-less diagrams | ? |
| 2% daily change | ? |
| Minimal code | ? |
| Poor results after a model switch | ? |

<details><summary>Answer</summary>

| Requirement | Solution |
|---|---|
| 4 languages | Multilingual embeddings |
| 60-page articles | Chunking |
| Part numbers + concepts | Hybrid search |
| Caption-less diagrams | Multimodal embeddings |
| 2% daily change | Incremental indexing |
| Minimal code | Integrated vectorization |
| Poor results after a model switch | Same-model rule, re-index |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Generator trap** | "An embedding model can answer questions." | It only outputs vectors. |
| **Mixed-model trap** | "Any embedding model works for queries." | Same model, version and dimensions as the indexed vectors. |
| **Upgrade trap** | "Just point queries at the newer model." | Re-embed and re-index everything. |
| **Dimension trap** | "More dimensions is always better." | Quality vs cost trade-off. The field must match. |
| **Hosting trap** | "Azure AI Search hosts the embedding model." | It doesn't. Bring your own model. |
| **Reversibility trap** | "We can decode a vector to text." | Conversion is one-way, so keep text fields too. |
| **Chunking trap** | "Embed whole documents." | Respect the token limit and chunk. |
| **Exact-match trap** | "Embeddings find exact IDs." | Add keyword, so hybrid. |
| **Ada trap** | "ada-002 supports `dimensions`." | That's a `text-embedding-3` feature. |
| **Multilingual trap** | "English model is fine for all languages." | Use a multilingual model. |
| **Image trap** | "Text embeddings search images." | Use a multimodal embedding model. |
| **Deployment-name trap** | "`model` is the base model name." | In Azure requests it's the **deployment name**. |
| **Key trap** | "Embed keys in app code." | Entra ID / managed identity plus a role. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| Search by meaning | Embeddings + vector search |
| Exact IDs/codes plus meaning | Hybrid search |
| Cross-language search | Multilingual embedding model |
| Text-to-image or image-to-image search | Multimodal embedding model |
| Docs longer than the input limit | Chunk before embedding |
| Storage/memory too high | Shorter `dimensions` (3-series), evaluate first |
| Results bad after model change | Same-model rule; re-embed and re-index |
| Dimension mismatch error | Match index field to model output (or set `dimensions`) |
| Minimal-code indexing in Azure AI Search | Integrated vectorization |
| Full control of pipeline | Manual vectorization |
| Query-time text-to-vector in the index | Vectorizer (same model as the skill) |
| Costly nightly re-embeds | Incremental indexing |
| 429 during bulk embedding | Backoff, batching, quota |
| Keyless access | Entra ID + Cognitive Services OpenAI User |
| Generate an answer | Chat/LLM model (not an embedding model) |

---

## 5. Quick Revision Sheet

```text
EMBEDDING = vector of numbers representing MEANING (close = similar)
Embedding models output VECTORS, never text answers.

SAME MODEL (+ version + dimensions) for INDEX and QUERY.
Change the model  ->  re-embed + re-index.

DIMENSIONS: more = more nuance but more cost; text-embedding-3 supports `dimensions`
            (ada-002 does not). Index field dimensions must MATCH.
INPUT LIMIT: chunk long docs first (3-series: 8,191 tokens; some models far less).

AZURE AI SEARCH: does NOT host embedding models.
  Integrated vectorization = indexer + skillset (chunking + embedding skill) + vectorizer
  Manual vectorization     = you chunk, embed, push vectors, send query vectors
  Skill (index) and vectorizer (query) must use the SAME model.
Vector conversion is ONE-WAY -> keep text fields and vector fields.

Vector = meaning.   Keyword = exact tokens.   Hybrid = both.
Multilingual model = cross-language.   Multimodal model = text <-> image.
Auth: Entra ID / managed identity + Cognitive Services OpenAI User (no long-lived keys).
Cost: incremental indexing, shorter dimensions, retries/backoff.
```

### Best-answer checklist

1. Does the task need **vectors** (meaning) or a **generated answer**? Pick embedding vs chat model accordingly.
2. Did anything change the **model, version or dimensions** between index and query? That's the usual culprit.
3. Does the content exceed the **token limit**? Chunk first.
4. Need **multiple languages** or **images**? Choose multilingual or multimodal models.
5. Exact identifiers involved? Add keyword, so hybrid.
6. For Azure AI Search, choose **integrated** (less code) or **manual** (more control) vectorization.
7. For cost, think **incremental indexing**, **shorter dimensions** and **backoff**.

---

**Next concept:** Chunking (same harder exam-style format)

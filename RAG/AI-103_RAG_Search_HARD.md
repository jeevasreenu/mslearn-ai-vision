# AI-103: RAG / Search (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, code/config snippets, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> This file is the **overview** of RAG and search. Embeddings, chunking, vector, semantic and hybrid search, Azure AI Search, RAG architecture and grounding each get their own deeper file next. Here the exam focus is **when RAG is the answer, how the pipeline fits together, and which retrieval approach fits which problem**.

---

## 0. Core Concepts (read first)

### 0.1 What is RAG?

**Retrieval-augmented generation (RAG)** combines **search** with an **LLM** so answers are **grounded in your data** instead of only the model's training knowledge.

```text
1. RETRIEVE  → user question → query an index / data store → relevant content
2. AUGMENT   → combine question + retrieved content (grounding data) into the prompt
3. GENERATE  → model answers using that content, ideally with citations
```

Why RAG exists:

| LLM limitation | How RAG helps |
|---|---|
| Trained on public data up to a cutoff | Brings in **current** information |
| Doesn't know your **private** documents | Retrieves from **your** content |
| Can hallucinate | Provides evidence to ground the answer |
| Can't cite sources | Retrieved chunks carry source references |
| Updating knowledge by retraining is slow | Update the **index**, not the model |
| Access control matters | Retrieval can enforce **permissions** per user |

### 0.2 Key building blocks

| Block | Role |
|---|---|
| **Data sources** | SharePoint, Blob storage, databases, OneLake, web, etc. |
| **Ingestion / indexing** | Extract, **chunk**, enrich, **embed**, and load content into an index |
| **Index** | Data structure optimised for retrieval (keyword, vector, semantic, or hybrid) |
| **Embeddings** | Numeric vectors representing meaning, used for vector similarity |
| **Retriever / search query** | Finds the top relevant chunks for a question |
| **Reranker** | Re-scores top results (for example, semantic ranking) |
| **Prompt / system message** | Tells the model *how* to use retrieved content (answer only from context, cite, fallback) |
| **LLM (generator)** | Writes the grounded answer |
| **Evaluation** | Measures retrieval quality and answer quality (groundedness, relevance) |

### 0.3 Retrieval methods (overview)

| Method | Matches by | Strong at | Weak at |
|---|---|---|---|
| **Keyword (full-text, BM25)** | Exact terms | Product codes, IDs, names, exact phrases | Synonyms, paraphrase, conversational queries |
| **Vector (similarity)** | **Meaning** via embeddings | Paraphrase, concepts, "means the same, different words" | Exact tokens (SKUs, error codes) |
| **Hybrid** | Keyword **+** vector, results fused (RRF) | Best general recall for RAG | Slightly more complexity |
| **Semantic ranking (reranker)** | Re-scores top results by meaning | Boosting the best passages to the top | Re-ranks only what was already retrieved |

> **Default recommendation for classic RAG:** **hybrid search + semantic ranking.** Hybrid improves recall, and semantic ranking improves precision at the top.

### 0.4 Classic RAG vs agentic retrieval (Azure AI Search)

| | **Classic RAG** | **Agentic retrieval** |
|---|---|---|
| Query handling | **One query** → hybrid search + semantic ranking | **LLM-based query planning** breaks a complex question into focused **subqueries** (planning uses chat history) |
| Execution | Single pipeline | Subqueries run **in parallel**, each **semantically reranked**, results **merged** |
| Output | Ranked results/chunks | Unified grounding data, **source references**, and an **activity log**. Can optionally synthesise an answer |
| Best for | Simple/straightforward requirements, **GA-feature** needs, low latency | **Complex, multi-part, context-dependent** questions; multi-source access |
| Trade-off | Struggles with multi-ask or ambiguous questions | **Adds latency** versus a single query (and LLM cost) |
| Maturity note | Proven approach | Some features, such as LLM query planning, were **preview** at the time of the source pages. Preview features have no SLA and aren't recommended for production |

> Example where agentic retrieval wins: *"Find me a hotel near the beach, with airport transportation, within walking distance of vegetarian restaurants."* One query rarely covers all three asks.

### 0.5 Foundry IQ (managed knowledge layer)

- **Foundry IQ** = managed knowledge layer for agents in Microsoft Foundry, **built on Azure AI Search** (you're not choosing "Foundry IQ vs Azure AI Search"; it's the front door to it).
- **Knowledge source** = a connection to data (Blob, SharePoint, OneLake, web, an existing search index, and more).
- **Knowledge base** = reusable, topic-centric bundle of one or more knowledge sources plus retrieval settings. **Many agents can share one knowledge base**, so each agent doesn't rebuild its own RAG pipeline.
- Uses the **agentic retrieval engine** (query planning, parallel keyword/vector/hybrid search, semantic reranking, optional answer synthesis with source references).
- Agents connect to a knowledge base through the **Model Context Protocol (MCP)** tool in Foundry Agent Service.
- Supports **document-level access control / permission-aware** retrieval.
- The connection guide requires a **Foundry project**. **Hub-based projects aren't supported** for this connection.

### 0.6 RAG vs prompting vs fine-tuning

| Need | Best first approach |
|---|---|
| Control tone, format, scope, fallback | **Prompt / instructions** |
| **Current or private facts**, citations, large changing document library | **RAG** |
| Consistent, specialised **behavior/style/format** at scale | **Fine-tuning** |
| Both fresh facts and consistent style | **RAG + fine-tuning together** |

Memory line: *"Is my problem about **accessing the right data**, or **controlling how the model behaves**?"* Data → RAG. Behavior → prompt, then fine-tune.

### 0.7 Security and governance

- Retrieval must honour **who is asking**. Use **document-level security / security trimming** so users only retrieve content they're authorised to see. **Filtering results after the model has seen them is too late.**
- Prefer **Microsoft Entra ID + RBAC** over keys.
- Sensitivity labels and permissions should flow through indexing and retrieval where supported.

### 0.8 Common RAG failure modes (diagnose before fixing)

| Symptom | Where the problem is | Fix |
|---|---|---|
| Right answer exists in the corpus but isn't retrieved | **Retrieval** (chunking, query, search type) | Hybrid + semantic ranking, better chunking, query rewriting, metadata filters |
| Correct passage retrieved but the model still invents | **Generation / prompt** | "Answer only from context; otherwise say you don't know"; lower temperature |
| Passage retrieved but truncated mid-thought | **Chunking** | Adjust chunk size/overlap, structure-aware chunking |
| Exact IDs/SKUs not found | **Vector-only** retrieval | Add keyword → **hybrid** |
| Paraphrased questions miss | **Keyword-only** retrieval | Add vector → **hybrid** |
| Answers cite outdated documents | **Index freshness** | Reindex / incremental update; add date metadata/filters |
| Users see content they shouldn't | **Security trimming** | Document-level access control |
| Multi-part questions answered partially | **Single-query limit** | Agentic retrieval / query decomposition |
| Too slow / costly | **Too many chunks / big prompt / LLM planning** | Retrieve fewer, rerank, smaller model, classic RAG for simple flows |
| Prompt too long, errors | **Context window** | Retrieve fewer/shorter chunks, rerank |

### 0.9 Evaluating RAG (know the names)

| Metric | Asks |
|---|---|
| **Groundedness** | Is the answer supported by the retrieved context? |
| **Relevance** | Does the answer address the question? |
| **Retrieval quality** | Did retrieval return the right chunks? |
| **Completeness / coherence** | Is the answer complete and well formed? |

Always evaluate **retrieval and generation separately** so you know which half is broken.

### 0.10 Five ideas the exam really tests

1. **RAG = retrieve → augment → generate.** Use it for **current/private facts**, not for behavior changes.
2. **Diagnose the layer first.** Retrieval problem vs generation/prompt problem.
3. **Hybrid + semantic ranking is the strong default** for classic RAG.
4. **Agentic retrieval = LLM query planning + parallel subqueries.** Better for complex questions, but adds latency.
5. **Security trimming happens at retrieval**, not after generation.

---

## 1. Scenario Questions

### Question 1: RAG or fine-tuning?

A company's HR policies change monthly. Employees want an assistant that answers questions **with citations to the current policy document**. The team proposes fine-tuning a model on the policy PDFs every month. What is the BEST recommendation?

A. Fine-tune monthly, because fine-tuning teaches facts reliably  
B. Use **RAG** over the policy documents, updating the **index** when policies change, and instruct the model to cite sources  
C. Increase the model temperature  
D. Use a larger context window and paste all policies into every prompt

<details>
<summary>Answer</summary>

### ✅ B

Frequently changing facts plus citations = RAG. Updating an index is cheap and fast. Retraining is slow, goes stale between runs, and can't provide traceable citations.

- **A ❌** Fine-tuning shapes behavior and style. It's a poor way to keep facts current.
- **C ❌** Irrelevant.
- **D ❌** Expensive, hits context limits, and doesn't scale to a large library.
</details>

---

### Question 2: Diagnose the layer

Logs for a RAG bot show that, for a failing question, the **correct policy passage is included in the prompt**. The model nevertheless answers with a made-up rule. What should you change FIRST?

A. The chunk size  
B. The search type from keyword to vector  
C. The **prompt/instructions**: answer only from the provided context, and say you don't know otherwise  
D. The index freshness

<details>
<summary>Answer</summary>

### ✅ C

Retrieval succeeded. The failure is in **generation behavior**. Add a grounded-only rule and an explicit fallback.

- **A, B, D ❌** Retrieval-layer fixes for a problem that isn't in retrieval.

**Trap:** The stem says the correct passage **is** in the prompt. That evidence rules out the retrieval layer.
</details>

---

### Question 3: Retrieval miss on exact identifiers

Users search a parts catalogue with queries like **"error code E-4471"** and **"SKU TX-9920-B"**. The index uses **vector search only**. Relevant parts aren't returned, though they exist. What is the BEST fix?

A. Increase `max_tokens`  
B. Move to **hybrid search** (keyword + vector), optionally with semantic ranking  
C. Increase temperature  
D. Use a smaller embedding

<details>
<summary>Answer</summary>

### ✅ B

Vector search matches meaning and is weak on exact tokens such as IDs and codes. Hybrid adds keyword (BM25) matching and fuses results.

- **A, C ❌** Generation parameters don't affect retrieval.
- **D ❌** Doesn't address exact-token matching.
</details>

---

### Question 4: Paraphrase miss

An FAQ index uses **keyword search only**. A user asks "How do I get my money back?" but the document says "Refund policy". Nothing relevant is returned. What should you do?

A. Add **vector** retrieval (hybrid), so meaning-based matches are found  
B. Add more stop words  
C. Increase `max_tokens`  
D. Lower temperature to 0

<details>
<summary>Answer</summary>

### ✅ A

Keyword search needs the same terms. Vector search matches concepts. Hybrid combines the strengths of both.
</details>

---

### Question 5: Classic RAG or agentic retrieval?

A travel assistant receives questions such as *"Find a hotel near the beach, with airport transfers, and walkable to vegetarian restaurants"*, often depending on earlier chat turns. Single-query retrieval returns partial matches. Which approach fits BEST?

A. Classic RAG with a single hybrid query only  
B. **Agentic retrieval**: LLM-based query planning decomposes the question into subqueries, runs them in parallel, reranks and merges results  
C. Keyword search only  
D. Increase the temperature

<details>
<summary>Answer</summary>

### ✅ B

Multi-part, context-dependent questions are the target of agentic retrieval. Trade-off: **added latency** and LLM cost compared with a single-query pipeline.

- **A ❌** Single query misses parts of multi-ask questions.
- **C ❌** Weakest option.
- **D ❌** Irrelevant.
</details>

---

### Question 6: When classic RAG is the better choice (Select TWO)

For which TWO situations is **classic RAG** (hybrid search + semantic ranking) a better fit than agentic retrieval?

A. Simple, single-intent questions where **low latency** matters  
B. A requirement to use only **generally available (GA)** features and avoid preview functionality  
C. Highly complex, multi-part questions that depend on prior chat turns  
D. Questions that need to be decomposed into many subqueries across several sources  
E. Questions where nothing needs to be retrieved

<details>
<summary>Answer</summary>

### ✅ A and B

Classic RAG is proven, simpler and faster, and suits GA-only requirements. C and D describe agentic strengths. E isn't a RAG situation.

**Trap:** "Agentic is newer" doesn't mean "always better". It adds latency and may involve preview features.
</details>

---

### Question 7: Security trimming

A RAG assistant indexes all company documents, including HR and legal files. Testing shows that a junior employee's query can return **snippets from restricted HR documents**. The team suggests telling the model "never reveal confidential content". What is the MOST appropriate fix?

A. The prompt instruction is enough  
B. Enforce **document-level access control at retrieval time** (security trimming using the user's identity/permissions) so unauthorised content is never retrieved  
C. Lower temperature  
D. Increase the number of retrieved chunks

<details>
<summary>Answer</summary>

### ✅ B

If restricted content reaches the prompt, the damage may already be done. Enforce permissions **before** the model sees data. Prompts guide, they don't enforce.

- **A ❌** Not enforcement.
- **C, D ❌** Irrelevant or harmful.
</details>

---

### Question 8: Shared knowledge for many agents

An enterprise has 12 agents. Each team has built its own chunking, embedding and indexing pipeline over overlapping SharePoint and Blob content, producing inconsistent answers and heavy maintenance. What should they adopt?

A. A separate vector database per agent  
B. **Foundry IQ knowledge bases**: define reusable, topic-centric knowledge bases over shared knowledge sources, and connect multiple agents to them  
C. Fine-tune each agent  
D. Put all documents directly into each agent's instructions

<details>
<summary>Answer</summary>

### ✅ B

Foundry IQ (built on Azure AI Search) centralises retrieval so many agents share a permission-aware knowledge layer instead of rebuilding pipelines.

- **A ❌** Duplicates the problem.
- **C ❌** Doesn't solve retrieval or freshness.
- **D ❌** Doesn't scale and goes stale.
</details>

---

### Question 9: Connecting Foundry IQ (config snippet)

```json
{
  "agent_service": "Foundry Agent Service",
  "project_type": "hub-based project",
  "goal": "Connect a Foundry IQ knowledge base to the agent via MCP",
  "result": "Connection not supported"
}
```

What is the MOST likely cause and fix?

A. The knowledge base needs a higher temperature  
B. **Hub-based projects aren't supported** for this connection. Use a **Foundry project**  
C. The agent needs a larger `max_tokens`  
D. The index needs a different embedding

<details>
<summary>Answer</summary>

### ✅ B

The Foundry IQ-to-Agent Service connection requires a Foundry project. Hub-based projects aren't supported.

**Trap:** Scan the snippet for `project_type`. This links back to the Foundry fundamentals topic.
</details>

---

### Question 10: Context window

A RAG app retrieves the top **40 chunks** (about 500 tokens each) and sends all of them to a model with a **16,000-token** context window, then asks for a 1,500-token answer. Requests fail intermittently. Which TWO changes help MOST?

A. **Retrieve fewer chunks** and/or **rerank** so only the best few are sent  
B. Reduce chunk size where appropriate  
C. Increase temperature  
D. Switch from hybrid to keyword search  
E. Remove the system message

<details>
<summary>Answer</summary>

### ✅ A and B

$$40 \times 500 = 20{,}000 \text{ tokens} > 16{,}000$$

Prompt plus output must fit the context window. Send fewer, more relevant chunks (semantic ranking helps choose them).

- **C, D, E ❌** Don't address the token budget.
</details>

---

### Question 11: Evaluate retrieval and generation separately

A team measures only the final answer quality of their RAG bot, which is poor, and can't tell whether to fix search or the prompt. What should they do?

A. Evaluate **retrieval** (did the right chunks come back?) and **generation** (groundedness, relevance) **separately**, then fix the weaker layer  
B. Switch models immediately  
C. Increase temperature  
D. Fine-tune

<details>
<summary>Answer</summary>

### ✅ A

Separating the layers tells you which half is broken. Check retrieval quality, then groundedness and relevance.
</details>

---

### Question 12: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | RAG retrieves relevant content and adds it to the prompt so the model can generate a grounded answer. | |
| 2 | Fine-tuning is the best way to keep an assistant's knowledge of changing documents current. | |
| 3 | Hybrid search combines keyword and vector retrieval. | |
| 4 | Semantic ranking re-scores results that were already retrieved. | |
| 5 | Agentic retrieval can add latency compared with a single-query pipeline. | |
| 6 | Telling the model not to reveal restricted content replaces the need for access control on retrieval. | |
| 7 | Foundry IQ is built on top of Azure AI Search. | |
| 8 | Vector search is the best method for exact SKU or error-code matches. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **Yes** | Retrieve → augment → generate. |
| 2 | **No** | Facts that change belong in the index (RAG). |
| 3 | **Yes** | Hybrid fuses both. |
| 4 | **Yes** | Reranking improves ordering of retrieved candidates. |
| 5 | **Yes** | Multiple subqueries and LLM planning add time. |
| 6 | **No** | Enforcement must happen at retrieval. |
| 7 | **Yes** | The knowledge base is an object on your Azure AI Search service. |
| 8 | **No** | Keyword (or hybrid) handles exact tokens better. |
</details>

---

### Question 13: Match the problem to the layer (drag-and-drop)

Match each symptom to the **layer** to fix: **Retrieval · Chunking · Prompt/generation · Index freshness · Security trimming · Retrieval approach (agentic)**.

| Symptom | Layer |
|---|---|
| A. Correct passage retrieved, model still invents | ? |
| B. Cites last year's policy | ? |
| C. Passages cut off mid-explanation | ? |
| D. Multi-part question only half answered | ? |
| E. Intern sees restricted documents | ? |
| F. Exact part numbers never found with vector-only search | ? |

<details>
<summary>Answer</summary>

| Symptom | Layer |
|---|---|
| A | **Prompt/generation** |
| B | **Index freshness** |
| C | **Chunking** |
| D | **Retrieval approach (agentic retrieval / query decomposition)** |
| E | **Security trimming** |
| F | **Retrieval** (add keyword, so hybrid) |
</details>

---

### Question 14: Which approach? (Select TWO)

Which TWO scenarios are BEST solved with RAG rather than prompt changes or fine-tuning?

A. An assistant must answer questions about **newly published product manuals** and cite page numbers  
B. An assistant must **always reply in a formal brand voice**  
C. A support bot must use **the latest internal troubleshooting articles**, which are updated weekly  
D. A model must always output **a specific JSON structure**  
E. A model should refuse to discuss competitors

<details>
<summary>Answer</summary>

### ✅ A and C

- **A, C ✅** Current/private facts with citations.
- **B, D, E ❌** Behavior/format/scope problems. Use instructions, structured outputs, or (at scale) fine-tuning.
</details>

---

## 2. Mini Case Study: Contoso Legal Research

### Background

Contoso Legal is building a research assistant on Microsoft Foundry.

1. It must answer questions from **100,000 case files and memos** stored in **SharePoint and Blob storage**, with **citations**.
2. Files are **updated daily**.
3. Lawyers search by **case numbers** (for example, `CV-2024-00817`) and also by **concepts** ("breach of fiduciary duty by a founder").
4. Some questions are **multi-part** ("compare how two jurisdictions treat X and summarise recent rulings").
5. Associates must only see **cases they are staffed on**.
6. Six other internal agents need the **same legal knowledge** and the team doesn't want six pipelines.
7. In testing, the correct passage is sometimes retrieved but the bot **adds statements not in the text**.
8. Leadership wants **GA features only** for the first release.

### Case Q1: Retrieval method for requirement 3

A. Vector only  
B. Keyword only  
C. **Hybrid search + semantic ranking**  
D. Random sampling

<details><summary>Answer</summary>

### ✅ C

Case numbers need exact keyword matching, and concepts need vector similarity. Hybrid covers both, and semantic ranking sharpens the top results.
</details>

### Case Q2: Daily updates

A. Fine-tune daily  
B. **Update the index incrementally** as documents change  
C. Rebuild the model weekly  
D. Ignore updates

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q3: Access restriction

A. Prompt: "Only show cases the user is staffed on"  
B. **Document-level access control / security trimming at retrieval**, tied to the user's identity  
C. Hide the UI button  
D. Lower temperature

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q4: Shared knowledge for six more agents

A. Six separate indexes  
B. A **Foundry IQ knowledge base** shared by all agents (connected through the MCP tool)  
C. Fine-tune each agent  
D. Paste documents into instructions

<details><summary>Answer</summary>

### ✅ B

Remember that the Agent Service connection needs a **Foundry project**, not a hub-based project.
</details>

### Case Q5: Multi-part questions vs the "GA only" rule

Requirement 4 favours agentic retrieval, but requirement 8 says GA features only. What is the BEST approach?

A. Ignore requirement 8  
B. Start with **classic RAG** (hybrid + semantic ranking, GA) for the first release, **verify the current GA status** of the agentic features you need, and adopt agentic retrieval when its needed capabilities are GA or the preview risk is accepted  
C. Drop requirement 4  
D. Use keyword search only

<details><summary>Answer</summary>

### ✅ B

Respect the stated constraint, and validate feature status at decision time, since preview and GA status changes.
</details>

### Case Q6: Hallucinated additions

A. Chunk size  
B. **Grounded-only instructions with an explicit fallback**, a low temperature, and a groundedness evaluation  
C. Switch to vector-only  
D. Add more documents

<details><summary>Answer</summary>

### ✅ B

Retrieval already returned the right passage, so the issue is generation behavior (same logic as Question 2).
</details>

### Case Q7: Map requirements to components

| Requirement | Component |
|---|---|
| Case numbers + concepts | ? |
| Daily freshness | ? |
| Per-case permissions | ? |
| Shared across 7 agents | ? |
| No invented statements | ? |

<details><summary>Answer</summary>

| Requirement | Component |
|---|---|
| Case numbers + concepts | Hybrid search + semantic ranking |
| Daily freshness | Incremental indexing |
| Per-case permissions | Document-level security trimming at retrieval |
| Shared across 7 agents | Foundry IQ knowledge base |
| No invented statements | Grounded-only prompt + fallback + groundedness evaluation |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Fine-tune-for-facts trap** | "Fine-tune so the model knows our documents." | Changing/private facts → RAG. Fine-tuning shapes behavior. |
| **Wrong-layer trap** | "Bot invents things, so fix chunking." | If the right passage was retrieved, fix the prompt/generation. |
| **Vector-only trap** | "Vector search finds everything." | Weak on exact IDs/codes. Use hybrid. |
| **Keyword-only trap** | "Keyword search is enough." | Misses paraphrases. Add vectors. |
| **Rerank trap** | "Semantic ranking finds documents the search missed." | It only **re-scores** already retrieved results. |
| **Agentic-always trap** | "Agentic retrieval is always better." | Adds latency/cost, may involve preview features. Classic fits simple/GA needs. |
| **Prompt-security trap** | "Tell the model to hide confidential data." | Enforce access control at retrieval. |
| **Context trap** | "Send as many chunks as possible." | Token budget and noise. Retrieve fewer, rerank. |
| **Freshness trap** | "Retrain to update knowledge." | Update the index. |
| **Foundry-IQ-vs-Search trap** | "Foundry IQ replaces Azure AI Search." | It's built **on** Azure AI Search. |
| **Hub trap** | "Connect Foundry IQ from any project." | Requires a **Foundry project**, not hub-based. |
| **Evaluate-blind trap** | "Judge only the final answer." | Evaluate retrieval and generation separately. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| Current/private facts, citations | **RAG** |
| Behavior, tone, scope | Prompt/instructions |
| Consistent specialised style at scale | Fine-tuning (optionally with RAG) |
| Exact IDs/names/codes | Keyword (**hybrid**) |
| Paraphrase/conceptual queries | Vector (**hybrid**) |
| Best default classic RAG | **Hybrid + semantic ranking** |
| Multi-part, context-dependent questions | **Agentic retrieval** (accept extra latency) |
| Low latency, simple questions, GA only | **Classic RAG** |
| Many agents need shared knowledge | **Foundry IQ knowledge base** |
| Users must only see permitted content | **Document-level security trimming at retrieval** |
| Correct passage retrieved but wrong answer | Fix **prompt/generation** |
| Right doc exists but not retrieved | Fix **retrieval/chunking/search type** |
| Outdated answers | Fix **index freshness** |
| Prompt too large | Fewer chunks, rerank, smaller chunks |
| Unsure which half is broken | Evaluate retrieval and generation separately |

---

## 5. Quick Revision Sheet

```text
RAG = RETRIEVE → AUGMENT → GENERATE
Use RAG for: current / private facts, citations, big changing libraries
Use prompt for: behavior.  Fine-tune for: consistent style at scale.

SEARCH TYPES
  Keyword (BM25)   = exact terms
  Vector           = meaning (embeddings)
  Hybrid           = keyword + vector (fused)
  Semantic ranking = rerank the retrieved results

CLASSIC RAG    = one query: hybrid + semantic ranking  (simple, faster, GA)
AGENTIC RETR.  = LLM query planning → parallel subqueries → rerank → merge
                 (complex questions; adds latency; some features preview)
FOUNDRY IQ     = knowledge bases on Azure AI Search, shared by many agents,
                 connected via MCP, needs a Foundry project (not hub-based)

SECURITY: enforce permissions at RETRIEVAL (security trimming), not in the prompt
EVALUATE: retrieval quality + groundedness + relevance, separately

Right passage retrieved + wrong answer  = PROMPT problem
Right passage not retrieved             = RETRIEVAL / CHUNKING / SEARCH TYPE problem
```

### Best-answer checklist

1. Is it a **facts/data** problem (RAG) or a **behavior** problem (prompt/fine-tune)?
2. Does the stem show **where** it fails: retrieval, chunking, generation, freshness, security?
3. Exact tokens → **keyword**. Meaning → **vector**. Unsure → **hybrid + semantic ranking**.
4. Multi-part or context-dependent questions → **agentic retrieval**. Mind latency and preview status.
5. Permissions → **enforce at retrieval**.
6. Many agents → **shared knowledge base** (Foundry IQ).
7. Token limits → fewer, better chunks.

---

**Next concept:** Embeddings (same harder exam-style format)

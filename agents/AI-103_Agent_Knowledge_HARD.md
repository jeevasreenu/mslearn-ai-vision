# AI-103: Agent Knowledge (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, config/API snippets, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Scope: **how agents get enterprise knowledge through Foundry IQ**: knowledge bases, knowledge sources (indexed vs remote), the agentic retrieval engine, **retrieval reasoning effort**, output modes (extractive vs synthesized), connecting a knowledge base to an agent (project connection, MCP tool, toolbox), identity and permission enforcement, lifecycle (refresh, status), and choosing Foundry IQ vs the Azure AI Search tool vs file search.
> Already covered elsewhere, so only referenced here: the individual **grounding tools and identity patterns** (Grounding file), **classic vs agentic RAG** (RAG architecture file), **Azure AI Search service, indexers and RBAC roles** (Azure AI Search file), **semantic ranker** (Semantic search file), **agent memory** (Agent memory file).
> Foundry IQ is **moving fast**: some features are GA (stable REST API), others are preview, and the portals expose preview-only access to all agentic retrieval features. Item markers: unmarked = Microsoft Learn or Microsoft blogs. *(secondary)* = non-Microsoft pages and community posts. *(general)* = standard behavior from general knowledge that I couldn't confirm in the pages I found. **Verify *(secondary)* and *(general)* items and any preview status on Microsoft Learn before test day.**

---

## 0. Core Concepts (read first)

### 0.1 What "agent knowledge" means

A Foundry model has a **knowledge cutoff** and can't see your proprietary data. **Agent knowledge** = the mechanisms that give an agent **access to enterprise and external content at run time**. In Foundry Agent Service there are several routes:

| Route | What it is | Best for | Covered in |
|---|---|---|---|
| **File search** | A vector store the service parses, chunks, embeds and searches | Files attached to an agent or a conversation | Grounding file |
| **Azure AI Search tool** | Direct query of **one** existing index | Simple grounding on one index | Grounding file |
| **SharePoint tool / Fabric tool / web search** | Single-purpose grounding tools | One source type each | Grounding file |
| **Foundry IQ knowledge base** | A reusable, **multi-source**, permission-aware knowledge layer with **agentic retrieval**, connected to agents through **MCP** | Many sources, many agents, complex questions | **This file** |

> **Foundry IQ** *enables agents to access, process and act on knowledge from anywhere*. You create a **knowledge base** that connects to one or more **knowledge sources**. The **agentic retrieval engine** processes queries, and an **optional LLM** (from Azure OpenAI in Foundry Models) adds **query planning and reasoning**. Agents in Foundry Agent Service call the knowledge base to retrieve relevant content.

### 0.2 The Foundry IQ components

| Component | Meaning |
|---|---|
| **Knowledge base** | The **top-level resource** that groups one or more knowledge sources under **one endpoint** and orchestrates agentic retrieval. It defines **which sources to query** and **retrieval parameters** (reasoning effort, output mode, and so on). **Multiple agents can share the same knowledge base.** |
| **Knowledge source** | A **top-level resource on your Azure AI Search service** that defines content used in agentic retrieval. Each is **either indexed or remote**. Knowledge sources are **created independently**, then **referenced in a knowledge base**. A knowledge base can reference several, and the engine queries **all of them in one request** (**subqueries are generated for each knowledge source**) |
| **Agentic retrieval** | The **multi-query pipeline**: decomposes complex questions into subqueries, runs them **in parallel**, **semantically reranks**, and returns a unified response. The LLM for planning is **optional but recommended** |
| **Azure AI Search (Foundry IQ service)** | The underlying indexing and retrieval infrastructure. **You still need a Foundry IQ (Azure AI Search) service** to use knowledge bases. It's the *front door* to Azure AI Search, not an alternative to it |

Relationship facts:
- **Foundry IQ vs agentic retrieval:** Foundry IQ = knowledge bases + knowledge sources + native integrations with Azure OpenAI in Foundry Models and Foundry Agent Service. **Agentic retrieval is the engine** that powers it. For custom solutions you can call agentic retrieval **directly through the Azure AI Search APIs**.
- **Foundry Agent Service is not required.** You can call a knowledge base from Foundry Agent Service, **Microsoft Agent Framework**, or **any application** that supports the knowledge base APIs. Agent Service just provides a turnkey hosting platform with built-in support.
- **Foundry IQ vs Fabric IQ vs Work IQ:** three separate Microsoft "IQ" layers. **Foundry IQ** = enterprise knowledge for agents. **Fabric IQ** = a semantic layer over business data. **Work IQ** = Microsoft 365 work signals. **Copilot knowledge sources and Foundry IQ knowledge sources aren't interchangeable** *(secondary)*.

### 0.3 Knowledge sources: indexed vs remote (high-yield)

| | **Indexed** knowledge source | **Remote** knowledge source |
|---|---|---|
| How content is handled | **Ingested** into Azure AI Search, then chunked, enriched, vectorised and stored in an index you own | **Queried live at retrieval time**, **never copied into an index** |
| What gets generated | A **data source, skillset, index and indexer** (managed pipeline) | Nothing to ingest. The source or tool is called at query time |
| Strengths | **Predictable latency**, custom **enrichment and vectorization**, control over the index, scheduled **incremental refresh** | **No duplicate copy**, always-current data, existing governance applies (for example, Microsoft 365) |
| Weaknesses | Index storage/cost, **sync delay** | Latency depends on the live source, less control over enrichment |
| Permissions | **ACL synchronisation** for supported sources, Purview sensitivity labels honored, **query-time trimming** | Enforced **at the source at query time**, under the **caller's identity** *(secondary: needs a user token separate from the service credential)* |

**Source kinds** (the exact list differs by API version and portal, so treat as examples):

| Kind | Indexed or remote | Notes |
|---|---|---|
| `searchIndex` (existing **Azure AI Search index**) | Indexed | Wraps an index you already built, including text and vectors. **Must be on the same search service as the knowledge base** and have **plain text or vector content with a semantic configuration** |
| `azureBlob` (Blob Storage / ADLS Gen2) | Indexed | Generates an indexer pipeline from a blob container |
| **Azure SQL** *(portal)* | Indexed *(secondary)* | Rows from a table or view |
| **Microsoft OneLake** | Indexed | Ingests files from a Fabric lakehouse. **Preview** in the page I found. Needs the search service's **system-assigned managed identity** with the **Admin role on the Fabric workspace**. **Shortcut-derived content is excluded from permission-aware retrieval in the preview** |
| **Microsoft SharePoint (indexed)** | Indexed | Crawls SharePoint. **GA in the 2026-10-01 REST API**. Uses `contentExtractionMode` (**minimal** or **standard**). SharePoint indexer prerequisites and limits apply |
| **Microsoft SharePoint (remote)** | Remote | Queries SharePoint at run time **with Microsoft 365 governance**, instead of keeping a copy |
| **Web** (Bing-based) | Remote | **Real-time public web data**, with **domain restrictions** (Web IQ is the next-generation web grounding). Not supported with `minimal` effort |
| **MCP** | Remote | Lets the retrieval pipeline **call tools on an existing MCP server**. Was **private preview** in an April 2026 blog *(secondary)*, later listed among preview sources |
| **Fabric IQ, Work IQ, File Search, Azure SQL, MCP** | Preview sources | The June 2026 Foundry blog lists these as **new preview knowledge sources** |

Limits and choices:
- **Up to 10 knowledge sources per knowledge base** *(secondary; the reasoning-effort page states the 10 cap for `minimal`)*.
- Choose **indexed** when you need **predictable latency, custom enrichment/vectorization and control over the index**. Choose **remote** when you want **live data, no copy, and source-native governance**.

### 0.4 Retrieval reasoning effort (very high-yield)

**Reasoning effort controls how much LLM processing happens before retrieval** (query planning), trading **relevance** against **cost and latency**. More LLM work improves relevance, but it takes longer and uses billable LLM resources.

| Level | LLM planning? | Behavior | Limits / notes |
|---|---|---|---|
| **`minimal`** | **No** (model-free) | **Disables LLM-based query planning.** Issues **direct text and vector searches across all knowledge sources**, returns the **best-matching passages**. **No query expansion.** Predictable and easy to control. The `alwaysQueryKnowledgeSource` request property is **ignored** | **`outputMode` must be `extractiveData`.** **Answer synthesis and web knowledge aren't supported.** Max **10** knowledge sources. Recommended for **migrations from the Search API** or when **you manage planning yourself** |
| **`low`** | Yes | **Default** agentic mode: **a single pass of LLM-based query planning and knowledge-source selection** | Needs a model |
| **`medium`** | Yes | More thorough: **iterative search** when initial results don't meet relevance standards (FAQ: *iterative search depends on specifying a medium retrieval reasoning effort*) | Needs a model. Higher cost/latency |
| **`auto`** | Yes | **Preview**, requires a supporting preview API version | Verify status |

Rules:
- **GA 2026-10-01 REST API** supports `minimal`, `low` and `medium`.
- Set it **in the knowledge base** (default for all queries) **or in a retrieve request** (**the request overrides the knowledge base**).
- **Set it explicitly** rather than relying on a service default, which can vary by enabled features.
- **Planning effort and answer synthesis are separate choices.**
- **A model is required** for `low`, `medium`, `auto`, **answer synthesis** and **web summarization**. **Not required** for model-free `minimal` extraction.
- **Parallel processing of multiple subqueries requires LLM query planning.** Without an LLM, `minimal` simply merges results from multiple queries across sources.
- **Supported models for query planning:** **gpt-4o, gpt-4.1 and gpt-5 series** from Azure OpenAI in Foundry Models. You specify the **model deployment when you create the knowledge base**. The search service's managed identity needs access to the Azure AI services resource (**Cognitive Services User**, per the preview page).

### 0.5 What the engine returns: extractive data vs synthesized answer

| | **Extractive data** (`extractiveData`) | **Answer synthesis** |
|---|---|---|
| Output | **Raw content passages with citations**, so the **agent reasons over the evidence** and can trace answers to source documents | A **natural-language answer** composed by the knowledge base's LLM, **with source references** |
| LLM in the knowledge base | Not required (`minimal`) | **Required** |
| Latency/cost | Lower | Higher (extra LLM step) |
| Pick when | The **agent's model should do the final reasoning**, you want maximum control, or you want the cheapest path | You want a **ready-to-use cited answer** or less work for the agent |
| Notes | The only output mode allowed with `minimal` | **Generally available in Search REST API 2026-10-01** (model-backed planning and answer synthesis) |

The response also carries **source references and an activity log** (what was planned and queried), which helps debugging and citation display.

### 0.6 Connecting a knowledge base to an agent

**Connection pattern (Learn):** the knowledge base is reached through the **Model Context Protocol (MCP)**. Every knowledge base is **also a standalone MCP server exposing one tool, `knowledge_base_retrieve`**, so any MCP-compatible client can call it (LangGraph through `langchain-mcp-adapters` in a community tutorial *(secondary)*).

Steps in Foundry Agent Service:
1. **Create a project connection** that targets the knowledge base's MCP endpoint.
2. **Optimise agent instructions for knowledge retrieval** (tell the agent **when to call the knowledge base tool**, to **ground answers on retrieved content** and to **show citations**; *general*).
3. **Create an agent with the MCP tool** that references the connection.
4. **Invoke the agent** with a query. The knowledge base then plans, searches, reranks and (optionally) synthesises, and the agent uses the result to ground its answer.

Prerequisites and facts:
- A **Foundry IQ service with a knowledge base** containing one or more knowledge sources.
- A **Foundry project with an LLM deployment**. **Hub-based projects aren't supported.**
- Supported on **basic and standard agent setups**.
- Latest preview **Python SDK `azure-ai-projects` 2.0.0 or later** (or the preview REST API shown in the article).
- **RBAC recommended for production.** To assign roles you need **Owner or User Access Administrator** (or `Microsoft.Authorization/roleAssignments/write`) on both resources. If roles aren't feasible, **key-based authentication** is the fallback.
- **Foundry User** on the project's parent resource (access model deployments, create agents).
- On the search side, the **identity that calls the knowledge base** needs read access (**Search Index Data Reader**, *per a community sample*). The **Foundry IQ service needs RBAC enabled** (API access control set to **Both** or **Role-based access control**) for keyless access.
- **Hosted agents:** you can reach a knowledge base **through a toolbox**. The toolbox exposes the knowledge base's **MCP endpoint as a single tool**, and the agent calls it with **its own managed identity** (keyless), after you **grant the agent access to the knowledge base**. The knowledge base uses a chat model deployment to synthesise answers.

| Connector | Connection type | Best for |
|---|---|---|
| **Foundry IQ knowledge base** (MCP tool) | **RemoteTool** (MCP endpoint) *(secondary sample)* | **Agentic retrieval**: query planning, multi-source, richer citations |
| **Azure AI Search tool** | **CognitiveSearch** connection *(secondary sample)* | Simple grounding, a **single index**, direct query |
| **File search** | Vector store | Files attached to agents/conversations |

### 0.7 Security and governance

- **Permission-aware responses:** Foundry IQ **enforces user permissions** and returns grounded answers **with citations**.
- **ACL sync** for supported indexed sources and honoring of **Microsoft Purview sensitivity labels**. **Query-time trimming** ensures only authorised content is returned.
- **Run queries under the caller's Microsoft Entra identity** for end-to-end permission enforcement. Identity flows through two channels *(secondary)*: the **service credential** (the agent/MI calling the knowledge base) and the **end user's token** for per-user filtering on remote or permission-trimmed sources.
- A **service identity with broad read access cannot, by itself, enforce per-user permissions.** (This is the same lesson as the Grounding file's OBO discussion.)
- **Federated/remote sources** (SharePoint remote, web, MCP) are queried live, so **permissions are evaluated at the source**. **Indexed sources** rely on **synced ACLs**.
- **Preview and external services:** preview APIs that connect to **other Microsoft or third-party services** may process or store data **outside the Azure compliance boundary**. It's **your responsibility** to manage data flow and add your own responsible-AI mitigations (metaprompts, content filters).
- **Encryption, permission sync and sensitivity-label governance controls** were announced in preview in June 2026.

### 0.8 Lifecycle, freshness, status, pricing

| Topic | Fact |
|---|---|
| **Freshness** | Indexed sources: **schedule recurring indexer runs for incremental refresh**. Indexing and synchronisation are triggered automatically. Remote sources are live |
| **Ingestion enrichment** | Automatic **chunking, embedding generation, metadata extraction**. Layout-aware ingestion and image enrichment were announced in preview (June 2026) |
| **Status** | **Knowledge bases are generally available** (June 2026 announcement). **Model-backed planning and answer synthesis are GA in Search REST API 2026-10-01.** Other capabilities (for example `auto` effort, some source kinds, portal experiences) are **preview**. **Availability depends on the REST API version** you use. The Foundry and Azure portals **continue to provide preview-only access to all agentic retrieval features** |
| **Pricing** | Knowledge bases need an **agentic retrieval plan** (see Azure AI Search file). **Foundry IQ Serverless (preview)** offers scale-to-zero consumption pricing with a **Developer tier in public preview** |
| **LLM costs** | Planning and synthesis use **billable LLM calls**. Higher effort = higher cost/latency |

### 0.9 When to choose which knowledge route (decision rules)

```text
Files attached to this agent/conversation                      → File search (vector store)
One existing index, simple grounding                           → Azure AI Search tool (1 index per tool)
Many sources (Blob, SharePoint, OneLake, web, MCP…), many agents, complex questions → Foundry IQ knowledge base
Need live data, no copy, source-native governance              → Remote knowledge source
Need predictable latency, custom enrichment, scheduled refresh → Indexed knowledge source
Lowest cost/latency, you plan queries yourself                 → minimal effort + extractiveData (no LLM)
Standard agentic retrieval                                     → low effort (default)
Hard, multi-hop questions needing iteration                    → medium effort
Agent should reason over raw evidence                          → extractiveData
Want a ready-made cited answer                                 → answer synthesis (needs a model)
Per-user permissions                                           → ACL sync (indexed) / caller identity (remote) – not a broad service identity
Not using Foundry Agent Service                                → Call the KB via MCP or the Search APIs (LangGraph, Agent Framework…)
```

### 0.10 Common problems and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Can't connect a knowledge base to the agent | **Hub-based project** | Use a **Foundry project** |
| Agent says it has no knowledge tool | MCP tool not added to the agent, or wrong connection | Add the **MCP tool** referencing the project connection |
| 401/403 from the knowledge base | Missing **read role** for the calling identity, or **RBAC not enabled** on the search service | Assign the role, and set API access control to **Both** or **RBAC** |
| Agent answers from model memory | Instructions don't say to use the knowledge tool | **Optimise instructions** ("call the knowledge base before answering, answer only from it, cite"), consider `tool_choice` |
| Error: answer synthesis with `minimal` | `minimal` supports **only `extractiveData`** | Use `low`/`medium` with a model, or switch output to extractive |
| Web source rejected with `minimal` | Web knowledge isn't supported at `minimal` | Use `low`/`medium` |
| More than 10 sources fails | Source cap | Split into several knowledge bases by topic |
| Planning model rejected | Unsupported model family | Use **gpt-4o, gpt-4.1 or gpt-5 series** |
| Multi-part questions only partially answered | `minimal` (no planning) | `low` or `medium` |
| Too slow/expensive | High effort + synthesis everywhere | Lower effort, extractive output, per-request override |
| Stale answers from an indexed source | Indexer not scheduled / not refreshed | **Schedule recurring indexer runs** (incremental refresh) |
| Search index source creation fails | Index on a different service, or no semantic configuration | **Same search service** and a **semantic configuration** |
| OneLake source fails | Missing managed identity / Fabric workspace **Admin** role | Enable system-assigned MI, grant workspace Admin |
| Shortcut content missing permission trimming | Preview limitation | Don't rely on shortcut-derived content for permission-aware retrieval |
| Users see restricted content | Broad service identity, no ACL sync / user token | **ACL sync**, caller identity, query-time trimming |
| Tokens expire mid-session in a custom client | Static bearer token header *(secondary)* | Use a token provider that refreshes |
| Preview feature in production | No SLA | Use GA API versions where possible, plan for change |

### 0.11 Five ideas the exam really tests

1. **Knowledge base = reusable, multi-source endpoint. Knowledge source = connection (indexed or remote). Agentic retrieval = engine.** Agents share knowledge bases.
2. **Indexed vs remote** is an architecture decision (latency/enrichment/control vs live/no-copy/source governance).
3. **Reasoning effort** (`minimal` / `low` / `medium`) trades cost and latency for relevance. **`minimal` has no LLM, only extractive output, no synthesis, no web, max 10 sources.**
4. **Agents connect through MCP** (`knowledge_base_retrieve`), with a project connection. **Hub-based projects aren't supported**, and Agent Service isn't mandatory.
5. **Permissions must be enforced per user** (ACL sync, caller identity). A broad service identity can't do it. Mind **GA vs preview** by API version.

---

## 1. Scenario Questions

### Question 1: Name the component (drag-and-drop)

Match each description to: **Knowledge base · Knowledge source · Agentic retrieval · Foundry IQ service (Azure AI Search) · Project connection · MCP tool**.

| Description | Component |
|---|---|
| A. Top-level resource that groups sources under one endpoint and sets retrieval behavior | ? |
| B. A top-level resource on the search service that defines content, either indexed or remote | ? |
| C. The multi-query engine that plans, runs parallel subqueries, reranks and merges | ? |
| D. The infrastructure you must have to use knowledge bases | ? |
| E. The Foundry project resource that points an agent to the knowledge base's MCP endpoint | ? |
| F. The agent-side tool that calls `knowledge_base_retrieve` | ? |

<details>
<summary>Answer</summary>

| Description | Component |
|---|---|
| A | **Knowledge base** |
| B | **Knowledge source** |
| C | **Agentic retrieval** |
| D | **Foundry IQ service (Azure AI Search)** |
| E | **Project connection** |
| F | **MCP tool** |
</details>

---

### Question 2: Why a knowledge base? (Select TWO)

An enterprise has **12 agents**. Each team built its own chunking, embedding, routing and permission pipeline over overlapping SharePoint and Blob content. Answers are inconsistent and maintenance is heavy. Which TWO statements describe how Foundry IQ helps?

A. **One knowledge base provides access to multiple sources**, so you don't connect each agent to each source individually  
B. **Multiple agents can share the same knowledge base**, with permission-aware retrieval and citations  
C. Each agent still needs its own private index of the same content  
D. Foundry IQ removes the need for an Azure AI Search service  
E. Foundry IQ replaces Azure AI Search entirely

<details>
<summary>Answer</summary>

### ✅ A and B

- **C ❌** Defeats the purpose.
- **D, E ❌** Foundry IQ is built **on** Azure AI Search. You need a Foundry IQ (Azure AI Search) service. It's the front door to it, not a replacement.
</details>

---

### Question 3: Indexed or remote? (drag-and-drop)

Match each requirement to **Indexed knowledge source** or **Remote knowledge source**.

| Requirement | Type |
|---|---|
| A. Predictable query latency and custom enrichment/vectorization | ? |
| B. Query SharePoint live with Microsoft 365 governance, with no separate copy | ? |
| C. Scheduled incremental refresh through an indexer | ? |
| D. Real-time public web data with domain restrictions | ? |
| E. Call tools on an existing MCP server at query time | ? |
| F. Generates a data source, skillset, index and indexer | ? |

<details>
<summary>Answer</summary>

| Requirement | Type |
|---|---|
| A | **Indexed** |
| B | **Remote** (SharePoint remote) |
| C | **Indexed** |
| D | **Remote** (web) |
| E | **Remote** (MCP) |
| F | **Indexed** |
</details>

---

### Question 4: Existing index (snippet)

```json
{
  "knowledge_source": { "kind": "searchIndex", "indexName": "research-papers" },
  "knowledge_base": { "searchService": "contoso-search-eu" },
  "existing_index": {
    "searchService": "contoso-search-us",
    "fields": ["content (searchable string)", "contentVector (vector)"],
    "semantic_configuration": null
  },
  "error": "Knowledge source creation failed"
}
```

Which TWO problems explain the failure? *(requirements from the search-index knowledge-source page)*

A. The index must be on the **same search service** as the knowledge base  
B. The index needs a **semantic configuration** to meet the criteria for agentic retrieval  
C. Vector fields can't be used  
D. The index needs 3 replicas  
E. The knowledge base must be hub-based

<details>
<summary>Answer</summary>

### ✅ A and B

The existing index has to be on the same service and have plain text or vector content **with a semantic configuration**. (The semantic ranker is built into agentic retrieval, see the Semantic search file.)

**Trap:** the two different `searchService` values and `semantic_configuration: null` are the clues.
</details>

---

### Question 5: Reasoning effort mapping (drag-and-drop)

Match each need to: **minimal · low · medium**.

| Need | Effort |
|---|---|
| A. Lowest cost and latency, **no LLM planning**, you'll manage planning yourself | ? |
| B. The default agentic mode: **a single pass of LLM query planning** and source selection | ? |
| C. **Iterative** search when initial results don't meet relevance standards | ? |
| D. A migration from existing Search API queries | ? |

<details>
<summary>Answer</summary>

| Need | Effort |
|---|---|
| A | **minimal** |
| B | **low** |
| C | **medium** |
| D | **minimal** |
</details>

---

### Question 6: `minimal` conflicts (snippet)

```json
{
  "retrievalReasoningEffort": "minimal",
  "outputMode": "answerSynthesis",
  "knowledgeSources": ["blob-manuals", "sharepoint-policies", "web-standards",
                       "onelake-sensors", "sql-parts", "...(7 more)"]
}
```

The knowledge base update is rejected. Which TWO changes are needed? *(rules from the reasoning-effort page)*

A. For `minimal`, **`outputMode` must be `extractiveData`**. Use `low` or `medium` (with a model) if synthesis is required  
B. **Web knowledge isn't supported with `minimal`**, and `minimal` allows a **maximum of 10 knowledge sources**. Remove the web source and reduce to 10 or fewer (or use another effort and split by topic)  
C. Increase the model temperature  
D. Switch to a hub-based project  
E. Add more replicas

<details>
<summary>Answer</summary>

### ✅ A and B

`minimal` = no LLM, extractive output only, no answer synthesis, no web knowledge, max 10 sources.
</details>

---

### Question 7: Pick the effort (Select TWO)

For which TWO workloads is **`minimal`** the BEST starting point?

A. A **cost-sensitive internal search** that already runs well with direct text and vector queries, where the team will **manage query planning itself**  
B. A **migration** from Search API queries that wants predictable, easily controlled behavior  
C. Multi-hop research questions that need **iterative** refinement  
D. Answers that must be **synthesised** by the knowledge base's LLM  
E. Questions that must also query the **public web**

<details>
<summary>Answer</summary>

### ✅ A and B

C → `medium`. D and E aren't supported at `minimal`.
</details>

---

### Question 8: Request overrides knowledge base

A knowledge base is configured with **`low`**. For one rare, difficult research flow, the app needs deeper iterative planning, but must not change the default for everyone else. What is the BEST approach?

A. Change the knowledge base to `medium` for all queries  
B. **Set `medium` in that specific retrieve request.** The **request-level setting overrides** the knowledge base default  
C. Create a new Azure AI Search service  
D. Switch every source to remote

<details>
<summary>Answer</summary>

### ✅ B

Also **set the effort explicitly** rather than relying on a service default that can vary with enabled features.
</details>

---

### Question 9: Planning model

A team deploys a small non-OpenAI model and tries to use it for the knowledge base's **query planning**. It's rejected. What does the FAQ say?

A. Any chat model works  
B. **Only gpt-4o, gpt-4.1 and gpt-5 series models from Azure OpenAI in Foundry Models are supported for query planning.** Specify the supported deployment when creating the knowledge base  
C. Only embedding models are supported  
D. Planning models aren't allowed

<details>
<summary>Answer</summary>

### ✅ B

The search service's managed identity also needs access to the Azure AI services resource (Cognitive Services User, per the preview page).
</details>

---

### Question 10: Extractive or synthesized?

A research agent should **reason over the raw evidence itself**, compare passages, and cite them, while the team wants to keep knowledge-base LLM costs low. Which output mode fits BEST?

A. **Extractive data** (raw passages with citations), letting the agent's model do the reasoning  
B. Answer synthesis for every query  
C. No citations  
D. A web-only source

<details>
<summary>Answer</summary>

### ✅ A

Extractive output returns raw content with citations so agents can reason over it and trace answers. Answer synthesis adds a ready-to-use natural-language answer but needs a model and adds latency and cost. (Both are separate from the planning effort choice.)
</details>

---

### Question 11: Order the connection steps

Put these steps in order for connecting a knowledge base to a Foundry Agent Service agent:

**a)** Create an agent with the MCP tool  
**b)** Invoke the agent with a query  
**c)** Create a project connection to the knowledge base's MCP endpoint  
**d)** Optimise the agent instructions for knowledge retrieval

<details>
<summary>Answer</summary>

### ✅ c → d → a → b

Connection, instructions, agent with the MCP tool, invoke.
</details>

---

### Question 12: Hub-based project (snippet)

```json
{
  "agent_service": "Foundry Agent Service",
  "project_type": "hub-based project",
  "goal": "Connect a Foundry IQ knowledge base through MCP",
  "result": "Not supported"
}
```

What is the correct fix?

A. Increase `max_tokens`  
B. **Use a Foundry project.** Hub-based projects aren't supported for this connection  
C. Switch the knowledge source to remote  
D. Lower the reasoning effort

<details>
<summary>Answer</summary>

### ✅ B

Also needed: an LLM deployment in the project. This ties back to the Foundry fundamentals file (hub-based vs Foundry projects).
</details>

---

### Question 13: 403 from the knowledge base (Select TWO)

A deployed agent calls the knowledge base and gets **403 Forbidden**. The search service has **API access control set to API keys only**, and the project's managed identity has no role on the search service. Which TWO actions fit BEST?

A. Enable **role-based access control** on the Foundry IQ service (**Both** or **Role-based access control**) for keyless access  
B. Assign the calling identity the **read role on the search service** (for example, **Search Index Data Reader**, per the community sample)  
C. Increase temperature  
D. Make the project hub-based  
E. Add more knowledge sources

<details>
<summary>Answer</summary>

### ✅ A and B

If roles aren't feasible, key-based authentication is the fallback, but **RBAC is recommended for production**.
</details>

---

### Question 14: Agent ignores the knowledge base (Select TWO)

The knowledge base MCP tool is attached and works in direct REST tests. The agent, however, **answers from general knowledge** and never calls `knowledge_base_retrieve`. The instructions say "You are a helpful HR assistant." Which TWO changes help MOST?

A. **Optimise the instructions**: say when to call the knowledge base tool, to answer from retrieved content and to show citations  
B. Use **`tool_choice: required`** on turns where retrieval is necessary  
C. Raise temperature  
D. Remove the connection  
E. Switch to a hub-based project

<details>
<summary>Answer</summary>

### ✅ A and B

The Learn connection article has an explicit "optimise agent instructions for knowledge retrieval" step. (Details of the wording are *general*.)
</details>

---

### Question 15: Which knowledge route? (drag-and-drop)

Match each scenario to: **File search · Azure AI Search tool · Foundry IQ knowledge base (MCP) · Remote SharePoint source · Minimal effort + extractiveData**.

| Scenario | Route |
|---|---|
| A. A single, existing, custom-enriched index, with simple grounding | ? |
| B. A PDF uploaded by a user into one conversation | ? |
| C. Ten agents sharing knowledge from Blob, SharePoint and the web, with multi-part questions | ? |
| D. SharePoint content that must stay in place under Microsoft 365 governance | ? |
| E. Cheapest possible retrieval with no LLM planning | ? |

<details>
<summary>Answer</summary>

| Scenario | Route |
|---|---|
| A | **Azure AI Search tool** |
| B | **File search** |
| C | **Foundry IQ knowledge base (MCP)** |
| D | **Remote SharePoint source** |
| E | **Minimal effort + extractiveData** |
</details>

---

### Question 16: Per-user permissions

A knowledge base spans **indexed SharePoint** and **remote SharePoint** sources. The agent calls it using only the **agent's managed identity**, which has broad read access. Contractors are seeing HR-only paragraphs. What is the BEST fix? (Select TWO)

A. **Synchronise ACLs** for supported indexed sources and use **query-time trimming**  
B. **Run queries under the caller's Entra identity** (pass the end user's token for per-user filtering), rather than relying on a broad service identity  
C. Add "do not reveal HR content" to the instructions as the only control  
D. Give the agent identity Owner on SharePoint  
E. Lower the reasoning effort

<details>
<summary>Answer</summary>

### ✅ A and B

A service identity can't enforce per-user permissions by itself. Prompts aren't enforcement. This repeats the Grounding file's OBO lesson.
</details>

---

### Question 17: OneLake prerequisites (Select TWO)

A team creates an **indexed OneLake** knowledge source and it fails. Which TWO prerequisites should they check? *(from the OneLake page)*

A. The Foundry IQ service must have a **system-assigned managed identity**  
B. That identity must hold the **Admin role in the Fabric workspace**  
C. The service must be in a private-only region with no managed identity  
D. The source must use API keys only  
E. Shortcut-derived content is fully supported for permission-aware retrieval

<details>
<summary>Answer</summary>

### ✅ A and B

Also: keyless authentication for the creator needs **Search Service Contributor** and **Search Index Data Contributor**. **Shortcut-derived content is excluded from permission-aware retrieval in the preview**, so E is false. This source is preview in the page.
</details>

---

### Question 18: Freshness

A knowledge base indexes a product-manual **Blob** container. Manuals change weekly, but answers cite old versions. What should the team do?

A. Use `minimal` effort  
B. **Schedule recurring indexer runs** for incremental refresh (indexing and sync can be automatic), and confirm the knowledge source's ingestion status  
C. Switch to answer synthesis  
D. Make it remote

<details>
<summary>Answer</summary>

### ✅ B

Remote sources are live, but **web or SharePoint remote** is a different choice with its own latency and governance. For blob content, refresh the index.
</details>

---

### Question 19: Without Foundry Agent Service

A team builds a **LangGraph** application (not on Foundry Agent Service) and wants to use an existing knowledge base. Which statements are correct? (Select TWO)

A. Foundry Agent Service **isn't required**. A knowledge base can be called from **any application** that supports the knowledge base APIs, or over **MCP**  
B. Every knowledge base is also a **standalone MCP server** exposing **`knowledge_base_retrieve`**, so any MCP-compatible client can call it  
C. A knowledge base can only be used by Foundry Agent Service  
D. LangGraph can't call MCP servers  
E. The search service isn't needed

<details>
<summary>Answer</summary>

### ✅ A and B

Custom clients must handle details such as **token refresh** and **a different MCP result shape** *(secondary)*.
</details>

---

### Question 20: Hosted agent and toolbox

A **hosted agent** needs the knowledge base with **keyless authentication**. Which pattern fits? (Select TWO)

A. Create a **toolbox connection** that targets the knowledge base's **MCP endpoint**, so the toolbox exposes it as a **single tool**  
B. **Grant the agent's managed identity access** to the knowledge base and enable RBAC on the search service  
C. Put an admin API key in the agent code  
D. Hosted agents can't use knowledge bases  
E. Use the portal's classic workflow only

<details>
<summary>Answer</summary>

### ✅ A and B

Per the hosted-agent quickstart. The knowledge base also uses a chat model deployment to synthesise answers.
</details>

---

### Question 21: Status and planning

A project plan assumes **every** Foundry IQ capability is GA with an SLA. Which statements are the BEST corrections? (Select TWO)

A. **Knowledge bases are generally available**, and **model-backed query planning and answer synthesis are GA in Search REST API 2026-10-01**  
B. **Other capabilities are still preview** (for example `auto` effort, some source kinds and portal experiences). **Availability depends on the REST API version**, and the portals provide preview-only access to all agentic retrieval features  
C. All source kinds are GA everywhere  
D. Preview features have an SLA  
E. API versions don't matter

<details>
<summary>Answer</summary>

### ✅ A and B

Preview features have no SLA and aren't recommended for production. Verify the contract for each feature you depend on.
</details>

---

### Question 22: Three IQs

Match each description to **Foundry IQ · Fabric IQ · Work IQ**.

| Description | IQ |
|---|---|
| A. Enterprise knowledge layer for agents (knowledge bases, agentic retrieval on Azure AI Search) | ? |
| B. A semantic layer that brings business meaning to data in Power BI/Fabric | ? |
| C. Microsoft 365 work signals about how the organisation operates | ? |

<details>
<summary>Answer</summary>

| Description | IQ |
|---|---|
| A | **Foundry IQ** |
| B | **Fabric IQ** |
| C | **Work IQ** |

They are separate products *(secondary)*, although Foundry IQ can use Fabric IQ and Work IQ as (preview) knowledge sources.
</details>

---

### Question 23: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | A knowledge base can reference multiple knowledge sources and be shared by multiple agents. | |
| 2 | Remote knowledge sources copy all content into your index. | |
| 3 | `minimal` reasoning effort uses an LLM for query planning. | |
| 4 | A retrieve request's reasoning effort overrides the knowledge base setting. | |
| 5 | Foundry Agent Service is required to use a Foundry IQ knowledge base. | |
| 6 | Hub-based projects are supported for connecting a knowledge base to an agent. | |
| 7 | Parallel processing of multiple subqueries requires LLM query planning. | |
| 8 | Planning effort and answer synthesis are separate choices. | |
| 9 | Indexed knowledge sources generate a data source, skillset, index and indexer. | |
| 10 | The knowledge base MCP tool is named `knowledge_base_retrieve`. | |
| 11 | Preview agentic-retrieval features are covered by an SLA. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **Yes** | Core design. |
| 2 | **No** | Remote sources are queried live, not copied. |
| 3 | **No** | `minimal` is model-free. |
| 4 | **Yes** | Request overrides the knowledge base. |
| 5 | **No** | Any app or MCP client can call it. |
| 6 | **No** | Not supported. |
| 7 | **Yes** | Without an LLM, `minimal` just merges. |
| 8 | **Yes** | Different settings. |
| 9 | **Yes** | The managed ingestion pipeline. |
| 10 | **Yes** | The one tool each knowledge base exposes. |
| 11 | **No** | Preview, no SLA. |
</details>

---

### Question 24: Match the symptom to the fix (drag-and-drop)

Match each symptom to: **Use a Foundry project · Add the MCP tool + connection · Enable RBAC + read role · Optimise instructions / tool_choice · Switch from minimal · Use supported planning model · Split knowledge bases · Schedule indexer refresh · Same service + semantic configuration · ACL sync + caller identity · Use GA API version / verify status**.

| Symptom | Fix |
|---|---|
| A. Connection to the agent isn't supported | ? |
| B. Agent says it has no knowledge tool | ? |
| C. 403 from the knowledge base | ? |
| D. Agent answers from general knowledge | ? |
| E. Synthesis or web source rejected | ? |
| F. Planning model rejected | ? |
| G. 12 sources won't fit | ? |
| H. Indexed content is stale | ? |
| I. Search-index source creation fails | ? |
| J. Users see restricted content | ? |
| K. A feature behaves differently across API versions | ? |

<details>
<summary>Answer</summary>

| Symptom | Fix |
|---|---|
| A | **Use a Foundry project** |
| B | **Add the MCP tool + connection** |
| C | **Enable RBAC + read role** |
| D | **Optimise instructions / `tool_choice`** |
| E | **Switch from `minimal`** |
| F | **Use a supported planning model** (gpt-4o, gpt-4.1, gpt-5 series) |
| G | **Split knowledge bases** (by topic) |
| H | **Schedule indexer refresh** |
| I | **Same service + semantic configuration** |
| J | **ACL sync + caller identity** |
| K | **Use GA API version / verify status** |
</details>

---

## 2. Mini Case Study: Tailspin Industrial Knowledge Platform

### Background

Tailspin Industrial is building shared knowledge for **field-service agents** on Microsoft Foundry.

1. Content: **equipment manuals in Blob Storage** (updated weekly), **repair policies on SharePoint** (permission-trimmed, must stay in place under Microsoft 365 governance), a **public electrical-standards site**, and an **existing research index** that another team built.
2. **Eight agents** need the same knowledge, with **citations**.
3. Technicians ask **multi-part questions** ("compare the repair policy for model A and B and give the relevant standard"). A separate **FAQ lookup** feature needs the **lowest cost and latency**, with no LLM.
4. A **research agent** should **reason over raw evidence itself**.
5. The first connection attempt used a **hub-based project**.
6. Deployed agents get **403**. The search service allows **API keys only**.
7. In testing, the agent **answers from memory** and doesn't call the knowledge base.
8. Contractors can see **HR-only repair-policy paragraphs** because the agent calls the knowledge base with a **broad service identity**.
9. Manuals' answers cite **last month's version**.
10. A planner proposes a **small non-OpenAI model** for query planning.
11. A **hosted agent** needs **keyless** access.
12. Leadership asks whether all of this is **GA with an SLA**.

### Case Q1: Knowledge architecture (requirements 1 and 2)

Which design is BEST?

A. One **knowledge base** referencing **indexed Blob** and **existing search index** sources, **remote SharePoint** (stays in place under M365 governance) and a **web** source with **domain restrictions**, shared by all eight agents  
B. Eight separate pipelines  
C. Copy everything into each agent's instructions  
D. A separate private index per agent

<details><summary>Answer</summary>

### ✅ A

Web is remote, SharePoint remote respects Microsoft 365 governance, Blob and the existing index are indexed. The existing index must be on the **same search service** and have a **semantic configuration**.
</details>

### Case Q2: Reasoning effort (requirement 3)

A. `medium` for everything  
B. **`low` (or `medium`)** for the multi-part technician questions, and **`minimal` with `extractiveData`** for the FAQ lookup (no LLM, lowest cost/latency, max 10 sources, no web)  
C. `minimal` for everything including web and synthesis  
D. No planning anywhere

<details><summary>Answer</summary>

### ✅ B

Use per-request overrides where one knowledge base serves both patterns (or a separate knowledge base for the FAQ).
</details>

### Case Q3: Research agent (requirement 4)

A. Answer synthesis only  
B. **Extractive data** with citations so the agent's model reasons over raw passages

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q4: Hub-based project (requirement 5)

A. Keep the hub-based project  
B. **Use a Foundry project** (hub-based isn't supported) with an LLM deployment

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q5: 403 errors (requirement 6)

Which TWO?

A. **Enable RBAC** on the search service (Both, or RBAC)  
B. **Assign the read role** to the calling identity (project/agent managed identity)  
C. Make the service public  
D. Share the admin key with developers

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q6: Agent ignores the tool (requirement 7)

Which TWO?

A. **Optimise the instructions** (when to call the knowledge tool, answer from retrieved content, cite)  
B. **`tool_choice: required`** where retrieval is necessary  
C. Raise temperature  
D. Delete the connection

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q7: Contractors see HR text (requirement 8)

Which TWO?

A. **ACL sync** for indexed sources and **query-time trimming**  
B. **Run queries under the caller's Entra identity** (user token) so remote/permissioned sources are trimmed per user  
C. A prompt line forbidding HR content  
D. Give the service identity more access

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q8: Stale manuals (requirement 9)

A. Raise the reasoning effort  
B. **Schedule recurring indexer runs** (incremental refresh) for the Blob source and check ingestion status

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q9: Planning model (requirement 10)

A. Approve the small non-OpenAI model  
B. Use **gpt-4o, gpt-4.1 or a gpt-5 series** deployment for planning, specified when the knowledge base is created

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q10: Hosted agent (requirement 11)

Which TWO?

A. **Toolbox connection** to the knowledge base's MCP endpoint (single tool)  
B. **Grant the agent's managed identity access** to the knowledge base (RBAC enabled)  
C. Admin key in code  
D. Not possible

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q11: GA question (requirement 12)

A. Everything is GA with an SLA  
B. **Knowledge bases are GA, and model-backed planning and answer synthesis are GA in REST API 2026-10-01. Other features** (for example `auto` effort, some sources such as OneLake, portal experiences) **are preview with no SLA.** Verify each dependency's status and API version

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q12: Map the requirement to the feature

| Requirement | Feature |
|---|---|
| 8 agents share knowledge | ? |
| SharePoint stays in place | ? |
| Weekly manual updates | ? |
| Cheap FAQ lookup | ? |
| Multi-part questions | ? |
| Research agent reasons itself | ? |
| Hub-based project problem | ? |
| 403 errors | ? |
| Agent ignores the tool | ? |
| Contractor leak | ? |
| Planning model | ? |
| Hosted agent keyless | ? |
| SLA question | ? |

<details><summary>Answer</summary>

| Requirement | Feature |
|---|---|
| 8 agents share knowledge | One knowledge base (MCP, project connection) |
| SharePoint stays in place | Remote SharePoint source (M365 governance) |
| Weekly manual updates | Indexer schedule (incremental refresh) on the indexed Blob source |
| Cheap FAQ lookup | `minimal` + `extractiveData` (no LLM) |
| Multi-part questions | `low` or `medium` (LLM planning, parallel subqueries) |
| Research agent reasons itself | Extractive data |
| Hub-based project problem | Use a Foundry project |
| 403 errors | Enable RBAC + read role |
| Agent ignores the tool | Instructions + `tool_choice` |
| Contractor leak | ACL sync + caller identity + query-time trimming |
| Planning model | gpt-4o / gpt-4.1 / gpt-5 series |
| Hosted agent keyless | Toolbox + managed identity access |
| SLA question | GA vs preview by API version, verify |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Replacement trap** | "Foundry IQ replaces Azure AI Search." | It's built **on** Azure AI Search. You need the service. |
| **Agent-Service trap** | "Only Agent Service can use a knowledge base." | Any app or MCP client can. Agent Service just has built-in support. |
| **Per-agent trap** | "Each agent needs its own pipeline." | One knowledge base, shared by many agents. |
| **Remote-copy trap** | "Remote sources are ingested." | Queried live, never copied. |
| **Indexed-always trap** | "Always index everything." | Remote suits live data, no copy and source governance. |
| **Existing-index trap** | "Any index works." | Same search service and a semantic configuration. |
| **Minimal trap** | "`minimal` still plans with an LLM." | No LLM. Extractive only. No synthesis or web. Max 10 sources. |
| **Default trap** | "Rely on the service default effort." | Set it explicitly. |
| **Override trap** | "Knowledge-base effort can't change per request." | The request overrides it. |
| **Synthesis trap** | "Planning effort enables synthesis." | Separate settings. Synthesis needs a model. |
| **Model trap** | "Any model can plan queries." | gpt-4o, gpt-4.1, gpt-5 series. |
| **Hub trap** | "Hub-based projects work." | Foundry project required. |
| **Identity trap** | "A broad service identity is fine." | It can't enforce per-user permissions. Use ACL sync and caller identity. |
| **Prompt-security trap** | "Tell the agent to hide restricted data." | Enforce in retrieval. |
| **Instruction trap** | "Attaching the tool guarantees use." | Optimise instructions, use `tool_choice`. |
| **Freshness trap** | "Indexed content updates itself instantly." | Schedule indexer runs. |
| **OneLake-shortcut trap** | "Shortcut content gets permission trimming." | Excluded in the preview. |
| **GA trap** | "Everything in Foundry IQ is GA." | Mixed. Depends on the API version. Portals preview-only. |
| **Compliance trap** | "Preview connectors stay inside the boundary." | They may move data outside. Your responsibility. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| Share knowledge across many agents | **Knowledge base** |
| Content stays in place, live, source governance | **Remote** knowledge source |
| Predictable latency, custom enrichment | **Indexed** knowledge source |
| Reuse an existing index | **Search index** knowledge source (same service, semantic configuration) |
| Weekly changing blobs | **Indexed Blob** + scheduled indexer |
| Public web with domain limits | **Web** (remote), not with `minimal` |
| Lowest cost/latency, no LLM | **`minimal`** + `extractiveData` |
| Default agentic planning | **`low`** |
| Iterative multi-hop | **`medium`** |
| One-off deeper search | Request-level override |
| Agent reasons over evidence | **Extractive data** |
| Ready-made cited answer | **Answer synthesis** (model required) |
| Planning model | **gpt-4o / gpt-4.1 / gpt-5 series** |
| Connect to agent | **Project connection + MCP tool** (`knowledge_base_retrieve`), Foundry project |
| Hosted agent, keyless | **Toolbox** + managed identity access |
| Non-Agent-Service client | **MCP** or Search APIs |
| 403 | **RBAC enabled + read role** |
| Agent skips the tool | **Instructions + `tool_choice`** |
| Per-user permissions | **ACL sync, caller identity, query-time trimming** |
| More than 10 sources | **Split by topic** |
| Single index, simple grounding | **Azure AI Search tool** |
| Files in one chat | **File search** |
| Production dependency | **GA API version**, verify status |

---

## 5. Quick Revision Sheet

```text
FOUNDRY IQ = managed knowledge layer on AZURE AI SEARCH (front door, not a replacement)
  KNOWLEDGE BASE   = top-level endpoint; groups sources; sets retrieval behavior; shared by many agents; ~10 sources
  KNOWLEDGE SOURCE = top-level resource on the search service; INDEXED or REMOTE; created independently, referenced by the KB
  AGENTIC RETRIEVAL= engine: plan -> parallel subqueries (keyword/vector/hybrid) -> semantic rerank -> merge (+ optional synthesis)
  Agent Service NOT required (any app / MCP client / Agent Framework)

INDEXED: azureBlob, Azure SQL, OneLake (preview), SharePoint indexed (GA 2026-10-01), searchIndex (same service + semantic config)
         generates data source + skillset + index + indexer; scheduled incremental refresh; ACL sync, Purview labels
REMOTE : SharePoint remote (M365 governance), Web (Bing, domain limits), MCP (tools on an MCP server); queried LIVE, never copied

REASONING EFFORT (KB default; retrieve request OVERRIDES; set explicitly):
  minimal = NO LLM, direct text+vector, extractiveData ONLY, no synthesis, no web, max 10 sources
  low     = DEFAULT, single pass of LLM planning + source selection
  medium  = iterative search
  auto    = preview
  model required for low/medium/auto/synthesis/web summarization; planning models: gpt-4o, gpt-4.1, gpt-5 series
OUTPUT : extractiveData (raw passages + citations; agent reasons) | answer synthesis (KB LLM writes cited answer)

CONNECT: project connection -> optimise instructions -> agent with MCP tool (knowledge_base_retrieve) -> invoke
         Foundry project (NOT hub-based); basic + standard setup; azure-ai-projects >= 2.0.0
         roles: Foundry User (project parent) + read role for the calling identity on the search service; RBAC enabled (Both/RBAC)
         hosted agent: toolbox -> KB MCP endpoint as one tool, agent managed identity (keyless)
SECURITY: ACL sync + Purview labels + query-time trimming + CALLER'S Entra identity; a broad service identity can't enforce per-user access
STATUS : KBs GA; model-backed planning + synthesis GA in REST 2026-10-01; auto effort, some sources, portals = preview; depends on API version
```

### Best-answer checklist

1. **Many sources, many agents, complex questions?** Knowledge base. **One index, simple?** Azure AI Search tool. **One chat's files?** File search.
2. **Indexed or remote?** Latency/enrichment/control vs live/no-copy/source governance.
3. **Reasoning effort:** `minimal` (no LLM, extractive, no synthesis/web, ≤10 sources), `low` (default), `medium` (iterative). Override per request if needed.
4. **Output:** extractive (agent reasons) or synthesis (model-written answer).
5. **Connection:** Foundry project (not hub-based), project connection, MCP tool, RBAC and read role, instructions that call the tool.
6. **Permissions:** ACL sync and caller identity, never a broad service identity or a prompt.
7. **Freshness:** schedule indexer runs.
8. **Status:** check GA vs preview by API version. Preview = no SLA.

---

**Pending from the original list:** the general **Agents** overview. Send it, or the next topic, when you're ready.

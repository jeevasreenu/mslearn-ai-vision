# AI-103: Foundry Agent Service (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, config/code snippets, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Scope: **the managed platform itself**: agent types, runtime components (agents, conversations, responses), environment setup (basic vs standard), RBAC, tools and toolboxes, memory, multi-agent options, publishing, observability and optimisation. **Agent roles/goals/instructions** were covered earlier. **Grounding tools** (file search, Azure AI Search, SharePoint, Fabric, web) were covered in the Grounding file and are only referenced here.
> This product changes **very fast**. Many sub-features are **preview**, several are **being retired**, and the "classic" and "new" experiences coexist. The exam logic (what each component is for, and which constraints apply) matters more than the labels. **Verify current status on Microsoft Learn before test day.** Items from non-Microsoft pages are marked *(secondary source)*.

---

## 0. Core Concepts (read first)

### 0.1 What Foundry Agent Service is

**Foundry Agent Service** is a **managed platform for building, deploying and scaling AI agents**. You can use any framework and any supported model from the Foundry catalog, with a single entry point for model inference and tools.

| Component | What it does |
|---|---|
| **Agent Runtime** | Hosts and scales prompt agents and hosted agents. Manages **conversations, tool calls and agent lifecycle** |
| **Toolboxes** | Curate a set of tools once (web search, file search, code interpreter, MCP servers, custom functions), then share them across agents through **one managed MCP endpoint** with central authentication, governance and versioning |
| **Models** | Many catalog models. **Swap models without changing agent code** |
| **Observability** | End-to-end tracing, metrics, evaluations, Application Insights integration |
| **Optimization** | **Agent optimizer (preview)** evaluates behavior and generates better instructions, tool descriptions, model selections (and skills for hosted agents) |
| **Identity & Security** | Microsoft Entra identity, RBAC, content filters, virtual network isolation |
| **Publishing** | Version agents, create **stable endpoints**, share through **Microsoft Teams, Microsoft Copilot** and the Entra Agent Registry |

Status: the service is **generally available**, but **some sub-features are in public preview** and may have different constraints. Pricing is **consumption-based** and depends on **model tokens, hosting compute, and separately metered tools** (you aren't billed for the agent object itself *(secondary source)*).

> **Agent Service vs Foundry Models:** Models alone give inference. Agent Service adds **state, tool orchestration, identity, hosting, publishing and observability**.

### 0.2 Ways to build (agent types and paths)

| Path | What it is | Use when |
|---|---|---|
| **Prompt agent** | **Declarative**: configure **instructions + model + tools**, and Foundry runs it. **No code or infrastructure** | "Least to manage" for text. **Start here** for a first agent |
| **Voice-based prompt agent** | A prompt agent configured for real-time spoken conversation through **Voice Live** | Voice experience without hosting its orchestration |
| **Hosted agent** *(public preview)* | **Bring your own code and framework as a container**. Foundry provides a managed endpoint, scaling and identity | Full control (custom logic, any framework, filesystem persistence) |
| **External agent via Responses API** | An agent you already run elsewhere calls the **Responses API** | You keep your own runtime but want Foundry models/tools/tracing |
| **Workflow agent** *(preview)* | Visual/declarative orchestration of multiple agents and logic | See 0.9. **Being retired** |

Hosted agents (public preview) give every session its **own VM-isolated sandbox with a persistent filesystem**, **scale to zero**, resume with files intact, **BYO VNet** for outbound traffic, **built-in versioning with stable endpoints and weighted rollouts**, and support for the OpenResponses protocol (mapped to the **Activity Protocol** for one-click Microsoft 365 publishing). They need **additional permissions/RBAC** beyond prompt agents.

Prompt agents can also use the **Microsoft Copilot harness (preview)**, which adds built-in capabilities such as file read/write, shell, web and subagents, in a subset of regions, **without bring-your-own-model support**.

### 0.3 Runtime components: agents, conversations, responses

| Component | Role | Use when |
|---|---|---|
| **Agent** | Supplies **reusable model, instructions and tools** to a response | Several requests need the same behavior/tool configuration |
| **Conversation** | **Persists history** (input/output items) server-side across turns | Later turns need server-side history |
| **Response** | **One unit of execution**: runs a model or agent against input and produces output items | Every interaction. Works with or without an agent or conversation |

Rules of thumb:
- **Start with a response** for a single interaction. **Add an agent** for reusable behavior, **a conversation** for persisted history, or both.
- Without a conversation, an app can carry context by **referencing a previous stored response** or **resending earlier items**.
- **Streaming** and **background** mode change **how** a response is received, not the relationship among the three components.
- Older material says **threads, runs, messages**. In the new experience, treat "run" as **response generation**.
- Memory (preview) can also be attached to an agent (see 0.8).

> Foundry Agent Service is **stateful**: it stores **conversations/responses** and **files/vector stores**. Data **persists until you delete it**.

### 0.4 Environment setup: basic vs standard (high-yield)

| | **Basic setup** | **Standard setup** |
|---|---|---|
| Agent state storage | **Microsoft-managed** (logically separated) | **Your own Azure resources** (single-tenant, customer-managed) via **capability hosts** |
| Compatibility | Compatible with **OpenAI Assistants**, platform built-in storage | Full data sovereignty and compliance control |
| Needs | Foundry resource + project | **BYO** Azure **Storage** (files), Azure **Cosmos DB** for NoSQL (threads/conversations/agent metadata), Azure **AI Search** (vector stores), plus **Key Vault** per the setup guide |
| Use when | Prototyping, simple needs | **Production with compliance, data residency, project-level isolation, private networking** |

Standard-setup facts:
- State at rest lives in **your** Storage (files and attachments), **Cosmos DB** (messages, conversation history, agent metadata) and **AI Search** (vector stores).
- The Cosmos DB account needs **at least 3,000 RU/s total** per the Learn page (**provisioned or serverless**).
- The identity running the deployment needs, beyond creating the account/project, **Storage Blob Data Contributor** on the storage account and **Cosmos DB Operator** on the Cosmos DB account. **Azure AI Search doesn't require a caller role.**
- A **project managed identity** receives roles on the connected resources.
- Private AI Search / private networking needs the **standard setup with virtual network injection** (see Grounding file).
- The docs list **three** environment configuration modes. Basic and Standard are the two to know for the exam.

**Project = the unit of isolation and sharing**
- **All agents in the same project share** the same file storage, thread storage and search indexes.
- **Data is isolated between projects.** Agents in one project can't access another project's resources.

### 0.5 Permissions (RBAC)

| Action | Role |
|---|---|
| Create the account and project | **Foundry Account Owner** (subscription scope) |
| **Standard setup only**: assign RBAC on Cosmos DB, AI Search, Storage | **Role Based Access Control Administrator** (or Owner), key permission `Microsoft.Authorization/roleAssignments/write` |
| **Create and edit agents** | **Foundry User** |
| **Invoke agent endpoints only** (no create/edit) | **Foundry Agent Consumer** |
| Create **project connections** (for example, MCP auth, Bing) | **Foundry Project Manager** |
| Insights (hosted agent) | **Foundry Project Manager** (prompt agent: Foundry User) |

Role names were recently renamed (Foundry User = Azure AI User, and so on). Role IDs and permissions are unchanged.

### 0.6 Tools

| Tool | What it is | Key facts |
|---|---|---|
| **Function calling** | Your own function schema. The model asks, **your app runs it** | For prompt agents, function tools **run on the client side** |
| **Code Interpreter** | Model writes and **runs Python in a sandbox** (data analysis, charts, files) | **Extra charges** beyond tokens. Each concurrent conversation creates a **separate session**. A session is active **1 hour by default** with a **30-minute idle timeout**. Not in all regions |
| **File search / Azure AI Search / SharePoint / Fabric / web search** | Grounding tools | See the Grounding file |
| **MCP tool** | Connect to a **remote MCP server** (public or private endpoint) | **Approval flow** (human-in-the-loop) available. Auth via **project connection**. Third-party servers may take data **outside the Foundry compliance boundary** |
| **OpenAPI tool** | Call an HTTP API described by an OpenAPI spec | Credentials stored in a **project connection** |
| **A2A tool** *(preview)* | Connect one agent to another (**Agent2Agent**) | Used for multi-agent designs |
| **Partner/catalog tools** | Tools catalog (MCP servers such as GitHub, Dataverse, Teams, Cosmos DB...) | Some Microsoft 365/Agent 365 tools are **preview**. Dataverse MCP needs publishing and **admin approval** |
| **Skills (preview)** | Packaged reusable task instructions (`SKILL.md`) | Added to a toolbox, needs a runtime that supports them |

**Tool facts to remember**
- **A tool definition ≠ a connection.** A connection supplies endpoint/credentials. Creating a connection doesn't attach a tool to an agent, and not every tool needs one.
- **Not every model/region supports every tool.** Check **tool support by region and model**.
- **Instructions guide tool choice** ("For customer sales data, use the Fabric tool"), and you can **force** a tool with `tool_choice`.
- Local MCP connections in an IDE don't make a tool available to a cloud agent.

### 0.7 Toolbox (preview)

A **toolbox** = a reusable, **versioned** bundle of tools (and skills), managed in Foundry and exposed through **one MCP endpoint** that any agent or runtime (Agent Framework, LangGraph, GitHub Copilot SDK *(secondary source)*) can consume.

| Pillar | Meaning |
|---|---|
| Discover *(coming soon)* | Find approved tools |
| Build | Assemble and version a toolbox |
| Consume | Agents call the toolbox MCP endpoint |
| Govern | Central credentials, policy, guardrails, versioning |

- **RBAC:** **Foundry User** on the project for: the **developer**, the **agent identity** (prompt agents), and **end users** (only for **OAuth/user-Entra-token passthrough** flows).
- **`require_approval`** can be configured on a tool.
- Warning in the docs: connecting **non-Foundry tools** can incur costs and send data **outside Foundry's compliance boundary**.
- **Not every tool type is available in every region or with every model.**

### 0.8 Memory (preview)

| Concept | Detail |
|---|---|
| **Short-term memory** | The current session's conversation (managed as session context) |
| **Long-term memory** | **Distilled knowledge across sessions**, extracted from conversations, consolidated, and retrieved later |
| **Memory store** | Managed persistent store of **memory items**. Defines which information types matter (user profile, chat summary, and procedural memory per a Microsoft blog) |
| **Scope** | Partition key (for example, a **user's Entra ID or UUID**). Each scope keeps an **isolated collection**. **Treat scope as a security boundary** |
| **Phases** | **Extraction → consolidation (merge duplicates, resolve conflicts) → retrieval** (hybrid search, with core user info retrieved at the start) |
| **Updates** | **Asynchronous**: wait for the configured update delay before expecting recall |
| **Controls** | Item-level create/read/update/delete, **default TTL**, direct **remember-or-forget** commands |
| **Limits (Dec 2025 preview report)** *(secondary source)* | Up to **10,000 items per scope**, **1,000 requests per minute**. Preview limits change |
| **Agent use** | Attach the **memory search tool** to the agent |

> **Memory ≠ chat history ≠ grounding.** History is a transcript of what happened, memory is durable user-specific knowledge, and grounding is authoritative organisational content.
> Memory is a privacy risk surface. Design **consent, retention (TTL), scope and deletion**, and never store credentials or sensitive data without policy.

### 0.9 Multi-agent options (status matters)

| Mechanism | Status (per sources) | Note |
|---|---|---|
| **Connected agents** (classic) | **Removed** in the new Agent Service *(secondary source)*. Replacement is the **A2A tool** | Don't build new designs on it |
| **Portal workflows** (declarative, visual/YAML) | **Preview. Foundry is retiring workflows on December 1, 2026.** Use **Microsoft Agent Framework** for new workflows. (Learn) | Code-based orchestration in hosted agents is unaffected |
| **Microsoft Agent Framework** | Open-source SDK merging Semantic Kernel and AutoGen. **1.0 GA April 3, 2026** *(secondary source)* | Built-in patterns: sequential, concurrent, group chat, handoff, Magentic *(secondary source)* |
| **A2A / MCP** | A2A is **public preview** (June 2026 blog). MCP is a first-class tool type | |
| **Classic agents** | **Deprecated, retire March 31, 2027.** Migrate to the new GA Agent Service | New Agent Service reached GA **March 16, 2026** *(secondary source)* |

> Why multi-agent: **specialisation** (focused roles, tools, and least privilege), **scalability** and **reuse**. (See the Agent instructions file's "split a giant prompt" lesson.)

### 0.10 Publishing and distribution

| Item | Facts |
|---|---|
| **Why publish** | Move an agent from a **shared project dev asset** to a **managed Azure resource** with a **stable endpoint**. In a project, everyone with access can interact with all agents and shares conversation context and permissions |
| **Agent Application** *(legacy publishing experience page)* | Wraps an agent version with its **own invocation URL, authentication policy, unique Entra agent identity and Entra agent blueprint**, as a **separate Azure resource with its own RBAC scope**. A **Deployment** child resource references a specific version and supports start/stop |
| **Benefits** | **External sharing** without granting project access, **stable endpoint** across new versions, **distinct agent identity**, **independent RBAC** |
| **Protocols** | **Responses** and **Activity** protocols |
| **Publish to Microsoft Copilot / Teams** | **Foundry handles Teams bot registration**, no separate **Azure Bot Service** resource. One package powers Teams chat, Microsoft 365 Copilot Chat and BizChat *(secondary source)*. Works for prompt, hosted and workflow agents *(secondary source)*. Routed through **Microsoft 365 admin center** review/approval *(secondary source)* |
| **Data handling warning** | Microsoft 365/Teams **process and store** publishing data and agent responses under **their own** terms and data-residency commitments. Evaluate compliance first |
| **Private network projects** | Portal publishing **isn't supported when public network access is disabled**. Use the **REST API** with `enable_m365_public_endpoint` (source-IP-filtered public Activity route). **Teams/Copilot traffic is not private end to end.** If no public ingress is allowed, don't use this path |
| **Autopilot agents** *(public preview)* | Agents with their **own identity and user account** (email, calendar, Teams) *(June 2026 blog)* |

### 0.11 Observability, evaluation, optimisation

| Capability | Facts |
|---|---|
| **Tracing** | **GA for prompt, hosted and external agents** (workflow agents preview). Stored in **Application Insights** using **OpenTelemetry semantic conventions**. **Server-side tracing turns on automatically once you connect Application Insights**, with **no code change**. Add **client-side instrumentation** for your own surrounding logic |
| **Roles to read traces** | **Log Analytics Reader** on the connected Application Insights (plus **Privileged Monitoring Data Reader** if tables are protected) |
| **Evaluation** | Continuous evaluation: same evaluators in dev, CI/CD and production traffic. AI-assisted evaluators are **billed by tokens** |
| **Insights (preview)** | Analyses production traces into recurring, reviewable Insights. Needs a **GPT-5 or newer** deployment and connected App Insights |
| **Agent optimizer (preview)** | Evaluation-driven loop over a **dataset**: improves **instructions, function-tool descriptions, model selection** (hosted agents also **skills**). The optimizer can't evaluate **tool execution** for client-side function tools (it improves their descriptions) |
| **Why it matters** | An agent can return HTTP 200 and still call a tool with a **wrong parameter**. Traditional APM sees only the technical layer |

### 0.12 Five ideas the exam really tests

1. **Three runtime components:** response (one execution), agent (reusable config), conversation (persisted history). **Start with a response, add the others as needed.**
2. **Basic = Microsoft-managed state. Standard = your Storage + Cosmos DB + AI Search** for compliance/isolation. The **project** is the isolation unit.
3. **Roles:** Foundry User (create/edit), **Agent Consumer** (invoke only), **RBAC Administrator** for standard setup role assignments.
4. **Tools need real configuration** (tool, connection, model/region support). A **toolbox** centralises and versions tools. Approvals and least privilege protect risky actions.
5. **Mind lifecycle status:** hosted agents, memory, toolboxes, workflows, optimizer and A2A are **preview**. **Workflows retire Dec 1, 2026. Classic agents retire Mar 31, 2027.**

---

## 1. Scenario Questions

### Question 1: Pick the runtime component (drag-and-drop)

Match each need to: **Response · Agent · Conversation**.

| Need | Component |
|---|---|
| A. A one-off call to summarise a pasted paragraph, with no reuse or history | ? |
| B. Several apps must reuse the same instructions and tool set | ? |
| C. Follow-up questions must see earlier turns, stored server-side | ? |
| D. The unit that actually runs a model or agent against input and produces output items | ? |

<details>
<summary>Answer</summary>

| Need | Component |
|---|---|
| A | **Response** (start with a response for a single interaction) |
| B | **Agent** |
| C | **Conversation** |
| D | **Response** |
</details>

---

### Question 2: Context without a conversation

An app calls the service for each user turn but never creates a conversation. Users complain the agent "forgets" earlier turns. The team doesn't want to adopt server-side conversations yet. What are valid ways to carry context? (Select TWO)

A. **Reference a previous stored response** when creating the next response  
B. **Resend earlier items** with each request  
C. Increase temperature  
D. Create a second agent for each turn  
E. Disable streaming

<details>
<summary>Answer</summary>

### ✅ A and B

Without a conversation, context must be carried explicitly. A conversation is the server-side option.
</details>

---

### Question 3: Which agent type?

For each need, choose **Prompt agent · Voice-based prompt agent · Hosted agent · External agent calling the Responses API**.

| # | Need | Type |
|---|---|---|
| 1 | A support assistant defined entirely by instructions, a model and tools, with **no code or infrastructure** to manage | ? |
| 2 | A real-time spoken experience, without hosting its orchestration | ? |
| 3 | A custom framework and logic packaged as a **container**, with a **per-session sandbox and persistent filesystem** | ? |
| 4 | An agent already running in your own infrastructure that should use Foundry models and tools | ? |

<details>
<summary>Answer</summary>

| # | Type |
|---|---|
| 1 | **Prompt agent** |
| 2 | **Voice-based prompt agent** (through Voice Live) |
| 3 | **Hosted agent** (public preview) |
| 4 | **External agent via the Responses API** |
</details>

---

### Question 4: Basic or standard setup (compliance)

A regulated insurer requires that **all conversation history, uploaded files and vector stores remain in its own Azure subscription**, with **project-level isolation** and ownership of data residency. A pilot used the basic setup. What should they do?

A. Keep the basic setup. Microsoft-managed storage is under the customer's control  
B. Move to the **standard agent setup**: bring **Azure Storage, Azure Cosmos DB and Azure AI Search** and connect them through capability hosts  
C. Disable conversation storage  
D. Use a hub-based project

<details>
<summary>Answer</summary>

### ✅ B

Basic stores state in Microsoft-managed (logically separated) storage. Standard keeps agent state in customer-managed, single-tenant resources.

- **A ❌** Not customer-owned.
- **C ❌** Breaks the product's stateful design.
- **D ❌** Unrelated to data residency.
</details>

---

### Question 5: Where does each kind of data live? (drag-and-drop)

In a **standard setup**, match each data type to the BYO resource: **Azure Storage · Azure Cosmos DB · Azure AI Search**.

| Data | Resource |
|---|---|
| A. Files uploaded by developers and end users | ? |
| B. Messages, conversation history and agent metadata | ? |
| C. Vector stores created by the agent (file search) | ? |

<details>
<summary>Answer</summary>

| Data | Resource |
|---|---|
| A | **Azure Storage** |
| B | **Azure Cosmos DB** |
| C | **Azure AI Search** |
</details>

---

### Question 6: Standard setup deployment fails (snippet)

```json
{
  "pipeline_identity_roles": ["Foundry Account Owner (subscription)"],
  "step": "Provision standard agent setup (Cosmos DB, Storage, AI Search connections)",
  "error": "AuthorizationFailed: client does not have permission to perform action 'Microsoft.Authorization/roleAssignments/write'"
}
```

What is the MOST likely cause and fix?

A. The model deployment region is wrong  
B. For **standard setup**, the identity must also be able to **assign roles on the connected resources** (**Role Based Access Control Administrator**, or Owner). Foundry Account Owner alone creates the account and project but can't assign RBAC  
C. The agent needs the Foundry Agent Consumer role  
D. Cosmos DB needs serverless mode only

<details>
<summary>Answer</summary>

### ✅ B

The error names `roleAssignments/write`. Also confirm the deployment identity has **Storage Blob Data Contributor** and **Cosmos DB Operator** on the respective accounts.

**Trap:** The error text is the clue.
</details>

---

### Question 7: Least privilege (Select TWO)

A solution has **developers** who create and edit agents and a **public web app** whose identity only needs to **invoke** a published agent. Which TWO assignments follow least privilege?

A. **Foundry User** for the developers  
B. **Foundry Agent Consumer** for the web app identity  
C. Foundry Account Owner for the web app  
D. Role Based Access Control Administrator for the developers  
E. Foundry Owner for the web app

<details>
<summary>Answer</summary>

### ✅ A and B

- **C, E ❌** Over-privileged.
- **D ❌** Only needed to assign roles in a standard setup, not for authoring agents.
</details>

---

### Question 8: Project isolation

Two teams (**Payments** and **HR**) share one Foundry project. An HR agent's file-search vector store content appears in searches run by the Payments agent. Which statement explains this and gives the fix?

A. A model bug. Increase `max_tokens`  
B. **All agents in the same project share the same file storage, thread storage and search indexes.** Isolation requires **separate projects** (data is isolated between projects)  
C. Use different agent names  
D. Enable streaming

<details>
<summary>Answer</summary>

### ✅ B

The project is the unit of sharing and isolation. Naming doesn't isolate data.
</details>

---

### Question 9: Choose the tool (drag-and-drop)

Match each need to: **Code Interpreter · Function calling · MCP tool · OpenAPI tool · Toolbox · Memory · File search**.

| Need | Tool |
|---|---|
| A. Analyse an uploaded CSV and generate a chart | ? |
| B. Call your internal `get_order(order_id)` function, executed by your app | ? |
| C. Use tools hosted on a remote GitHub MCP server | ? |
| D. Call an existing REST API described by an OpenAPI spec | ? |
| E. Reuse and version the same tool set across eight agents with central credentials | ? |
| F. Remember a user's preferred language across sessions | ? |
| G. Answer questions over PDFs attached to a conversation | ? |

<details>
<summary>Answer</summary>

| Need | Tool |
|---|---|
| A | **Code Interpreter** |
| B | **Function calling** (client-side execution) |
| C | **MCP tool** |
| D | **OpenAPI tool** |
| E | **Toolbox** |
| F | **Memory** (preview) |
| G | **File search** |
</details>

---

### Question 10: Code Interpreter surprises (Select TWO)

A data team enables **Code Interpreter**. Their bill rises beyond token costs, and under load they notice more sandboxes than users. Which TWO statements are correct?

A. Code Interpreter has **additional charges beyond token-based fees**  
B. If an agent calls it **simultaneously in two conversations, two sessions** are created (each active about an hour by default, with a **30-minute idle timeout**)  
C. Code Interpreter is free and shared across all conversations  
D. A single session is reused across all users forever  
E. It isn't sandboxed

<details>
<summary>Answer</summary>

### ✅ A and B

Also check **regional and model availability**, since the tool isn't available everywhere.
</details>

---

### Question 11: Approval and connection roles (MCP)

An agent uses a remote **MCP server** that exposes `create_remedy_case` (writes to a system of record). The team wants **a human to approve each call**, and an engineer must **create the project connection** that stores the MCP credentials. Which TWO statements are correct?

A. Configure **approval for MCP tool calls** (human-in-the-loop) so the agent pauses for confirmation. In a toolbox you can set **`require_approval`** per tool  
B. Creating the **project connection** for MCP authentication needs **Foundry Project Manager** on the project (**Foundry User** is needed to create and test agents)  
C. Writing "ask permission first" in the instructions provides guaranteed enforcement  
D. MCP servers are always inside Foundry's compliance boundary  
E. No role is needed to create connections

<details>
<summary>Answer</summary>

### ✅ A and B

- **C ❌** Instructions guide. Approval gates enforce.
- **D ❌** Non-Microsoft servers may process data outside the compliance boundary under their own terms.
</details>

---

### Question 12: Toolbox benefits (Select TWO)

Eight agents each wire the same five tools with different credentials, and a security review finds inconsistent governance. Which TWO statements describe how a **toolbox** helps?

A. Curate the tools **once**, version them, and expose them through **one managed MCP endpoint** that agents (and other runtimes) consume  
B. **Centralise authentication, policy and versioning** instead of duplicating credentials per agent  
C. A toolbox is an agent  
D. A toolbox deploys the external MCP servers for you  
E. Toolboxes are generally available with an SLA in every region

<details>
<summary>Answer</summary>

### ✅ A and B

A toolbox is **not** an agent or a deployment. Its owner manages contents, versions and policies. Toolboxes are **preview**, and tool availability varies by region and model. Foundry User is needed for the developer, the agent identity, and (for OAuth flows) end users.
</details>

---

### Question 13: Memory design (Select TWO)

A shopping assistant should remember **each customer's dietary preferences across sessions and devices**, with isolation between customers and the ability to **honour "forget this"** requests. Which TWO design points are correct?

A. Use **memory** with a **scope keyed to the customer's identity** (for example, Entra ID or a UUID) so each scope is an isolated collection, and treat **scope as a security boundary**  
B. Use **item-level management and remember-or-forget commands** (and a **default TTL**) to honour deletion and retention policies  
C. Put all customers in a single scope to save storage  
D. Memory updates are instant, so tests can query immediately after sending a preference  
E. Memory replaces grounding data, so you don't need documents

<details>
<summary>Answer</summary>

### ✅ A and B

- **C ❌** Breaks isolation.
- **D ❌** Updates are **asynchronous**. Wait for the configured delay.
- **E ❌** Memory is user-specific distilled knowledge. Grounding supplies authoritative content.

Memory is **preview**, so limits and behavior can change.
</details>

---

### Question 14: Multi-agent plan (Select TWO)

A team plans a new multi-agent solution using **connected agents** and a **visual portal workflow**. Which TWO statements reflect the current guidance?

A. Connected agents are a **classic-platform** mechanism that the new Agent Service **removed**, with the **A2A tool** as the replacement *(secondary source)*  
B. **Portal workflows are preview and Foundry is retiring them on December 1, 2026.** For new workflows, use **Microsoft Agent Framework**  
C. Portal workflows are GA and permanent  
D. Connected agents are the recommended new approach  
E. Code-based orchestration in hosted agents is also retiring on December 1, 2026

<details>
<summary>Answer</summary>

### ✅ A and B

- **E ❌** The workflow retirement **doesn't affect code-based orchestration in hosted agents**.

Verify current status, since this area has changed several times.
</details>

---

### Question 15: Classic agents

A team's production assistant still runs on **Foundry Agent Service (classic)** threads and runs. What should they plan?

A. Nothing. Classic agents are permanent  
B. **Migrate to the new GA Agent Service before classic agents retire on March 31, 2027**, following the migration guide  
C. Convert to Assistants API only  
D. Delete all agents

<details>
<summary>Answer</summary>

### ✅ B
</details>

---

### Question 16: Publishing (snippet)

```json
{
  "agent": "claims-assistant (prompt agent, v7 tested)",
  "need": ["Share with partner companies without giving them access to the Foundry project",
           "Keep the same URL when v8 ships",
           "Separate identity and RBAC from the project's shared identity"],
  "current": "Partners are added as Foundry project users"
}
```

What is the BEST approach?

A. Keep adding partners to the project  
B. **Publish the agent** so it becomes an **Agent Application** (managed Azure resource) with a **stable endpoint, its own Entra agent identity/blueprint and independent RBAC**, then grant partners access to invoke it. New versions roll out behind the same endpoint  
C. Share the project API key  
D. Export the agent as a PDF

<details>
<summary>Answer</summary>

### ✅ B

In a project, everyone with access can interact with all agents and shares conversation context and permissions. Publishing gives external sharing, a stable URL and separate authorization. Grant invoke access with a role such as Foundry Agent Consumer on the application scope.
</details>

---

### Question 17: Teams and Copilot publishing (Select TWO)

A compliance team asks about publishing a Foundry agent to **Microsoft Teams and Microsoft 365 Copilot** from a project with **public network access disabled**. Which TWO statements are correct?

A. Foundry handles **Teams bot registration**, so **no separate Azure Bot Service resource** is needed  
B. **Portal publishing isn't supported** for projects with public network access disabled. Use the **REST API** with the source-IP-filtered public Activity route (`enable_m365_public_endpoint`), and note this channel path is **not private end to end**  
C. Teams/Copilot traffic travels over the project's private endpoint  
D. Microsoft 365 and Teams don't store any data related to the agent  
E. No compliance review is needed

<details>
<summary>Answer</summary>

### ✅ A and B

Microsoft 365/Teams process and store publishing data and responses under their own terms and residency commitments, so evaluate compliance first. If no public ingress is allowed at all, don't use this path.
</details>

---

### Question 18: Hosted agent facts (Select TWO)

Which TWO statements about **hosted agents** are correct?

A. You **bring your own code and framework as a container**, and Foundry provides a managed endpoint, scaling and identity  
B. Each session gets its own **VM-isolated sandbox with a persistent filesystem**, and agents can **scale to zero** and resume with files intact  
C. Hosted agents are GA with no additional permissions needed  
D. Hosted agents can't use virtual networks  
E. Hosted agents can't be versioned

<details>
<summary>Answer</summary>

### ✅ A and B

Hosted agents are **public preview**, need **additional permissions/RBAC**, support **BYO VNet** for outbound traffic, and provide **versioning with stable endpoints and weighted rollouts**.
</details>

---

### Question 19: Tracing (snippet)

```json
{
  "agent": "refund-assistant (prompt agent)",
  "observed": "HTTP 200, normal latency, no exceptions. A customer reports a $5,000 refund instead of $500.",
  "tracing": "Not configured"
}
```

What should the team do FIRST to diagnose which step produced the wrong amount? (Select TWO)

A. **Connect Application Insights** to the project (server-side tracing turns on automatically, with no code change)  
B. Grant engineers **Log Analytics Reader** on the connected Application Insights so they can query traces  
C. Increase temperature  
D. Remove the refund tool  
E. Rely on HTTP status codes

<details>
<summary>Answer</summary>

### ✅ A and B

Traces show tool calls, arguments, latency and retrieval operations. Add **continuous evaluation** and a **require-approval** gate for the refund tool going forward.

**Trap:** HTTP 200 means the request succeeded technically, not that the behavior was correct.
</details>

---

### Question 20: Agent optimizer

A team wants to improve a prompt agent's **instructions**, its **function-tool descriptions**, and test **alternative model deployments**, using a dataset of real scenarios. Which feature fits?

A. Fine-tuning every week  
B. **Agent optimizer (preview)**: an evaluation-driven loop that generates improved instructions, tool descriptions and model selections (hosted agents also get skills)  
C. Content filters  
D. Private endpoints

<details>
<summary>Answer</summary>

### ✅ B

Limitation: for client-side function tools it improves the tool and parameter **descriptions** but **can't evaluate the tool execution**. It's preview, so no SLA.
</details>

---

### Question 21: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | A response can run with or without an agent or a conversation. | |
| 2 | Basic setup stores agent state in your own Cosmos DB. | |
| 3 | Agents in the same project can access each other's files and vector stores by default. | |
| 4 | Foundry Agent Consumer can create and edit agents. | |
| 5 | Function-calling tools for prompt agents run on the client side. | |
| 6 | Tracing is GA for prompt, hosted and external agents. | |
| 7 | Agent data stored by the service is deleted automatically after 30 days. | |
| 8 | Portal workflows retire on December 1, 2026. | |
| 9 | A toolbox is an agent that can answer user questions. | |
| 10 | Not every model and region supports every tool. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **Yes** | The response is the unit of execution. |
| 2 | **No** | That's **standard** setup. Basic is Microsoft-managed. |
| 3 | **Yes** | The project is the sharing/isolation unit. |
| 4 | **No** | Consumer is invoke-only. **Foundry User** creates/edits. |
| 5 | **Yes** | Per the optimizer documentation. |
| 6 | **Yes** | Workflow agents are preview. |
| 7 | **No** | Data persists until you delete it. |
| 8 | **Yes** | Per Microsoft Learn. |
| 9 | **No** | A toolbox shares tools and skills through an MCP endpoint. |
| 10 | **Yes** | Check tool support by region/model. |
</details>

---

### Question 22: Match the symptom to the fix (drag-and-drop)

Match each symptom to: **Standard setup · Separate projects · Foundry Agent Consumer · Role Based Access Control Administrator · Toolbox · Approval gate on the tool · Memory with a scope · Connect Application Insights · Publish as Agent Application · Migrate off classic agents · Agent Framework**.

| Symptom | Fix |
|---|---|
| A. Data must stay in the customer's subscription | ? |
| B. Teams must not see each other's vector stores | ? |
| C. A web app should only call agents | ? |
| D. Standard-setup deployment fails on role assignment | ? |
| E. Five tools are duplicated across eight agents | ? |
| F. A destructive tool must never run unreviewed | ? |
| G. Remember a user's preferences across sessions | ? |
| H. Can't tell which step produced a wrong answer | ? |
| I. Partners need a stable URL without project access | ? |
| J. Production still on threads/runs (classic) | ? |
| K. New multi-agent orchestration after workflows retire | ? |

<details>
<summary>Answer</summary>

| Symptom | Fix |
|---|---|
| A | **Standard setup** |
| B | **Separate projects** |
| C | **Foundry Agent Consumer** |
| D | **Role Based Access Control Administrator** |
| E | **Toolbox** |
| F | **Approval gate on the tool** |
| G | **Memory with a scope** |
| H | **Connect Application Insights** (tracing) |
| I | **Publish as Agent Application** |
| J | **Migrate off classic agents** |
| K | **Microsoft Agent Framework** |
</details>

---

## 2. Mini Case Study: Woodgrove Bank Agent Platform

### Background

Woodgrove Bank is building agents on Foundry Agent Service.

1. A customer-service agent must keep **all conversation history, files and vector stores in the bank's own subscription**, and **retail and corporate teams must not see each other's data**.
2. The agent uses **five tools** (CRM MCP server, refund API, knowledge search, ticketing, FX rates). **Eight agents** need the same tools, with **centralised credentials and versioning**.
3. The **refund tool writes to the ledger**. A human must approve every refund above a limit.
4. Customers should be recognised across sessions (**language and preferred branch**), and **"forget me"** must work.
5. The agent must be offered to **partner brokers** at a **stable URL** that doesn't change when new versions ship, **without giving brokers access to the Foundry project**.
6. The agent must also appear in **Microsoft Teams** for staff. The project has **public network access disabled**.
7. After launch, a refund agent returned HTTP 200 while **refunding the wrong amount**. The team has **no tracing**.
8. The platform team still has an old **classic** agent and a **portal workflow** with branching approvals.
9. A pipeline provisions the **standard setup** but fails on role assignment.

### Case Q1: State and isolation (requirement 1)

Which TWO?

A. **Standard agent setup** with **BYO Storage, Cosmos DB and AI Search**  
B. **Separate projects** for retail and corporate (the project is the isolation unit)  
C. Basic setup with different agent names  
D. One shared project with naming conventions

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q2: Shared tools (requirement 2)

A. Copy the credentials into each agent  
B. A **toolbox** exposing the five tools through one managed MCP endpoint, versioned, with central credentials. Developer, agent identity and (for OAuth flows) end users get **Foundry User**  
C. A hub-based project  
D. A larger model

<details><summary>Answer</summary>

### ✅ B

Remember: toolbox is **preview**, and tool support varies by region and model.
</details>

### Case Q3: Refund control (requirement 3)

Which TWO?

A. **Approval (human-in-the-loop)** for the refund tool (`require_approval` in a toolbox, or MCP approval)  
B. Enforce the **limit in the refund API/backend** as well  
C. Only write "ask a human" in the instructions  
D. Lower temperature

<details><summary>Answer</summary>

### ✅ A and B

Guidance isn't enforcement. This repeats the Agent instructions lesson.
</details>

### Case Q4: Cross-session recognition (requirement 4)

A. Resend all history every time  
B. **Memory** (preview): a memory store with a **scope per customer identity**, **item-level management**, **remember-or-forget** commands and a **default TTL**  
C. One shared scope  
D. Store preferences in the system prompt

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q5: Brokers (requirement 5)

A. Add brokers to the project  
B. **Publish as an Agent Application**: stable endpoint, own Entra agent identity/blueprint and RBAC. Grant brokers invoke-only access (for example, **Foundry Agent Consumer**)  
C. Share keys  
D. Email the agent

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q6: Teams with a private project (requirement 6)

Which TWO statements are correct?

A. Foundry handles Teams bot registration, so **no Azure Bot Service resource** is needed  
B. **Portal publishing isn't available** for projects with public network access disabled. Use the **REST API** with `enable_m365_public_endpoint`, accepting that this channel route **isn't private end to end**  
C. Teams uses the project's private endpoint  
D. No data is stored by Microsoft 365 or Teams

<details><summary>Answer</summary>

### ✅ A and B

Also review the compliance implications of Microsoft 365/Teams processing.
</details>

### Case Q7: The wrong refund (requirement 7)

Which TWO?

A. **Connect Application Insights** (automatic server-side tracing)  
B. Give engineers **Log Analytics Reader** on it, and add **continuous evaluation**  
C. Rely on HTTP status codes  
D. Increase temperature

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q8: Legacy items (requirement 8)

Which TWO?

A. Migrate the **classic** agent to the new Agent Service before **March 31, 2027**  
B. Plan to move the **portal workflow** to **Microsoft Agent Framework** before **December 1, 2026**  
C. Do nothing, both are permanent  
D. Rebuild everything as connected agents

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q9: Pipeline failure (requirement 9)

A. Change the model region  
B. Give the pipeline identity **Role Based Access Control Administrator** (or Owner), plus **Storage Blob Data Contributor** and **Cosmos DB Operator** on the respective accounts  
C. Switch to basic setup  
D. Give the pipeline Foundry Agent Consumer

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q10: Map the requirement to the feature

| Requirement | Feature |
|---|---|
| Data in the bank's subscription | ? |
| Retail vs corporate isolation | ? |
| Shared tools, central credentials | ? |
| Refund approval | ? |
| Cross-session preferences | ? |
| Broker access at a stable URL | ? |
| Teams, private project | ? |
| Diagnose wrong refunds | ? |
| Legacy workflow | ? |
| Role assignment failure | ? |

<details><summary>Answer</summary>

| Requirement | Feature |
|---|---|
| Data in the bank's subscription | Standard setup |
| Retail vs corporate isolation | Separate projects |
| Shared tools, central credentials | Toolbox (preview) |
| Refund approval | Approval gate + backend limit |
| Cross-session preferences | Memory with identity scope (preview) |
| Broker access at a stable URL | Agent Application, invoke-only role |
| Teams, private project | REST publishing with the M365 public endpoint (not private end to end) |
| Diagnose wrong refunds | App Insights tracing + evaluation |
| Legacy workflow | Microsoft Agent Framework |
| Role assignment failure | Role Based Access Control Administrator |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Component trap** | "An agent holds the conversation." | **Conversation** holds history. **Agent** supplies reusable config. **Response** runs. |
| **Always-agent trap** | "Every call needs an agent and a conversation." | Start with a **response**, add the others as needed. |
| **Basic-ownership trap** | "Basic setup is in my subscription." | Basic = **Microsoft-managed**. Standard = **yours**. |
| **Standard-roles trap** | "Foundry Account Owner is enough." | Standard also needs **RBAC Administrator/Owner** (`roleAssignments/write`) plus data roles on Storage/Cosmos. |
| **Project trap** | "Agent names isolate data." | **Projects** isolate. Agents in one project share storage/indexes. |
| **Consumer trap** | "Consumer can tweak agents." | **Invoke only.** Foundry User creates/edits. |
| **Tool-definition trap** | "Creating a connection attaches the tool." | A connection supplies auth/endpoint. The tool must still be added. |
| **Model/region trap** | "Every tool works with every model." | Check **tool support by region and model**. |
| **Function-call trap** | "Foundry executes my function." | For prompt agents, function tools **run client-side**. |
| **Approval trap** | "Instructions enforce approval." | Use **approval gates** (and backend limits). |
| **Toolbox trap** | "A toolbox is an agent." | A shared, versioned bundle behind an MCP endpoint (preview). |
| **Memory trap** | "Memory = chat history." | Memory is distilled, scoped, **asynchronous**, preview. History is a transcript. |
| **Scope trap** | "One scope is fine." | Scope is a **security boundary**. Key it by user identity. |
| **Workflow trap** | "Portal workflows are the future." | **Retire Dec 1, 2026.** Use **Microsoft Agent Framework**. |
| **Connected-agents trap** | "Use connected agents for new designs." | Classic mechanism, removed in the new service *(secondary source)*. A2A is the replacement (preview). |
| **Classic trap** | "Classic agents are permanent." | **Retire March 31, 2027.** |
| **Publish-trap** | "Add partners to the project." | **Publish** an Agent Application (stable endpoint, own identity/RBAC). |
| **Teams-privacy trap** | "Teams publishing stays on the private endpoint." | Source-IP-filtered **public** Activity route, **not private end to end**. |
| **HTTP-200 trap** | "No errors means correct behavior." | Use **tracing and evaluation**. |
| **Preview trap** | "Hosted agents, memory, toolbox, optimizer are GA." | **Preview**, no SLA. Verify. |
| **Code-Interpreter-cost trap** | "Only tokens are billed." | **Extra charges** and **per-conversation sessions**. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| Least to manage, text agent | **Prompt agent** |
| Real-time voice | **Voice-based prompt agent** |
| Custom code/framework, per-session sandbox | **Hosted agent** (preview) |
| Existing agent elsewhere using Foundry models | **Responses API** |
| One-off call | **Response** |
| Reuse instructions + tools | **Agent** |
| Server-side history | **Conversation** |
| Data must stay in my subscription | **Standard setup** (BYO Storage, Cosmos DB, AI Search) |
| Teams need data isolation | **Separate projects** |
| Create/edit agents | **Foundry User** |
| Invoke only | **Foundry Agent Consumer** |
| Assign RBAC for standard setup | **RBAC Administrator** / Owner |
| Create project connections | **Foundry Project Manager** |
| Run Python for analysis/charts | **Code Interpreter** (extra cost, sessions) |
| Your own function | **Function calling** (client-side) |
| Remote tool server | **MCP tool** (+ approvals, connection) |
| Reuse tools across agents with governance | **Toolbox** (preview) |
| Persist user preferences across sessions | **Memory** (preview, scoped) |
| Multi-agent in new builds | **Microsoft Agent Framework** (workflows retire Dec 1, 2026) |
| Agent-to-agent | **A2A tool** (preview) |
| Share externally with stable URL | **Publish as Agent Application** |
| Staff access in Teams/Copilot | **Publish to Microsoft Copilot/Teams** (no Azure Bot Service) |
| Private project and Teams | REST + `enable_m365_public_endpoint` (not private end to end) |
| Diagnose agent steps | **Application Insights tracing** |
| Improve instructions/tool descriptions/model | **Agent optimizer** (preview) |
| Still on classic agents | Migrate before **March 31, 2027** |

---

## 5. Quick Revision Sheet

```text
FOUNDRY AGENT SERVICE = managed platform: runtime, toolboxes, models, observability, optimization, identity/security, publishing
BUILD PATHS : prompt agent (declarative, no code) | voice prompt agent | hosted agent (container, preview) | external via Responses API
RUNTIME     : RESPONSE = one execution | AGENT = reusable model+instructions+tools | CONVERSATION = persisted history
              start with a response; carry context via previous response ID or resend items; stateful - data persists until deleted

SETUP  : BASIC = Microsoft-managed state (Assistants-compatible)
         STANDARD = BYO Storage (files) + Cosmos DB (threads/metadata) + AI Search (vector stores); capability hosts; Cosmos >=3000 RU/s
         PROJECT = isolation unit (agents in a project share files/threads/indexes)
ROLES  : Account Owner (create) | RBAC Administrator (standard-setup role assignments) | Foundry User (create/edit agents)
         Foundry Agent Consumer (invoke only) | Project Manager (connections)

TOOLS  : function calling (client-side) | Code Interpreter (extra cost, sessions: ~1h active, 30m idle) | MCP (approvals, connection)
         OpenAPI | A2A (preview) | file search / AI Search / SharePoint / Fabric / web (Grounding file)
         tool support varies by region AND model | instructions guide, tool_choice forces
TOOLBOX (preview): curated, versioned tools -> one managed MCP endpoint; central auth/governance; require_approval
MEMORY  (preview): memory store + SCOPE (security boundary); extraction -> consolidation -> retrieval; async; TTL; forget
MULTI-AGENT: connected agents removed (secondary) -> A2A | workflows RETIRE Dec 1, 2026 -> Microsoft Agent Framework
CLASSIC AGENTS retire Mar 31, 2027

PUBLISH: Agent Application = stable endpoint + own Entra agent identity/blueprint + own RBAC; Responses/Activity protocols
         Teams/Copilot: Foundry bot registration, no Azure Bot Service, admin-center review (secondary);
         private project -> REST + enable_m365_public_endpoint (NOT private end to end); M365 stores data under its own terms
OBSERVE: connect App Insights -> automatic server-side tracing (GA prompt/hosted/external; workflow preview); OpenTelemetry
         Log Analytics Reader to query | continuous evaluation | Insights (preview) | Agent optimizer (preview)
```

### Best-answer checklist

1. Which **runtime component** does the requirement describe (response, agent, conversation)?
2. **Compliance or data ownership** needs? **Standard setup.** **Team isolation**? **Separate projects.**
3. Check the **role** (create/edit vs invoke-only vs RBAC assignment vs connection creation).
4. A tool problem? Is it the **tool, connection, model/region support, approval, or instructions**?
5. Shared tools across agents? **Toolbox.** Cross-session user facts? **Memory** with a scoped identity.
6. External or Teams distribution? **Publish** (stable endpoint, own identity). Mind the **private network** caveat.
7. "Works but wrong"? **Tracing and evaluation**, not HTTP status.
8. Is the feature **preview or retiring**? Flag **no SLA / migration dates**.

---

**Pending from the original list:** *Agents* (concept overview). Send it when you want it, or send the next topic.

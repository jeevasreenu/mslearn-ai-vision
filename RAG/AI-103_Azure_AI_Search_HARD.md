# AI-103: Azure AI Search / Foundry IQ (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, config snippets, capacity arithmetic, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Scope: the **service itself**: pricing models and tiers, replicas/partitions/search units, the indexer pipeline (data source → indexer → skillset → index), AI enrichment and knowledge store, security (keys vs Entra ID roles), and how it relates to Foundry IQ. The retrieval methods (vector, semantic, hybrid) have their own files and are only referenced here.
> Microsoft Learn now labels many pages **"Foundry IQ (Azure AI Search)"**. Same service, new branding. Tier limits, preview status and prices change, so the exam logic matters more than the numbers.

---

## 0. Core Concepts (read first)

### 0.1 What Azure AI Search is (and isn't)

**Azure AI Search** is a managed search service that indexes content and serves **keyword (BM25), vector, hybrid, semantic-ranked, and agentic retrieval** queries for apps and AI agents. It underpins **Foundry IQ**, the managed knowledge layer that turns enterprise content into reusable, **permission-aware knowledge bases** for agents in Microsoft Foundry.

- It's a **search/retrieval engine**, **not a primary data store**. Indexers connect to **external data sources**, so your content still lives in Blob Storage, SQL, Cosmos DB, SharePoint, and so on.
- A **search service** contains many **indexes**. Each index has a schema of fields.
- Two engines share the same infrastructure: **classic search** (single-shot query against an index, GA) and **agentic retrieval** (LLM-assisted multi-query over a knowledge base; parts were preview).

### 0.2 Two pricing models

| | **Dedicated** | **Serverless** *(preview)* |
|---|---|---|
| Best for | **Steady, predictable, high-utilisation** workloads | **Infrequent, bursty, highly variable** workloads (including agent-driven and multitenant) |
| Capacity | **You provision** replicas × partitions on a chosen **service tier** | **Automatic**. You don't configure replicas, partitions or search units |
| Billing | Fixed **hourly rate by Search Units (SUs)** and tier, **always incurred** | **Consumption**: **Compute Units (CUs)** plus **indexed storage (GB/month)**. **Scales to zero** when idle |
| Planning focus | Infrastructure sizing | Workload efficiency (query patterns, index size, ingestion pattern) |
| Tier | Free, Basic, Standard (S1–S3, S3 HD), Storage Optimized (L1–L2) | **Serverless Developer** (preview tier) |
| Caveats | Pay for idle capacity | **No SLA, not recommended for production** (preview). **Doesn't support migration to or from other pricing tiers.** Some features unsupported. Limited regions |

> **SUs and CUs are not interchangeable.** Don't use SU-based calculators for Serverless. One CU is roughly 1 vCPU core + 8 GB RAM + associated storage I/O.

### 0.3 Dedicated tiers

| Tier | Facts to remember |
|---|---|
| **Free** | **One per subscription.** Shared infrastructure, **no scale-up**, **50 MB storage**, **no SLA**, 1 replica, limited to **3 indexes / 3 indexers / 3 data sources**, may be **deleted after extended inactivity**. **Never for production** |
| **Basic** | Supports **production workloads** and can meet the SLA with up to **three replicas**. Up to **3 partitions and 3 replicas (9 SU)** on services created after April 3, 2024 |
| **Standard (S1, S2, S3, S3 HD)** | **Default tier.** Scale partitions and replicas up to **36 SU**. Larger and faster partitions as you move up |
| **Storage Optimized (L1, L2)** | **Larger storage per partition**, for big indexes with lower query volumes |

The tier determines: **max indexes/objects**, **size and speed of partitions**, **billable rate**, **workload characteristics**, and sometimes **premium feature availability**.

### 0.4 Replicas, partitions, search units (high-yield arithmetic)

$$\text{SU} = \text{replicas} \times \text{partitions}$$

| Lever | Provides | Add it when |
|---|---|---|
| **Replicas** (copies of the search engine; 1–12) | **Query throughput (QPS)** and **high availability** | Queries are slow under load, or you need the SLA |
| **Partitions** (units of storage) | **Storage capacity** and **indexing throughput** | The index is near its storage limit, or indexing is too slow |

- You pay for **both** (an SU is "allocated as either a replica or a partition. You need both").
- **SLA:** use a **billable tier with at least 2 replicas** for **read-only** workloads and **3 or more replicas for read-write** workloads. **Free tier has no SLA.**
- Extra replicas also let maintenance happen on one replica while queries continue on the others.
- **Replicas don't speed up ingestion**, and **partitions don't increase query concurrency**.

Example: 3 replicas × 4 partitions = **12 SU**. Doubling query capacity with the same storage: 6 replicas × 4 partitions = **24 SU**.

### 0.5 The core objects and the indexer pipeline

```text
 DATA SOURCE ──► INDEXER ──► [SKILLSET: enrichment] ──► INDEX ──► queries
 (Blob, SQL,      (crawler;     (optional; skills        (searchable
  Cosmos DB,       runs on-      read/write an in-        schema + data)
  SharePoint…)     demand or     memory "enriched
                   on schedule)  document tree")
                                      └──► KNOWLEDGE STORE (optional, Azure Storage)
```

| Object | Role |
|---|---|
| **Data source** | Connection to external content |
| **Indexer** | Crawler that pulls content, **cracks documents** (extracts text/images), runs the skillset, and loads the index. Can run **on a schedule** |
| **Skillset** | Reusable set of **skills** attached to an indexer. Built-in or custom |
| **Index** | Schema of fields plus the searchable data. Where queries run |
| **Field mappings** | Move **raw source fields** unchanged into index fields |
| **Output field mappings** | Move **enriched nodes** from the in-memory enrichment tree into index fields |
| **Index projections** | Map one source document to **many chunk documents** (covered in Chunking) |
| **Knowledge store** | **Secondary output** of a skillset: projects enriched data to **Azure Storage** (table, object and file projections) for analytics or downstream apps |

**Two ways to get data in**

| Model | How | Use when |
|---|---|---|
| **Pull (indexer)** | Indexer crawls a supported data source | Supported sources, scheduled refresh, built-in enrichment |
| **Push (API/SDK)** | Your code uploads documents to the index | Custom pipelines, unsupported sources, real-time updates, or you already chunk and embed in code |

### 0.6 AI enrichment (skills)

AI enrichment = integrating **Foundry Tools** (and your own code) to make content searchable that isn't searchable raw.

- **Built-in skills** include: translation and language detection, **entity recognition**, **key phrase extraction**, **OCR** (printed/handwritten text), **image analysis** (descriptions as text), **Text Split** (chunking), **Azure OpenAI embedding**, and **Azure Vision multimodal embeddings**.
- **Custom skills** call **your external code** (Web API).
- **Raw content must be text or images.** You **can't enrich vectors**, but the **output** of enrichment can be vectorised and indexed.
- Skills have a **context** (whole document `/document` or a node deeper in the tree), **inputs**, and **outputs** (new nodes in the enrichment tree).
- A pipeline that uses built-in cognitive skills needs an **attached Foundry Tools resource** (billing for those skills). The **Text Split skill is non-billable.**
- Some enrichment features are **billed as add-ons**: the pricing page lists **agentic retrieval, semantic ranker, custom entity lookup skill, and document cracking (image extraction)**.

### 0.7 Index schema essentials (general Azure AI Search knowledge, verify on Learn)

| Field attribute | Enables |
|---|---|
| **key** | Unique document ID (exactly one string key field) |
| **searchable** | Full-text (and, for vectors, vector) search |
| **filterable** | `$filter` expressions |
| **sortable** | `$orderby` |
| **facetable** | Facet counts / navigation |
| **retrievable** | Field can be returned in results |

- **Vector fields:** `Collection(Edm.Single)` plus `dimensions` and a vector profile. **Not filterable.** (See Vector Search.)
- **Scoring profiles** and **semantic configurations** can be **added or changed without rebuilding** the index.
- **Changing an existing field's type or attributes generally requires dropping and rebuilding the index.** Plan the schema before loading big data.

### 0.8 Security

**Authentication options (data plane)**

| Option | Notes |
|---|---|
| **API keys** (default at creation) | **Not the most secure**. Coarse: **admin key** = full service access, **query key** = read-only on an index. Can't attribute actions to a person |
| **Role-based access control (Microsoft Entra ID)** | **Recommended.** Optional, enabled on the service. No keys in code. Works with managed identities, Conditional Access |
| **Both** | Migration mode. **If a request carries both, the API key is used** |

Failure mode for unauthorised requests: **`http401WithBearerChallenge`** (default) or `http403`.

**Control plane vs data plane**
- **Control plane:** create/delete services, list keys, scale, network and auth settings (Azure Resource Manager). **Always available** (can't be switched off).
- **Data plane:** operations on the service endpoint: **object management** (indexes, indexers) and **content access** (query/upload). **Data plane roles only work when role-based access is enabled.**

**Built-in roles**

| Role | Grants |
|---|---|
| **Search Service Contributor** | Manage the service's **objects** (indexes, indexers, skillsets, and so on). **Not** a content reader |
| **Search Index Data Contributor** | **Read/write** index content (upload, update, delete, query) |
| **Search Index Data Reader** | **Read-only query** access |

Facts:
- Multiple role assignments **combine**.
- You can **scope a role to a single index** (or other single object), which is valuable for **multi-tenant isolation**.
- To assign roles, you need **Owner, User Access Administrator, Role Based Access Control Administrator**, or a custom role with `Microsoft.Authorization/roleAssignments/write`.
- On a **roles-only** service, even an administrator must be **assigned data plane roles** to get full data plane access in the portal.
- **Document-level access control** (row-level security) restricts **which documents each user can retrieve**, and is enforced **at retrieval**. It's the foundation of **permission-aware** Foundry IQ knowledge bases.
- Network controls (general knowledge, verify): **private endpoints** for inbound, **shared private link** for indexer outbound to private data sources, **managed identity** from search to data sources and to the Azure OpenAI embedding model.

### 0.9 Foundry IQ relationship

| Term | Meaning |
|---|---|
| **Foundry IQ (Azure AI Search)** | Search service direct APIs **plus** managed retrieval layer |
| **Knowledge source** | Connection to content (Blob, SharePoint, OneLake, web, existing index…). Can **auto-generate** the indexer pipeline |
| **Knowledge base** | Reusable, topic-centric bundle of knowledge sources and retrieval settings, shared by many agents |
| **Agent connection** | Via the **MCP tool** in Foundry Agent Service, and needs a **Foundry project** (not **hub-based**) |
| **Billing** | Knowledge bases require a **standard agentic retrieval plan**. Activity is billed under "Azure AI Search" |

### 0.10 Common problems and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Queries slow under heavy traffic | Not enough replicas | **Add replicas** |
| Index near storage cap / slow indexing | Not enough partitions | **Add partitions** (or Storage Optimized tier) |
| No SLA on production | Free tier or only 1 replica | Billable tier with **2+ replicas (read-only) / 3+ (read-write)** |
| Free service disappeared | Inactivity deletion | Don't use Free for anything important |
| Can't scale Free service | No scale-up on Free | Upgrade to a billable tier (create a new service) |
| Can't move Serverless to Dedicated | **No migration** between pricing models | Create a new service and re-index |
| 401/403 after enabling roles | No **data plane** role assigned | Assign **Search Index Data Reader/Contributor** |
| Admin key shared by developers | Key-based default | Enable **RBAC**, assign roles, disable keys when ready |
| Enriched field missing in index | No **output field mapping** or no matching index field | Add output field mapping and index field |
| Can't search scanned PDFs | No OCR | Add **OCR skill** (via skillset) |
| Need enriched data in Power BI/analytics | Only index output configured | **Knowledge store** projections |
| Tenants see each other's docs | One shared index, no trimming | **Per-tenant indexes** with scoped roles, or **document-level access control** |
| Semantic/agentic billing surprise | Add-on features | Check plan and billing consent |

### 0.11 Five ideas the exam really tests

1. **SU = replicas × partitions. Replicas = query throughput and HA. Partitions = storage and indexing speed.**
2. **SLA needs 2+ replicas (read-only) or 3+ (read-write).** Free tier has no SLA.
3. **Pipeline: data source → indexer → (skillset) → index.** Search isn't your primary data store.
4. **Prefer Entra ID role-based access over keys.** Control plane ≠ data plane. Reader/Contributor/Service Contributor differ.
5. **Serverless = consumption, scales to zero, preview, no migration. Dedicated = provisioned, predictable, hourly.**

---

## 1. Scenario Questions

### Question 1: Pricing model

Pick the BEST pricing model for each workload.

| # | Workload | Dedicated / Serverless |
|---|---|---|
| 1 | An internal agent prototype used a few times a week, where the team wants to pay close to nothing when idle and avoid capacity planning | ? |
| 2 | A customer-facing search with steady, high-utilisation traffic that requires an **SLA** | ? |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **Serverless** (preview) | Infrequent/variable traffic, scales to zero, consumption billing. Acceptable for a prototype |
| 2 | **Dedicated** (Basic/Standard with 2+ or 3+ replicas) | Steady load plus SLA. Serverless Developer is preview with no SLA |

**Trap:** "Bursty" alone doesn't justify Serverless if the workload needs an SLA today.
</details>

---

### Question 2: Which scale lever? (capacity arithmetic)

A production service has **2 replicas × 2 partitions** (S1). Storage use is 40% of capacity, but during peak hours **query latency doubles** and CPU on the service is saturated. The team wants to **double query throughput**. What should they do, and what is the new SU count?

A. Add **partitions** to 2 × 4 = **8 SU**  
B. Add **replicas** to 4 × 2 = **8 SU**  
C. Switch to the Free tier  
D. Add replicas to 4 × 2 = **6 SU**

<details>
<summary>Answer</summary>

### ✅ B

Query throughput scales with **replicas**. $4 \times 2 = 8$ SU.

- **A ❌** Partitions add storage/indexing capacity, not QPS (and storage is only 40% used).
- **C ❌** No scale-up and no SLA.
- **D ❌** Arithmetic is wrong ($4\times 2 = 8$).
</details>

---

### Question 3: Storage pressure

An index holds product vectors plus text and is at **92% of partition storage**. Query latency is fine. Indexing jobs are getting slower. Which TWO actions are MOST appropriate?

A. **Add partitions** (more storage and indexing throughput)  
B. Consider reducing vector size (for example, **quantization**) to lower storage and memory pressure  
C. Add replicas only  
D. Move to the Free tier  
E. Delete the semantic configuration

<details>
<summary>Answer</summary>

### ✅ A and B

Partitions add **storage and indexing throughput**. Vector compression reduces index size (see Vector Search).

- **C ❌** Replicas copy the existing index, adding query capacity but not storage per partition.
- **D, E ❌** Irrelevant.
</details>

---

### Question 4: The SLA

A team runs an app that **both queries and updates** the index continuously (read-write) and wants the **service-level agreement**. They currently have an S1 service with **2 replicas**. What is the minimum change?

A. None. 2 replicas cover read-write  
B. Scale to **3 or more replicas** (SLA for read-write workloads)  
C. Add partitions  
D. Switch to Serverless Developer

<details>
<summary>Answer</summary>

### ✅ B

Two replicas meet the SLA for **read-only** workloads. **Read-write** workloads need **three or more**.

- **C ❌** Partitions don't affect availability SLA.
- **D ❌** Preview, no SLA.
</details>

---

### Question 5: Free tier traps (Select TWO)

A developer builds the production search for a small company on the **Free** tier "to save money". Which TWO statements describe real risks?

A. There is **no SLA** and the tier is limited to **one replica**  
B. A free service **might be deleted after extended inactivity**  
C. Free tier supports unlimited indexes and 10 GB storage  
D. Free tier can be scaled up with extra partitions  
E. Free tier is dedicated hardware

<details>
<summary>Answer</summary>

### ✅ A and B

Free is on **shared infrastructure**, with **scale-up unsupported**, **50 MB** of storage, a limit of **3 indexes/indexers/data sources**, and **one service per subscription**.

- **C, D, E ❌** All false.
</details>

---

### Question 6: Serverless limitation

A team started on **Serverless Developer** (preview). After launch, the workload becomes steady and high-volume, and they want to move to a **Standard** tier by changing the tier in the portal. What is the correct guidance?

A. Click "scale up" in the portal  
B. **Serverless doesn't support migration to or from other pricing tiers.** Create a new Dedicated service and re-index  
C. Convert replicas to CUs  
D. Open a support ticket to convert SUs to CUs

<details>
<summary>Answer</summary>

### ✅ B

Also, SUs and CUs aren't interchangeable, and preview tiers carry no SLA.
</details>

---

### Question 7: Keys versus roles (snippet)

```json
{
  "current_state": {
    "auth": "API key (default)",
    "usage": "Admin key shared by 12 developers, also embedded in the web app's server code"
  },
  "requirements": [
    "Per-identity access and audit",
    "Web app may only run queries",
    "Indexing pipeline may upload documents",
    "Platform admins manage indexes, indexers and skillsets"
  ]
}
```

Which design satisfies the requirements?

A. Keep the admin key and rotate it monthly  
B. **Enable role-based access**; assign **Search Index Data Reader** to the web app's identity, **Search Index Data Contributor** to the indexing pipeline's identity, **Search Service Contributor** to platform admins; then move off keys  
C. Give everyone Search Index Data Contributor  
D. Create a query key per developer

<details>
<summary>Answer</summary>

### ✅ B

RBAC provides per-identity control and audit, and least privilege.

- **A ❌** Rotation doesn't add granularity.
- **C ❌** Over-privileged. The web app only needs to query.
- **D ❌** Query keys are read-only but still shared secrets, with no identity or audit.
</details>

---

### Question 8: "Both" authentication mode

During migration, a service is set to **Both** (API key and role-based access). A request carries a valid **Entra ID token with only Search Index Data Reader** **and** an **admin API key**. What authorisation applies?

A. Reader permissions only  
B. **The API key is used** (when both are provided in the same request), so the request has admin rights  
C. The request is rejected  
D. The more restrictive of the two

<details>
<summary>Answer</summary>

### ✅ B

Once clients have migrated, switch to **role-based only** (and disable API keys) so a stray key can't bypass roles.
</details>

---

### Question 9: Roles don't match what the admin expects

A subscription **Owner** enables role-based access on a search service. Afterwards, she can still configure the service in the Azure portal but receives **authorisation failures when viewing index contents and running queries**. What is the BEST explanation and fix?

A. The service is corrupt  
B. **Control plane** permissions (Owner) don't automatically grant **data plane** access. Assign herself data plane roles such as **Search Service Contributor, Search Index Data Contributor, and/or Search Index Data Reader** as needed  
C. She must switch to the Free tier  
D. Owner can't be used with Search

<details>
<summary>Answer</summary>

### ✅ B

On a roles-only service, even administrators must be **assigned data plane roles**. Control plane roles are always on and separate.
</details>

---

### Question 10: Match the role (drag-and-drop)

Match each need to: **Search Service Contributor · Search Index Data Contributor · Search Index Data Reader · Owner/User Access Administrator**.

| Need | Role |
|---|---|
| A. A chat app that only runs queries | ? |
| B. A nightly job that uploads and deletes documents | ? |
| C. A developer who creates indexes, indexers and skillsets | ? |
| D. Assigning these roles to other identities | ? |

<details>
<summary>Answer</summary>

| Need | Role |
|---|---|
| A | **Search Index Data Reader** |
| B | **Search Index Data Contributor** |
| C | **Search Service Contributor** |
| D | **Owner / User Access Administrator** (or Role Based Access Control Administrator) |
</details>

---

### Question 11: Multi-tenant isolation (Select TWO)

A SaaS vendor serves 200 tenants. Requirements: a tenant's identity may only ever read **its own** content, and the design should enforce that **in the service**, not in prompts or UI code. Which TWO approaches are valid?

A. **One index per tenant**, with **role assignments scoped to that single index**  
B. **Document-level access control** in a shared index, so retrieval is trimmed to what each user may see  
C. A prompt instruction: "Only reveal the user's tenant data"  
D. Hide other tenants' data in the front-end  
E. Share one admin key and filter in client code

<details>
<summary>Answer</summary>

### ✅ A and B

Both enforce isolation at the service/retrieval layer. Per-index role scoping is explicitly supported. Document-level access control (row-level security) drives permission-aware retrieval.

- **C, D, E ❌** Not enforcement.
</details>

---

### Question 12: Put the pipeline in order (drag-and-drop)

Order the stages of an **AI enrichment** indexing run:

**a)** Index receives enriched documents  
**b)** Indexer connects to a data source and pulls content  
**c)** Skills run over the in-memory enriched document (for example, OCR, Text Split, embedding)  
**d)** Indexer cracks documents to extract text and images

<details>
<summary>Answer</summary>

### ✅ b → d → c → a

Import (b), crack (d), enrich (c), index (a). Optionally, enriched output is also **projected to a knowledge store**.
</details>

---

### Question 13: Missing enriched field (snippet)

```json
{
  "skillset": { "skills": [ { "@odata.type": "#Microsoft.Skills.Text.KeyPhraseExtractionSkill",
                              "context": "/document",
                              "inputs": [ { "name": "text", "source": "/document/content" } ],
                              "outputs": [ { "name": "keyPhrases", "targetName": "keyPhrases" } ] } ] },
  "indexer": { "fieldMappings": [ { "sourceFieldName": "metadata_storage_name", "targetFieldName": "fileName" } ],
               "outputFieldMappings": [] },
  "index": { "fields": [ "fileName", "content", "keyPhrases" ] },
  "observed": "The keyPhrases field in the index is empty for every document."
}
```

What is the MOST likely cause?

A. The embedding model is wrong  
B. **`outputFieldMappings` is empty.** The enriched node `/document/keyPhrases` is never mapped into the index field  
C. The index needs more replicas  
D. Key phrase extraction needs HNSW

<details>
<summary>Answer</summary>

### ✅ B

**Field mappings** move raw source fields. **Output field mappings** move **enriched nodes** from the in-memory tree into the index. Add a mapping such as source `/document/keyPhrases` → target `keyPhrases`.

**Trap:** The empty `outputFieldMappings` array is the clue.
</details>

---

### Question 14: Which skill / feature? (Select TWO)

A corpus of **scanned insurance forms (images in PDFs)** must be searchable and also yield **extracted entities for analysts** to query in Power BI. Which TWO choices fit BEST?

A. Add the **OCR skill** in a skillset so image text becomes searchable  
B. Configure a **knowledge store** to project enriched entities to Azure Storage for analytics  
C. Store the scans untouched. Search can read pixels directly  
D. Use HNSW to read the images  
E. Use the Free tier because skills are free

<details>
<summary>Answer</summary>

### ✅ A and B

OCR creates searchable text. A knowledge store persists enriched data (table, object and file projections) outside the index.

- **C ❌** Raw images aren't text. They need OCR/enrichment.
- **D ❌** HNSW is a vector algorithm.
- **E ❌** Built-in cognitive skills require a billable Foundry Tools resource.
</details>

---

### Question 15: "Source of truth" mistake

A developer plans to index 5 million documents from Blob Storage, then **delete the blobs** because "the search index already has everything". What is the MOST accurate concern?

A. None. Azure AI Search is a primary data store  
B. **Azure AI Search isn't designed as a primary data store.** Indexes are derived from external sources (you can't reconstruct original files, and vectors can't be converted back to text), and re-indexing after schema changes needs the source  
C. Blob Storage can't be indexed  
D. Deleting blobs deletes the service

<details>
<summary>Answer</summary>

### ✅ B

Keep the source content. You'll need it to rebuild or evolve the index, re-embed with a new model, or fix enrichment.
</details>

---

### Question 16: Push or pull?

A team already **chunks and embeds documents in their own pipeline** (custom code, with a proprietary parser), and wants real-time updates as documents change. Which ingestion model fits?

A. **Push model**: upload pre-processed chunk documents to the index through the API/SDK  
B. Pull model only, with no way to upload via code  
C. Serverless only  
D. Knowledge store

<details>
<summary>Answer</summary>

### ✅ A

Push gives full control and immediate updates. The pull model (indexer) is best for supported data sources, scheduled refresh, and built-in enrichment/integrated vectorization.
</details>

---

### Question 17: Foundry IQ plumbing

An enterprise has 10 agents that each built their own indexer pipeline over the same SharePoint and Blob content. They want **shared, permission-aware retrieval**. Which TWO statements are correct?

A. Create a **Foundry IQ knowledge base** over shared **knowledge sources**, and connect agents to it (through the **MCP tool**)  
B. The agent connection requires a **Foundry project** (hub-based projects aren't supported)  
C. Each agent needs its own copy of the content  
D. Knowledge bases work without any Azure AI Search service  
E. Knowledge bases have no separate billing consideration

<details>
<summary>Answer</summary>

### ✅ A and B

Foundry IQ is built **on** Azure AI Search. Knowledge bases require a **standard agentic retrieval plan**, so billing is a consideration (E is false).
</details>

---

### Question 18: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | Search units equal replicas multiplied by partitions. | |
| 2 | Adding replicas increases storage capacity per index. | |
| 3 | The SLA for read-write workloads requires three or more replicas. | |
| 4 | API key authentication is the recommended default. | |
| 5 | You can enrich vector data directly with skills. | |
| 6 | An indexer can run on a schedule to keep an index fresh. | |
| 7 | Serverless Developer is generally available with an SLA. | |
| 8 | Control plane roles can be disabled the same way as data plane roles. | |
| 9 | A knowledge store is a secondary output of a skillset. | |
| 10 | Role assignments can be scoped to a single index. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **Yes** | $\text{SU} = R \times P$. |
| 2 | **No** | Replicas add query throughput and HA. Partitions add storage. |
| 3 | **Yes** | 2+ for read-only, 3+ for read-write. |
| 4 | **No** | Keys are the default but **RBAC is recommended**. |
| 5 | **No** | Raw content must be text or images. Enrichment **output** can be vectorised. |
| 6 | **Yes** | Indexers can run on-demand or on a schedule. |
| 7 | **No** | Preview, no SLA, not for production. |
| 8 | **No** | Only data plane roles can be disabled. Control plane roles are built in. |
| 9 | **Yes** | Projects to Azure Storage. |
| 10 | **Yes** | Valuable for multi-tenancy. |
</details>

---

### Question 19: Match the symptom to the fix (drag-and-drop)

Match each symptom to: **Add replicas · Add partitions · Billable tier with 2+/3+ replicas · Enable RBAC and assign data plane roles · Output field mapping · OCR skill · Knowledge store · New Dedicated service + re-index · Push model**.

| Symptom | Fix |
|---|---|
| A. High QPS makes queries slow | ? |
| B. Index nearly out of storage | ? |
| C. Need the SLA | ? |
| D. Shared admin key, need per-identity audit | ? |
| E. Enriched field empty in the index | ? |
| F. Scanned PDFs not searchable | ? |
| G. Analysts want enriched entities in Power BI | ? |
| H. Moving from Serverless to a provisioned tier | ? |
| I. Custom parser plus real-time updates | ? |

<details>
<summary>Answer</summary>

| Symptom | Fix |
|---|---|
| A | **Add replicas** |
| B | **Add partitions** |
| C | **Billable tier with 2+ replicas (read-only) / 3+ (read-write)** |
| D | **Enable RBAC and assign data plane roles** |
| E | **Output field mapping** |
| F | **OCR skill** |
| G | **Knowledge store** |
| H | **New Dedicated service + re-index** |
| I | **Push model** |
</details>

---

## 2. Mini Case Study: Relecloud Media Archive

### Background

Relecloud Media is building search and an AI research assistant over a **10 million-file archive** of PDFs, scans and video transcripts stored in **Blob Storage**.

1. The **customer-facing search** runs 24/7 with heavy daytime query traffic. Indexing runs continuously for new content. Leadership requires the **SLA**.
2. A separate **internal pilot** used a few times a week by an AI team, which wants to pay almost nothing when idle.
3. Many files are **scanned images**. They need **OCR**, **chunking**, and **embeddings**, loaded with minimal custom code.
4. Data analysts want **extracted entities and key phrases** in **Power BI**.
5. Security: **no API keys** in app code. The web app only queries, the ingestion service writes, and platform admins manage objects. Each of 40 **partner tenants** may only see their own content.
6. A cost review notes **semantic ranker and agentic retrieval** are add-on charges.
7. A developer wants to **delete the Blob source files** after indexing "to save storage".
8. Ten internal agents each maintain their own pipeline over the same content.

### Case Q1: Customer-facing search service

A. Free tier  
B. **Dedicated** (Standard), sized with **3 or more replicas** because the workload is read-write and needs the SLA, and partitions sized for the index storage  
C. Serverless Developer  
D. One replica to save cost

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q2: Internal pilot

A. Dedicated S3 with 12 replicas  
B. **Serverless** (preview), accepting no SLA, and knowing it can't be migrated to a Dedicated tier  
C. Free tier forever  
D. Same service as production, with no isolation

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q3: Scans, chunking, embeddings, minimal code

A. Push model with custom code only  
B. **Indexer + skillset** (OCR, Text Split, embedding skill) with index projections, or a knowledge source that generates the pipeline  
C. Index raw images  
D. HNSW

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q4: Power BI entities

A. Query the index only  
B. **Knowledge store** projections to Azure Storage (tables/objects) for analytics  
C. Disable the skillset  
D. Export keys

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q5: Keyless access (requirement 5, first part)

Which TWO assignments?

A. **Search Index Data Reader** to the web app's identity  
B. **Search Index Data Contributor** to the ingestion service's identity  
C. Admin key in the web app  
D. Search Index Data Contributor to the web app

<details><summary>Answer</summary>

### ✅ A and B

Enable role-based access, then phase out keys.
</details>

### Case Q6: Partner tenant isolation (requirement 5, second part)

A. Prompt instructions  
B. **Per-tenant indexes with single-index role scoping**, or **document-level access control** in a shared index  
C. One admin key and client-side filters  
D. Rely on the UI

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q7: Cost review

A. Ignore add-ons  
B. Account for **add-on pricing** (semantic ranker, agentic retrieval, plus other enrichment features such as image extraction) and confirm the billing plan and consent settings  
C. Disable replicas  
D. Move to Free

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q8: Deleting the source

A. Approve it, because Azure AI Search is the system of record  
B. **Reject it.** Azure AI Search isn't a primary data store. Keep the source to re-index, re-embed or fix enrichment  
C. Approve it for scans only  
D. Replace Blob with an index

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q9: Ten agents, ten pipelines

A. Keep ten pipelines  
B. A shared **Foundry IQ knowledge base** over the knowledge sources, connected to agents through MCP, using a **Foundry project**  
C. Ten separate Free services  
D. Hub-based projects for all agents

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q10: Map the requirement

| Requirement | Solution |
|---|---|
| 24/7 search with SLA | ? |
| Idle-cost pilot | ? |
| Scans need to be searchable | ? |
| Entities in Power BI | ? |
| Query-only web app | ? |
| Per-partner isolation | ? |
| Add-on costs | ? |
| Source files | ? |
| Ten agents | ? |

<details><summary>Answer</summary>

| Requirement | Solution |
|---|---|
| 24/7 search with SLA | Dedicated tier, 3+ replicas (read-write) |
| Idle-cost pilot | Serverless (preview, no migration, no SLA) |
| Scans need to be searchable | OCR skill in a skillset |
| Entities in Power BI | Knowledge store |
| Query-only web app | Search Index Data Reader (Entra ID) |
| Per-partner isolation | Per-index role scoping or document-level access control |
| Add-on costs | Account for semantic ranker / agentic retrieval / image extraction pricing |
| Source files | Keep them. Search isn't a primary data store |
| Ten agents | Foundry IQ knowledge base (Foundry project, MCP) |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Replica trap** | "More replicas = more storage." | Replicas = query throughput and HA. **Partitions = storage/indexing.** |
| **SU trap** | "SU = replicas + partitions." | $\text{SU} = R \times P$. |
| **SLA trap** | "2 replicas meet the SLA for everything." | 2 for read-only, **3+ for read-write**. Free has none. |
| **Free-tier trap** | "Free is fine for a small production app." | No SLA, 50 MB, shared, no scale-up, can be deleted when inactive. |
| **Serverless trap** | "Serverless is just a cheaper tier I can switch from later." | Preview, no SLA, **no migration** to/from other tiers. |
| **Unit trap** | "SUs and CUs are the same." | Different units for different models. Don't mix calculators. |
| **Key trap** | "Keys are the recommended default." | RBAC recommended. Keys are coarse and unattributable. |
| **Both-mode trap** | "Entra token limits the request in Both mode." | If both are sent, the **API key** is used. |
| **Plane trap** | "Owner can read the data." | Control plane ≠ data plane. Assign data plane roles. |
| **Role trap** | "Search Service Contributor can query content." | It manages objects. Use Reader/Contributor for content. |
| **Tenant trap** | "Prompt the model not to reveal other tenants' data." | Enforce at the service: per-index roles or document-level access control. |
| **Mapping trap** | "Field mappings carry enriched data." | **Output field mappings** carry enriched nodes. |
| **Vector-skill trap** | "Skills can enrich vectors." | Raw input must be text or images. |
| **Store trap** | "Index = system of record." | Search isn't a primary data store. |
| **Schema trap** | "Change field attributes freely on a live index." | Existing field changes generally need a rebuild. Add scoring/semantic configs freely. |
| **Hub trap** | "Foundry IQ works with hub-based projects." | Foundry project required for the agent connection. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| Steady, predictable, SLA needed | **Dedicated** (Basic/Standard) |
| Bursty, infrequent, idle-to-zero, non-production | **Serverless** (preview) |
| Slow queries under load | **Add replicas** |
| Storage nearly full / slow indexing | **Add partitions** (or Storage Optimized) |
| Very large index, low QPS | Storage Optimized (L1/L2) |
| SLA, read-only | **2+ replicas** |
| SLA, read-write | **3+ replicas** |
| Free tier for production | Not allowed (no SLA) |
| Move from Serverless | New Dedicated service + re-index |
| Stop sharing keys | **Enable RBAC**, then disable keys |
| Query-only client | **Search Index Data Reader** |
| Upload/update/delete content | **Search Index Data Contributor** |
| Manage indexes/indexers/skillsets | **Search Service Contributor** |
| Admin can't read content on roles-only service | Assign data plane roles |
| Tenant isolation | Per-index role scoping or document-level access control |
| Crawl supported source on a schedule | **Indexer (pull)** |
| Custom parsing / real-time upload | **Push model** |
| Scanned images searchable | **OCR skill** |
| Enriched field empty in index | **Output field mapping** |
| Persist enriched data for analytics | **Knowledge store** |
| One source doc → many chunk docs | **Index projections** |
| Share retrieval across many agents | **Foundry IQ knowledge base** (Foundry project, MCP) |
| Plan costs beyond the tier | Add-ons: semantic ranker, agentic retrieval, image extraction, custom entity lookup |

---

## 5. Quick Revision Sheet

```text
AZURE AI SEARCH (Foundry IQ) = managed retrieval service: keyword + vector + hybrid + semantic + agentic
NOT a primary data store -> indexers pull from external sources (or you push)

PRICING MODELS
  Dedicated  = provisioned, hourly by SU, steady workloads, SLA possible
               tiers: Free | Basic | Standard S1-S3 (+S3 HD) | Storage Optimized L1-L2
  Serverless = consumption (CU + GB), scales to zero, PREVIEW, no SLA, no migration

CAPACITY:  SU = Replicas x Partitions
  Replicas   = query throughput + HA  (1-12)
  Partitions = storage + indexing throughput
  SLA: 2+ replicas read-only | 3+ replicas read-write | Free = none
  Free: 1 per sub, 50 MB, shared, no scale-up, may be deleted if inactive
  Basic: up to 3 replicas / 3 partitions | Standard: up to 36 SU

PIPELINE:  DATA SOURCE -> INDEXER -> [SKILLSET] -> INDEX   (+ optional KNOWLEDGE STORE)
  field mappings = raw fields | output field mappings = enriched nodes
  skills: OCR, entity recognition, key phrases, translation, Text Split, embeddings, custom
  raw input = text/images only (can't enrich vectors)
  pull = indexer | push = your code uploads documents

SECURITY
  Keys (default, coarse) -> prefer Entra ID RBAC | "Both": API key wins if both sent
  Control plane (always) vs data plane (roles enabled)
  Service Contributor = manage objects | Index Data Contributor = read/write | Index Data Reader = query
  Scope roles to a single index | Document-level access control = permission-aware retrieval
FOUNDRY IQ: knowledge sources + knowledge bases on Azure AI Search, MCP to agents, Foundry project, agentic retrieval plan
ADD-ONS: semantic ranker, agentic retrieval, custom entity lookup skill, image extraction
```

### Best-answer checklist

1. **Steady with SLA** (Dedicated) or **bursty, non-production** (Serverless)?
2. Slow **queries** = replicas. Full **storage/slow indexing** = partitions. Compute SU as R × P.
3. Does the SLA need **2+ or 3+ replicas** (read-only vs read-write)?
4. Any **keys** involved? Move to **RBAC** and choose the **least-privilege data plane role**.
5. Admin blocked on a roles-only service? **Control plane ≠ data plane.**
6. Enrichment missing? Check **skills, output field mappings, OCR**. Need analytics? **Knowledge store.**
7. Isolation needs? **Enforce in the service** (index-scoped roles or document-level access control).
8. Never treat the index as the **system of record**.

---

**Next concept:** RAG architecture (same harder exam-style format)

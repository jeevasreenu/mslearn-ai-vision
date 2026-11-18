# AI-103: Microsoft Foundry Fundamentals (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, code snippet, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Code snippets are simplified. The exam tests the *concept*, not exact SDK syntax.

---

## 0. Core Concepts (read first)

### 0.1 What is Microsoft Foundry?

Microsoft Foundry (formerly **Azure AI Foundry**, and before that Azure AI Studio) is Azure's **unified platform for building, deploying, evaluating and governing AI apps and agents**. It brings models, agents, tools, evaluation, observability and governance into one resource model, instead of stitching separate services together.

### 0.2 Resource hierarchy (most tested)

```text
Azure subscription
 └── Resource group
      └── Foundry resource      (Microsoft.CognitiveServices/accounts)
           │   = governance boundary: RBAC, networking, Azure Policy, billing
           ├── Project A        = development workspace (agents, tool connections, endpoint)
           ├── Project B
           └── Project C
```

| Level | Purpose | Set here |
|---|---|---|
| **Foundry resource** | Top-level governance and platform boundary | Networking (private endpoints/VNet), Azure Policy, resource-level RBAC, encryption |
| **Foundry project** | Development isolation for a team/app | Agents, tool connections, project endpoint, project-level access |
| **Connected Azure services** | Storage, search, secrets | Azure AI Search (Microsoft.Search), Storage, Key Vault |

**Key rule:** networking is configured at the **Foundry resource** level. Projects **inherit** it. If two workloads need different network isolation boundaries, use **separate Foundry resources**.

### 0.3 Two project types

| | **Foundry project** (new, hub-less) | **Hub-based project** (classic) |
|---|---|---|
| Parent | Foundry resource | AI Hub (built on Azure Machine Learning workspace) |
| Resources created | Fewer; simplified | Hub + storage + Key Vault + App Insights + container registry |
| Best for | Generative AI apps, **agents**, evaluation, most new work | Azure ML-dependent scenarios: **custom model training, Prompt Flow**, ML pipelines |
| Future features | New agent/model-centric features land here | Legacy path; some capabilities still need a hub |

> **Exam rule of thumb:** Agents / generative AI apps → **Foundry project**. Prompt Flow / custom training with Azure ML → **hub-based project**.

### 0.4 SDKs and endpoints

| Need | Use | Endpoint pattern |
|---|---|---|
| Agents, evaluations, Foundry-specific features | **Foundry SDK** (thin client over all project APIs) | `https://<resource>.services.ai.azure.com/api/projects/<project>` |
| Max OpenAI compatibility, lowest latency, **embeddings** | **OpenAI SDK** | `https://<resource>.openai.azure.com/openai/v1` |
| Anthropic Claude models deployed in Foundry | **Anthropic SDK** | `https://<resource>.services.ai.azure.com/anthropic` |
| Hosted agents / multi-agent orchestration in code | **Agent Framework** (C#/.NET, Python) | Responses API via project endpoint |
| LangGraph / LangChain apps | **LangChain Azure SDKs** | Project endpoint or `/openai/v1` |
| Prebuilt Vision, Speech, Language, Content Safety | **Foundry Tools SDKs** | Tool-specific endpoints |

Entra ID token scope for the Foundry REST API: `https://ai.azure.com/.default`.

### 0.5 Access control (RBAC)

| Role (current name) | Previously named | Use |
|---|---|---|
| **Foundry User** | Azure AI User | Build and use: agents, models, tools inside the resource/project |
| **Foundry Agent Consumer** | n/a | **Least privilege**: invoke agents only (e.g., call the Responses API), not create/modify |
| **Foundry Project Manager** | Azure AI Project Manager | Create projects; assign Foundry User |
| **Foundry Account Owner** | Azure AI Account Owner | Manage the resource; create projects; assign Foundry User |
| **Foundry Owner** | Azure AI Owner | Full ownership including data actions |
| **Cognitive Services Usages Reader** | n/a | At **subscription** scope, to view quota / deployment eligibility |

Important facts:
- RBAC applies only with **Microsoft Entra ID** authentication. A **key grants full access** without role restrictions.
- The portal **auto-assigns Foundry User** when the project creator can assign roles. **SDK/CLI/IaC does not.** Automation must assign roles explicitly.
- The **project's managed identity** also needs **Foundry User** on the Foundry resource.
- Old names (Azure AI User, etc.) may still appear in exam items or portal screens. Same role IDs and permissions.

### 0.6 Other facts worth knowing

- **Model inference runs on Microsoft-managed infrastructure**. Private endpoints give network-isolated *connectivity* but do **not** move the model runtime into your VNet.
- **Foundry Tools** = prebuilt AI services (Vision, Speech, Language, Content Safety...), formerly "Azure AI services".
- **Foundry IQ** = knowledge retrieval layer built on **Azure AI Search** (resource provider `Microsoft.Search`).
- The portal at **ai.azure.com** has a **New Foundry / Classic** toggle. Both run on the same platform but expose different project types and features.
- A **standalone Azure OpenAI resource** may be enough if you only need completions, with no agent hosting or evaluation. For first-time setup or agents/evaluation, the **Foundry resource** is the recommended starting point.

### 0.7 Five ideas the exam really tests

1. **Resource = governance, Project = isolation.**
2. **Networking lives on the resource**, so different network boundaries mean different resources.
3. **Hub-based only when Azure ML features are required.** Otherwise use Foundry projects.
4. **Entra ID + RBAC beats keys** for granular, auditable access.
5. **Pick the SDK/endpoint by scenario** (Foundry SDK for agents; OpenAI SDK for embeddings/max compatibility).

---

## 1. Scenario Questions

### Question 1: Team isolation

Contoso has three product teams building agents. Requirements:
- Each team must have its own agents and tool connections, isolated from the others.
- Security wants **one** private-networking configuration and **one** set of Azure Policy assignments for all teams.
- Admin overhead must be minimal.

Which design should you use?

A. One Foundry resource with one project per team  
B. Three separate Foundry resources, one per team  
C. One hub with three hub-based projects  
D. One Foundry resource with a single project shared by all teams, separated by naming conventions

<details>
<summary>Answer</summary>

### ✅ A

**Why correct:** Governance (networking, policy, RBAC) is set once on the Foundry resource and inherited. Projects provide development isolation (agents, connections, endpoint).

**Why others are wrong**
- **B ❌** Triplicates governance and admin work. Separate resources are justified only for *different* network/isolation boundaries.
- **C ❌** Hubs are the classic Azure ML-based model, used when Azure ML capabilities are needed. Not for this.
- **D ❌** Naming conventions are not isolation.

**Trap:** Don't create a resource per team by reflex. Projects are the isolation unit.
</details>

---

### Question 2: Different network boundaries

Two workloads will use Foundry:
- **Workload X** must be reachable only from a regulated VNet through private endpoints.
- **Workload Y** is a public prototype and must be accessible from the internet.

What should you do?

A. Create one Foundry resource with two projects and set private networking on Project X only  
B. Create two Foundry resources, each with its own networking configuration  
C. Create one Foundry resource and use RBAC to block internet users from Project X  
D. Create one hub and attach two projects with different compute

<details>
<summary>Answer</summary>

### ✅ B

**Why correct:** Networking is defined at the **Foundry resource** level, and projects inherit it. Different isolation boundaries require different resources.

**Why others are wrong**
- **A ❌** Network settings cannot be set per project.
- **C ❌** RBAC controls *who is authorized*, not *network reachability*.
- **D ❌** Hubs are not networking constructs. They provide ML platform capabilities.
</details>

---

### Question 3: Which project type?

A data-science team needs to:
- Use **Prompt Flow** to orchestrate LLM workflows.
- Run **custom model training** on Azure Machine Learning compute.

Another team only needs to build and evaluate **agents** with Foundry Agent Service.

Which project types should you recommend?

A. Hub-based project for both teams  
B. Foundry project for both teams  
C. Hub-based project for the data-science team; Foundry project for the agent team  
D. Foundry project for the data-science team; hub-based project for the agent team

<details>
<summary>Answer</summary>

### ✅ C

**Why correct:** Prompt Flow and Azure ML-based training are hub-based capabilities. Agents and new model-centric features are built for Foundry projects, and hub-based and Foundry projects can coexist.

**Why others are wrong**
- **A ❌** Forces the agent team onto the legacy model with fewer new features.
- **B ❌** Prompt Flow is supported in hub-based projects, and Azure ML-dependent scenarios need the hub.
- **D ❌** Reversed.
</details>

---

### Question 4: Standalone Azure OpenAI or Foundry resource?

An app team currently uses a standalone Azure OpenAI resource. They now want to add **hosted agents** and **evaluation workflows** while **keeping existing policies and RBAC**. What should they do?

A. Stay on Azure OpenAI and write their own agent hosting  
B. Move to a Foundry resource (migrating from the standalone Azure OpenAI resource), which adds agents and evaluation while retaining policies and RBAC  
C. Create a hub and re-deploy everything  
D. Buy a separate Azure AI Search resource and use it as the agent host

<details>
<summary>Answer</summary>

### ✅ B

The Foundry resource shares the `Microsoft.CognitiveServices` provider with Azure OpenAI and bundles model access, agent hosting and evaluation tooling.

- **A ❌** Reinvents the platform.
- **C ❌** A hub is unnecessary for agents.
- **D ❌** Azure AI Search is for retrieval, not agent hosting.

**Counter-case to remember:** If the workload only needs completions with no agents/evaluation, a standalone Azure OpenAI resource may be sufficient.
</details>

---

### Question 5: Pick the SDK and endpoint (drag-and-drop)

Match each scenario to the best **SDK / endpoint**.

| Scenario | Options |
|---|---|
| 1. Create and run an agent and run evaluations | OpenAI SDK `/openai/v1` · Foundry SDK project endpoint · Anthropic SDK · Foundry Tools SDK |
| 2. Generate embeddings with maximum OpenAI compatibility and lowest latency | (same options) |
| 3. Call a Claude model deployed in Foundry | (same options) |
| 4. Call a prebuilt Speech / Vision capability | (same options) |

<details>
<summary>Answer</summary>

| # | Answer |
|---|---|
| 1 | **Foundry SDK** (project endpoint `.../api/projects/<project>`) |
| 2 | **OpenAI SDK** (`https://<resource>.openai.azure.com/openai/v1`) |
| 3 | **Anthropic SDK** (`.../anthropic`) |
| 4 | **Foundry Tools SDK** (tool-specific endpoints) |
</details>

---

### Question 6: Code snippet, wrong endpoint

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint="https://contoso-foundry.openai.azure.com/openai/v1",
    credential=DefaultAzureCredential(),
)

# Create an agent and run an evaluation via the client
agent = client.agents.create(...)
```

The call fails because project-level agent APIs can't be found. What is the MOST likely cause?

A. `DefaultAzureCredential` cannot be used with Foundry  
B. The client was given the OpenAI-compatible endpoint instead of the **project endpoint** (`https://<resource>.services.ai.azure.com/api/projects/<project>`)  
C. Agents can only be created in the Azure portal  
D. The code needs an API key instead of Entra ID

<details>
<summary>Answer</summary>

### ✅ B

`AIProjectClient` (the Foundry SDK) targets the **project endpoint**. The `/openai/v1` endpoint is for the OpenAI SDK.

- **A ❌** Entra ID credentials are supported and recommended.
- **C ❌** Agents are created through the SDK/API too.
- **D ❌** Keys give full access and are not preferred. Entra ID also supports RBAC.

**Trap:** Scan the endpoint string. The endpoint host and path are often the whole question.
</details>

---

### Question 7: Least privilege (Select TWO)

A solution has:
- **Developers** who create and modify agents in the project.
- A **customer-facing web app** (service principal) that only needs to invoke existing agents through the Responses API.

Which TWO role assignments follow least privilege?

A. Assign **Foundry User** to the developers  
B. Assign **Foundry Owner** to the web app's service principal  
C. Assign **Foundry Agent Consumer** to the web app's service principal  
D. Assign **Foundry Account Owner** to the developers  
E. Assign **Cognitive Services Usages Reader** to the web app

<details>
<summary>Answer</summary>

### ✅ A and C

- **A ✅** Foundry User lets developers build and use agents and models.
- **C ✅** Foundry Agent Consumer is the least-privilege role for *invoking* agents only.
- **B ❌** Full ownership, way too much.
- **D ❌** Account Owner is for resource management and creating projects, more than developers need.
- **E ❌** That role is for viewing quota at subscription scope, unrelated.
</details>

---

### Question 8: Automated deployment, 403 errors

A DevOps pipeline uses Azure CLI/Bicep to create a Foundry resource and project. Developers who open the project later get **authorization errors** when creating agents. The same setup created through the Foundry portal works. What is the MOST likely cause?

A. Bicep cannot create Foundry projects  
B. The portal automatically assigns **Foundry User**, but CLI/SDK/IaC deployments do not, so the role assignments must be added explicitly (for users and the project's managed identity)  
C. Developers need a hub-based project  
D. The model deployment region is wrong

<details>
<summary>Answer</summary>

### ✅ B

Automatic role assignment happens through the portal UI (when the creator can assign roles). Automation must assign **Foundry User** on the Foundry resource to the users and to the **project managed identity**.

**Trap:** "Works in portal but fails in pipeline" often points to something the portal did *for you*.
</details>

---

### Question 9: Keys vs Entra ID

The security team requires that **each developer's access be restricted by role and auditable per identity**. Developers currently share the resource API key. What should you do?

A. Rotate the key monthly  
B. Move to Microsoft Entra ID authentication and assign Foundry RBAC roles to identities, instead of distributing keys  
C. Put the key in the prompt so the agent can authenticate  
D. Create one project per developer and share the key within the project

<details>
<summary>Answer</summary>

### ✅ B

RBAC roles apply only with Entra ID authentication. **A key grants full access with no role restriction**, and cannot be attributed to an individual.

- **A ❌** Rotation doesn't add granularity or per-user audit.
- **C ❌** Insecure and not how auth works.
- **D ❌** Still shared keys.
</details>

---

### Question 10: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | A Foundry resource can contain multiple projects that share governance settings. | |
| 2 | You can configure different private-networking settings for each project inside the same Foundry resource. | |
| 3 | Using a private endpoint moves the model runtime into your VNet. | |
| 4 | Foundry User and Foundry Agent Consumer grant the same permissions. | |
| 5 | The `https://ai.azure.com/.default` scope is used when requesting an Entra ID token for the Foundry REST API. | |
| 6 | Foundry projects require you to create an AI Hub first. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **Yes** | Resource = governance; projects inside inherit. |
| 2 | **No** | Networking is set at the resource level; projects inherit. |
| 3 | **No** | Private endpoints provide private *connectivity*. Inference stays on Microsoft-managed infrastructure. |
| 4 | **No** | Agent Consumer can only invoke agents; Foundry User can build and use more. |
| 5 | **Yes** | That is the documented token scope. |
| 6 | **No** | Foundry projects are hub-less; they sit directly under a Foundry resource. |
</details>

---

### Question 11: Tutorial doesn't match the screen (Select TWO)

A developer follows a Microsoft Learn tutorial. The screens and menu items differ from what they see in the portal at ai.azure.com. Which TWO explanations are most plausible?

A. The portal is on the **New Foundry** experience while the tutorial was written for **Foundry (Classic)** (or vice versa)  
B. The tutorial targets a **hub-based project** but the developer created a **Foundry project** (or vice versa)  
C. The model catalog is empty for the subscription  
D. The tutorial requires a different Azure region for the portal  
E. Foundry can only be used from Visual Studio

<details>
<summary>Answer</summary>

### ✅ A and B

Both portals run on the same platform, with different UX layers and different project types. Many older tutorials/Learn modules assume the classic hub-based setup.

- **C, D, E ❌** Not realistic explanations of mismatched UI.
</details>

---

### Question 12: Match the term (drag-and-drop)

Match each description to **Foundry resource, Foundry project, Hub, Foundry Tools, Foundry IQ**.

| Description | Term |
|---|---|
| Top-level boundary for networking, policy, RBAC and billing | ? |
| Team workspace that holds agents, tool connections and a project endpoint | ? |
| Azure ML-based construct that provisions storage, Key Vault, etc., and supports Prompt Flow | ? |
| Prebuilt Vision, Speech, Language and Content Safety capabilities | ? |
| Knowledge retrieval layer built on Azure AI Search | ? |

<details>
<summary>Answer</summary>

| Description | Term |
|---|---|
| Top-level boundary... | **Foundry resource** |
| Team workspace... | **Foundry project** |
| Azure ML-based construct... | **Hub** (hub-based projects) |
| Prebuilt Vision, Speech... | **Foundry Tools** |
| Knowledge retrieval layer on Azure AI Search | **Foundry IQ** |
</details>

---

### Question 13: Setup minimums

A new admin creates a Foundry resource and project via automation. Which assignments are the **minimum** to let a developer use Foundry features, and let the project work correctly?

A. Foundry User for the developer on the Foundry resource only  
B. Foundry User for the developer **and** Foundry User for the **project's managed identity**, both on the Foundry resource  
C. Owner at subscription scope for the developer  
D. Foundry Agent Consumer for the project's managed identity only

<details>
<summary>Answer</summary>

### ✅ B

Both the user principal and the project managed identity need **Foundry User** on the Foundry resource. If users must see quota or run deployment eligibility checks, also add **Cognitive Services Usages Reader** at subscription scope.

- **A ❌** Misses the managed identity.
- **C ❌** Over-privileged.
- **D ❌** Consumer can only invoke agents.
</details>

---

## 2. Mini Case Study: Fabrikam Health

### Background

Fabrikam Health is adopting Microsoft Foundry.

1. Three teams (**Claims**, **Support**, **Research**) each build their own agents and must be isolated from each other.
2. Compliance requires **private networking**, **Azure Policy** enforcement, and **no shared API keys**.
3. The **Research** team uses **Prompt Flow** and trains custom models on Azure ML compute.
4. Infrastructure is created through a **CI/CD pipeline** (CLI/Bicep).
5. A public **patient-portal web app** must only **invoke** the Support team's existing agents.
6. Developers want to use the **OpenAI SDK** for embeddings and the **Foundry SDK** for agents.

### Case Q1

How should the Claims and Support teams be organised?

A. Separate subscriptions, each with its own hub  
B. One Foundry resource (with networking/policy applied once) and a separate **Foundry project** for each team  
C. A single project for all teams  
D. One standalone Azure OpenAI resource per team

<details>
<summary>Answer</summary>

### ✅ B

Governance once at the resource, isolation by project. (Same as Question 1.)
</details>

### Case Q2

Where should the Research team's Prompt Flow and Azure ML training work happen?

A. In a Foundry project, because all new work goes there  
B. In a **hub-based project**, which coexists with Foundry projects  
C. In a standalone Azure AI Search resource  
D. In the patient-portal web app

<details>
<summary>Answer</summary>

### ✅ B

Prompt Flow and Azure ML-dependent training are hub-based capabilities.
</details>

### Case Q3

Which authentication and access design meets "no shared API keys" and the web app requirement?

A. Share the resource key with the web app  
B. Use Entra ID for all access. Give developers **Foundry User**, and give the web app's identity **Foundry Agent Consumer**  
C. Give the web app **Foundry Owner** so it never gets blocked  
D. Use keys but store them in the prompt

<details>
<summary>Answer</summary>

### ✅ B

Entra ID enables RBAC and per-identity audit. Agent Consumer is least privilege for invoking agents.
</details>

### Case Q4

The pipeline-created projects work for the pipeline identity but developers get authorization errors. What is the fix?

A. Recreate the projects in the portal for every team  
B. Add explicit **Foundry User** role assignments on the Foundry resource for the developers and the **project managed identities** in the pipeline  
C. Disable RBAC  
D. Switch all projects to hub-based

<details>
<summary>Answer</summary>

### ✅ B

Only the portal auto-assigns Foundry User. CLI/Bicep/SDK deployments must assign roles explicitly.
</details>

### Case Q5

Match the developer tasks to the SDK.

| Task | SDK |
|---|---|
| Create and run agents, run evaluations | ? |
| Generate embeddings | ? |

<details>
<summary>Answer</summary>

| Task | SDK |
|---|---|
| Create and run agents, run evaluations | **Foundry SDK** (project endpoint) |
| Generate embeddings | **OpenAI SDK** (`/openai/v1` endpoint) |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Resource-per-team trap** | "Each team needs its own resource." | One resource, project per team. Separate resources only for different network/isolation boundaries. |
| **Network-per-project trap** | "Set private networking on the project." | Networking is on the **resource**, and projects inherit. |
| **Hub trap** | "Hub = networking hub." | Hub = Azure ML-based platform (training, Prompt Flow). Network centralization is a landing-zone concern. |
| **Private endpoint trap** | "Private endpoint puts the model in my VNet." | Connectivity is private; inference stays on Microsoft-managed infrastructure. |
| **Key trap** | "RBAC restricts key holders." | A key grants full access with no role restriction. RBAC works with Entra ID. |
| **Portal-vs-pipeline trap** | "Roles are always assigned automatically." | Only the portal auto-assigns Foundry User. Automation must assign roles. |
| **Managed identity trap** | "Only users need roles." | The **project managed identity** also needs Foundry User on the resource. |
| **Least privilege trap** | "Give Owner so nothing breaks." | App that only invokes agents = Foundry Agent Consumer. |
| **Endpoint trap** | "Any endpoint works with any SDK." | Foundry SDK → project endpoint. OpenAI SDK → `/openai/v1`. |
| **Naming trap** | "Azure AI User is a different role from Foundry User." | Same role, renamed. Old names may still appear. |
| **Azure OpenAI trap** | "Always need a Foundry resource." | Completions-only workloads can stay on standalone Azure OpenAI. Agents/evaluation point to Foundry. |
| **Classic-vs-new trap** | "Docs don't match, so the product is broken." | Different portal experience/project type (classic hub-based vs new Foundry project). |

---

## 4. Decision Table

| Symptom / requirement in the question | Answer |
|---|---|
| Many teams, shared governance, isolated work | One Foundry resource + one project per team |
| Different network isolation per workload | Separate Foundry resources |
| Prompt Flow or custom training with Azure ML | Hub-based project |
| Build agents / evaluation / new features | Foundry project |
| Per-user, role-based, auditable access | Entra ID + Foundry RBAC (not keys) |
| App only calls agents | Foundry Agent Consumer |
| Developers build agents | Foundry User |
| Create projects + assign Foundry User | Foundry Project Manager / Account Owner |
| Authorization fails after CLI/Bicep deployment | Assign Foundry User explicitly (users + project managed identity) |
| Embeddings, max OpenAI compatibility | OpenAI SDK `/openai/v1` |
| Agents/evaluations in code | Foundry SDK project endpoint |
| Prebuilt Speech/Vision/Language/Content Safety | Foundry Tools |
| Retrieval over your data | Foundry IQ / Azure AI Search |
| Quota visibility | Cognitive Services Usages Reader (subscription scope) |

---

## 5. Quick Revision Sheet

```text
FOUNDRY RESOURCE  = governance boundary (networking, policy, RBAC, billing)
FOUNDRY PROJECT   = dev isolation (agents, connections, endpoint)
HUB-BASED PROJECT = Azure ML-based (Prompt Flow, custom training)
FOUNDRY TOOLS     = prebuilt Vision/Speech/Language/Content Safety
FOUNDRY IQ        = retrieval on Azure AI Search

Networking: RESOURCE level; projects inherit
Auth:       Entra ID + RBAC (keys = full access)
Roles:      Foundry User | Agent Consumer | Project Manager | Account Owner | Owner
Portal auto-assigns Foundry User; CLI/SDK/IaC does NOT
Project managed identity also needs Foundry User

Foundry SDK  -> https://<resource>.services.ai.azure.com/api/projects/<project>
OpenAI SDK   -> https://<resource>.openai.azure.com/openai/v1
Token scope  -> https://ai.azure.com/.default
```

### Best-answer checklist

1. Is this a **governance** (resource) or **isolation** (project) question?
2. Does the stem hint at **Azure ML features** (Prompt Flow, training)? If so, think hub-based.
3. Does it mention **keys, shared access, or audit**? Move to Entra ID + RBAC.
4. Is the identity only *invoking* agents? Choose **Agent Consumer**.
5. Does the code contain an **endpoint**? Check it matches the SDK.
6. Did it work in the **portal** but fail in **automation**? Think missing role assignments.

---

**Next concept:** Model selection (LLM / SLM / multimodal)

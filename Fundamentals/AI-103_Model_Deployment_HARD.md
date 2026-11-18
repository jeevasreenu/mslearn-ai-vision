# AI-103: Model Deployment (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, code/config snippet, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Quota numbers, SKU availability and model names change often. The exam tests the **decision logic**, not memorised numbers.

---

## 0. Core Concepts (read first)

### 0.1 What does "deploying a model" mean?

To make a model available for inference requests, you **deploy** it. A deployment gives you a callable **endpoint + deployment name**, with its own **capacity/rate limits**, **content filter**, and **deployment type**.

> You don't always need a deployment. **Instant access (preview)** lets you call supported models by name with no deployment, useful for trying a model quickly.

### 0.2 Three deployment options (the HOSTING axis)

| Option | For | Billing | Notes |
|---|---|---|---|
| **Serverless API** (preferred, most capable) | **Foundry Models sold by Azure** (including all Azure OpenAI models) and select partner/community models (e.g., Anthropic, Mistral, Cohere, Meta) | Per token, or reserved (PTU) | Microsoft hosts the infrastructure. Supports Standard, Provisioned, Batch, Developer deployment types |
| **Managed compute** (preview) | **Open-source, partner and custom models** on **dedicated GPU capacity** managed by Foundry | **Hourly per GPU/accelerator** (e.g., A100/H100/H200 families) | Use for your own/custom weights or open models not offered serverless. Does **not** use the Standard/Provisioned/Batch types |
| **Foundry Local on Azure Local** (preview) | Eligible models on **your own** Azure Arc-enabled Kubernetes clusters on Azure Local | Your infrastructure | On-premises / connected-edge scenarios |

> **Exam rule:** Standard / Global / Data Zone / Provisioned / Batch types apply to **Serverless API** only. **Managed compute doesn't use them.**

### 0.3 The deployment-type matrix (the TWO axes: WHERE processed × HOW you pay)

| Where data is **processed** → | Pay-per-token (Standard) | Reserved capacity (Provisioned / PTU) | Async discounted (Batch) |
|---|---|---|---|
| **Global** (any Azure region) | **Global Standard** | **Global Provisioned** | **Global Batch** |
| **Data Zone** (US / EU / APAC zone, as published) | **Data Zone Standard** | **Data Zone Provisioned** | **Data Zone Batch** |
| **Regional / geography** | **Standard** | **Regional Provisioned** | n/a |
| Any region, fine-tuned model evaluation | **Developer** (pay-per-token, no SLA, short-lived) | | |

Nesting of residency: **Global ⊃ Data Zone ⊃ Regional**. Regional is the strictest.

| Type | Choose when |
|---|---|
| **Global Standard** | **Default starting point.** Lowest price, broadest region coverage, launches first for new models. No residency requirement |
| **Data Zone Standard** | Prompts/responses must be processed **within a zone** (e.g., EU) but traffic is variable |
| **Standard (regional)** | Strictest residency: processed in the **chosen geography** |
| **Global / Data Zone / Regional Provisioned** | **Predictable, sustained high volume**, need consistent low-variance latency, throughput guarantees (billed in **PTUs**, reservations possible) |
| **Global / Data Zone Batch** | **Large asynchronous jobs** with no real-time need. About **50% cheaper**, target turnaround ~24 hours |
| **Developer** | **Temporary evaluation of fine-tuned models**. No SLA, no residency guarantee, **not for production** |

### 0.4 Data residency: the most-misunderstood fact

- **Data at rest** stays in the designated Azure geography for **all** deployment types.
- Only **inference (processing)** location differs:
  - **Global:** may be processed in any Azure region.
  - **Data Zone:** processed only inside the specified zone.
  - **Standard / Regional Provisioned:** processed within the customer-specified geography (may move between regions *within* that geography for operational purposes).

### 0.5 Quota, rate limits and 429s (Standard types)

| Concept | Fact |
|---|---|
| **Quota scope** | Per **subscription**, per **region**, per **model**, per **deployment type**, in **TPM** (tokens per minute). Not enforced at tenant level |
| **Assigning** | When you create a deployment, you assign it part of the quota. That assigned **TPM becomes the deployment's rate limit** |
| **RPM** | Derived **proportionally** from TPM (ratio varies by model). Not set independently |
| **429 Too Many Requests** | Deployment exceeded **TPM or RPM**, or the service is short on capacity. Read the message and `x-ratelimit-*` headers to tell which |
| **Why 429 below quota?** | (1) Quota exists at the subscription level but isn't **assigned to the deployment** receiving traffic. (2) TPM check uses an **estimate** that includes the prompt **plus the full `max_tokens` setting**. (3) RPM is checked over **short windows** (1 or 10 s). (4) Rejected requests can still count. (5) Under heavy demand the service can temporarily lower the effective limit |
| **Fix 429 (standard)** | Honour `retry-after`, exponential backoff with jitter; **lower `max_tokens`**; rebalance TPM across deployments; request quota increase (only helps when quota is the cause); spread load across deployments/regions; use Global/Data Zone types; add **Provisioned** for predictable load |
| **View quota** | Role **Cognitive Services Usages Reader** at **subscription** scope (a resource-group/resource assignment is not enough) |
| **Provisioned (PTU) 429** | Occurs at **100% utilisation** of the PTU deployment. Add **spillover** to a Standard deployment, or buy more PTUs |

> Quota ≠ capacity. Having approved quota doesn't guarantee capacity in a region at that instant.

### 0.6 Provisioned throughput (PTU) basics

- **PTU** = reserved model-processing capacity → **stable, low-variance latency and predictable throughput**.
- Billed hourly per PTU, with **monthly/annual reservations** for discounts.
- Best for **steady, high-volume production** where latency consistency matters. **Poor fit** for spiky, low-volume or experimental workloads (you pay for idle reserved capacity).
- **Spillover:** overflow requests from a PTU deployment go to a **Standard** deployment instead of failing with 429.

### 0.7 Other deployment-time settings and facts

| Setting | What it does |
|---|---|
| **Deployment name** | The identifier your code calls (can differ from the model name) |
| **Model version / upgrade policy** | Pin a version for stability, or allow auto-update. Models have a **lifecycle**: deprecation → retirement. Plan migration before retirement |
| **TPM/capacity** | Rate limit assigned to *this* deployment |
| **Content filter (guardrails)** | Applied **per deployment**. Choose or customise the policy at deployment time |
| **Azure Policy** | Can **restrict which deployment types** may be created (e.g., block Global types for residency compliance) |
| **Networking / identity** | Inherited from the Foundry resource. Use **Entra ID + RBAC** to call deployments |
| **Region availability** | New model → **Global** first, then **Data Zone**, then **regional**. Regional may arrive last or never |
| **Model router** | One deployment that routes across many models (one name, one rate limit, one content filter) |

### 0.8 Five ideas the exam really tests

1. **Two questions pick the type:** *Where may data be processed?* and *How do I want to pay / what throughput do I need?*
2. **Start with Global Standard** unless there's a specific reason (residency, reserved throughput, async batch).
3. **Data at rest stays in geography for every type.** Only inference location differs.
4. **Quota is per subscription/region/model/type; TPM assigned to the deployment is its rate limit.** 429 ≠ always "get more quota".
5. **Managed compute is for open/custom models on GPUs; the Standard/Provisioned/Batch types are Serverless API only.**

---

## 1. Scenario Questions

### Question 1: Default choice

A startup is building a new chat feature using a model sold by Azure. There are **no data-residency requirements**, traffic is unpredictable, they want the **lowest price** and access to **new models as soon as they launch**. Which deployment type should they start with?

A. Regional Provisioned  
B. Global Standard  
C. Data Zone Provisioned  
D. Global Batch

<details>
<summary>Answer</summary>

### ✅ B

Global Standard: lowest price, broadest region coverage, first to get new models, and pay-per-token suits variable traffic.

- **A ❌** Reserved capacity plus strictest residency: costly and unnecessary.
- **C ❌** Reserved capacity plus zone restriction. Not needed.
- **D ❌** Batch is asynchronous, so unsuitable for a live chat feature.

**Trap:** "Cheapest" ≠ "right for interactive". Batch is cheap but not real-time.
</details>

---

### Question 2: EU residency, variable traffic

A bank in Germany must ensure **prompts and responses are processed only within the EU**. Traffic is variable and low-to-moderate. They don't want to pre-purchase capacity. Which type fits BEST?

A. Global Standard  
B. Data Zone Standard (EU)  
C. Global Provisioned  
D. Developer

<details>
<summary>Answer</summary>

### ✅ B

Data Zone Standard keeps inference within the specified zone and bills pay-per-token.

- **A ❌** May process in any region globally.
- **C ❌** Global processing plus reserved capacity.
- **D ❌** No SLA, no residency guarantee, evaluation only.
</details>

---

### Question 3: Latency consistency at scale

A call-center assistant handles **steady, high-volume** traffic all day. Users are sensitive to **latency variance**, and the business wants **guaranteed throughput**. There are no zone restrictions. Which option fits BEST?

A. Global Standard with default quota  
B. Global Provisioned (PTU)  
C. Global Batch  
D. Developer

<details>
<summary>Answer</summary>

### ✅ B

Provisioned throughput gives reserved capacity with stable latency and predictable throughput, best for sustained, high-volume, latency-sensitive production.

- **A ❌** Shared pay-per-token capacity has more variability.
- **C ❌** Async, up to ~24 hours.
- **D ❌** Not for production.
</details>

---

### Question 4: Overnight document processing

A company must summarise **8 million archived documents** over the next few days. There is **no real-time requirement**, and cost reduction is the main goal. Which option is MOST appropriate?

A. Global Provisioned with maximum PTUs  
B. Global Standard run in a tight loop  
C. **Global Batch**  
D. Managed compute with a custom model

<details>
<summary>Answer</summary>

### ✅ C

Batch is for large asynchronous jobs: about 50% cheaper with a ~24-hour target turnaround.

- **A ❌** Expensive reserved capacity for a one-off job.
- **B ❌** Costs more than Batch and risks hitting rate limits.
- **D ❌** Unnecessary hosting change.

If the data must stay in the EU, use **Data Zone Batch**.
</details>

---

### Question 5: 429 below quota

A deployment has `100,000 TPM` assigned. Dashboards show token usage well below that, yet clients get intermittent 429 errors. The code sets `max_tokens=4000` on every call, while answers average 200 tokens. Which TWO actions are MOST likely to help?

A. Lower `max_tokens` to a value that matches typical answer length  
B. Honour `retry-after` headers and use exponential backoff with jitter  
C. Switch the model to a different embedding model  
D. Disable the content filter to free up tokens  
E. Change the deployment name

<details>
<summary>Answer</summary>

### ✅ A and B

- **A ✅** The TPM check uses an **estimate** that counts the full `max_tokens`, so a 4,000 setting reserves 4,000 tokens of the limit even for a 200-token answer.
- **B ✅** Correct retry behaviour handles burst/RPM-window throttling.
- **C ❌** Unrelated.
- **D ❌** Content filters don't consume TPM quota.
- **E ❌** Naming has no effect on rate limits.

**Trap:** "Request more quota" is not always the answer. Read the evidence in the stem.
</details>

---

### Question 6: Quota exists but deployment is throttled

The subscription has **500,000 TPM of approved quota** for a model in East US. A production deployment was created with **50,000 TPM** and receives heavy traffic. It returns 429s. Other deployments of the same model are idle. What is the MOST appropriate first action?

A. Create a new subscription  
B. **Increase the TPM assigned to the busy deployment** (reallocate unused quota)  
C. Switch to a different embedding model  
D. Move the model to managed compute

<details>
<summary>Answer</summary>

### ✅ B

A deployment's rate limit equals the TPM **assigned** to it. Quota only becomes usable when assigned. Reassign unused TPM to the busy deployment.

- **A ❌** Unnecessary.
- **C ❌** Irrelevant.
- **D ❌** Managed compute is for open/custom models and has no bearing here.
</details>

---

### Question 7: Viewing quota (permissions)

An engineer must **view quota usage and available capacity** across the subscription but must not manage deployments or read other data. Which role assignment follows least privilege?

A. Owner at the subscription  
B. **Cognitive Services Usages Reader at the subscription scope**  
C. Foundry Agent Consumer at the project  
D. Cognitive Services Usages Reader at the resource-group scope

<details>
<summary>Answer</summary>

### ✅ B

The Usages API is subscription-scoped. A resource-group or resource-level assignment doesn't authorise it.

- **A ❌** Over-privileged.
- **C ❌** Wrong role.
- **D ❌** Wrong scope.
</details>

---

### Question 8: Open-source model on GPUs

A research team wants to deploy a **fine-tuned open-source model** (weights they trained elsewhere) and serve it with **dedicated GPU capacity** that Foundry manages. Which deployment option fits?

A. Serverless API with Global Standard  
B. **Managed compute** (dedicated GPUs, hourly billing)  
C. Global Batch  
D. Instant access

<details>
<summary>Answer</summary>

### ✅ B

Managed compute serves open-source, partner and custom models on dedicated GPUs. Billing is hourly per accelerator.

- **A ❌** Serverless is for Foundry Models sold by Azure and select partner models.
- **C ❌** Batch is a Serverless type.
- **D ❌** Instant access is for trying supported models by name.

**Trap:** Deployment types (Standard/Provisioned/Batch) don't apply to managed compute.
</details>

---

### Question 9: PTU spillover

A PTU deployment handles steady traffic but occasionally exceeds 100% utilisation during peak hours, causing 429s. The business doesn't want to buy more PTUs for rare spikes. What should they configure?

A. Reduce the model's temperature  
B. Add **spillover** to a Standard deployment so overflow is served pay-per-token  
C. Delete the PTU deployment  
D. Switch to Developer type

<details>
<summary>Answer</summary>

### ✅ B

Spillover routes overflow to a Standard deployment instead of failing. It combines predictable baseline capacity with elastic burst handling.

- **A ❌** Temperature has no effect on capacity.
- **C ❌** Loses the reserved baseline.
- **D ❌** Not for production.
</details>

---

### Question 10: Config snippet, spot the problem

```json
{
  "deployment": {
    "name": "gpt-prod",
    "type": "GlobalStandard",
    "tpm": 30000
  },
  "requirement": "Regulator requires that inference for EU patients is processed only inside the EU.",
  "observed": "Audit shows requests were processed in non-EU regions."
}
```

What is the BEST correction?

A. Increase TPM to 300,000  
B. Redeploy using a **Data Zone (EU)** type (or a regional type if a single geography is required)  
C. Rename the deployment to `gpt-prod-eu`  
D. Move the Foundry project to a different resource group

<details>
<summary>Answer</summary>

### ✅ B

Global types may process inference anywhere. For EU-only processing use **Data Zone Standard (EU)**, or a regional type for stricter geography control.

- **A ❌** Capacity doesn't change location.
- **C ❌** Names don't affect routing.
- **D ❌** Resource groups don't change inference location.

**Trap:** Read the `type` field. `GlobalStandard` is the clue.
</details>

---

### Question 11: Governance guardrail

A compliance team wants to **prevent developers from creating Global deployment types** in any project, to guarantee that EU data never leaves the zone. What should they use?

A. A prompt instruction telling developers not to  
B. **Azure Policy** to restrict allowed deployment types  
C. Lower the TPM quota  
D. Content filters

<details>
<summary>Answer</summary>

### ✅ B

Azure Policy can restrict which deployment types are allowed. It is deterministic enforcement, not guidance.

- **A ❌** Not enforcement.
- **C ❌** Doesn't control type.
- **D ❌** Content filters govern harmful content, not deployment configuration.
</details>

---

### Question 12: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | With a Global Standard deployment, data **at rest** may be stored in any Azure region worldwide. | |
| 2 | Data Zone deployments process inference only within the specified data zone. | |
| 3 | Developer deployments are suitable for production workloads that need an SLA. | |
| 4 | Provisioned deployments are billed through reserved capacity (PTUs) rather than per token. | |
| 5 | Quota is enforced at the Azure tenant level. | |
| 6 | The Standard/Provisioned/Batch deployment types apply to managed compute deployments. | |
| 7 | You can attach a content filter policy to a model deployment. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **No** | Data at rest stays in the designated Azure geography for all types. Only inference location differs. |
| 2 | **Yes** | That's the definition of Data Zone. |
| 3 | **No** | Developer: no SLA, short-lived, evaluation of fine-tuned models only. |
| 4 | **Yes** | PTU reserved capacity. |
| 5 | **No** | Quota is per subscription, region, model and deployment type. |
| 6 | **No** | Those types apply to Serverless API only. |
| 7 | **Yes** | Content filtering is configured per deployment. |
</details>

---

### Question 13: Match requirement to type (drag-and-drop)

Match each scenario to the best option: **Global Standard · Data Zone Standard · Global Provisioned · Global Batch · Managed compute · Developer**.

| Scenario | Option |
|---|---|
| A. New prototype, no residency rules, cheapest per-token pricing | ? |
| B. Evaluate a newly fine-tuned model for a day | ? |
| C. Zone-restricted traffic that is variable, with no reserved capacity wanted | ? |
| D. Always-on, high-volume, latency-sensitive production with no zone limits | ? |
| E. Run a custom open-source model on dedicated GPUs | ? |
| F. Monthly reprocessing of a huge archive with no urgency | ? |

<details>
<summary>Answer</summary>

| Scenario | Option |
|---|---|
| A | **Global Standard** |
| B | **Developer** |
| C | **Data Zone Standard** |
| D | **Global Provisioned** |
| E | **Managed compute** |
| F | **Global Batch** |
</details>

---

### Question 14: Model lifecycle (Select TWO)

A production app calls a deployment pinned to a model version that Microsoft has announced will **retire** in 90 days. Which TWO actions are MOST appropriate?

A. Test the application against the **replacement model/version** and plan migration before retirement  
B. Ignore the notice because deployments never stop working  
C. Use configuration-driven deployment/model names so you can switch without a code change  
D. Delete the deployment immediately  
E. Increase `max_tokens`

<details>
<summary>Answer</summary>

### ✅ A and C

- **A ✅** Validate (evaluate) on the successor before the retirement date.
- **C ✅** Config-driven names simplify swaps.
- **B ❌** Retired models stop being served.
- **D ❌** Causes an outage.
- **E ❌** Irrelevant.
</details>

---

## 2. Mini Case Study: Contoso Global Bank

### Background

Contoso Global Bank is deploying models in Microsoft Foundry.

1. **Customer chat assistant (EU customers):** processing must remain **in the EU**; traffic is **variable**.
2. **Fraud-scoring API:** **steady, high-volume, 24/7**, needs **consistent low latency**, no residency limits.
3. **Nightly statement summarisation:** **millions of documents**, results needed by morning, cost-sensitive.
4. **Research team:** deploys a **custom fine-tuned open-source model** on **dedicated GPUs**.
5. **Fine-tuned model testing:** needs a short-lived, low-cost endpoint for a day of evaluation.
6. **Governance:** security wants to **block Global deployment types** for EU workloads and let a platform engineer **view subscription quota** without extra access.
7. **Operations:** the fraud API sometimes hits 100% PTU utilisation during peaks, causing 429s.

### Case Q1: Chat assistant (EU)

A. Global Standard  
B. **Data Zone Standard (EU)**  
C. Global Batch  
D. Developer

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q2: Fraud-scoring API

A. Global Batch  
B. Developer  
C. **Global Provisioned** (PTU, reservations for steady load)  
D. Global Standard with minimal quota

<details><summary>Answer</summary>

### ✅ C

Steady, high-volume, latency-consistent = Provisioned.
</details>

### Case Q3: Nightly summarisation

A. **Global Batch** (or **Data Zone Batch** if the data must stay in a zone)  
B. Provisioned with maximum PTUs  
C. Developer  
D. Managed compute

<details><summary>Answer</summary>

### ✅ A

Async with a ~24-hour target and about 50% lower cost. Note the "results by morning" requirement. Batch targets 24 hours, so start the job early enough.
</details>

### Case Q4: Custom open-source model

A. Serverless Global Standard  
B. **Managed compute**  
C. Data Zone Batch  
D. Provisioned

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q5: Fine-tuned model evaluation

A. Global Provisioned  
B. **Developer** deployment type  
C. Data Zone Provisioned  
D. Regional Provisioned

<details><summary>Answer</summary>

### ✅ B

Short-lived, no SLA, evaluation of fine-tuned models only.
</details>

### Case Q6: Governance

Which TWO actions satisfy requirement 6?

A. Use **Azure Policy** to restrict allowed deployment types  
B. Assign **Cognitive Services Usages Reader at subscription scope** to the platform engineer  
C. Assign **Owner** at subscription to the platform engineer  
D. Add a note to the deployment README

<details><summary>Answer</summary>

### ✅ A and B

Policy = enforcement. Usages Reader at subscription scope = least privilege for quota visibility.
</details>

### Case Q7: Peak 429s on the PTU deployment

A. Lower temperature  
B. **Configure spillover to a Standard deployment** (or add PTUs if peaks become sustained)  
C. Switch to Developer  
D. Reduce prompt quality

<details><summary>Answer</summary>

### ✅ B
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Residency-at-rest trap** | "Global means data is stored anywhere." | Data at rest stays in the designated geography. Only **inference location** differs. |
| **Cheapest-type trap** | "Batch is cheapest, so use it for everything." | Batch is **asynchronous** (~24 h). Not for interactive apps. |
| **Provisioned-for-everything trap** | "PTU is always better." | Only for steady, high-volume, latency-sensitive loads. Wasteful for spiky/low usage. |
| **Quota-fix trap** | "429 means request more quota." | Check assignment to the deployment, `max_tokens`, retry behaviour, burst windows. Quota only helps if quota is the cause. |
| **max_tokens trap** | "max_tokens only limits output." | The TPM estimate counts it, so oversizing causes false throttling. |
| **Assigned-TPM trap** | "Subscription quota = deployment limit." | The deployment's limit = TPM **assigned to it**. |
| **Managed compute trap** | "Standard/Provisioned/Batch apply everywhere." | They apply to **Serverless API only**. |
| **Developer trap** | "Developer is a cheap production option." | No SLA, no residency guarantee, short-lived, evaluation only. |
| **Scope trap** | "Usages Reader at resource-group is enough." | The Usages API requires **subscription** scope. |
| **Policy trap** | "Tell developers not to use Global." | **Azure Policy** enforces allowed deployment types. |
| **Region-availability trap** | "Every type is available everywhere for every model." | Availability order: Global → Data Zone → Regional (last, with no guaranteed date). |
| **Instant-access trap** | "Every call needs a deployment." | **Instant access (preview)** calls supported models by name without deploying. |
| **Lifecycle trap** | "Deployed models run forever." | Models get deprecated and retired. Plan migration. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| No residency need, lowest price, new models first | **Global Standard** |
| Must stay in a zone (e.g., EU), variable traffic | **Data Zone Standard** |
| Strict single-geography processing, variable traffic | **Standard (regional)** |
| Steady high volume, predictable latency, any region | **Global Provisioned** |
| Steady high volume plus zone limit | **Data Zone Provisioned** |
| Steady high volume plus strict geography | **Regional Provisioned** |
| Large async job, no urgency, cost-sensitive | **Global Batch** (**Data Zone Batch** if zone-restricted) |
| Short test of a fine-tuned model | **Developer** |
| Custom/open model on dedicated GPUs | **Managed compute** |
| Own on-prem / Arc Kubernetes cluster | **Foundry Local on Azure Local** (preview) |
| Quick try without deploying | **Instant access** (preview) |
| 429 with usage below quota | Check assigned TPM, `max_tokens`, retry/backoff, burst windows |
| 429 on PTU at 100% utilisation | **Spillover** or add PTUs |
| View quota with least privilege | **Cognitive Services Usages Reader** at subscription |
| Block certain deployment types | **Azure Policy** |
| Mixed-complexity workload, one endpoint | **Model router** deployment |

---

## 5. Quick Revision Sheet

```text
HOSTING:   Serverless API | Managed compute (open/custom, GPUs, hourly) | Foundry Local on Azure Local
TYPES (Serverless only):  Global / Data Zone / Regional  ×  Standard / Provisioned / Batch  (+ Developer)

Global Standard   = default: cheapest, widest, newest models, any-region processing
Data Zone         = inference stays in zone (US/EU/...)
Standard/Regional = inference stays in the geography
Provisioned (PTU) = reserved capacity, stable latency, steady high volume
Batch             = async, ~50% cheaper, ~24h
Developer         = fine-tuned model eval, no SLA, short-lived

Data AT REST   = always in the designated geography
Data INFERENCE = depends on type

Quota   = per subscription × region × model × type, in TPM
Deploy  = assigned TPM is the deployment's limit; RPM derived
429     = TPM/RPM exceeded or capacity pressure -> backoff, retry-after, lower max_tokens, rebalance
PTU 429 = 100% utilisation -> spillover to Standard / more PTUs
Roles   = Cognitive Services Usages Reader @ SUBSCRIPTION for quota visibility
Control = Azure Policy restricts deployment types
```

### Best-answer checklist

1. **Where** must inference run (global, zone, geography)?
2. **How** is traffic shaped: spiky or low volume (Standard), steady or high (Provisioned), async bulk (Batch)?
3. Is the model **open/custom**? If so, consider managed compute (types don't apply).
4. Is it only a **test of a fine-tuned model**? Developer.
5. For 429s, determine **which kind** before choosing quota, `max_tokens`, retry, spillover or PTU.
6. Need hard **enforcement**? Azure Policy and RBAC, not guidance.

---

**Next concept:** Prompt engineering (same harder exam-style format)

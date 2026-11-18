# AI-103: Model Selection: LLM / SLM / Multimodal (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, code/config snippet, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Specific model names change often. The exam tests the **selection logic** (criteria, trade-offs, tooling), not memorising version numbers.

---

## 0. Core Concepts (read first)

### 0.1 Model categories

| Category | What it is | Typical strengths | Typical weaknesses |
|---|---|---|---|
| **LLM** (large language model) | Large general-purpose text (often multimodal) model | Broad knowledge, complex reasoning, long/ambiguous tasks, tool use | Higher cost, higher latency, needs cloud capacity |
| **SLM** (small language model), e.g., Phi family, "mini/nano" class models | Compact model, fewer parameters | **Low cost, low latency, high throughput**, can run at edge/on-device, easy to fine-tune for narrow tasks | Weaker at broad/complex reasoning |
| **Reasoning model** | Model trained to "think" through multi-step problems before answering | Math, code, planning, multi-step logic, complex tool use | Slower and costlier per request; overkill for simple tasks |
| **Multimodal model** | Accepts (and sometimes produces) more than one modality: text + **image**, audio, video | Image understanding, document/chart reading, voice, mixed inputs | Cost/latency can be higher; check supported input/output types |
| **Embedding model** | Converts text/images to vectors | Search, retrieval, RAG, similarity, clustering | **Does not generate text** |
| **Image / video generation model** | Produces images/video from prompts | Creative generation | Not for text reasoning |
| **Speech / audio model** | Speech-to-text, text-to-speech, real-time voice | Voice agents, transcription | Task-specific |
| **Task-specific model** (classification, etc.) | Narrow, purpose-built | Very cheap and fast at one thing | Not general |

### 0.2 The selection criteria (memorise as **Q-C-L-T-S-M-R**)

| Criterion | Question to ask |
|---|---|
| **Q**uality | Is accuracy on *my* task good enough (reasoning, coding, extraction, QA)? |
| **C**ost | Cost per token / per request at my volume? |
| **L**atency | Time to first token / total response time acceptable? |
| **T**hroughput | Tokens per second / requests per minute at peak? Quota? |
| **S**afety | Content safety benchmarks, jailbreak resistance, compliance? |
| **M**odality | Does it accept the **input types** I need and produce the **output types** I need? |
| **R**egion / deployment | Available in my region, with required data residency and deployment type? Context window large enough? |

Also remember **context window** (how much input fits) and **max output tokens**.

### 0.3 Foundry tooling for choosing a model

| Tool | Purpose |
|---|---|
| **Model catalog** (Build → Models/Catalog) | Browse thousands of models from Microsoft, OpenAI, Anthropic, Meta, Mistral, DeepSeek, xAI and others. Filter by capability, input/output type, deployment option, license, task |
| **Model leaderboards** | Industry-standard benchmark rankings for **quality, safety, estimated cost, throughput** (text LLMs/SLMs) and quality for **embedding** models |
| **Trade-off charts** | Compare two metrics at once, e.g., **quality vs cost** |
| **Scenario leaderboards** | Benchmarks tuned to a use case (e.g., a specific task type) |
| **Compare models** | Side-by-side features, performance and estimated cost |
| **Playground** | Try a model interactively before committing |
| **Evaluations on your own data** | **Most trusted evidence**: benchmark scores are generic, so validate with representative prompts from your workload |
| **Model router** | One deployment that **automatically routes each prompt** to the best-suited model from a pool |

Benchmark caveat: **leaderboards are generic and some leaderboard features are in preview**. They guide shortlisting. Your own evaluation decides.

### 0.4 Model router (high-yield)

- A **routing model** you deploy once. It judges each prompt's difficulty and sends it to a suitable underlying model: **simple prompts → small/fast models; hard reasoning or complex tool use → frontier models**.
- **Routing modes:** **Balanced** (default, best cost-quality ratio), **Quality** (maximise accuracy), **Cost** (minimise spend).
- Benefits: lower average cost, often lower latency, automatic failover on retryable errors, **no routing logic in your code**, one endpoint / one rate limit / one content filter. The response's `model` field tells you which model answered.
- Works with Responses API, Chat Completions API (and Messages API in preview).
- Best for **mixed-complexity workloads**. If *every* request needs the same specific model (compliance pin, fixed behavior), use a **direct deployment**.

### 0.5 Decision rules of thumb

```text
Simple, high-volume, latency/cost sensitive (classification, extraction, FAQ)  → SLM / "mini/nano"
Complex reasoning, multi-step planning, hard coding, ambiguous tasks           → LLM / reasoning model
Needs to understand images / documents / charts / audio                        → multimodal model
Needs to search or retrieve by meaning                                         → embedding model (not a chat model)
On-device / offline / edge / strict data locality                              → SLM (e.g., Phi) deployed locally
Mixed workload, want cost savings without custom routing code                  → model router
Domain/style adaptation that prompts + RAG can't achieve                       → fine-tune (often an SLM)
Facts change / need citations                                                  → RAG, not a bigger model
```

### 0.6 Model-fit vs other fixes (very common exam trap)

| Problem | Best first fix |
|---|---|
| Wrong tone/format/behavior | **Prompt / instructions** |
| Missing or outdated facts | **RAG / grounding** |
| Needs consistent specialised style or format at scale | **Fine-tuning** |
| Model physically can't handle the input type (e.g., images) | **Different (multimodal) model** |
| Too slow/expensive for a simple task | **Smaller model** |
| Fails at complex multi-step reasoning | **Stronger / reasoning model** |

### 0.7 Five ideas the exam really tests

1. **Match model size to task complexity.** Bigger is not always better.
2. **Modality is a hard requirement.** If the model can't take images, no prompt fixes it.
3. **Benchmarks shortlist; your own evaluation decides.**
4. **Embedding models retrieve; chat models generate.** Don't mix them up.
5. **Model router** = automatic cost/quality optimisation for mixed workloads.

---

## 1. Scenario Questions

### Question 1: Cost and latency at scale

A retailer classifies 5 million short customer messages per day into 12 categories (billing, delivery, returns...). The task is simple and well-defined. Requirements: **lowest cost, lowest latency, high throughput**. Accuracy needs to be good but not state-of-the-art reasoning. Which model approach is BEST?

A. The largest reasoning model available, for maximum accuracy  
B. A small, low-cost model (SLM / "mini/nano" class), validated on a labeled sample of the messages  
C. An embedding model that generates the category as text  
D. A video-generation model

<details>
<summary>Answer</summary>

### ✅ B

**Why correct:** Simple, high-volume, narrowly-defined task with strict cost/latency needs is the textbook SLM use case. Validate accuracy on a labeled sample.

**Why others are wrong**
- **A ❌** Overkill: highest cost and latency for a simple task.
- **C ❌** Embedding models output **vectors**, not generated text. (They could support a similarity-based classifier, but "generates the category as text" is wrong.)
- **D ❌** Irrelevant.

**Trap:** "Most capable" ≠ "best fit".
</details>

---

### Question 2: Modality requirement

An insurance company wants an agent that reads **photos of vehicle damage** and **scanned claim forms**, then drafts an assessment. They have been testing a text-only model and it cannot process the photos. What should they do?

A. Add stricter prompt instructions to make the text model "look" at the images  
B. Increase the max output tokens  
C. Switch to a **multimodal model that supports image input** (and use it for document pages too)  
D. Add an embedding model to the pipeline

<details>
<summary>Answer</summary>

### ✅ C

**Why correct:** Image understanding requires a model with **image input** capability. Check the catalog's **Input type** filter (text, image, audio...).

**Why others are wrong**
- **A ❌** Prompts can't add a missing modality.
- **B ❌** Output length is unrelated.
- **D ❌** Embeddings enable search; they don't interpret images into assessments by themselves.

**Trap:** Modality mismatches are *capability* problems, not prompt problems.
</details>

---

### Question 3: Complex reasoning

A legal-tech app must analyse long contracts, identify conflicting clauses across sections, and produce a multi-step reasoned risk analysis. Quality matters far more than cost; responses can take several seconds. Which choice fits BEST?

A. A small, fast model to minimise latency  
B. A frontier / reasoning-capable LLM with a context window large enough for the contracts  
C. An embedding model only  
D. A speech model

<details>
<summary>Answer</summary>

### ✅ B

Multi-step reasoning over long documents with quality as the priority = stronger LLM / reasoning model. Also verify the **context window** can hold the contracts (or chunk + RAG if not).

- **A ❌** Likely to struggle on cross-clause reasoning.
- **C ❌** Doesn't generate analysis.
- **D ❌** Irrelevant.
</details>

---

### Question 4: Edge / offline

A field-service company needs an assistant on **rugged tablets that are often offline**, answering questions about equipment manuals. Data must stay on the device. Which approach fits BEST?

A. Call a large cloud-hosted LLM for every question  
B. Deploy a **small language model locally on the device**, grounded on the manuals stored locally  
C. Use a video-generation model  
D. Disable the model and use keyword search only, because AI can't run offline

<details>
<summary>Answer</summary>

### ✅ B

SLMs such as the Phi family are designed to run locally (edge/on-device), with or without cloud connectivity, with low latency and resource use.

- **A ❌** Needs connectivity and sends data off-device.
- **C ❌** Irrelevant.
- **D ❌** Incorrect premise. SLMs can run offline.
</details>

---

### Question 5: Mixed workload without custom routing code

An internal assistant receives both quick lookups ("what's the VPN setup URL?") and occasional hard tasks (debugging multi-file code, multi-constraint planning). The team uses one large model for everything and the bill is high. They do **not** want to build and maintain their own routing logic. What should they do?

A. Fine-tune the large model  
B. Deploy **model router** (Balanced mode to start) so each prompt is routed to a model suited to its difficulty  
C. Force everything onto the smallest model  
D. Use an embedding model for all requests

<details>
<summary>Answer</summary>

### ✅ B

Model router sends easy prompts to smaller/faster/cheaper models and hard ones to stronger models, with no routing code. Balanced is the default cost-quality ratio.

- **A ❌** Fine-tuning doesn't reduce per-request cost for easy prompts.
- **C ❌** Would hurt quality on the hard tasks.
- **D ❌** Not a text-generation model.
</details>

---

### Question 6: Model router modes (drag-and-drop)

Match each requirement to the **model router mode**.

| Requirement | Options: Balanced / Quality / Cost |
|---|---|
| A. High-volume FAQ bot where small quality differences are acceptable and spend must be minimised | ? |
| B. A clinical-summary tool where answer accuracy is the top priority | ? |
| C. General-purpose assistant, best cost-quality ratio, no strong preference | ? |

<details>
<summary>Answer</summary>

| Requirement | Mode |
|---|---|
| A | **Cost** |
| B | **Quality** |
| C | **Balanced** (default) |
</details>

---

### Question 7: Choosing the shortlist (Select TWO)

You need to shortlist models for a customer-support copilot and understand quality vs cost trade-offs. Which TWO Foundry capabilities help MOST at the shortlisting stage?

A. Model leaderboards (quality, safety, estimated cost, throughput) and trade-off charts  
B. The Compare models side-by-side view  
C. Azure Policy  
D. Private endpoints  
E. Key Vault

<details>
<summary>Answer</summary>

### ✅ A and B

- **A ✅** Leaderboards plus trade-off charts (e.g., quality vs cost) compare benchmark scores.
- **B ✅** Side-by-side comparison of features, performance and estimated cost.
- **C, D, E ❌** Governance/security/secrets controls. They don't help you choose between models.
</details>

---

### Question 8: Benchmarks vs your data

The top model on a public quality leaderboard performs **worse than expected** on your company's contract-extraction task. What should you conclude and do?

A. The leaderboard is wrong; ignore all benchmarks  
B. Leaderboards are generic. **Evaluate candidate models on a representative sample of your own data** and choose based on those results  
C. Increase temperature to 2  
D. Fine-tune immediately without testing alternatives

<details>
<summary>Answer</summary>

### ✅ B

Benchmarks use standard datasets and generic tasks. They're for shortlisting. Workload-specific evaluation with representative prompts is the decisive evidence.

- **A ❌** Too extreme. Benchmarks are still useful for shortlisting.
- **C ❌** Doesn't address fit.
- **D ❌** Fine-tuning before comparing alternatives is premature.
</details>

---

### Question 9: Config snippet, spot the problem

```json
{
  "scenario": "Semantic search over 2M support articles",
  "chosen_model": "frontier-chat-llm",
  "usage": "Call chat completions with each article, ask the model to return a vector",
  "complaint": "Slow, expensive, vectors are inconsistent"
}
```

What is the BEST correction?

A. Use a larger context window  
B. Use a dedicated **embedding model** to generate vectors, and store them in a vector-capable index (e.g., Azure AI Search)  
C. Use a video-generation model  
D. Lower the max output tokens

<details>
<summary>Answer</summary>

### ✅ B

Vectors for search come from **embedding models** (cheap, fast, consistent). Chat models are the wrong tool for this job.

**Trap:** Read the *usage* field. The mismatch between task and model type is the clue.
</details>

---

### Question 10: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | A small language model can often outperform a larger model on a narrow, well-defined task after fine-tuning. | |
| 2 | If a text-only model cannot accept images, adding stricter prompts will let it process images. | |
| 3 | Leaderboard benchmark scores are enough on their own to pick a production model. | |
| 4 | Model router can send simple prompts to smaller models and complex prompts to stronger models automatically. | |
| 5 | An embedding model is the right choice for generating long-form answers to users. | |
| 6 | Context window size is a valid model-selection criterion. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **Yes** | Narrow tasks plus fine-tuning let SLMs be very competitive at lower cost/latency. |
| 2 | **No** | Modality is a capability. Needs a model with image input. |
| 3 | **No** | Generic benchmarks shortlist. Evaluate on your own data. |
| 4 | **Yes** | The core purpose of model router. |
| 5 | **No** | Embedding models produce vectors, not text answers. |
| 6 | **Yes** | Must fit your prompts, documents and conversation history. |
</details>

---

### Question 11: Fix the right layer (Select TWO)

A support bot built on a capable LLM (a) gives outdated return-policy details and (b) sometimes answers in the wrong tone. Which TWO changes address these issues MOST appropriately?

A. Add a **grounding/RAG** source with the current return policy  
B. Switch to a model with **10× more parameters**  
C. Update the **instructions/system prompt** to define tone and format  
D. Fine-tune a new model on tone examples before trying a prompt change  
E. Reduce the context window

<details>
<summary>Answer</summary>

### ✅ A and C

- **A ✅** Outdated facts → grounding/RAG.
- **C ✅** Tone/format → instructions (cheapest first fix).
- **B ❌** Bigger models don't know your *current* policy.
- **D ❌** Premature, since the prompt change is cheaper and faster.
- **E ❌** Doesn't help either issue.
</details>

---

### Question 12: Match the need to the model type (drag-and-drop)

Match each need to: **LLM/reasoning model · SLM · Multimodal model · Embedding model · Speech model**.

| Need | Model type |
|---|---|
| 1. Convert call-center audio to text | ? |
| 2. Find the most similar past tickets to a new ticket | ? |
| 3. Read a chart screenshot and explain the trend | ? |
| 4. Run an assistant locally on a laptop with low memory | ? |
| 5. Multi-step financial scenario planning with tool calls | ? |

<details>
<summary>Answer</summary>

| Need | Model type |
|---|---|
| 1 | **Speech model** (speech-to-text) |
| 2 | **Embedding model** |
| 3 | **Multimodal model** (image input) |
| 4 | **SLM** |
| 5 | **LLM / reasoning model** |
</details>

---

### Question 13: When NOT to use model router

Which scenario is the **weakest** fit for model router?

A. A chat assistant with a mix of easy and hard questions  
B. A coding tool where each step can need different capability levels  
C. A regulated workflow where compliance **requires one specific, pinned model** for every request, with fixed behavior and documented validation  
D. A cost-sensitive agent loop with varied step complexity

<details>
<summary>Answer</summary>

### ✅ C

When a specific model must be used for every request (pinned for compliance/validation), use a **direct deployment**. Model router is best for mixed-complexity workloads where variability is acceptable.
</details>

---

### Question 14: Latency vs quality evaluation

A team compares a router deployment with their current single-model deployment. Which evaluation approach is MOST appropriate?

A. Compare using 3 hand-picked easy prompts  
B. Use a **representative set of production-like prompts** (sanitised), measure **quality, cost, and latency (including tail latency)** against acceptance criteria, then adjust routing mode or constrain the model pool  
C. Only compare price per million tokens  
D. Skip evaluation because routing is automatic

<details>
<summary>Answer</summary>

### ✅ B

Evaluate the configuration you'll actually run, on representative workloads, across quality, cost, latency and policy. Then iterate (mode, model subset, or keep a direct deployment for specific requests).

- **A ❌** Biased sample.
- **C ❌** Ignores quality/latency and actual usage mix.
- **D ❌** Automatic ≠ validated.
</details>

---

## 2. Mini Case Study: Northwind Insurance

### Background

Northwind Insurance is building AI features on Microsoft Foundry.

1. **Claim triage:** classify ~2 million short incoming emails per day into 15 queues. Needs lowest cost and latency.
2. **Damage assessment:** analyse customer-uploaded **vehicle photos** and **PDF claim forms** and draft an assessment.
3. **Policy copilot:** answer adjuster questions on policies that change monthly, **with citations**.
4. **Complex fraud analysis:** multi-step reasoning across claim history, with accuracy valued over speed.
5. **Field app:** adjusters at remote sites need a basic assistant **offline** on tablets.
6. **General internal helpdesk:** mixed easy/hard questions; the team doesn't want to maintain routing logic.

### Case Q1: Claim triage

Which model approach?

A. Frontier reasoning model  
B. Small, low-cost model validated on labeled samples  
C. Image-generation model  
D. Embedding model generating text

<details>
<summary>Answer</summary>

### ✅ B

Simple, high-volume, cost/latency-critical.
</details>

### Case Q2: Damage assessment

Which requirement is **decisive** for model choice?

A. Output language  
B. Support for **image input** (multimodal) and handling document pages  
C. Embedding dimension  
D. Speech sampling rate

<details>
<summary>Answer</summary>

### ✅ B

Modality is a hard requirement. Filter the catalog by image input.
</details>

### Case Q3: Policy copilot

Policies change monthly and answers need citations. Which is the BEST design?

A. Use the largest LLM and trust its training knowledge  
B. Fine-tune a model monthly on the policies  
C. Use an LLM with **RAG/grounding** over the current policy documents (embedding model + search index) and instructions to cite sources  
D. Use an SLM with no data access

<details>
<summary>Answer</summary>

### ✅ C

Changing facts + citations = grounding. Bigger or fine-tuned models would still go stale.
</details>

### Case Q4: Fraud analysis

Which choice fits?

A. SLM for lowest cost  
B. Reasoning-capable LLM, accepting higher cost and latency  
C. Speech model  
D. Embedding model only

<details>
<summary>Answer</summary>

### ✅ B
</details>

### Case Q5: Offline field app

A. Cloud LLM on every call  
B. SLM deployed locally on the tablets  
C. Model router  
D. Image-generation model

<details>
<summary>Answer</summary>

### ✅ B

Model router is a cloud service, so it isn't suited to offline use.
</details>

### Case Q6: Internal helpdesk

Best fit?

A. Model router (Balanced to start)  
B. Always the smallest model  
C. Always the largest model  
D. Fine-tune weekly

<details>
<summary>Answer</summary>

### ✅ A

Mixed difficulty, no custom routing code wanted, and you can evaluate Balanced vs Cost vs Quality.
</details>

### Case Q7: Map the use cases

| Use case | Model type |
|---|---|
| Claim triage | ? |
| Damage assessment | ? |
| Policy copilot retrieval layer | ? |
| Fraud analysis | ? |
| Offline field app | ? |

<details>
<summary>Answer</summary>

| Use case | Model type |
|---|---|
| Claim triage | **SLM** |
| Damage assessment | **Multimodal** |
| Policy copilot retrieval layer | **Embedding model** (+ LLM for generation) |
| Fraud analysis | **LLM / reasoning model** |
| Offline field app | **SLM (local)** |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Bigger-is-better trap** | "Use the most powerful model." | Match model to task. Simple/high-volume tasks → SLM. |
| **Modality trap** | "Prompt it harder to read images." | Needs a multimodal model with the right **input type**. |
| **Embedding trap** | "Embedding model can answer questions." | Embeddings → vectors for retrieval. Chat/LLM generates answers. |
| **Benchmark trap** | "Top of the leaderboard wins." | Leaderboards shortlist. **Your own evaluation** decides. |
| **Fine-tune-first trap** | "Fine-tune to fix wrong behavior/facts." | Prompt first for behavior; RAG for facts; fine-tune for specialised style at scale. |
| **Freshness trap** | "A newer/bigger model knows the latest policy." | Current/private facts need grounding. |
| **Router-everywhere trap** | "Always use model router." | Great for mixed workloads. Use a direct deployment when a specific model must be pinned. |
| **Router-vs-code trap** | "I must build routing logic." | Model router provides it (modes: Balanced/Quality/Cost). |
| **Reasoning-for-everything trap** | "Reasoning models are always best." | Slower and costlier. Use for complex multi-step tasks only. |
| **Context-window trap** | "Context size doesn't matter." | Must fit your documents/history, or chunk + retrieve. |
| **Edge trap** | "AI always needs the cloud." | SLMs (e.g., Phi) can run locally/offline. |
| **Preview trap** | "Leaderboards are production-grade guarantees." | Leaderboard features may be preview, and benchmarks have limitations. |

---

## 4. Decision Table

| Symptom / requirement | Answer |
|---|---|
| Simple, high-volume, low-latency, low-cost | SLM / mini-nano class |
| Complex multi-step reasoning, hard coding, planning | LLM / reasoning model |
| Needs to understand images/charts/documents | Multimodal model (check image input) |
| Voice transcription or voice agent | Speech model |
| Semantic search / similarity / RAG retrieval | Embedding model |
| Local / offline / on-device | SLM (e.g., Phi) deployed locally |
| Mixed easy/hard prompts, reduce cost without routing code | Model router (Balanced default) |
| Minimise spend on routed traffic | Router **Cost** mode |
| Maximise accuracy on routed traffic | Router **Quality** mode |
| Must use one specific model for every request | Direct deployment |
| Compare quality/cost/safety/throughput | Model leaderboards, trade-off charts, Compare models |
| Validate for *your* workload | Evaluate with representative prompts |
| Outdated/missing facts | RAG / grounding |
| Wrong tone/format | Instructions / prompt |
| Specialised consistent style/format at scale | Fine-tuning (often SLM) |
| Documents too long for model | Larger context window, or chunk + RAG |

---

## 5. Quick Revision Sheet

```text
LLM        = broad, strong reasoning, higher cost/latency
SLM        = small, fast, cheap, edge-capable, great for narrow tasks (Phi, mini/nano)
REASONING  = multi-step "thinking", slower/costlier, for hard problems
MULTIMODAL = text + image/audio/video input (and sometimes output)
EMBEDDING  = vectors for search/RAG (does NOT generate text)
ROUTER     = one deployment, auto-picks model per prompt (Balanced | Quality | Cost)

Selection criteria: Quality · Cost · Latency · Throughput · Safety · Modality · Region/context
Tools: Model catalog · Leaderboards · Trade-off charts · Compare models · Playground · Your own evals

Benchmarks = shortlist.   Your own data eval = decision.
Behavior -> prompt.  Facts -> RAG.  Style at scale -> fine-tune.  Missing modality -> different model.
```

### Best-answer checklist

1. Is a **modality** (image/audio) required? If so, filter to multimodal first.
2. Is the task **simple/high-volume**, or **complex/multi-step**? Pick SLM or reasoning LLM accordingly.
3. Is the real problem **facts**, **behavior**, or **style**? Choose RAG, prompt, or fine-tune. Don't swap models by reflex.
4. Does the task need **vectors/search**? Use an embedding model.
5. **Mixed workload** and no custom routing code? Model router.
6. Does a **specific model have to be pinned**? Direct deployment.
7. Always validate with **your own representative data**.

---

**Next concept:** Model deployment (same harder exam-style format)

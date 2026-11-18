# AI-103: Model Parameters (Exam-Style, Harder)

> Format: long scenarios, close distractors, multi-select, Yes/No, drag-and-drop mapping, code/request snippets, and a mini case study.
> Answers are in collapsible sections, so attempt each question first.
> Parameter support differs between **GPT-style (non-reasoning)** and **reasoning** models. This difference is the most tested idea in this topic.

---

## 0. Core Concepts (read first)

### 0.1 What are model parameters?

Request-time settings that control **how the model generates output**: randomness, length, repetition, stopping, reproducibility, format. They are **not** instructions (prompt) and **not** knowledge (grounding).

### 0.2 The parameters (GPT-style / non-reasoning models)

| Parameter | Controls | Typical range | Use when | Watch out |
|---|---|---|---|---|
| **temperature** | Randomness of token selection. Low = focused/deterministic-leaning; high = varied/creative | 0 – 2 | **Low** (0–0.3): extraction, classification, factual Q&A, code. **Higher**: brainstorming, creative writing | Low temperature ≠ guaranteed identical outputs. Doesn't fix hallucination or security |
| **top_p** (nucleus sampling) | Samples only from the smallest set of tokens whose cumulative probability ≥ p | 0 – 1 | Alternative way to control diversity | **Change temperature OR top_p, not both** |
| **max_tokens** | Max tokens the model may **generate** (output cap) | 1 – model limit | Control length, cost, latency | Prompt tokens + max_tokens must fit the **context window**. Too low → **truncated** answer (`finish_reason: length`). Also counts toward the TPM **estimate** (oversizing causes early 429s) |
| **frequency_penalty** | Penalises tokens **in proportion to how often** they've already appeared | −2 to 2 | Reduce **verbatim repetition** | Too high → odd/avoidant wording |
| **presence_penalty** | Penalises tokens that have **appeared at all** | −2 to 2 | Encourage **new topics/vocabulary** | Too high → drifts off-topic |
| **stop** (stop sequences) | Ends generation when a sequence is produced | up to a few strings | Cut at delimiters, end of a list, structured formats | Stop string itself isn't returned |
| **seed** | Best-effort **reproducible** sampling | integer | Testing, regression, A/B comparison | **Not guaranteed**. Same seed **and identical** params/prompt needed. Check `system_fingerprint` for backend changes |
| **n** | Number of completions per request | 1+ | Compare candidates | **Multiplies output tokens and cost** |
| **logprobs / top_logprobs** | Return token probabilities | | Confidence scoring, classification diagnostics | Not for reasoning models |
| **stream** | Return tokens incrementally | true/false | **Perceived latency** in chat UIs | Doesn't make total generation faster; content filter/annotations arrive differently |
| **response_format / structured outputs** | Force JSON or schema-conformant output | text / json_object / **json_schema** | Machine-readable output | `json_schema` (structured outputs) is stronger than older `json_object` mode |
| **logit_bias** | Nudge specific token likelihood | | Rarely: ban/boost tokens | Advanced |

### 0.3 Reasoning models (gpt-5 / o-series family) are different

| | GPT-style | Reasoning models |
|---|---|---|
| Output cap | `max_tokens` | **`max_completion_tokens`** (covers **reasoning tokens + visible output**) |
| Randomness | `temperature`, `top_p` | **Not supported** (sending them can return **HTTP 400 Unsupported parameter**) |
| Penalties | `frequency_penalty`, `presence_penalty` | **Not supported** |
| Depth control | n/a | **`reasoning_effort`** (e.g., low / medium / high) |
| Verbosity | prompt wording | **`verbosity`** (low/medium/high) supported on newer models via Responses API |
| System role | `system` | **`developer`** (preferred) |
| Tool calling | Chat Completions fine | Prefer the **Responses API** |
| Billing surprise | Visible output only | **Hidden reasoning tokens are billed** and consume the completion budget |

> Why this matters: A migration from a GPT-4-class model to a reasoning model can fail on the **first call** with HTTP 400 because old code sends `temperature`, `top_p`, `max_tokens`, or `stop`. The fix is to **remove or rename** those parameters (for example, `max_tokens` → `max_completion_tokens`), not to set them to a "safe" value.

> Too-small `max_completion_tokens` on a reasoning model can be **entirely consumed by reasoning**, giving an **empty or truncated answer** with `finish_reason: length`. Leave headroom.

### 0.4 Practical settings cheat-sheet

| Task | Suggested starting point |
|---|---|
| Data extraction / classification / strict JSON | Low temperature (0–0.2), clear output contract / structured outputs, modest `max_tokens` |
| RAG Q&A (factual, grounded) | Low temperature, `max_tokens` sized to the expected answer (community guidance: roughly **500–800** for RAG), grounded-only instructions |
| Brainstorming / marketing copy | Higher temperature (e.g., 0.7–1.0) or adjusted top_p |
| Long, repetitive output problem | Modest `frequency_penalty` |
| Need new ideas / topic spread | Modest `presence_penalty` |
| Stop at a marker | `stop` sequence |
| Reproducible test runs | Fixed `seed` + identical params, monitor `system_fingerprint`, **still not guaranteed** |
| Responsive chat UI | `stream=true` |
| Hard reasoning, accuracy first | Reasoning model with higher `reasoning_effort` |
| Fast/cheap simple task on a reasoning model | Lower `reasoning_effort` (and lower `verbosity`) |

### 0.5 What parameters CANNOT fix

| Problem | Real fix |
|---|---|
| Hallucination / outdated facts | Grounding / RAG |
| Wrong tone / scope | Instructions (system/developer message) |
| Prompt injection / policy violation | Layered controls: Prompt Shields, filters, least privilege, approvals |
| Missing capability (images, tools) | Different model / configured tool |
| Rate limiting (429) | Quota, backoff, **lower max_tokens**, deployment type |

### 0.6 Five ideas the exam really tests

1. **Temperature (or top_p) = randomness only.** It doesn't add knowledge or security.
2. **Change temperature OR top_p, not both.**
3. **max_tokens limits output; prompt + output must fit the context window.** Truncation shows as `finish_reason: length`.
4. **Reasoning models: no temperature/top_p/penalties; use `max_completion_tokens` and `reasoning_effort`.**
5. **seed gives best-effort reproducibility, never a guarantee.**

---

## 1. Scenario Questions

### Question 1: Extraction pipeline

A pipeline on a GPT-style model extracts contract fields into JSON. Output varies between runs (sometimes extra commentary, sometimes a different key order). Which TWO changes are MOST appropriate?

A. Lower **temperature** (for example, 0–0.2)  
B. Use **structured outputs / JSON schema** and a clear output contract  
C. Increase **presence_penalty** to 2  
D. Increase **n** to 5 and pick randomly  
E. Raise **top_p** to 1 and temperature to 1.5

<details>
<summary>Answer</summary>

### ✅ A and B

Extraction needs low randomness plus format enforcement.

- **C ❌** Pushes the model toward new/different tokens.
- **D ❌** Multiplies cost, doesn't improve consistency.
- **E ❌** More randomness.
</details>

---

### Question 2: Truncated answers

Users report answers that stop mid-sentence. API responses show `finish_reason: "length"`. The request sets `max_tokens=100`, and typical answers need ~300 tokens. What should you do?

A. Increase temperature  
B. **Increase `max_tokens`** to fit the expected answer (while staying within the context window and cost/latency goals), and/or instruct a shorter answer  
C. Reduce top_p  
D. Add a stop sequence of "."

<details>
<summary>Answer</summary>

### ✅ B

`finish_reason: length` means the output cap was hit. Raise the cap or constrain verbosity via instructions.

- **A, C ❌** Don't change the length cap.
- **D ❌** Would cut every answer at the first period.

**Trap:** Don't confuse `length` (token cap) with `stop` (natural end or stop sequence) or `content_filter`.
</details>

---

### Question 3: Migration failure (snippet)

```python
resp = client.chat.completions.create(
    model="reasoning-deployment",        # a reasoning model
    messages=[{"role": "developer", "content": "You are a helpful assistant."},
              {"role": "user", "content": "Summarise this contract."}],
    temperature=0.2,
    top_p=0.9,
    max_tokens=800,
)
# -> HTTP 400: Unsupported parameter
```

The same code worked on a GPT-4-class deployment. What is the BEST fix?

A. Set temperature to 1 and keep the rest  
B. **Remove `temperature` and `top_p`, replace `max_tokens` with `max_completion_tokens`** (with headroom for reasoning tokens), and tune `reasoning_effort` if needed  
C. Add `seed=42`  
D. Switch the role back to `system`

<details>
<summary>Answer</summary>

### ✅ B

Reasoning models reject classic sampling parameters and use `max_completion_tokens`. It's a **removal/rename**, not a value change.

- **A ❌** Some models reject the parameter at any value.
- **C ❌** Doesn't address the errors.
- **D ❌** The role isn't the cause.

**Trap:** The snippet's comment `# a reasoning model` is the clue.
</details>

---

### Question 4: Empty answer from a reasoning model

After migrating, a reasoning-model call with `max_completion_tokens=300` returns an **empty or truncated** answer, yet billing shows ~300 tokens used. What is the MOST likely cause?

A. Content filters blocked the answer  
B. **The 300-token budget was consumed by hidden reasoning tokens**, leaving little or none for visible output. Increase `max_completion_tokens` and/or reduce `reasoning_effort`  
C. Temperature is too low  
D. The embedding model is misconfigured

<details>
<summary>Answer</summary>

### ✅ B

`max_completion_tokens` covers reasoning plus visible output. Leave headroom, or lower the effort for simple tasks.

- **A ❌** Would show a filter result, not a silent token budget issue.
- **C ❌** Temperature isn't used on these models.
- **D ❌** Unrelated.
</details>

---

### Question 5: temperature vs top_p

A developer sets `temperature=0.2` and `top_p=0.1` "for maximum determinism". What is the best guidance?

A. This is the recommended combination  
B. **Adjust one, not both.** Use a low temperature (or a low top_p), and test the effect  
C. Set both to 2  
D. Remove max_tokens

<details>
<summary>Answer</summary>

### ✅ B

Both control randomness, so changing both makes behaviour harder to reason about. The common guidance is to alter one and keep the other at its default.
</details>

---

### Question 6: Repetition (Select TWO)

A product-description generator repeats the same phrases ("high-quality, durable, high-quality...") and keeps circling the same two features. Which TWO parameters help MOST?

A. Modest **frequency_penalty** to discourage repeated tokens  
B. Modest **presence_penalty** to encourage new topics  
C. Set `max_tokens=1`  
D. Set `n=10`  
E. Set `stop` to an empty string

<details>
<summary>Answer</summary>

### ✅ A and B

- **frequency_penalty** reduces repetition **in proportion to frequency**.
- **presence_penalty** nudges toward **new** tokens/topics (penalises anything already used).

- **C ❌** Truncates to a single token.
- **D ❌** Cost multiplier, doesn't fix repetition.
- **E ❌** No effect.

Rule: frequency = "stop saying the same words"; presence = "talk about something new".
</details>

---

### Question 7: Reproducibility

A QA team compares two prompt versions and wants outputs as repeatable as possible between runs. Which approach is BEST?

A. Set `seed` to a fixed integer, keep **all other parameters and the prompt identical**, use a low temperature, and **log `system_fingerprint`**. Accept that reproducibility is best-effort  
B. Set `seed` only, and change prompts freely  
C. Set `n` very high  
D. Treat identical outputs as guaranteed whenever seed is set

<details>
<summary>Answer</summary>

### ✅ A

`seed` gives best-effort determinism. Backend changes (visible through `system_fingerprint`) can still alter outputs. It is not a guarantee.

- **B ❌** Changed prompts change outputs.
- **C ❌** Unrelated.
- **D ❌** Overstates the guarantee.
</details>

---

### Question 8: Latency perception

A chat UI feels slow because users wait several seconds before seeing any text. Total generation time can't change much. What should you do?

A. Increase temperature  
B. **Enable streaming** so tokens appear as they're generated  
C. Increase max_tokens  
D. Set n=3

<details>
<summary>Answer</summary>

### ✅ B

Streaming improves **perceived** responsiveness (time to first token). It doesn't reduce total generation time.

- **C ❌** Longer outputs can be slower.
- **D ❌** Multiplies work.
</details>

---

### Question 9: Stop sequences

A model generates a numbered list of exactly 3 recommendations, followed by unwanted extra commentary beginning with "Note:". Which approach BEST removes the extra text?

A. Set a **stop sequence** of `"Note:"` and instruct "return exactly three recommendations"  
B. Raise temperature  
C. Set presence_penalty to −2  
D. Remove the system message

<details>
<summary>Answer</summary>

### ✅ A

Stop sequences cut generation at a marker, and the instruction reduces how often the marker appears.

**Note:** Some reasoning models reject `stop`, so check support for your model.
</details>

---

### Question 10: Context window math

A model has a **16,000-token** context window. A request has **15,500 prompt tokens**. The developer sets `max_tokens=2,000`. What is the issue?

A. None. Output tokens are separate from the context window  
B. **Prompt + requested output (17,500) exceeds the context window.** Reduce the prompt (e.g., retrieve fewer/shorter chunks) or lower `max_tokens`  
C. Temperature must be 0  
D. top_p must be 1

<details>
<summary>Answer</summary>

### ✅ B

Prompt tokens + `max_tokens` must fit in the context window. Otherwise you get an error or a truncated response.

$$15{,}500 + 2{,}000 = 17{,}500 > 16{,}000$$
</details>

---

### Question 11: 429 errors linked to max_tokens

A deployment shows usage well below its TPM limit but still returns 429s. Every request sets `max_tokens=4000`; average answers are ~200 tokens. Which TWO actions are MOST appropriate?

A. **Lower `max_tokens`** to match realistic answer length  
B. Implement **retry with backoff**, honouring `retry-after`  
C. Increase temperature  
D. Set `n=4`  
E. Disable streaming

<details>
<summary>Answer</summary>

### ✅ A and B

The TPM check uses an **estimate** that includes the full `max_tokens`, so oversizing reserves capacity unnecessarily. Backoff handles burst limits.

- **D ❌** `n` increases token use.
</details>

---

### Question 12: Yes / No statements

| # | Statement | Yes / No |
|---|---|---|
| 1 | Lowering temperature to 0 guarantees identical output on every call. | |
| 2 | Setting `seed` makes outputs best-effort reproducible when other parameters and the prompt are identical. | |
| 3 | Reasoning models generally support `temperature` and `top_p` the same way GPT-style models do. | |
| 4 | `max_completion_tokens` on reasoning models covers both reasoning tokens and visible output. | |
| 5 | Increasing `n` increases the number of completions and generally the cost. | |
| 6 | Lowering temperature is an effective fix for hallucinated facts. | |
| 7 | Streaming reduces the total time the model takes to generate the full answer. | |
| 8 | `reasoning_effort` is a lever for reasoning models, not for GPT-style models. | |

<details>
<summary>Answer</summary>

| # | Answer | Reason |
|---|---|---|
| 1 | **No** | Reduces variability, doesn't guarantee determinism. |
| 2 | **Yes** | Best-effort, not guaranteed. |
| 3 | **No** | Typically rejected or unsupported on reasoning models. |
| 4 | **Yes** | Reasoning tokens are billed and consume the budget. |
| 5 | **Yes** | Multiplies output generation. |
| 6 | **No** | Hallucination → grounding. Temperature only changes randomness. |
| 7 | **No** | Improves perceived latency only. |
| 8 | **Yes** | It's a reasoning-model control. |
</details>

---

### Question 13: Match the symptom to the parameter (drag-and-drop)

Match each symptom to the **primary** parameter or lever: **temperature · max_tokens · frequency_penalty · presence_penalty · stop · seed · stream · reasoning_effort · structured outputs**.

| Symptom | Lever |
|---|---|
| A. Answers cut mid-sentence (`finish_reason: length`) | ? |
| B. Same phrase repeated over and over | ? |
| C. Need repeatable runs for A/B prompt testing | ? |
| D. UI feels slow; text appears all at once at the end | ? |
| E. Downstream parser needs strictly valid schema | ? |
| F. Reasoning model is too slow/expensive on simple tasks | ? |
| G. Output too random for classification | ? |
| H. Generation should end at a delimiter | ? |

<details>
<summary>Answer</summary>

| Symptom | Lever |
|---|---|
| A | **max_tokens** (`max_completion_tokens` on reasoning models) |
| B | **frequency_penalty** |
| C | **seed** (+ identical params, monitor `system_fingerprint`) |
| D | **stream** |
| E | **structured outputs** (JSON schema) |
| F | **reasoning_effort** (lower) |
| G | **temperature** (lower) |
| H | **stop** |
</details>

---

### Question 14: Parameters vs the right layer (Select TWO)

A GPT-style support bot (a) gives outdated return-policy details and (b) is sometimes too chatty. Which TWO changes are MOST appropriate?

A. Add **grounding/RAG** with the current policy  
B. Set `temperature=0` to fix outdated facts  
C. Add instructions for concise answers and set a sensible **max_tokens**  
D. Set `presence_penalty=2` to fix outdated facts  
E. Increase `n`

<details>
<summary>Answer</summary>

### ✅ A and C

- Outdated facts → **RAG**. Verbosity → **instructions + output cap**.
- **B, D ❌** Parameters can't supply new facts.
- **E ❌** Irrelevant.
</details>

---

## 2. Mini Case Study: Tailwind Logistics

### Background

Tailwind Logistics runs several AI features on Microsoft Foundry.

1. **Shipment-label extraction** (GPT-style model): strict JSON, no commentary.
2. **Marketing copy generator**: creative, but it keeps repeating phrases.
3. **Customer FAQ bot (RAG)**: factual; answers should be about 3 sentences.
4. **Regression test harness**: runs the same 500 prompts after every prompt edit and needs outputs as repeatable as possible.
5. **Route-planning assistant** on a **reasoning model**: the existing code sends `temperature`, `top_p`, `max_tokens` and fails with HTTP 400. After a first fix, some answers come back empty.
6. **Chat UI**: users complain it feels slow even though total generation time is acceptable.

### Case Q1: Label extraction

Best configuration?

A. Temperature 1.5 and `n=5`  
B. **Low temperature, JSON schema/structured outputs, modest max_tokens**  
C. High presence_penalty  
D. Stream with no schema

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q2: Marketing copy repetition

Best adjustment?

A. Set temperature to 0  
B. Add a modest **frequency_penalty** (and optionally **presence_penalty**), and tune temperature/top_p (one, not both)  
C. Set max_tokens=1  
D. Switch to an embedding model

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q3: FAQ bot

Which TWO belong in the configuration?

A. Low temperature  
B. A `max_tokens` sized to the expected 3-sentence answers, plus grounded-only instructions  
C. High temperature for variety  
D. `n=10`

<details><summary>Answer</summary>

### ✅ A and B
</details>

### Case Q4: Regression harness

Best approach?

A. Fixed `seed`, identical other parameters, low temperature, log `system_fingerprint`, and treat results as best-effort repeatable  
B. Random seeds  
C. Increase `n`  
D. Change the prompt along with the seed

<details><summary>Answer</summary>

### ✅ A
</details>

### Case Q5: Route planner (two-step fix)

What are the correct fixes for (1) the HTTP 400 and (2) the empty answers?

A. (1) Remove `temperature` and `top_p`, replace `max_tokens` with `max_completion_tokens`; (2) **increase `max_completion_tokens` for reasoning-token headroom** and/or lower `reasoning_effort`  
B. (1) Set temperature to 1; (2) increase temperature  
C. (1) Add `seed`; (2) add `stop`  
D. (1) Switch to `system` role; (2) set `n=3`

<details><summary>Answer</summary>

### ✅ A
</details>

### Case Q6: Chat UI

A. Lower temperature  
B. **Enable streaming**  
C. Increase max_tokens  
D. Use `n=2`

<details><summary>Answer</summary>

### ✅ B
</details>

### Case Q7: Map each feature to its main lever

| Feature | Main lever |
|---|---|
| Label extraction | ? |
| Marketing copy repetition | ? |
| FAQ bot length | ? |
| Regression harness | ? |
| Route planner depth/cost | ? |
| Chat UI perceived speed | ? |

<details><summary>Answer</summary>

| Feature | Main lever |
|---|---|
| Label extraction | Low temperature + structured outputs |
| Marketing copy repetition | frequency/presence penalties |
| FAQ bot length | max_tokens + concise instructions |
| Regression harness | seed (+ identical params) |
| Route planner depth/cost | reasoning_effort (+ max_completion_tokens headroom) |
| Chat UI perceived speed | stream |
</details>

---

## 3. Exam Traps

| Trap | Wrong thinking | Right thinking |
|---|---|---|
| **Temperature-fixes-everything trap** | "Lower temperature to stop hallucination." | Temperature = randomness. Hallucination → grounding. |
| **Determinism trap** | "temperature 0 / seed = identical output always." | Reduces variability / best effort only. |
| **Both-knobs trap** | "Set temperature and top_p both low." | Adjust one, not both. |
| **max_tokens trap** | "max_tokens = how much the model reads." | It caps **output**. Prompt + output must fit the context window. |
| **Truncation trap** | "Cut-off answer → temperature issue." | `finish_reason: length` → raise the cap or shorten the answer. |
| **Reasoning-parameter trap** | "Keep the same parameters when switching to a reasoning model." | Remove temperature/top_p/penalties, use `max_completion_tokens` and `reasoning_effort`. |
| **Hidden-token trap** | "Reasoning tokens are free/invisible to budget." | They are billed and count toward the completion budget. |
| **Penalty mix-up trap** | "frequency and presence are the same." | Frequency scales with repetition count. Presence is a one-time penalty for appearing. |
| **Streaming trap** | "Streaming makes generation faster." | Perceived latency only. |
| **n trap** | "n=5 gives better quality at no cost." | Multiplies tokens and cost. |
| **429 trap** | "Oversized max_tokens is harmless." | It inflates the TPM estimate and can trigger 429s. |
| **Security trap** | "Low temperature prevents prompt injection." | Needs layered security controls. |
| **Default-value trap** | "Send the default value to be safe." | Some models reject the parameter entirely. Omit it. |

---

## 4. Decision Table

| Symptom / requirement | Lever |
|---|---|
| Deterministic-leaning, factual, extraction, classification | Low temperature (or low top_p, not both) |
| Creative / brainstorming | Higher temperature (or top_p) |
| Answer cut off | Raise `max_tokens` / `max_completion_tokens` |
| Too long / costly output | Lower the cap + concise instructions |
| Repeating the same words | frequency_penalty |
| Stuck on same topics | presence_penalty |
| End at marker | stop |
| Repeatable tests | seed + identical params + `system_fingerprint` |
| See token probabilities | logprobs (not on reasoning models) |
| Faster-feeling UI | stream |
| Valid JSON / schema | Structured outputs (json_schema) |
| Compare multiple candidates | n (cost × n) |
| Hard reasoning accuracy | Reasoning model + higher `reasoning_effort` |
| Simple task on a reasoning model, cost/latency | Lower `reasoning_effort` / verbosity |
| HTTP 400 "Unsupported parameter" after model swap | Remove unsupported params, rename to `max_completion_tokens` |
| Empty answer from a reasoning model | Raise `max_completion_tokens` headroom / lower effort |
| 429 with low observed usage | Lower `max_tokens`, backoff, check assigned TPM |
| Outdated/missing facts | RAG (not a parameter) |
| Tone/scope | Instructions (not a parameter) |

---

## 5. Quick Revision Sheet

```text
GPT-STYLE MODELS
  temperature / top_p   = randomness (change ONE, not both)
  max_tokens            = output cap (prompt + output <= context window)
  frequency_penalty     = penalise repetition by COUNT
  presence_penalty      = penalise tokens that appeared AT ALL
  stop                  = end at a sequence
  seed                  = best-effort reproducible (+ system_fingerprint)
  n                     = multiple completions (cost x n)
  stream                = perceived latency, not total time
  structured outputs    = schema-valid JSON

REASONING MODELS (gpt-5 / o-series)
  NO temperature / top_p / penalties (HTTP 400)
  max_completion_tokens = reasoning + visible output
  reasoning_effort      = depth/cost/latency lever
  developer role, Responses API for tools

Parameters cannot fix: hallucination (RAG), tone/scope (instructions),
injection (layered controls), missing capability (tool/model), 429 (quota/backoff).

finish_reason: length = output cap hit
```

### Best-answer checklist

1. **GPT-style or reasoning model?** That decides which parameters even exist.
2. Is the symptom about **randomness, length, repetition, stopping, reproducibility, or format**? Pick the matching lever.
3. Is the symptom really **facts, tone, security or capability**? Then a parameter is the wrong answer.
4. Check **context-window math** (prompt + output).
5. For 429s with low observed usage, think **max_tokens estimate** and **backoff**.
6. Treat `seed` and `temperature=0` as **best-effort**, never guarantees.

---

**Next concept:** RAG / Search (same harder exam-style format)

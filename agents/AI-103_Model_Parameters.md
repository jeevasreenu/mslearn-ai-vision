# AI-103: Model Parameters

## 1. What are model parameters?

Model parameters are inference settings that control how a deployed generative AI model produces a response.

For AI-103, focus on recognizing the requirement in a scenario and selecting the correct setting.

```text
Need creativity/randomness?       -> temperature or top_p
Need shorter/longer output?       -> max completion/output tokens
Need less word repetition?        -> frequency_penalty
Need more new topics/concepts?    -> presence_penalty
Need reproducibility?             -> seed (where supported)
Need generation to stop at text?  -> stop sequence (where supported)
Need reasoning depth?             -> reasoning_effort (supported models/frameworks)
```

> Important: available parameters and supported ranges can differ by model, API, and SDK. Always distinguish the exam concept from a specific SDK's implementation.

---

# 2. Temperature

`temperature` controls randomness in token sampling.

```text
Lower temperature
      -> more focused
      -> more predictable
      -> more deterministic-like

Higher temperature
      -> more varied
      -> more random
      -> more creative
```

### Typical scenario thinking

Use lower temperature for tasks such as:

- Classification
- Information extraction
- Business-rule responses
- Technical answers where consistency matters

Use higher temperature when more variety is useful:

- Brainstorming
- Creative writing
- Marketing ideas
- Generating multiple alternative suggestions

### Example

```text
Requirement:
Generate creative product names with varied ideas.

Think:
Higher temperature
```

```text
Requirement:
Classify incidents consistently into predefined categories.

Think:
Lower temperature
```

### Exam trap

Increasing temperature does **not**:

- Add current knowledge
- Improve retrieval
- Guarantee factual accuracy
- Enforce JSON Schema

---

# 3. Top-p

`top_p` implements nucleus sampling.

Conceptually, the model considers tokens within the selected cumulative probability mass.

```text
Lower top_p
-> narrower set of likely tokens
-> more conservative output

Higher top_p
-> broader candidate set
-> potentially more varied output
```

### Simple example

Suppose candidate token probabilities are conceptually:

```text
Azure       0.50
Microsoft   0.25
Cloud       0.15
AI          0.07
Other       0.03
```

A smaller `top_p` restricts sampling to the highest-probability portion of the distribution.

### Key AI-103 rule

`temperature` and `top_p` both influence sampling variation.

A common recommendation is to tune **one rather than aggressively changing both simultaneously**, because their interaction can make behavior harder to predict.

---

# 4. Temperature vs Top-p

| Parameter | Main purpose |
|---|---|
| `temperature` | Adjust randomness of sampling |
| `top_p` | Limit sampling to a probability mass of likely tokens |

### Memorize

```text
Temperature = HOW RANDOM?
Top-p       = HOW BROAD A PROBABILITY MASS?
```

### Exam scenario

> You need more diverse responses from a generative AI application.

Possible answer:

- Increase temperature appropriately, or
- adjust top-p appropriately,

but do not automatically modify both.

---

# 5. Maximum Output / Completion Tokens

Parameters such as `max_tokens` or `max_completion_tokens` restrict how many tokens the model may generate, depending on the model/API.

```text
Input tokens + generated/reasoning tokens
             -> constrained by model/API limits
```

### Use it when

- You need to restrict response length.
- You want to control generation cost/latency exposure.
- The application expects concise responses.

### Important trap

A token is **not the same as a word**.

Therefore:

```text
100 tokens != exactly 100 words
```

### Exam scenario

> Generated answers are unnecessarily long. You want to cap the generated response.

Think:

**Maximum output/completion token setting**

Do not confuse this with temperature.

---

# 6. Frequency Penalty

`frequency_penalty` discourages tokens based on how frequently they have already appeared.

Think:

```text
Repeated words/phrases too often
          ->
Increase frequency penalty appropriately
```

### Example

Poor output:

```text
Azure AI is useful.
Azure AI is powerful.
Azure AI is flexible.
Azure AI is scalable.
```

A frequency penalty can discourage repeated token usage.

### Exam keyword

```text
Reduce repetition
Repeated phrases
Repeated tokens
```

Think:

**frequency_penalty**

---

# 7. Presence Penalty

`presence_penalty` influences whether tokens that have already appeared should be less likely to appear again, encouraging the model toward new material.

Simple exam memory:

```text
Presence penalty
-> encourage introduction of new topics/concepts

Frequency penalty
-> reduce repeated use based on frequency
```

---

# 8. Frequency Penalty vs Presence Penalty

This is a common confusion point.

| Parameter | Think |
|---|---|
| `frequency_penalty` | "You keep repeating this too much." |
| `presence_penalty` | "Move toward something new." |

### Memory trick

```text
FREQUENCY
-> How frequently has it appeared?

PRESENCE
-> Has it appeared at all?
```

---

# 9. Stop Sequences

A stop sequence tells compatible generation APIs to stop when a particular sequence is generated.

Example concept:

```text
Question: ...
Answer: ...
END
```

If `END` is configured as the stop sequence, generation can terminate when that sequence is reached.

### Use cases

- Template-based generation
- Preventing generation past a known delimiter
- Controlling completion boundaries

### Important note

Support varies by model/API. Do not assume every modern model supports every historical completion parameter.

---

# 10. Seed

A `seed` can be used in supported APIs to help obtain more reproducible sampling behavior.

Think:

```text
Same request + same configuration + same seed
-> attempt at more repeatable output
```

### Important

Do not interpret seed as an absolute guarantee that responses will always remain identical across model/backend changes.

### Exam keyword

```text
Reproducibility
Repeatable sampling
Testing
```

Think:

**seed**, if the selected model/API supports it.

---

# 11. Reasoning Effort

Some reasoning-capable models/framework integrations expose a `reasoning_effort` setting, for example levels such as:

```text
low
medium
high
```

It controls the amount of reasoning effort applied before producing the final response, subject to model/API support.

### Scenario thinking

```text
Simple task
-> lower reasoning effort may be sufficient

Complex reasoning task
-> higher reasoning effort might improve reasoning quality
```

### Trade-offs

More reasoning can affect:

- Latency
- Token usage
- Cost

### Exam trap

`reasoning_effort` is not another name for `temperature`.

```text
Temperature       -> sampling randomness
Reasoning effort  -> reasoning behavior/depth
```

---

# 12. Response Format

Some APIs expose settings such as `response_format` or structured-output schema configuration.

Do not confuse **sampling parameters** with **output-contract settings**.

```text
Need creativity?
-> temperature/top_p

Need exact structured fields?
-> structured outputs / JSON Schema
```

If downstream code requires:

```json
{
  "category": "Network",
  "severity": "High"
}
```

prefer structured-output schema enforcement rather than simply lowering temperature.

---

# 13. Model Parameters Decision Table

| Requirement | Parameter/concept |
|---|---|
| More creative/varied output | Higher temperature or appropriate top-p adjustment |
| More focused/predictable output | Lower temperature / narrower sampling |
| Restrict generated response size | Maximum output/completion tokens |
| Reduce repeated words/tokens | Frequency penalty |
| Encourage new material/topics | Presence penalty |
| Stop at predefined delimiter | Stop sequence, if supported |
| Improve reproducibility in testing | Seed, if supported |
| Control reasoning effort | Reasoning effort, if supported |
| Exact JSON contract | Structured outputs, not sampling parameters |
| Current/private knowledge | RAG, not model sampling parameters |

---

# 14. High-Value AI-103 Exam Traps

## Trap 1: Creativity

```text
Requirement:
Generate more varied marketing slogans.

Think:
Temperature / top-p
```

Do not choose embeddings or RAG unless knowledge retrieval is actually required.

---

## Trap 2: Factual Knowledge

```text
Requirement:
Answer from the company's latest private policy.
```

Wrong:

```text
Lower temperature
```

Correct concept:

```text
RAG / grounding
```

Temperature changes sampling behavior. It does not provide missing knowledge.

---

## Trap 3: Exact JSON

```text
Requirement:
Every answer must match a JSON Schema.
```

Wrong:

```text
temperature = 0
```

Correct:

```text
Structured outputs / JSON Schema
```

---

## Trap 4: Repetition

```text
Requirement:
Generated text repeats the same phrases excessively.
```

Think:

```text
frequency_penalty
```

---

## Trap 5: Response Length

```text
Requirement:
Limit generated output size.
```

Think:

```text
max output/completion tokens
```

Not:

```text
temperature
```

---

# Practice Questions

## Question 1

A generative AI application creates marketing slogans. Users complain that the suggestions are too similar and predictable.

What should you consider first?

A. Lower temperature  
B. Increase temperature appropriately  
C. Reduce maximum output tokens  
D. Increase frequency penalty only  

### Correct answer: B

**Why B is correct:** Higher temperature generally increases sampling variation and can produce more diverse responses.

**Why the others are incorrect:**

- **A:** Lower temperature generally makes output more focused and predictable.
- **C:** Token limits control output length rather than creativity.
- **D:** Frequency penalty primarily addresses repetition and is not the main creativity control.

---

## Question 2

You need an incident-classification application to produce focused, less-random responses.

Which setting is most directly relevant?

A. Increase temperature  
B. Lower temperature  
C. Increase maximum output tokens  
D. Increase presence penalty  

### Correct answer: B

**Why B is correct:** Lower temperature reduces sampling randomness.

**Why the others are incorrect:**

- **A:** Increases variation.
- **C:** Controls generated length.
- **D:** Encourages movement toward new material rather than deterministic classification.

---

## Question 3

A model repeatedly uses the same words and phrases throughout a generated response.

Which parameter is designed specifically to discourage frequently repeated tokens?

A. Frequency penalty  
B. Temperature  
C. Max completion tokens  
D. Seed  

### Correct answer: A

**Why A is correct:** Frequency penalty penalizes tokens based on how frequently they have already occurred.

**Why the others are incorrect:**

- **B:** Controls sampling randomness.
- **C:** Limits generated size.
- **D:** Relates to reproducibility where supported.

---

## Question 4

You want generated content to move toward new concepts rather than continually reuse material already introduced.

Which parameter is most relevant?

A. Presence penalty  
B. Maximum output tokens  
C. Seed  
D. Stop sequence  

### Correct answer: A

**Why A is correct:** Presence penalty discourages reuse of tokens that have already appeared and can encourage new material.

**Why the others are incorrect:**

- **B:** Controls output length.
- **C:** Helps with reproducibility.
- **D:** Terminates generation at matching sequences.

---

## Question 5

Your application must prevent model responses from growing beyond a configured generated-token budget.

Which setting should you use?

A. Temperature  
B. Top-p  
C. Maximum output/completion tokens  
D. Frequency penalty  

### Correct answer: C

**Why C is correct:** The maximum completion/output token setting caps generation according to the selected API/model semantics.

**Why the others are incorrect:**

- **A and B:** Affect sampling.
- **D:** Controls repetition behavior.

---

## Question 6

You are tuning a model's response diversity. You already changed `temperature`.

What is generally the safer approach to `top_p`?

A. Always maximize it as well  
B. Always set it to zero  
C. Avoid aggressively tuning both simultaneously unless there is a specific reason  
D. Make top-p equal to maximum output tokens  

### Correct answer: C

**Why C is correct:** Temperature and top-p both affect sampling, and their combination can make results harder to predict.

**Why the others are incorrect:**

- **A/B:** There is no universal value suitable for every task.
- **D:** The parameters represent entirely different concepts.

---

## Question 7

A downstream service requires every response to strictly match a JSON Schema.

What is the best solution?

A. Temperature = 0  
B. High frequency penalty  
C. Structured outputs using the required schema  
D. Increase top-p  

### Correct answer: C

**Why C is correct:** Schema enforcement is an output-contract problem, not a sampling problem.

---

## Question 8

A chatbot must answer questions using the latest internal HR policies.

Which configuration solves the core requirement?

A. Lower temperature  
B. Higher top-p  
C. Retrieval and grounding using the policy documents  
D. Frequency penalty  

### Correct answer: C

**Why C is correct:** The requirement is access to current private knowledge. This is a RAG/grounding scenario.

---

## Question 9

During automated tests, developers want sampling behavior to be more reproducible when the selected API supports such control.

Which parameter is relevant?

A. Seed  
B. Presence penalty  
C. Maximum completion tokens  
D. Top-p only  

### Correct answer: A

**Why A is correct:** A seed can help make sampling more reproducible when supported.

---

## Question 10

A reasoning-capable model exposes a `reasoning_effort` setting. A task requires deeper reasoning rather than greater creativity.

Which parameter should you consider?

A. Increase temperature  
B. Reasoning effort  
C. Frequency penalty  
D. Stop sequence  

### Correct answer: B

**Why B is correct:** Reasoning effort and sampling randomness are different controls. For a reasoning-depth requirement, reasoning effort is the relevant setting when supported.

---

# One-Minute Revision Sheet

```text
TEMPERATURE
Randomness / creativity
Lower -> focused
Higher -> varied

TOP_P
Nucleus sampling
Controls breadth of probability mass considered

MAX OUTPUT / COMPLETION TOKENS
Caps generated output
Token != word

FREQUENCY PENALTY
Reduce repeated-token usage
Think: "You keep repeating this."

PRESENCE PENALTY
Encourage new material
Think: "Move to something new."

STOP
Stop generation when a configured sequence appears
Model/API dependent

SEED
More reproducible sampling behavior
Model/API dependent

REASONING EFFORT
Controls reasoning effort for supported models
Not the same as temperature

STRUCTURED OUTPUTS
Exact response schema
Not solved by temperature

RAG
Current/private/external knowledge
Not solved by model sampling parameters
```

# Final Exam Decision Rule

```text
Creative?
-> temperature / top_p

Too repetitive?
-> frequency penalty

Need new topics?
-> presence penalty

Too long?
-> max output/completion tokens

Need predictable structure?
-> structured outputs

Need current knowledge?
-> RAG

Need reproducibility?
-> seed, if supported

Need deeper reasoning?
-> reasoning effort, if supported
```

## Suggested next AI-103 topic

**Embeddings, vector search, chunking, semantic search, hybrid search, and RAG**

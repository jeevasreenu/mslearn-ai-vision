# AI-103: Agent Evaluation / Monitoring (Hard Exam-Style Set)

> Scenario-based questions with close distractors, "select TWO", Yes/No, matching and ordering formats.
> Focus: **what to measure, which evaluator fits, how traces and dashboards work, and how to keep quality up after deployment.**
> Facts below come from sources retrieved in this session (listed at the end). Many evaluators carry a **preview** label, so check the current AI-103 skills outline.

## Core Facts You Must Know First

| Fact | Why it matters in questions |
|---|---|
| Observability has **three pillars**: **evaluation** (before production), **tracing** (what exactly happened in a run), **monitoring** (behavior over time) | "Which pillar solves this?" scenarios |
| Built-in **agent evaluators work like unit tests**: they take **agent messages** as input and output **Pass/Fail** (or a scaled score converted to binary by a threshold) | Output-format scenarios |
| Two best practices: **System evaluation** (end-to-end outcome) and **Process evaluation** (step-by-step execution) | Outcome vs process scenarios |
| **System evaluators:** Task Completion, Task Adherence, Intent Resolution, Task Navigation Efficiency, Customer Satisfaction | Matching scenarios |
| **Process evaluators:** Tool Call Accuracy, Tool Selection, Tool Input Accuracy, Tool Output Utilization, Tool Call Success | "Right tool, wrong parameter" scenarios |
| **Task Adherence** = did the agent's actions follow its **assigned task, rules, procedures and policy constraints** (from the system message and prior steps)? | Compliance scenarios |
| **Task Navigation Efficiency** = did tool calls match an expected sequence? **Requires ground truth** | "Needs a reference path" distractors |
| **Customer Satisfaction** = holistic satisfaction across six dimensions, on a **1-5 Likert scale** | Score-type scenarios |
| **Task Adherence guardrail** (Content Safety API) can **block** misaligned tool calls or **escalate to HITL** | Runtime-control scenarios |
| A test **dataset** = test cases (input + **expected outcome**). For tool-calling agents the expected outcome should be **verifiable system state**, not just what the agent *said* it did | Test-design scenarios |
| Evaluation lets you set **acceptance thresholds** (for example an **85% task adherence passing rate**) before release | Release-gate scenarios |
| **Tracing:** connect **Application Insights** to the project. **Server-side tracing** needs **no code changes** and works for any agent hosted in Foundry. **Client-side instrumentation** is a second step to trace your own code around the agent call | "Why are there no traces?" scenarios |
| Traces use **OpenTelemetry semantic conventions** (GenAI) and are stored in **Azure Monitor Application Insights** | Format and storage scenarios |
| To **query** traces you need **Log Analytics Reader** on the connected resource. If tables are protected, also **Privileged Monitoring Data Reader** | RBAC scenarios |
| **Agent Monitoring Dashboard** (Monitor tab, preview): **token usage, latency, success rates, evaluation outcomes** for production traffic. Needs a connected Application Insights resource | Dashboard scenarios |
| **Continuous evaluation:** evaluators run against **live production traffic** using the **same evaluator definitions** as dev and CI/CD, so results are comparable | Drift scenarios |
| **AI Red Teaming Agent** (built on **PyRIT**): automated adversarial scans, scores attack-response pairs, reports **Attack Success Rate (ASR)**. Maps to **Map / Measure / Manage** (NIST) | Safety scenarios |
| Five layers of AI observability: **technical, agent execution, safety/policy, quality, business** | "HTTP 200 but wrong outcome" scenarios |

## Evaluator Quick Reference

| Evaluator | Level | Asks | Output | Trap |
|---|---|---|---|---|
| **Task Completion** (preview) | System | Did it finish the task with a usable deliverable meeting all requirements? | Pass/Fail | Outcome only, not the steps |
| **Task Adherence** (preview) | System | Did it follow its instructions, rules and policy constraints? | Pass/Fail | Compliance, not correctness of the answer |
| **Intent Resolution** (preview) | System | Did it understand what the user actually wanted? | Scaled 1-5 to Pass/Fail | Understanding, not completing |
| **Task Navigation Efficiency** | System | Did tool calls match an expected sequence? | Pass/Fail + precision/recall/F1 | **Needs ground truth** |
| **Customer Satisfaction** (preview) | System | Holistic user satisfaction | 1-5 Likert | Six dimensions |
| **Tool Call Accuracy** | Process | Right calls with right parameters? | Scaled 1-5 to Pass/Fail | Overall tool-call quality |
| **Tool Selection** | Process | Picked the correct tools, no unnecessary ones? | Pass/Fail | Which tool, not which args |
| **Tool Input Accuracy** | Process | Parameter correctness against strict criteria | Pass/Fail | Arguments, not tool choice |
| **Tool Output Utilization** | Process | Did the agent actually use the tool result? | Pass/Fail | Ignored results |
| **Tool Call Success** | Process | Did calls run without technical errors? | Pass/Fail | Technical success, not semantic |

---

## Q1. Healthy by APM, wrong by business

A refund agent returns HTTP 200 with normal latency and no exceptions. A customer asked for a $500 refund and the agent **called the correct tool with $5,000**. Which statement is **most accurate**?

- A. The agent is healthy because every technical metric is green
- B. Traditional monitoring covers only the **technical** layer. You need **agent execution** visibility (tool calls and arguments) and **quality/policy evaluation** to catch semantically wrong behavior
- C. Increase the timeout
- D. Reduce `temperature` to zero and the problem is solved

**Answer: B**

- **B is correct.** A system can be technically healthy and semantically wrong. Tracing shows the tool call and arguments, and evaluators such as Tool Input Accuracy and Task Adherence catch the failure.
- **A is wrong.** HTTP 200 says nothing about whether the action was correct.
- **C is wrong.** There is no timeout problem.
- **D is wrong.** Lower temperature doesn't guarantee correct tool arguments.

---

## Q2. Pick the evaluator: wrong argument

In Q1's refund case you want an evaluator that **specifically checks whether the parameters passed to the tool were correct**. Which is the **best** choice?

- A. Customer Satisfaction
- B. **Tool Input Accuracy**
- C. Task Navigation Efficiency
- D. Tool Call Success

**Answer: B**

- **B is correct.** It checks parameter correctness against strict criteria (grounded values, type compliance, required parameters).
- **A is wrong.** It measures overall user satisfaction on a 1-5 scale.
- **C is wrong.** It compares tool-call sequences to a ground-truth path and needs reference data.
- **D is wrong.** The call technically **succeeded**, which is exactly why this evaluator would pass it.

---

## Q3. Pick the evaluator: policy compliance

A regulated-industry agent must **follow rules in its system message** (for example, "never issue a refund over $500 without approval"). You want to validate that the agent's actions adhere to those constraints. Which evaluator?

- A. Task Adherence
- B. Tool Call Success
- C. Customer Satisfaction
- D. Intent Resolution

**Answer: A**

- **A is correct.** Task Adherence measures whether the agent's actions follow its assigned tasks, rules, procedures and policy constraints.
- **B is wrong.** It checks for technical errors only.
- **C is wrong.** It measures user sentiment dimensions.
- **D is wrong.** It checks whether the agent understood the user's goal.

---

## Q4. Pick the evaluator: understanding the request

The agent answers politely and finishes, but users say it solved *a different problem* than the one they asked about. Which evaluator targets this first?

- A. Intent Resolution
- B. Tool Call Success
- C. Task Navigation Efficiency
- D. Tool Output Utilization

**Answer: A**

- **A is correct.** It evaluates whether the agent correctly identified and addressed what the user actually wanted.
- **B is wrong.** Technical call errors aren't the issue.
- **C is wrong.** It needs an expected path and measures sequence efficiency.
- **D is wrong.** It checks whether tool results were used. It doesn't check understanding of the request.

---

## Q5. Ground truth required

Which evaluator **requires ground truth** (an expected tool-call sequence)?

- A. Task Completion
- B. Customer Satisfaction
- C. **Task Navigation Efficiency**
- D. Task Adherence

**Answer: C**

- **C is correct.** It checks whether the agent's tool calls match an expected optimal path and reports precision, recall and F1.
- **A, B and D are wrong.** They assess the conversation or outcome without a reference sequence.

---

## Q6. Outcome vs process

A team's agent **passes** Task Completion but is slow and expensive because it calls **unneeded tools**. Which evaluation approach best exposes the cause?

- A. Rely on system evaluation only
- B. Add **process evaluation** such as **Tool Selection** (unnecessary tools) and Tool Call Accuracy
- C. Increase `max_output_tokens`
- D. Remove tracing

**Answer: B**

- **B is correct.** Process evaluators verify step-by-step execution. Tool Selection flags unnecessary tool use that an outcome-only check misses.
- **A is wrong.** An end-to-end pass can hide inefficient steps.
- **C and D are wrong.** Unrelated, and removing tracing would reduce visibility.

---

## Q7. Test dataset design (select TWO)

You are building a test dataset for a **tool-calling** agent that updates records. Which **TWO** practices fit?

- A. Include a description of what's being tested, the input, and the **expected outcome**
- B. Define the expected outcome as **verifiable system state** after the agent acts, not only what the agent said it did
- C. Use only the agent's own final text as the expected outcome
- D. Use identical test cases for all scenarios to keep it simple
- E. Skip edge cases

**Answer: A and B**

- **C is wrong.** The agent could claim success without making the change.
- **D and E are wrong.** Coverage and edge cases are what expose failures.

---

## Q8. Release gate

Your team wants a **repeatable go/no-go** before shipping a prompt change. Which approach matches Foundry guidance?

- A. Manually try three prompts
- B. Run an evaluation on a **test dataset** with evaluators, compare against a **baseline**, and set an **acceptance threshold** (for example 85% task adherence passing rate) in CI/CD
- C. Ship, then wait for complaints
- D. Compare token costs only

**Answer: B**

- **B is correct.** Evaluations catch regressions before users do, and thresholds make release decisions objective.
- **A is wrong.** It isn't systematic and misses regressions.
- **C is wrong.** Without evals, regressions surface only in production.
- **D is wrong.** Cost says nothing about quality.

---

## Q9. "No traces appear"

A team deployed a **prompt agent** in Foundry but sees nothing in the **Traces** tab. They have not connected any monitoring resource. What is the **simplest** fix?

- A. Add OpenTelemetry code to every agent call
- B. **Connect an Application Insights resource** to the project. Server-side tracing turns on automatically with no code changes
- C. Fine-tune the model
- D. Increase quota

**Answer: B**

- **B is correct.** Server-side tracing works for any agent hosted in Foundry once Application Insights is connected. Traces typically appear within minutes.
- **A is wrong.** Client-side instrumentation is a second step for tracing your own code.
- **C and D are wrong.** Unrelated.

---

## Q10. Client-side vs server-side tracing

When do you **additionally** need **client-side** instrumentation?

- A. Never. Server-side tracing covers all of your code
- B. When you want visibility into **your own application code** around the agent call (custom logic before or after it)
- C. When you want to switch off Application Insights
- D. When using a hosted agent only

**Answer: B**

- **B is correct.** Server-side tracing shows the agent's behavior. Add client-side instrumentation for your own surrounding logic.
- **A is wrong.** Server-side tracing doesn't see your app code.
- **C and D are wrong.** Neither is the stated use.

---

## Q11. Permissions to read telemetry (select TWO)

An engineer can open the Foundry project but **cannot query traces**. Which **TWO** roles may be needed?

- A. **Log Analytics Reader** on the connected Application Insights / Log Analytics resource
- B. **Privileged Monitoring Data Reader**, if the underlying tables are **protected**
- C. Billing Reader only
- D. Global Administrator only
- E. Storage Blob Data Owner

**Answer: A and B**

- **C, D and E are wrong.** They don't grant telemetry query access, and Global Admin is excessive.

---

## Q12. Drift after launch

An agent scored well in pre-release evaluation. Six weeks later, answer quality has dropped, although **no code changed**. A model update and shifted knowledge-base content are suspected. Which practice addresses this?

- A. Re-run the original test set once a year
- B. **Continuous evaluation on live production traffic**, using the **same evaluator definitions** as development, plus alerts on the Monitor dashboard
- C. Increase `top_p`
- D. Disable monitoring to save cost

**Answer: B**

- **B is correct.** Behavior shifts through model updates, prompt changes, retrieval drift and new query distributions, so evaluation must be continuous rather than episodic.
- **A is wrong.** Too infrequent.
- **C and D are wrong.** They don't detect drift.

---

## Q13. What does the Monitor dashboard show?

Which information appears in the **Agent Monitoring Dashboard**?

- A. Only GPU utilization
- B. **Token usage, latency, success rates and evaluation outcomes** for production traffic, with operational, evaluation and red-teaming views
- C. Only billing invoices
- D. Raw source code of the agent

**Answer: B**

- **B is correct.** It reads telemetry from the connected Application Insights resource. The dashboard views are marked preview.
- **A, C and D are wrong.** Not part of the dashboard.

---

## Q14. Red teaming

Before deploying a tool-using agent, a security team wants **automated adversarial probing** (prompt injection, harmful content) with a measurable **success rate of attacks**. Which tool fits?

- A. Task Navigation Efficiency evaluator
- B. **AI Red Teaming Agent** (built on PyRIT), reporting **Attack Success Rate (ASR)**
- C. Customer Satisfaction evaluator
- D. Token usage chart

**Answer: B**

- **B is correct.** It automates scans, scores attack-response pairs and produces a scorecard. It can be integrated into CI/CD for continuous red teaming.
- **A and C are wrong.** Quality evaluators, not adversarial testing.
- **D is wrong.** Operational metric only.

---

## Q15. Runtime control vs offline evaluation

You want to **stop an agent from executing an off-task tool call at runtime** (not just score it afterward) and optionally escalate to a person. Which capability fits?

- A. Customer Satisfaction evaluator
- B. **Task Adherence guardrail/signal**, which can block misaligned tool invocations or escalate to **human-in-the-loop** review
- C. A larger test dataset
- D. Tracing only

**Answer: B**

- **B is correct.** The Task Adherence signal is designed for downstream tool-invocation blocking and HITL escalation.
- **A is wrong.** It's an offline score.
- **C is wrong.** Datasets test before release and don't block at runtime.
- **D is wrong.** Tracing observes, it doesn't block.

---

## Q16. Match the need to the capability

| # | Need |
|---|---|
| 1 | See exactly which tool the agent called, with what arguments, and how long each step took |
| 2 | Pass/fail check that the agent followed its policy constraints |
| 3 | Alert when quality drops on live traffic |
| 4 | Adversarial scan scored with attack success rate |
| 5 | Verify the agent's tool-call sequence against a known optimal path |

Options: **(a)** AI Red Teaming Agent, **(b)** Task Adherence evaluator, **(c)** Task Navigation Efficiency evaluator, **(d)** Tracing (Application Insights, OpenTelemetry), **(e)** Continuous evaluation and monitoring

**Answer:** 1-d, 2-b, 3-e, 4-a, 5-c

---

## Q17. Yes / No statements

| # | Statement | Answer |
|---|---|---|
| 1 | Built-in agent evaluators take agent messages as input and output pass/fail results (scaled scores are converted by thresholds) | **Yes** |
| 2 | Server-side tracing requires code changes in every agent | **No** |
| 3 | A tool call that succeeds technically can still be the wrong action | **Yes** |
| 4 | Task Navigation Efficiency can run without any expected sequence | **No** |
| 5 | Continuous evaluation reuses the same evaluator definitions as development | **Yes** |
| 6 | Traces in Foundry are stored in Azure Monitor Application Insights using OpenTelemetry conventions | **Yes** |

**Why:** 1. They act like unit tests. 2. Connect Application Insights. No code is needed for server-side tracing. 3. Tool Call Success checks only technical errors. 4. It needs ground truth. 5. Comparable results across environments. 6. That is the storage and format.

---

## Q18. Ordering: closing the quality loop

Order the steps for a mature evaluation and monitoring cycle.

1. Define a **dataset** and choose **evaluators**
2. Run evaluations and set **acceptance thresholds**
3. Deploy with **tracing** connected to Application Insights
4. Run **continuous evaluation** on live traffic and alert on drops
5. Use **traces** and failed cases to diagnose, fix, and re-evaluate

**Answer: 1 -> 2 -> 3 -> 4 -> 5**

---

## Rapid-Fire Cheat Sheet

| If you see... | Think... |
|---|---|
| Pillars of observability | Evaluation, tracing, monitoring |
| Evaluators behave like... | Unit tests, with pass/fail |
| End-to-end outcome vs step-by-step | System vs process evaluation |
| Followed policy and system-message rules | Task Adherence |
| Understood what the user wanted | Intent Resolution |
| Finished with a usable deliverable | Task Completion |
| Tool-call sequence vs optimal path | Task Navigation Efficiency (needs ground truth) |
| Wrong tool args | Tool Input Accuracy |
| Unneeded tools | Tool Selection |
| Overall tool-call quality | Tool Call Accuracy |
| Technical errors in calls | Tool Call Success |
| User sentiment, 1-5 | Customer Satisfaction |
| No traces | Connect Application Insights |
| Trace your own code too | Client-side instrumentation |
| Can't query traces | Log Analytics Reader (+ Privileged Monitoring Data Reader if protected) |
| Quality drifts with no code change | Continuous evaluation on live traffic |
| Token, latency, success-rate view | Agent Monitoring Dashboard |
| Adversarial testing with ASR | AI Red Teaming Agent (PyRIT) |
| Block off-task tool calls at runtime | Task Adherence guardrail (+ HITL) |
| HTTP 200 but business failure | Add agent-execution, quality and policy layers |

## Memory Aid

```text
BEFORE ship : EVALUATE  (dataset + evaluators + thresholds, CI/CD)
WHILE running: TRACE    (App Insights + OpenTelemetry: what did it do?)
OVER time    : MONITOR  (dashboard + continuous evaluation + alerts)
ATTACK       : RED TEAM (PyRIT, Attack Success Rate)
BLOCK        : Task Adherence guardrail -> block or escalate to a human

SYSTEM  = did it get the right outcome?  (Completion, Adherence, Intent, Navigation, Satisfaction)
PROCESS = did it take the right steps?   (Tool Call Accuracy / Selection / Input / Output / Success)
```

## Sources Used (retrieved this session)

- Microsoft Learn: Agent evaluators for generative AI (system vs process evaluators, pass/fail output, preview status)
- Microsoft Learn: Agentic Workflows Task Adherence (preview) (blocking and HITL escalation)
- Microsoft Learn: Evaluate your AI agents (acceptance thresholds, rubric evaluator)
- Microsoft Learn: Set up tracing in Microsoft Foundry (server-side vs client-side, Application Insights, roles)
- Microsoft Learn: Monitor agents with the Agent Monitoring Dashboard (metrics, continuous evaluation)
- Microsoft Learn: AI Red Teaming Agent (PyRIT, ASR, NIST Map/Measure/Manage)
- Microsoft Foundry Blog and Community Hub: Evaluating AI Agents practical guide; Monitoring and Observability in Microsoft Foundry (continuous evaluation, drift)
- Microsoft Azure Architecture Blog: Foundry Observability (five layers, refund scenario)
- Microsoft Mechanics: Automate evaluations (Task Adherence guardrail, Analyze Results)
- Secondary: GetHandsOn.ai evaluator list (Tool Selection, Tool Input Accuracy, etc.), Jannik Reinhard and DZone observability posts. The per-evaluator preview versus GA labels change often, so verify them against the current Learn pages.

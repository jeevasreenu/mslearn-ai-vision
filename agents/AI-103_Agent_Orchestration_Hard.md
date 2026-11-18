# AI-103: Agent Orchestration (Hard Exam-Style Set)

> Scenario-based questions with close distractors, "select TWO", Yes/No, matching and ordering formats.
> This topic builds on *Single vs Multi-Agent*. Here the focus is **how** multiple agents are coordinated.

## Core Facts You Must Know First

| Fact | Why it matters in questions |
|---|---|
| Use the **lowest complexity** that reliably works: direct model call -> single agent with tools -> multi-agent orchestration | "Do we even need orchestration?" scenarios |
| Five built-in patterns (Agent Framework): **Sequential, Concurrent, Handoff, Group Chat, Magentic** | Pattern-selection scenarios |
| **Sequential**: agents run one after another. By default each agent consumes the **previous agent's full conversation** (input + response messages). You can configure it to consume **only the previous agent's response messages** | Context-bloat / noisy-input scenarios |
| **Concurrent**: every participant gets the **same input** and responds **independently**; the workflow collects the results (a custom aggregator can combine them) | Parallel analysis, voting, speed |
| **Group chat**: a **central manager** chooses who speaks next. Can pause to ask a human. Has a **max rounds** limit so discussion ends even if agents would keep talking | Debate, review, runaway-discussion scenarios |
| **Handoff**: **no manager is in charge.** Agents themselves decide to transfer control based on expertise, and specialists can hand back to triage | Dynamic routing, unknown order |
| **Magentic**: a **manager agent** keeps a **task ledger** (remaining work) and a **progress ledger** (completed steps, lessons learned), assigns work to specialists, checks progress each round, and **re-plans** when stalled. Guardrails: max round count, max stall count, max reset count | Open-ended problems, no fixed plan |
| **Human-in-the-loop**: orchestrations support **tool approval** (approval-required tools pause the workflow before execution) and **request info** | Sensitive-action scenarios |
| Orchestration builders sit **above** workflow primitives: **executors** do the work, **edges** route messages, the workflow emits **events**. Builders return ordinary workflows that you can run, stream and compose | "What are the building blocks?" scenarios |
| **Foundry multi-agent workflows**: visual (drag-and-drop) or **YAML** definition, built on Microsoft Agent Framework, for **declarative, deterministic, auditable** processes. Conditions use **Power Fx**. `Local.` variables are yours; `System.` variables are **read-only** | Foundry-specific scenarios |
| To guard against infinite tool-call loops in a single agent, set **iteration limits** | Loop scenarios |

## Pattern Comparison

| Pattern | Who decides the next step? | Parallel? | Typical use | Trap |
|---|---|---|---|---|
| **Sequential** | Fixed order (pipeline) | No | Draft -> review -> polish, document processing | Not for dynamic routing |
| **Concurrent** | Nobody. All run at once | **Yes** | Multiple perspectives, voting, speed | Agents don't build on each other's output |
| **Group chat** | **Manager** picks next speaker | No | Debate, validation, quality gate, human input | Needs a max-rounds cap |
| **Handoff** | **The agents themselves** | No | Triage -> specialist, unknown order | No central manager |
| **Magentic** | **Manager agent** with dynamic plan | Agent-driven | Open-ended, complex, no predetermined plan | Overkill for fixed flows |

---

## Q1. Sequential pipeline with noisy context

A three-stage sequential pipeline is: **Summarizer -> Classifier -> Formatter**. The Classifier performs poorly because it receives the Summarizer's entire prior conversation, including the raw input and intermediate chatter. You want each agent to see **only what the previous agent produced**. What is the best change?

- A. Switch to concurrent orchestration
- B. Configure the sequential orchestration so each agent consumes **only the previous agent's response messages**
- C. Add a fourth agent to clean the messages
- D. Increase the model temperature

**Answer: B**

- **B is correct.** By default each agent consumes the previous agent's full conversation. The orchestration can be configured to pass only the response messages.
- **A is wrong.** Concurrent agents don't consume each other's output, so the pipeline dependency is lost.
- **C is wrong.** It adds cost and latency to fix something configuration already handles.
- **D is wrong.** Temperature doesn't control what context is passed.

---

## Q2. Concurrent: what actually happens

A support-ticket workflow sends one ticket to **sentiment**, **category** and **priority** agents using concurrent orchestration. Which statement is **correct**?

- A. The category agent receives the sentiment agent's output
- B. Every participant receives the same input and responds independently; the workflow collects the results
- C. A manager agent picks one agent to answer
- D. Agents run in sequence to keep the context consistent

**Answer: B**

- **B is correct.** Concurrent is fan-out/fan-in with independent responses. A custom aggregator can combine them.
- **A is wrong.** That would be sequential.
- **C is wrong.** A manager picking speakers describes group chat.
- **D is wrong.** That contradicts "concurrent".

---

## Q3. Runaway group chat

Product, engineering, design and security agents debate a feature proposal in a group chat. The discussion keeps looping and token cost climbs. Which control **directly** prevents an endless debate?

- A. Lower the temperature
- B. Set a **maximum number of rounds** so the chat ends even if participants would continue
- C. Switch to handoff so there is no manager
- D. Add more agents to reach consensus faster

**Answer: B**

- **B is correct.** Group chat supports a max-rounds limit. The manager moderates and eventually issues a recommendation.
- **A is wrong.** It doesn't bound the number of turns.
- **C is wrong.** Handoff changes control flow and doesn't impose a global round cap.
- **D is wrong.** More agents mean more turns.

---

## Q4. Who is in charge?

A triage agent greets a customer, identifies the issue, and then **itself** decides to route to a refund agent or an order-status agent. Those specialists can send the customer **back to triage** if the request changes. There is no central coordinator. Which pattern is this?

- A. Group chat
- B. Sequential
- C. Handoff
- D. Magentic

**Answer: C**

- **C is correct.** In handoff there's no manager. Agents decide on their own to transfer control, and handing back is allowed.
- **A is wrong.** Group chat has a **manager that chooses the next speaker**.
- **B is wrong.** The order is not fixed.
- **D is wrong.** Magentic has a manager maintaining ledgers and a plan.

---

## Q5. Magentic internals (select TWO)

Which **TWO** statements correctly describe Magentic orchestration?

- A. The manager maintains a **task ledger** and a **progress ledger**
- B. It runs a fixed, predefined sequence of agents
- C. The manager can **revise the plan** when the team stops making progress
- D. Specialists decide among themselves who speaks next, with no manager
- E. Every agent must run in parallel on every round

**Answer: A and C**

- **A and C are correct.** The task ledger tracks remaining work, the progress ledger tracks completed steps and lessons learned, and the manager re-plans on stalls.
- **B is wrong.** That's sequential.
- **D is wrong.** That's handoff.
- **E is wrong.** Magentic isn't "everyone in parallel every round". The manager assigns work.

---

## Q6. Magentic guardrails

A Magentic workflow keeps retrying the same failing approach and never converges. Which configuration set provides the **built-in safeguards**?

- A. Max round count, max stall count and max reset count
- B. `top_p`, `temperature` and `max_output_tokens`
- C. Content filter severity levels
- D. Embedding dimension and chunk overlap

**Answer: A**

- **A is correct.** Round, stall and reset limits bound total rounds, how long the team may make no progress, and how many times the manager may reset its plan.
- **B is wrong.** These are sampling and output settings.
- **C is wrong.** Filters moderate content, not workflow progress.
- **D is wrong.** These belong to retrieval/RAG.

---

## Q7. Human approval before a risky action

A multi-agent workflow includes a `process_refund` tool. Policy requires a human to approve any refund **before it executes**, while the rest of the workflow continues normally. What is the best approach?

- A. Tell the agent in its instructions to "ask for approval first"
- B. Mark the tool as **approval-required** so the workflow **pauses for human review** before execution
- C. Disable the tool
- D. Run the refund agent concurrently with a second verifier agent

**Answer: B**

- **B is correct.** Orchestrations support human-in-the-loop through tool approval. Approval-required tools pause the workflow until a human responds.
- **A is wrong.** A prompt instruction isn't an enforced control.
- **C is wrong.** It removes the capability instead of governing it.
- **D is wrong.** Another agent is not human oversight.

---

## Q8. Foundry workflows or code-first?

A bank needs a **deterministic, auditable** onboarding process. Business analysts want to design it visually and developers want it stored in source control and CI/CD. Which Foundry capability fits best?

- A. Magentic orchestration, because the plan can emerge dynamically
- B. **Multi-agent workflows** in Foundry Agent Service: visual designer plus **YAML** definition
- C. A single agent with a larger system prompt
- D. Fine-tuning a model on onboarding examples

**Answer: B**

- **B is correct.** Workflows provide declarative, versionable orchestration with visual and YAML views, for predictable, auditable processes.
- **A is wrong.** Emergent planning is the opposite of deterministic.
- **C is wrong.** A single agent can't provide auditable step control.
- **D is wrong.** Fine-tuning doesn't define process flow.

---

## Q9. Workflow variables and conditions

In a Foundry workflow, you want to branch based on whether the last agent message contains the text `COMPLETED`. Which statement is **correct**?

- A. Use an IF condition written in **Power Fx** and pass the message through a `Local.` variable
- B. Overwrite `System.LastMessage` inside a Set variable node
- C. Conditions can only be written in Python
- D. Variables cannot be shared between nodes

**Answer: A**

- **A is correct.** Local variables carry values between nodes, and IF conditions use Power Fx.
- **B is wrong.** `System.` variables are **read-only**. Copy the value into a `Local.` variable instead.
- **C is wrong.** Conditions use Power Fx expressions.
- **D is wrong.** Passing variables between nodes is a core mechanic.

---

## Q10. Match scenario to pattern

| # | Scenario |
|---|---|
| 1 | Contract: extract clauses -> assess risk -> draft summary, fixed order |
| 2 | Same stock analyzed in parallel by fundamental, technical and ESG agents |
| 3 | Marketing, legal and brand agents debate and approve a campaign with a moderator |
| 4 | Billing, technical and refund specialists take over a customer request when appropriate |
| 5 | Unknown root cause incident, plan must be built and revised as findings arrive |

Options: **(a)** Sequential, **(b)** Concurrent, **(c)** Group chat, **(d)** Handoff, **(e)** Magentic

**Answer:** 1-a, 2-b, 3-c, 4-d, 5-e

---

## Q11. Yes / No statements

| # | Statement | Answer |
|---|---|---|
| 1 | Orchestration builders return ordinary workflows that can be run, streamed and composed | **Yes** |
| 2 | In group chat, agents decide the next speaker on their own with no manager | **No** |
| 3 | A direct model call is sufficient if prompt engineering solves the task | **Yes** |
| 4 | Sequential orchestration by default passes the previous agent's input and response messages to the next agent | **Yes** |
| 5 | Concurrent orchestration lets agents refine each other's answers across rounds | **No** |
| 6 | `System.` variables in Foundry workflows are read-only | **Yes** |

**Why:** 1. Builders use the same workflow model internally. 2. That is handoff. Group chat has a manager. 3. Lowest complexity that works. 4. Full conversation by default, configurable to responses only. 5. Concurrent agents answer independently. 6. Write to `Local.` variables.

---

## Q12. Anti-pattern

A team has a **fixed, four-step** document pipeline that never changes and wants to use Magentic "to be future-proof". What is the **best advice**?

- A. Proceed. Magentic is always the best pattern
- B. Use **sequential** orchestration. Magentic's dynamic planning adds cost, latency and unpredictability that a fixed pipeline doesn't need
- C. Use group chat so the agents can discuss each step
- D. Use concurrent so it's faster

**Answer: B**

- **B is correct.** Choose the simplest pattern that matches the coordination need.
- **A is wrong.** More power means more coordination overhead and failure modes.
- **C is wrong.** Discussion isn't needed for a deterministic pipeline.
- **D is wrong.** Steps depend on each other, so they can't run in parallel.

---

## Q13. Orchestrator delegating bounded tasks

In the **Microsoft Copilot harness** in Foundry Agent Service (public preview), a main agent delegates narrowly scoped work to built-in subagents while it **coordinates the final result**. Which description of this idea is correct?

- A. The subagents hold the final accountability and talk directly to the user
- B. A main agent stays in charge and **delegates bounded tasks** to subagents, then assembles the outcome
- C. It requires you to build every orchestration layer yourself
- D. It replaces tool calling entirely

**Answer: B**

- **B is correct.** The harness runs the agent loop and sandbox for you. The main agent coordinates and delegates bounded tasks.
- **A is wrong.** The main agent coordinates the result.
- **C is wrong.** The harness is a **managed** execution system.
- **D is wrong.** Connected tools (including MCP) remain part of it.

> **Preview caution:** this was announced as a public preview, so verify its status against the current AI-103 skills outline before relying on it for the exam.

---

## Q14. Long-running human approval

A hosted agent must wait for a manager's approval that may take **days**, without holding a request open or losing its place, even if the container restarts. Which approach matches the documented pause-and-resume design?

- A. Keep an HTTP request open until the human replies
- B. Use a **durable multi-turn chain** that moves to a suspended state; the next input on the **same task ID** resumes the handler
- C. Restart the agent from scratch when the human replies
- D. Store the approval in the system prompt

**Answer: B**

- **B is correct.** The chain persists between turns, so the wait can be minutes, hours or days and survives restarts. Keep only small references in metadata and store full state elsewhere.
- **A is wrong.** Long open requests are fragile.
- **C is wrong.** It loses the place.
- **D is wrong.** A prompt isn't durable workflow state.

---

## Q15. Ordering: one Magentic round

Put the manager's behavior in a sensible order.

1. Check progress after the round
2. Turn the task into a plan
3. Assign work to specialists
4. Revise the plan if the team stops moving

**Answer: 2 -> 3 -> 1 -> 4**

---

## Q16. Building blocks (select TWO)

At the **workflow layer** of Microsoft Agent Framework, which **TWO** statements are correct?

- A. **Executors** do the work
- B. **Edges** route messages between executors
- C. **Edges** perform the model inference
- D. **Events** are the only way to define agents
- E. Workflows can't be composed

**Answer: A and B**

- **C is wrong.** Edges route. Executors do the work.
- **D is wrong.** Events are emitted during execution. They don't define agents.
- **E is wrong.** Orchestrations return workflows that can be composed.

---

## Rapid-Fire Cheat Sheet

| If you see... | Think... |
|---|---|
| Fixed order, each step builds on the last | Sequential |
| Downstream agent sees too much upstream chatter | Configure responses-only context |
| Independent perspectives, speed, voting | Concurrent (+ aggregator) |
| Debate with a moderator, quality gate | Group chat |
| Endless group discussion | Max rounds |
| No manager, agents pass control | Handoff |
| Unknown plan, task ledger and progress ledger | Magentic |
| Magentic not converging | Round, stall and reset limits |
| Human must approve a risky tool | Approval-required tool |
| Deterministic, auditable, visual or YAML | Foundry multi-agent workflows |
| Branch condition in a workflow | Power Fx. `System.` is read-only, `Local.` is writable |
| Wait days for a human | Durable suspended chain, same task ID |
| Same tool called repeatedly (single agent) | Iteration limits |
| "Use Magentic for everything" | Wrong. Choose the simplest pattern that fits |

## Memory Aid

```text
SEQUENTIAL = assembly line
CONCURRENT = parallel experts, independent answers
GROUP CHAT = meeting room, manager picks the speaker, max rounds
HANDOFF    = receptionist transfers the call, no manager
MAGENTIC   = project manager with a task ledger + progress ledger

Who decides next?
  Fixed order -> Sequential | Nobody -> Concurrent | Manager -> Group chat / Magentic | Agents -> Handoff
```

## Sources Used (retrieved this session)

- Microsoft Learn, Azure Architecture Center: AI agent orchestration patterns (complexity spectrum, patterns)
- Microsoft Learn, Agent Framework: Workflow orchestrations; Sequential orchestration; Human-in-the-loop
- Microsoft Agent Framework Dev Blog: Orchestration patterns reach 1.0 (Magentic builder, executors/edges/events, guardrails)
- Microsoft Foundry Blog: Introducing multi-agent workflows in Foundry Agent Service
- Microsoft Community Hub: Orchestrating multi-agent conversations with Foundry Workflows (variables, Power Fx)
- Microsoft Learn, Foundry: Add a human-in-the-loop approval step
- Microsoft Foundry Blog: Microsoft Copilot harness in Foundry Agent Service
- Third-party summary of Agent Framework patterns (handoff, group chat, concurrent behavior and max rounds)

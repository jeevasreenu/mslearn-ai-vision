# AI-103: Single vs Multi-Agent (Hard Exam-Style Set)

> Scenario-based questions with close distractors, "select TWO", Yes/No, matching and ordering formats.

## Core Facts You Must Know First

| Fact | Why it matters in questions |
|---|---|
| Complexity spectrum: **direct model call -> single agent with tools -> multi-agent orchestration**. Use the **lowest level that reliably meets requirements** | "Over-engineering" scenarios |
| Each added level adds **coordination overhead, latency, cost and new failure modes** | Trade-off scenarios |
| A **single agent with tools** is often the right default: simpler to debug and test, still supports dynamic tool use. Set **iteration limits** to guard against infinite tool-call loops | Default-choice and loop scenarios |
| Justify multi-agent when a single agent can't reliably cope due to **prompt complexity, tool overload, or security/compliance boundaries** (also: multiple teams, expected growth, parallel specialization) | "When to split" scenarios |
| Five orchestration patterns: **Sequential, Concurrent, Group chat, Handoff, Magentic** | Pattern-selection scenarios |
| **MCP** = standard for connecting agents to **tools and context**. **A2A** = standard for **agent-to-agent** communication | Protocol scenarios |
| **Microsoft Agent Framework** = open-source SDK unifying **Semantic Kernel and AutoGen**; includes the orchestration patterns | Framework scenarios |

## The Five Orchestration Patterns

| Pattern | How it works | Choose it when | Trap |
|---|---|---|---|
| **Sequential** | Fixed linear pipeline. Each agent processes the previous agent's output | Clear dependencies, progressive refinement (draft -> review -> polish) | Not for tasks needing dynamic routing or parallelism |
| **Concurrent** | Fan-out/fan-in. Agents run **in parallel** on the same task, independently | Independent perspectives, speed, diverse output | Agents don't pass results between each other |
| **Group chat** | Agents collaborate in a **shared conversation** guided by a **chat manager** | Brainstorming, decision-making, validation / quality gates, human-in-the-loop | Mostly for discussion and review, not for mutating live systems |
| **Handoff** | **Dynamic delegation.** An agent decides to act or **pass full control** to another | The best agent is **not known upfront** (intelligent routing) | Control moves to one agent at a time. It isn't parallel |
| **Magentic** | A **manager agent builds and refines a task ledger** with tool-empowered specialists | **Open-ended, complex** problems with no predetermined plan, where agents act on external systems | Overkill for simple, well-defined flows |

---

## Q1. Over-engineering

A team builds an agent that answers HR questions from one policy knowledge base and looks up leave balance through one API. Latency and debugging effort are a concern. A colleague proposes five specialized agents (intent, retrieval, leave, policy, summarizer). What is the **best** recommendation?

- A. Adopt the five-agent design for better modularity
- B. Use a **single agent with tools** (search + API), adding iteration limits. Move to multi-agent only if prompt complexity, tool overload or security boundaries demand it
- C. Replace the agent with a direct model call and no tools
- D. Use Magentic orchestration to plan dynamically

**Answer: B**

- **B is correct.** One domain, two tools, and a stated concern for latency and debuggability point to a single agent. Use the lowest complexity that works.
- **A is wrong.** Each extra agent adds coordination, latency, cost and failure modes without a justified need.
- **C is wrong.** A direct model call has no tool access, so it can't look up leave balances or search the knowledge base.
- **D is wrong.** Magentic is for open-ended problems and is the heaviest option.

---

## Q2. When a single agent should be split

A single agent has 40 tools, a 3,000-word system prompt covering finance, HR and IT, and now confuses which tool to use. Which change is **most justified**?

- A. Increase temperature to diversify tool selection
- B. Split into **specialized agents** (for example finance, HR, IT) with a routing/orchestrator layer
- C. Add more few-shot examples to the same prompt
- D. Switch to a larger context window only

**Answer: B**

- **B is correct.** Tool overload and prompt complexity are two of the main reasons to move to multi-agent. Each specialist gets a focused prompt and a small toolset.
- **A is wrong.** Randomness doesn't improve tool selection.
- **C is wrong.** It further inflates a prompt that is already too complex.
- **D is wrong.** The problem is clarity and tool selection, not window capacity.

---

## Q3. Security and compliance boundary

A workflow reads patient records (restricted) and also writes marketing copy (unrestricted). Auditors require that the marketing component **can never access** patient-data tools. Which design satisfies this best?

- A. One agent with all tools and a system prompt saying "never use patient tools for marketing"
- B. **Separate agents** with distinct identities and tool permissions, so the marketing agent simply has no access to patient tools
- C. One agent with a higher `top_p`
- D. One agent that logs every tool call

**Answer: B**

- **B is correct.** Distinct security boundaries are a classic reason for multi-agent. Enforcement comes from **permissions**, not instructions.
- **A is wrong.** A prompt is not a security control.
- **C is wrong.** Sampling is irrelevant.
- **D is wrong.** Logging is detective, not preventive. The agent still has access.

---

## Q4. Choose the pattern: document pipeline

A contract is processed as **extract clauses -> assess risk -> draft summary -> compliance polish**. Each step needs the previous step's output, and the order never changes. Which pattern?

- A. Concurrent
- B. Sequential
- C. Handoff
- D. Group chat

**Answer: B**

- **B is correct.** Fixed order plus dependency on the previous output means a sequential pipeline.
- **A is wrong.** Concurrent suits independent work. These steps depend on each other.
- **C is wrong.** Handoff is for dynamic routing when the right agent isn't known upfront. Here the order is known.
- **D is wrong.** A shared discussion isn't needed for a deterministic pipeline.

---

## Q5. Choose the pattern: independent analysis

An investment assistant must analyze one company simultaneously from **fundamental, technical, sentiment and ESG** angles, then combine the results. The analyses don't depend on one another, and the user wants a fast response. Which pattern?

- A. Sequential
- B. Concurrent
- C. Magentic
- D. Handoff

**Answer: B**

- **B is correct.** Independent perspectives on the same input, run in parallel and aggregated (fan-out/fan-in).
- **A is wrong.** Sequential would add latency, and nothing depends on a prior step.
- **C is wrong.** There is no open-ended planning problem. The tasks are known.
- **D is wrong.** Handoff passes control to one agent at a time and isn't parallel.

---

## Q6. Choose the pattern: customer-support routing

A front-door agent receives mixed requests (billing, technical, returns). It's unknown in advance which specialist should handle each request, and the specialist should then **take over the conversation**. Which pattern?

- A. Concurrent
- B. Sequential
- C. Handoff
- D. Group chat

**Answer: C**

- **C is correct.** Handoff gives dynamic delegation with full control passed to the best-suited agent.
- **A is wrong.** Running all specialists in parallel wastes cost and confuses the user.
- **B is wrong.** There is no fixed pipeline.
- **D is wrong.** Group chat is for collaborative deliberation, not for transferring ownership of a request.

---

## Q7. Choose the pattern: quality gate

A marketing agent drafts a campaign. A legal agent, a brand agent and a human reviewer must **discuss and iteratively approve** it before release. Which pattern fits best?

- A. Sequential
- B. Concurrent
- C. Group chat (with a chat manager)
- D. Magentic

**Answer: C**

- **C is correct.** Group chat suits collaborative validation and quality gates, with a manager coordinating turns and with human-in-the-loop support.
- **A is wrong.** Sequential gives one-way refinement with no back-and-forth discussion.
- **B is wrong.** Parallel independent reviews can't iterate on each other's feedback.
- **D is wrong.** Magentic targets open-ended problems where agents take actions on systems, not a review gate.

---

## Q8. Choose the pattern: open-ended incident

A production incident has an unknown root cause. The solution plan can't be defined upfront, so agents must investigate logs, query systems, try mitigations, and have the plan **refined as new findings appear**. Which pattern?

- A. Sequential
- B. Concurrent
- C. Magentic
- D. Handoff

**Answer: C**

- **C is correct.** A manager agent builds and updates a **dynamic task ledger** while specialist agents act with tools. It fits open-ended problems with no predetermined path.
- **A is wrong.** No fixed order is known.
- **B is wrong.** Parallel analysis can't adapt the plan as results arrive.
- **D is wrong.** Handoff routes ownership. It does not maintain and refine a global plan.

---

## Q9. Select TWO: real disadvantages of multi-agent

Which **TWO** are genuine trade-offs of moving from a single agent to multi-agent?

- A. Added coordination overhead and latency
- B. Loss of ability to use tools
- C. More failure modes and harder end-to-end debugging and testing
- D. Inability to use MCP
- E. Models can no longer be changed per agent

**Answer: A and C**

- **A and C are correct.** More agents mean more messages, handoffs, state to share and places to fail.
- **B is wrong.** Each agent can use tools.
- **D is wrong.** MCP can be used by any agent.
- **E is wrong.** Different agents can use different models. That is a benefit of multi-agent.

---

## Q10. Protocol matching

Match each need to the best standard.

| # | Need |
|---|---|
| 1 | An agent must call a company database through a standard tool interface |
| 2 | An agent built in one framework must delegate a task to an agent hosted elsewhere |
| 3 | Define REST APIs the agent can call, described by a spec |

Options: **(a)** A2A, **(b)** MCP, **(c)** OpenAPI

**Answer:** 1-b, 2-a, 3-c

- **MCP** standardizes how agents connect to **tools and context**.
- **A2A** standardizes **agent-to-agent** communication across boundaries.
- **OpenAPI** describes REST APIs that an agent can invoke as tools.

---

## Q11. Infinite loops

A single tool-using agent sometimes calls the same search tool dozens of times without converging, which drives up cost. What is the **most appropriate** safeguard?

- A. Convert the system to Magentic
- B. Set **iteration / max tool-call limits** and handle the "limit reached" case gracefully
- C. Remove all tools
- D. Increase `max_output_tokens`

**Answer: B**

- **B is correct.** Architecture guidance explicitly recommends iteration limits to guard against infinite tool-call loops in single-agent designs.
- **A is wrong.** A more complex pattern adds more loop risk and doesn't fix the cause.
- **C is wrong.** It removes the capability the agent needs.
- **D is wrong.** It only lengthens the generated output.

---

## Q12. Yes / No statements

| # | Statement | Answer |
|---|---|---|
| 1 | A single agent with tools can loop through several model calls and tool invocations before answering | **Yes** |
| 2 | Multi-agent systems are always more accurate than a single agent | **No** |
| 3 | Concurrent orchestration passes each agent's result to the next agent | **No** |
| 4 | Handoff orchestration is suited to cases where the best agent is not known upfront | **Yes** |
| 5 | If prompt engineering alone solves the task, an agent is not needed | **Yes** |
| 6 | Microsoft Agent Framework unifies concepts from Semantic Kernel and AutoGen | **Yes** |

**Why:**

1. That is the standard agent loop.
2. Multi-agent adds overhead and failure modes. It is justified by need, not by default.
3. That describes sequential. Concurrent agents work independently.
4. Dynamic routing is the purpose of handoff.
5. A direct model call is the lowest complexity level.
6. Agent Framework is the successor to both.

---

## Q13. Foundry building blocks (read carefully)

Your org wants a main agent that **delegates to specialist sub-agents using natural-language routing**, without writing custom orchestration code, in Foundry. Which capability **originally** provided this?

- A. Connected agents (the main agent routes tasks to sub-agents in natural language)
- B. Fine-tuning
- C. Azure AI Search semantic ranker
- D. Content filters

**Answer: A**

- **A is correct.** Connected agents let a primary agent delegate to purpose-built subagents with no custom orchestrator or hand-coded routing.
- **B, C and D are wrong.** None of them coordinates agents.

> **Version caution:** Connected agents were a feature of the **classic** Foundry Agent Service, and Microsoft's documentation says the classic agents are being retired and recommends migrating. Newer guidance points toward **multi-agent workflows**, the **A2A tool**, and **Microsoft Agent Framework** for orchestration. Check the current AI-103 study guide and Learn pages for which one your exam version names.

---

## Q14. Single vs multi: decision table

For each scenario, choose **Single agent** or **Multi-agent**.

| # | Scenario | Answer |
|---|---|---|
| 1 | One domain, a few tools, simple lookups, small team | **Single agent** |
| 2 | Components must run under different security/compliance boundaries | **Multi-agent** |
| 3 | Several teams own different capabilities that evolve independently | **Multi-agent** |
| 4 | Single-step classification or summarization | **Direct model call** (not even an agent) |
| 5 | Strong need for the simplest, most predictable and easiest-to-debug design | **Single agent** |
| 6 | Heavy tool overload and prompt bloat, with unreliable tool selection | **Multi-agent** |

---

## Q15. Ordering: choosing an architecture

Order these decisions as a sensible design process.

1. Evaluate whether a **single agent with tools** meets requirements
2. Check whether the task is solvable with a **direct model call / prompt engineering**
3. If not reliable, identify the cause (prompt complexity, tool overload, security boundary, parallelism)
4. Pick the orchestration pattern that matches the coordination need
5. Add iteration limits, observability and evaluation

**Answer: 2 -> 1 -> 3 -> 4 -> 5**

- Start at the lowest complexity and escalate only for a justified reason.

---

## Rapid-Fire Cheat Sheet

| If you see... | Think... |
|---|---|
| Simple domain, few tools, latency and debugging matter | Single agent |
| Single-step task, no tools | Direct model call |
| 30+ tools, giant prompt, wrong tool picks | Split into specialists |
| Different security/compliance boundaries | Separate agents with separate permissions |
| Fixed order, each step depends on the last | Sequential |
| Independent analyses, speed, aggregate | Concurrent |
| Review, debate, quality gate, human in the loop | Group chat |
| Best agent unknown, specialist takes over | Handoff |
| Open-ended, plan evolves, task ledger | Magentic |
| Tool/data connection standard | MCP |
| Agent-to-agent standard | A2A |
| Same tool called repeatedly | Iteration limits |
| "Always use multi-agent for accuracy" | False. It adds overhead |

## Memory Aid

```text
Direct call  -> single step, no tools
Single agent -> default; one domain; dynamic tools
Multi-agent  -> only when prompt/tool/security/team complexity demands it

SEQUENTIAL = assembly line
CONCURRENT = parallel experts
GROUP CHAT = meeting room with a moderator
HANDOFF    = receptionist transfers the call
MAGENTIC   = project manager with a living to-do list
```

## Sources Used

- Microsoft Learn, Azure Architecture Center: AI agent orchestration patterns (complexity spectrum; sequential, concurrent, group chat, handoff, magentic)
- Microsoft Learn, Cloud Adoption Framework: Single agent or multiple agents
- Microsoft Learn: Connected agents (classic) in Foundry Agent Service, including the retirement notice for classic agents
- Microsoft Foundry Blog: Multi-agent workflows in Foundry Agent Service
- Microsoft Learn / Agent Framework docs: Agents in workflows

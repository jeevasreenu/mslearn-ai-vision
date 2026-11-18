# AI-103: Human-in-the-Loop (Hard Exam-Style Set)

> Scenario-based questions with close distractors, "select TWO", Yes/No, matching and ordering formats.
> Focus: **where a human decision is inserted, how the agent pauses and resumes, and which mechanism enforces it.**
> Facts below are grounded in sources retrieved in this session (listed at the end).

## Core Facts You Must Know First

| Fact | Why it matters in questions |
|---|---|
| **HITL** = controlled intervention points where human judgment augments AI output. Think of it as a **dynamic control layer** triggered by **risk, confidence or context**, not a manual step on everything | Design / "approval fatigue" scenarios |
| Robust pattern: **AI agent + decision gate + human oversight**. The **decision gate** is the control plane that decides *when* to involve a human. Human review is **modular**, not hardcoded | "Send to human if needed" is the weak version |
| Place approval where **business impact justifies it**: committing funds or refunds, sending **external** messages, changing **access/security settings**, sharing **sensitive data**, **deleting** records (hard to reverse), **out-of-policy exceptions** | Choosing which actions get a gate |
| Approving every minor step "simply replaces one slow process with another" | Over-gating distractors |
| **Microsoft Agent Framework (MAF):** wrap a function in **`ApprovalRequiredAIFunction`** to require approval before it executes | Code-first approval |
| In MAF, a run that needs user input **completes with a response saying what input is required**, instead of a final answer. The **caller** gets the input and passes it back in a **new run** | "Who is responsible for collecting approval?" |
| MAF types: **`ToolApprovalRequestContent`** (request) and **`ToolApprovalResponseContent`** (decision, created with approved true/false). The response is matched by **CallId** | Approval round-trip scenarios |
| **Reuse the same `AgentSession`** when sending the approval response so the interrupted run can continue | Resume scenarios |
| **AG-UI:** MAF still decides *whether* a tool needs approval. AG-UI only **transports** the request to the client and the decision back | Responsibility-split scenarios |
| **Foundry hosted agents:** a `@multi_turn_task` chain **doesn't end when a turn returns**. It moves to a **suspended** state under one **`task_id`**. The next input on the **same `task_id`** re-enters the handler with `ctx.entry_mode == "resumed"` | Long-wait approvals |
| The chain is **durable**: the wait can be minutes, hours or **days** and **survives container restarts**. Keep only **small references** in `ctx.metadata`. Store full history/artifacts in your own storage or a **framework checkpoint** | State-size scenarios |
| If you build on **LangGraph or Microsoft Agent Framework** over a **background response**, use the **framework's own interrupt and approval mechanism** | Framework scenarios |
| **MCP tool approval in Foundry:** the service pauses and emits an approval request with an **id, tool name, server label and arguments**. Your app shows it, collects the decision and **resumes** (for example using `previous_response_id`) | Tool-governance scenarios |
| Agents created in the **Foundry portal enforce MCP/knowledge-base tool approval by default**, with no UI toggle. Agents created through **SDK or REST** have an option to not require approval | "Workflow hangs forever" scenarios |
| **Foundry workflows** can contain HITL steps (approvals or clarifying questions), but are marked **preview** and **Microsoft Foundry is retiring workflows on December 1, 2026**. New orchestration should use **Microsoft Agent Framework** | Version-sensitive scenarios |
| **Copilot Studio** pattern: an agent invokes an **agent flow with multistage approval**. The outcome returns to the agent, which notifies the user | Low-code HITL |
| **Agent Governance Toolkit** (open source): a policy rule with action **`require_approval`**, named **approvers**, a timeout, and callback or **webhook** handlers (Slack/Teams/Jira). A `deny` action blocks outright | Policy-as-code approval |

## Where Does the Human Go?

| Placement | Meaning | Example |
|---|---|---|
| **Pre-action approval** | Agent proposes. Human approves **before** execution | Refund, delete, external email |
| **Clarification** | Agent asks a human for **missing input** | "Which account do you mean?" |
| **Escalation** | Agent hands off when **confidence is low** or **policy exception** | Out-of-policy expense |
| **Post-hoc review** | Human reviews logs/results **after** low-risk actions | Summaries, read-only lookups |

---

## Q1. Decision gate vs "always ask a human"

A team's agent sends **every** output to a human reviewer "just in case". Review queues are huge and reviewers approve without reading. Which redesign **best** follows the HITL pattern recommended for Foundry?

- A. Remove human review completely
- B. Add a **decision gate** that routes to a human based on **risk, confidence or context**, and let low-risk, high-confidence outputs proceed
- C. Add a second reviewer to every item
- D. Increase the agent's `max_output_tokens`

**Answer: B**

- **B is correct.** HITL works best as a dynamic control layer activated by risk, confidence or context, with human review kept modular.
- **A is wrong.** It removes control where impact is high.
- **C is wrong.** It amplifies approval fatigue.
- **D is wrong.** Unrelated.

---

## Q2. Which actions deserve approval? (select TWO)

An agent can look up order status, summarize a ticket, **issue refunds**, and **change a customer's access permissions**. Which **TWO** most justify mandatory approval?

- A. Looking up order status
- B. Summarizing a ticket for internal context
- C. Issuing refunds (commits company funds)
- D. Changing user access or security settings
- E. Formatting a table

**Answer: C and D**

- **C and D are correct.** Funds commitments and access/security changes are named high-impact approval points.
- **A, B and E are wrong.** Low-impact, reversible and read-only. Gating them only creates friction.

---

## Q3. Approval enforced in code (Microsoft Agent Framework)

A developer wants the `delete_file` tool to **never execute without human approval**, regardless of what the model decides. Which implementation is correct?

- A. Add "ask permission before deleting" to the system prompt
- B. Wrap the function in **`ApprovalRequiredAIFunction`** so the agent returns an approval request instead of executing it
- C. Lower the temperature to 0
- D. Rename the tool to `safe_delete_file`

**Answer: B**

- **B is correct.** The wrapper makes approval a property of the **tool**, so the run pauses and returns a request for the caller.
- **A is wrong.** A prompt is a request to the model, not an enforced control.
- **C is wrong.** Determinism of sampling doesn't prevent a tool call.
- **D is wrong.** A name has no effect.

---

## Q4. Who collects the approval?

In MAF, an agent run reaches an approval-required tool. Which statement is **correct**?

- A. The framework automatically asks the user and resumes without any caller code
- B. The run completes with a response indicating what input is required. The **caller** collects the decision and passes it back as part of a **new run**
- C. The tool is executed first and approval is checked afterward
- D. The agent restarts from scratch and ignores the tool

**Answer: B**

- **B is correct.** The caller is responsible for getting the input and sending it back.
- **A is wrong.** The framework surfaces the request. Your app owns the UI and the decision.
- **C is wrong.** Approval comes **before** execution.
- **D is wrong.** The session continues. It doesn't restart.

---

## Q5. Resuming the run

A client receives a `ToolApprovalRequestContent`, creates a `ToolApprovalResponseContent` and sends it, but the agent doesn't continue the interrupted run correctly. Which correction fits the documented behavior?

- A. Send the response using a **new** `AgentSession` each time
- B. **Reuse the same `AgentSession`** when sending the approval response, and match the response to the request (created from the request, with `approved` true or false)
- C. Set `approved` to a random value
- D. Delete the request first

**Answer: B**

- **B is correct.** The same session lets the client continue the interrupted run, and the response is created from the request (matched by CallId).
- **A is wrong.** A new session loses the interrupted run.
- **C and D are wrong.** They break the round-trip.

---

## Q6. AG-UI responsibility split

In an AG-UI app with a protected tool, which component **decides whether the tool requires approval**?

- A. The AG-UI client
- B. **MAF tool approval** (for example `ApprovalRequiredAIFunction`). AG-UI only **transports** the request and the decision
- C. The browser
- D. The model's temperature

**Answer: B**

- **B is correct.** AG-UI transports the approval request to the client and the decision back to the server.
- **A and C are wrong.** They display and return the decision. They don't define the policy.
- **D is wrong.** Unrelated.

---

## Q7. Approval that takes days

A hosted agent in Foundry must wait for a regional manager who may reply in **three days**. Requirements: don't hold an HTTP request open, don't lose the step, survive container restarts. Which design matches Foundry's documented pause-and-resume pattern?

- A. Poll in a `while True` loop inside one request
- B. Use a **`@multi_turn_task`** chain: the turn returns an approval request and the chain goes **suspended** under one **`task_id`**. The next input on the **same `task_id`** resumes the handler (`entry_mode == "resumed"`)
- C. Start a new `task_id` for the reply
- D. Put the pending approval in the system prompt

**Answer: B**

- **B is correct.** The chain is durable, so the wait can be arbitrarily long and survives restarts.
- **A is wrong.** It holds a request open and fails across restarts.
- **C is wrong.** A new `task_id` starts a different chain.
- **D is wrong.** A prompt isn't workflow state.

---

## Q8. What to store across the pause

During the approval turn, a developer puts the **full 200-page generated report** into `ctx.metadata` so it is available after resume. What is the better practice?

- A. Keep it. Metadata is the intended store for large artifacts
- B. Keep only a **small reference** (for example an ID or step number) in `ctx.metadata`, and store the full request/history/artifacts in **your own storage or a framework checkpoint**
- C. Store the report in the model's context window
- D. Store it in the approval summary string

**Answer: B**

- **B is correct.** Metadata should hold small watermarks that survive the pause. Large state belongs elsewhere.
- **A is wrong.** Metadata is for small references.
- **C is wrong.** A context window isn't durable storage.
- **D is wrong.** It bloats the approval message sent to the human.

---

## Q9. MCP approval UX is missing

A web app calls a Foundry agent that has an **MCP tool** with side effects. When the agent tries to call it, the chat shows an **empty assistant message**, and the next message breaks the flow. The app has no approval UI. What is the correct fix?

- A. Remove authentication from the MCP server
- B. Handle the **approval request** in the app: display the **tool name, server label and arguments**, collect approve/reject, and **resume** the response with the decision (for example using the previous response ID)
- C. Increase `max_output_tokens`
- D. Disable streaming only

**Answer: B**

- **B is correct.** The service **pauses** at a tool call requiring approval. The client must surface it and send the decision.
- **A is wrong.** It reduces security and doesn't address the missing approval handling.
- **C and D are wrong.** The stall isn't caused by output length or streaming.

> If the tool is trusted and low-risk, you may instead configure it **not** to require approval through the SDK/REST. Portal-created agents enforce approval by default.

---

## Q10. "My agent hangs forever" (portal agent)

An agent created in the Foundry **portal** uses a knowledge-base tool. Every request **stalls** waiting for approval and no one is available to click. Which statement is **most accurate**?

- A. Approval can never be changed for any agent
- B. Portal-created agents enforce this check by default. For **non-interactive** or trusted low-risk tools, **create the agent through the SDK/REST** and configure approval behavior there. Otherwise your client must handle approvals
- C. The model deployment is throttled
- D. Re-upload the knowledge base

**Answer: B**

- **B is correct.** This was the answer given in the Q&A thread: portal agents enforce approval by default with no UI toggle, and SDK/REST creation exposes the option.
- **A is wrong.** SDK/REST expose approval behavior.
- **C and D are wrong.** The stall is waiting for an approval decision, not a capacity or index problem.

> **Exam caution:** this comes from a community Q&A answer. Treat it as practical behavior, not guaranteed exam content.

---

## Q11. Workflows vs Agent Framework (version-sensitive)

A team wants to build a **new** orchestration with approval steps. A colleague suggests Foundry's **visual workflows**. According to the current Learn page, what should you do?

- A. Use Foundry workflows. They are generally available with no deprecation notice
- B. Prefer **Microsoft Agent Framework** for new orchestration. Foundry **workflows are in preview and scheduled to retire on December 1, 2026**, and a migration guide exists for existing ones
- C. Use fine-tuning for approval logic
- D. Use a routine, because routines handle approval steps

**Answer: B**

- **B is correct.** The Learn page marks workflows as preview with the retirement date, and points new builds to Agent Framework.
- **A is wrong.** It ignores the retirement notice.
- **C is wrong.** Fine-tuning doesn't implement control flow.
- **D is wrong.** Routines are for when an agent runs. Approval steps and complex state need a workflow or an agent framework.

> Workflows *can* include HITL steps such as approvals or clarifying questions, which is why older materials mention them. Check which wording your exam version uses.

---

## Q12. Policy-as-code approval

A governance team wants rules **outside the prompt**: "any `transfer` requires approval from `treasury-ops` and `compliance`; any `delete` is never allowed". Which approach matches the **Agent Governance Toolkit** pattern?

- A. Put both rules in the system prompt
- B. Define a **policy** with a rule action **`require_approval`** (with approvers) for transfers and **`deny`** for deletes, and wrap the agent function with an approval handler (callback or webhook)
- C. Rely on content filters
- D. Increase the model's context window

**Answer: B**

- **B is correct.** `require_approval` pauses and waits for a human decision. `deny` blocks outright.
- **A is wrong.** Prompts aren't enforced policy.
- **C is wrong.** Content filters moderate content, not business actions.
- **D is wrong.** Irrelevant.

> **Scope note:** this is a Microsoft open-source toolkit tutorial. Know the concept (policy rules, require_approval versus deny). It is less likely to be tested by name.

---

## Q13. Match the need to the mechanism

| # | Need |
|---|---|
| 1 | Pause one specific tool call until a person approves, in code |
| 2 | Wait days for a manager's reply, surviving restarts |
| 3 | Review an MCP tool call showing tool name, server label and arguments |
| 4 | Business-friendly multistage approval inside a low-code agent |
| 5 | Route to a human only when risk is high or confidence is low |

Options: **(a)** Decision gate, **(b)** `ApprovalRequiredAIFunction`, **(c)** Suspended `multi_turn_task` chain on one `task_id`, **(d)** Copilot Studio agent flow with approvals, **(e)** MCP tool approval request

**Answer:** 1-b, 2-c, 3-e, 4-d, 5-a

---

## Q14. Yes / No statements

| # | Statement | Answer |
|---|---|---|
| 1 | In MAF, an approval-required tool call completes the run with a request for input instead of a final answer | **Yes** |
| 2 | A suspended Foundry chain resumes when new input arrives on a **different** `task_id` | **No** |
| 3 | A durable suspended chain can wait for days and survive container restarts | **Yes** |
| 4 | Requiring approval for every read-only lookup is the recommended way to make agents safe | **No** |
| 5 | Prompts such as "ask permission first" are an enforced approval control | **No** |
| 6 | AG-UI decides which tools require approval | **No** |

**Why:** 1. The caller then supplies the decision in a new run. 2. The **same** `task_id` resumes the handler. 3. Durability is the point of the chain. 4. Approval belongs where impact justifies it. 5. Enforce in the tool, workflow or policy layer. 6. MAF decides. AG-UI transports.

---

## Q15. Ordering: a safe HITL tool call

Put the steps in the correct order.

1. Caller sends the decision back in a new run (same session)
2. Agent decides to call a protected tool
3. Framework returns an approval request instead of executing
4. Human reviews the action, arguments and likely impact
5. Tool executes if approved, or is skipped if rejected

**Answer: 2 -> 3 -> 4 -> 1 -> 5**

---

## Rapid-Fire Cheat Sheet

| If you see... | Think... |
|---|---|
| Reviewers rubber-stamping | Decision gate by risk/confidence/context |
| Which actions need a human | Funds, external messages, access changes, sensitive data, deletes, exceptions |
| Tool must never run unapproved (MAF) | `ApprovalRequiredAIFunction` |
| Run ended with "input required" | Caller collects the decision, sends it in a new run |
| Continue the interrupted run | Reuse the same `AgentSession` |
| AG-UI | Transport only. MAF decides |
| Wait minutes to days, survive restarts | `@multi_turn_task` suspended chain, same `task_id` |
| What goes in `ctx.metadata` | Small references only. Store big state elsewhere |
| MCP side-effect tool | Approval request: tool name, server label, arguments |
| Portal agent hangs on approval | Enforced by default. SDK/REST can configure it. Or handle approvals in the client |
| New orchestration with approval | Microsoft Agent Framework (Foundry workflows retire Dec 1, 2026) |
| Rules outside the prompt | Policy `require_approval` / `deny` |
| Low-code approvals | Copilot Studio agent flow with multistage approval |
| "Ask first" in the system prompt | Not a control |

## Memory Aid

```text
HITL = DECIDE (gate) -> PAUSE (approval request) -> HUMAN (review) -> RESUME (same session / same task_id) -> ACT or SKIP

Code approval : ApprovalRequiredAIFunction -> ToolApprovalRequestContent -> ToolApprovalResponseContent
Long waits    : @multi_turn_task  suspended  -> same task_id  -> entry_mode == "resumed"
Tool review   : MCP approval request = tool name + server label + arguments
Low-code      : Copilot Studio agent flow + approvals
```

## Sources Used (retrieved this session)

- Microsoft Learn: Add a human-in-the-loop approval step (Foundry hosted agents, `multi_turn_task`, suspended chain)
- Microsoft Learn: Using function tools with human in the loop approvals (Agent Framework, `ApprovalRequiredAIFunction`)
- Microsoft Learn: Human-in-the-Loop with AG-UI (Agent Framework)
- Microsoft Learn: Build a workflow in Microsoft Foundry (Preview), including the workflows retirement notice
- Microsoft Foundry Blog: When AI Should Ask for Help: Human-in-the-Loop Patterns in Microsoft Foundry (decision gate)
- Microsoft Foundry Blog: Building Human-in-the-loop AI Workflows with Microsoft Agent Framework
- Microsoft Copilot Agents Labs: Expense Claims Agent with Approvals (Human-in-the-Loop)
- Agent Governance Toolkit, Tutorial 38: Human-in-the-Loop Approval Workflows
- Microsoft Q&A threads on Foundry MCP/knowledge-base approval defaults (community answers, lower authority)
- Third-party: CPI Consulting, "How to Add Human Approval to Microsoft Foundry Agent Workflows" (list of approval-worthy actions); DevLeader and AzureGuru articles on MAF tool approval (CallId round-trip); DeepWiki page on MCP approval flow (approval request fields). These are secondary sources.

# AI-103: Microsoft Foundry Fundamentals

> Concept notes, exam comparisons, revision points, and practice questions for AI-103.
>
> Updated: November 2026

---

## 1. What is Microsoft Foundry?

Microsoft Foundry is Microsoft's unified platform for building, customizing, evaluating, deploying, observing, and governing AI applications and agents on Azure.

It brings together:

- A catalog of foundation and generative AI models
- Model deployment and inference
- AI application development
- Agent development and hosting
- Tools and knowledge connections
- Evaluation and optimization
- Tracing and production monitoring
- Responsible AI and safety controls
- Enterprise identity, networking, and governance

### Main exam idea

Microsoft Foundry is not only a model-hosting service. It supports the complete lifecycle from experimentation to production operation.

```text
Discover model -> Build app/agent -> Add tools and knowledge
-> Test -> Trace -> Evaluate -> Deploy/Publish -> Monitor -> Improve
```

---

## 2. Core Foundry Building Blocks

## 2.1 Foundry resource

A Foundry resource is an Azure resource that provides access to Foundry capabilities. It acts as an administrative and operational boundary for items such as models, projects, connections, security, and governance.

### Remember

- Created in an Azure subscription and resource group
- Associated with an Azure region
- Governed with Azure identity and access controls
- Can support development through the portal and SDKs

---

## 2.2 Foundry project

A Foundry project is a workspace used by a development team to build and manage an AI solution.

A project can organize:

- Models and deployments
- Agents and agent versions
- Connections to data and services
- Evaluation assets and results
- Traces and observability data
- Application configuration

### Why projects matter

Projects help separate applications, teams, or environments. A production design commonly uses separate projects or resources for development, testing, and production, depending on governance requirements.

### Exam trap

A project is a development and management boundary. It is not the same as an Azure subscription or resource group.

---

## 2.3 Foundry portal

The Foundry portal provides a visual environment to:

- Browse and compare models
- Create deployments
- Experiment in playgrounds
- Configure prompt-based agents
- Add tools and knowledge
- Test prompts and agents
- Run evaluations
- Inspect traces
- Monitor deployed applications

### Portal versus SDK

| Requirement | Better starting choice |
|---|---|
| Rapid exploration and testing | Foundry portal/playground |
| Repeatable automation | SDK, REST API, Azure CLI, or infrastructure as code |
| CI/CD integration | SDK/CLI/templates and pipelines |
| Interactive agent configuration | Agents playground |
| Production application code | Foundry SDK/API |

The portal and SDK are complementary. The portal is not limited to nonproduction work, but production processes should normally be repeatable and version controlled.

---

## 2.4 Foundry model catalog

The model catalog provides models from Microsoft and other supported providers.

Model categories can include:

- Large language models
- Small language models
- Reasoning models
- Multimodal models
- Embedding models
- Image-generation models
- Specialized code or industry models

### Model selection factors

Choose a model based on:

- Task quality
- Reasoning complexity
- Supported input and output modalities
- Context window
- Latency
- Throughput
- Cost
- Region availability
- Deployment type
- Safety and compliance requirements
- Required tool/function support

### Exam trap

The largest model is not automatically the best choice. A small model may be preferable for a focused, high-volume, low-latency workload.

---

## 2.5 Model deployment

A model selected from the catalog usually must be deployed before an application can invoke it through a managed endpoint.

A deployment provides:

- A callable endpoint or inference route
- A deployment name
- Capacity and quota configuration
- Version and upgrade choices
- Monitoring and access controls

### Model name versus deployment name

- **Model name:** Identifies the underlying model family/version.
- **Deployment name:** Identifies your deployed instance/configuration used by application code.

### Common exam trap

Application configuration often requires the **deployment name**, not simply the catalog model name.

---

## 3. Building with Models and Agents

## 3.1 Generative AI application

A basic generative application sends instructions and context to a model and receives generated output.

Use this pattern when:

- One model call is sufficient
- The workflow is controlled by application code
- Tool selection is deterministic
- The application does not need autonomous multistep behavior

---

## 3.2 AI agent

An agent uses a model for reasoning and combines it with instructions, tools, knowledge, and state to pursue a goal.

An agent may:

- Interpret a user's objective
- Decide which tool to call
- Retrieve knowledge
- Execute multiple steps
- Retain conversation state
- Return a final response or perform an action

### Agent building blocks

```text
Agent = Model + Instructions + Tools + Knowledge + State + Guardrails
```

### Agent versus ordinary chat application

| Basic generative app | Agent |
|---|---|
| Usually follows an application-defined flow | Can decide the next step dynamically |
| Often one or a few model calls | May perform a multistep workflow |
| Application selects tools | Agent may select tools |
| Simpler to test and control | More flexible but harder to govern |

Use the simplest architecture that satisfies the requirement.

---

## 3.3 Foundry Agent Service

Foundry Agent Service is a managed platform for building, deploying, and scaling AI agents.

Its capabilities include:

- Managed agent runtime
- Prompt-based agents
- Voice-based prompt agents
- Hosted agents
- Model access
- Conversation and lifecycle management
- Tools and toolboxes
- Versioning and publishing
- Tracing, evaluation, metrics, and monitoring
- Microsoft Entra identity and RBAC
- Content filtering and network isolation options

---

## 3.4 Agent Runtime

The Agent Runtime hosts and scales supported agents and manages operational concerns such as:

- Conversations
- Tool calls
- Agent execution
- State/lifecycle
- Scaling
- Endpoint operation

### Exam point

Choose a managed runtime when the requirement is to reduce custom hosting and lifecycle-management work.

---

## 3.5 Agent types

### Prompt-based agent

A declaratively configured agent that combines:

- A Foundry model
- Instructions
- Tools
- Natural-language prompts

Use it when you want the least infrastructure and a configuration-first experience.

### Voice-based prompt agent

A prompt-based agent optimized for real-time spoken interaction.

Use it for:

- Voice assistants
- Real-time customer support
- Spoken conversational experiences

### Hosted agent

A hosted agent packages your own agent code and framework as a container while Foundry provides managed hosting, endpoint, scaling, and identity.

Use it when:

- You need custom orchestration logic
- You use your own framework
- You require code-level control
- Declarative prompt-agent configuration is insufficient

### Quick comparison

| Requirement | Agent type |
|---|---|
| Minimal code and managed orchestration | Prompt-based agent |
| Real-time speech conversation | Voice-based prompt agent |
| Custom framework and orchestration code | Hosted agent |

---

## 4. Instructions, Knowledge, Memory, Tools, and Toolboxes

## 4.1 Instructions

Instructions define the agent's:

- Role
- Goal
- Constraints
- Response style
- Tool-use rules
- Conditions for escalation or refusal

Good instructions should clearly state what the agent must do when information is missing and when human approval is required.

---

## 4.2 Knowledge

Knowledge provides facts that ground the agent's answers.

Examples:

- Product documentation
- Company policies
- Azure AI Search indexes
- Files
- Foundry IQ knowledge bases
- Enterprise information stores

### Main purpose

Knowledge reduces dependence on a model's pretrained knowledge and supports current, private, or domain-specific answers.

---

## 4.3 Memory and state

Memory/state retains relevant information across conversation turns or workflow steps.

Examples:

- Previous user requests
- User preferences
- Intermediate workflow results
- Conversation history

### Knowledge versus memory

| Knowledge | Memory/state |
|---|---|
| External facts used for grounding | Information retained from interaction/workflow |
| Policies and manuals | Prior turns and user preferences |
| Usually retrieved from a data source | Usually associated with a thread/session/user |

---

## 4.4 Tools

Tools allow an agent to retrieve information or perform an operation.

Examples include:

- File search
- Web search
- Code Interpreter
- Custom functions
- OpenAPI tools
- MCP servers
- Azure AI Search
- Business APIs

### Security rule

A tool call generated by a model is a proposal, not automatic authorization. The solution should validate parameters, authenticate the caller, enforce authorization, and require approval for consequential actions.

---

## 4.5 Toolboxes

A toolbox is a centrally managed collection of tools that can be shared across agents through a managed MCP endpoint.

Benefits can include:

- Central authentication
- Governance
- Versioning
- Reuse across agents
- Consistent tool configuration

### Tool versus toolbox

- **Tool:** One capability an agent can invoke.
- **Toolbox:** A governed, reusable collection of tools.

---

## 4.6 Model Context Protocol (MCP)

MCP is an open protocol used to expose tools and contextual capabilities to AI applications and agents through a standardized interface.

### Why it matters

MCP can reduce custom integration work and make tool providers reusable across compatible agents and clients.

### Exam caution

MCP standardizes tool/context integration. It does not by itself replace authentication, authorization, validation, network controls, or human approval.

---

## 5. Retrieval-Augmented Generation in Foundry

RAG retrieves relevant information from an external knowledge source and supplies it to a model as context.

### Typical flow

```text
User query
  -> Create query embedding
  -> Retrieve relevant chunks
  -> Add chunks to prompt/context
  -> Model generates grounded answer
  -> Return response and citations
```

### Use RAG when

- Knowledge changes frequently
- Private organizational data is required
- Users need citations
- Answers must be grounded in documents

### RAG versus fine-tuning

| RAG | Fine-tuning |
|---|---|
| Adds retrieved facts at runtime | Adapts model behavior using training examples |
| Good for changing knowledge | Good for repeated style/task behavior |
| Can support citations | Does not naturally provide source citations |
| Update the source/index | Requires a training and deployment lifecycle |

---

## 6. Evaluation, Tracing, Monitoring, and Optimization

## 6.1 Evaluation

Evaluation measures the quality, safety, and reliability of models and agents.

Foundry evaluations can use:

- Existing test datasets
- Generated responses
- Simulated conversations
- Production traces

Common metrics include:

- Groundedness
- Relevance
- Similarity
- Coherence
- Task completion
- Content safety
- Tool-call correctness

### Turn-level versus conversation-level evaluation

- **Turn-level:** Scores an individual query-response pair.
- **Conversation-level:** Scores a complete multi-turn interaction and end-to-end outcome.

### When to evaluate

- During development
- Before deployment
- In CI/CD to detect regression
- Repeatedly against production interactions

---

## 6.2 Tracing

Tracing captures the execution path of an application or agent.

A trace may show:

- Model calls
- Prompt and response flow
- Tool calls
- Retrieval steps
- Latency
- Token usage
- Errors
- Agent decisions

### Main use

Use tracing to debug **why** an interaction behaved in a particular way.

---

## 6.3 Monitoring

Monitoring observes production health and behavior over time.

Monitor:

- Availability
- Error rates
- Latency
- Token usage
- Cost
- Safety signals
- Quality trends
- Tool failures
- Retrieval quality

### Tracing versus evaluation versus monitoring

| Capability | Main question |
|---|---|
| Tracing | What happened during this execution? |
| Evaluation | How good or safe was the output/interaction? |
| Monitoring | How is the production system behaving over time? |

---

## 6.4 Optimization

Optimization improves performance based on evidence from tests, traces, evaluations, and production measurements.

Possible improvements include:

- Better instructions
- Improved tool descriptions
- More appropriate model selection
- Better retrieval/chunking
- Lower token usage
- Reduced latency
- More reliable error handling

Do not optimize only for answer quality. Production systems also balance safety, latency, availability, and cost.

---

## 7. Agent Development Lifecycle

A practical Foundry agent lifecycle is:

1. Choose the appropriate agent type.
2. Create the agent in the portal or code.
3. Define instructions and model.
4. Add tools and knowledge.
5. Test expected and adversarial scenarios.
6. Save meaningful versions.
7. Debug with tracing.
8. Evaluate quality and safety.
9. Publish a stable agent endpoint/application.
10. Integrate it into the target application or channel.
11. Monitor production behavior.
12. Improve, version, evaluate, and republish.

### Why versioning matters

Versioning enables teams to:

- Compare prompt and tool changes
- Reproduce behavior
- Roll back a regression
- Evaluate a candidate version before release

---

## 8. Security and Governance

## 8.1 Microsoft Entra ID

Microsoft Entra ID provides identity-based authentication for users, applications, and Azure resources.

---

## 8.2 Managed identity

A managed identity allows an Azure-hosted workload to authenticate to supported Azure services without storing credentials in code.

### Preferred pattern

Use managed identity and RBAC when supported instead of embedding API keys in source code or configuration files.

---

## 8.3 Role-based access control

Azure RBAC controls which identities can perform operations at a defined scope.

Apply least privilege:

- Grant only necessary permissions
- Use the narrowest practical scope
- Separate development and production access
- Restrict publishing and administrative actions

---

## 8.4 Network isolation

Depending on supported configuration and requirements, use controls such as:

- Private endpoints
- Virtual network integration/isolation
- Firewall restrictions
- Controlled outbound access

Network isolation complements identity controls. It does not replace authentication and authorization.

---

## 8.5 Secrets

If secrets are unavoidable:

- Store them in Azure Key Vault
- Rotate them
- Never hard-code them
- Restrict access with identity and RBAC

---

## 8.6 Responsible AI

Use layered controls:

- Content filters
- Guardrails
- Input validation
- Prompt-injection defenses
- Red-team testing
- Quality and safety evaluations
- Tool authorization
- Human approval for high-impact actions
- Audit and trace data
- Production monitoring

### Important exam rule

A model's instruction to call a tool does not override organizational authorization or approval requirements.

---

## 9. Common AI-103 Exam Traps

1. **Model name vs deployment name:** Applications often use the deployment name.
2. **Evaluation vs tracing:** Evaluation scores quality; tracing explains execution.
3. **Tracing vs monitoring:** Tracing follows one execution; monitoring tracks trends over time.
4. **Knowledge vs memory:** Knowledge supplies facts; memory retains interaction state.
5. **Tool vs knowledge:** A tool performs/retrieves; knowledge grounds.
6. **RAG vs fine-tuning:** RAG is for changing/source-based knowledge; fine-tuning adapts behavior.
7. **Prompt agent vs hosted agent:** Prompt agent minimizes infrastructure; hosted agent supports custom code/frameworks.
8. **Portal vs SDK:** Portal supports exploration; SDK/automation supports repeatable production delivery.
9. **Authentication vs authorization:** Identity proves who/what; RBAC defines allowed actions.
10. **Content filter vs complete safety design:** Content filtering is one layer, not the entire governance strategy.
11. **Agent flexibility vs control:** Do not choose an agent when a deterministic workflow is sufficient.
12. **MCP vs security:** MCP standardizes connectivity but does not eliminate access-control requirements.

---

# 10. Practice Questions

## Question 1: Platform purpose

A company wants one Azure platform to compare models, build agents, evaluate quality, trace executions, and monitor deployed generative AI applications. Which platform should it use?

**A.** Azure Virtual Machines only  
**B.** Microsoft Foundry  
**C.** Azure DNS  
**D.** Azure Files only

### Correct answer

**B. Microsoft Foundry**

### Why B is correct

Microsoft Foundry combines model, application, agent, evaluation, observability, and governance capabilities for the AI development lifecycle.

### Why the other options are incorrect

- **A:** Virtual machines provide compute but not the integrated Foundry AI lifecycle.
- **C:** Azure DNS provides name resolution, not AI application development.
- **D:** Azure Files is storage and does not provide models, agents, evaluation, or tracing.

### Exam concept

Foundry is an integrated AI application and agent platform, not merely a hosting endpoint.

---

## Question 2: Project purpose

A team needs a workspace to organize deployments, agents, connections, evaluations, and traces for one AI solution. What should it create?

**A.** A Foundry project  
**B.** A DNS zone  
**C.** A storage queue only  
**D.** A local Python virtual environment only

### Correct answer

**A. A Foundry project**

### Why A is correct

A Foundry project provides a workspace and management boundary for developing an AI solution and its associated artifacts.

### Why the other options are incorrect

- **B:** A DNS zone manages DNS records.
- **C:** A queue can support messaging but does not organize the complete AI solution.
- **D:** A virtual environment manages local Python packages, not cloud AI resources.

### Exam trap

Do not confuse a Foundry project with an Azure resource group or a local development project.

---

## Question 3: Model selection

A high-volume classification workload has clear labels, modest reasoning requirements, and strict latency and cost targets. What should the team evaluate first?

**A.** The largest available reasoning model  
**B.** A suitable small language model  
**C.** An image-generation model  
**D.** A speech-synthesis model

### Correct answer

**B. A suitable small language model**

### Why B is correct

An SLM can be appropriate for focused tasks where cost, throughput, and latency are important.

### Why the other options are incorrect

- **A:** A large reasoning model may increase cost and latency without providing necessary value.
- **C:** An image-generation model solves a different task.
- **D:** Speech synthesis converts text to audio.

### Exam concept

Choose the smallest model that meets measured quality requirements.

---

## Question 4: Deployment name

A developer selected a model in the catalog and created a deployment called `support-prod`. Which value will the application commonly use to address that deployed configuration?

**A.** Only the model publisher's company name  
**B.** The deployment name `support-prod`  
**C.** The Azure subscription display name  
**D.** The resource-group location string

### Correct answer

**B. The deployment name `support-prod`**

### Why B is correct

The deployment name identifies the deployed model configuration that the application invokes.

### Why the other options are incorrect

- **A:** The publisher name does not identify the team's deployment.
- **C:** A subscription display name is not a model inference deployment identifier.
- **D:** A location string does not uniquely identify the deployment.

---

## Question 5: Prompt-based versus hosted agent

A team wants to bring its own agent framework and custom orchestration code but wants Foundry to provide managed hosting, scaling, endpoint, and identity. Which agent type should it select?

**A.** Prompt-based agent  
**B.** Hosted agent  
**C.** Embedding model  
**D.** Search indexer

### Correct answer

**B. Hosted agent**

### Why B is correct

A hosted agent supports custom code and frameworks packaged for managed hosting in Foundry.

### Why the other options are incorrect

- **A:** A prompt-based agent is configuration-first and is best when the team wants less custom orchestration.
- **C:** An embedding model creates vectors and is not an agent-hosting option.
- **D:** An indexer ingests data into a search index.

### Exam trap

The phrase **bring your own framework/code** strongly points to a hosted agent.

---

## Question 6: Voice agent

A customer-service application requires low-latency, real-time spoken conversations without the team hosting the voice orchestration. Which agent type is the best starting point?

**A.** Voice-based prompt agent  
**B.** Text embedding deployment  
**C.** Batch search indexer  
**D.** Image-generation deployment

### Correct answer

**A. Voice-based prompt agent**

### Why A is correct

A voice-based prompt agent is optimized for real-time spoken interactions and managed voice orchestration.

### Why the other options are incorrect

- **B:** Embeddings support semantic retrieval.
- **C:** An indexer performs data ingestion.
- **D:** Image generation does not provide real-time speech interaction.

---

## Question 7: Knowledge versus memory

An agent must answer questions using the latest employee policy documents. Which agent component primarily satisfies this requirement?

**A.** Conversation memory only  
**B.** A grounded knowledge source  
**C.** Higher temperature  
**D.** Longer response tokens

### Correct answer

**B. A grounded knowledge source**

### Why B is correct

A knowledge source provides current policy facts that can be retrieved and supplied to the model.

### Why the other options are incorrect

- **A:** Memory retains prior interaction information; it is not the authoritative policy repository.
- **C:** Temperature changes randomness.
- **D:** Output tokens change maximum response length.

### Exam trap

**Latest documents** indicates external knowledge/RAG, not conversation memory.

---

## Question 8: Toolbox

An organization wants several agents to reuse the same governed set of web search, file search, code execution, and custom-function tools with centralized authentication and versioning. What should it create?

**A.** A toolbox  
**B.** A larger context window only  
**C.** A separate model for each function  
**D.** A higher temperature configuration

### Correct answer

**A. A toolbox**

### Why A is correct

A toolbox centralizes a reusable set of agent tools with governance, authentication, and versioning.

### Why the other options are incorrect

- **B:** Context size does not centralize tool governance.
- **C:** Models do not replace business functions and tool endpoints.
- **D:** Temperature affects output variation.

---

## Question 9: Tracing

An agent gave a wrong answer. The developer needs to see which documents were retrieved, which tools were called, and where latency occurred in that individual execution. What should the developer inspect?

**A.** Traces  
**B.** Only the monthly Azure invoice  
**C.** A model catalog description  
**D.** DNS records

### Correct answer

**A. Traces**

### Why A is correct

Tracing exposes the end-to-end execution path, including retrieval, model calls, tool calls, errors, and latency.

### Why the other options are incorrect

- **B:** An invoice may show cost but not the execution flow.
- **C:** A catalog description explains a model but not one request's behavior.
- **D:** DNS records do not expose agent reasoning or tool execution.

### Exam concept

Tracing answers: **What happened in this execution?**

---

## Question 10: Evaluation

A team wants to compare two agent versions using a repeatable dataset and measure groundedness, relevance, safety, and task completion before publishing. What should it run?

**A.** An evaluation  
**B.** A DNS lookup  
**C.** A storage replication test only  
**D.** A temperature increase

### Correct answer

**A. An evaluation**

### Why A is correct

Evaluation applies measurable quality and safety criteria to outputs or interactions and supports version comparison.

### Why the other options are incorrect

- **B:** DNS lookup does not measure AI quality.
- **C:** Storage replication concerns availability of stored data, not response quality.
- **D:** Temperature is a generation parameter, not a measurement process.

---

## Question 11: Conversation-level evaluation

An agent must complete a five-step support process across several turns. The organization wants to measure whether the entire interaction reaches the correct outcome. Which evaluation unit should it choose?

**A.** Conversation-level evaluation  
**B.** Tokenization only  
**C.** Image-level evaluation  
**D.** A single network ping

### Correct answer

**A. Conversation-level evaluation**

### Why A is correct

Conversation-level evaluation measures an end-to-end multi-turn outcome such as task completion.

### Why the other options are incorrect

- **B:** Tokenization does not measure workflow success.
- **C:** The scenario concerns a multi-turn agent interaction.
- **D:** A ping measures connectivity, not application quality.

---

## Question 12: Monitoring

After publishing an agent, the operations team must detect increasing latency, errors, token usage, and safety incidents over several weeks. Which capability is most directly required?

**A.** Production monitoring  
**B.** Only a one-time playground test  
**C.** A larger model regardless of measurements  
**D.** Deleting trace data immediately

### Correct answer

**A. Production monitoring**

### Why A is correct

Monitoring tracks health, usage, quality, cost, and safety trends during production operation.

### Why the other options are incorrect

- **B:** A one-time test cannot reveal production trends.
- **C:** Increasing model size does not diagnose system health.
- **D:** Removing all trace data would reduce observability and can conflict with operational requirements.

---

## Question 13: Authentication

An agent hosted on Azure must access an Azure AI Search service without storing an API key in code. What should the solution use when supported?

**A.** Managed identity with appropriate Azure RBAC  
**B.** A key committed to Git  
**C.** An anonymous public endpoint  
**D.** The user's plaintext password

### Correct answer

**A. Managed identity with appropriate Azure RBAC**

### Why A is correct

Managed identity provides Azure-managed credentials, while RBAC grants the required permissions.

### Why the other options are incorrect

- **B:** Committing keys exposes credentials.
- **C:** Anonymous access violates least-privilege security.
- **D:** User passwords should not be stored or used by the application.

### Exam concept

Managed identity handles authentication; RBAC handles authorization.

---

## Question 14: Safe tool execution

An agent can initiate vendor payments through a custom function. What is the most appropriate production design?

**A.** Execute every generated tool call without validation  
**B.** Validate parameters, enforce authorization, and require human approval before payment  
**C.** Raise the temperature so the agent explores more options  
**D.** Store finance credentials in the system prompt

### Correct answer

**B. Validate parameters, enforce authorization, and require human approval before payment**

### Why B is correct

Payments are consequential. The application must enforce deterministic security and approval controls outside the model.

### Why the other options are incorrect

- **A:** Model-generated arguments can be incorrect or maliciously influenced.
- **C:** Temperature is unrelated to authorization and would increase variation.
- **D:** Prompts are not secure secret stores.

---

## Question 15: RAG versus fine-tuning

Company procedures change weekly. An assistant must answer from the newest procedures and include citations. Which design is best?

**A.** RAG over an updated knowledge/index source  
**B.** Fine-tune after every document update as the primary knowledge solution  
**C.** Increase output-token limits  
**D.** Use conversation memory as the authoritative repository

### Correct answer

**A. RAG over an updated knowledge/index source**

### Why A is correct

RAG retrieves current content at runtime and can preserve source metadata for citations.

### Why the other options are incorrect

- **B:** Fine-tuning is not the preferred mechanism for rapidly changing facts and does not naturally provide citations.
- **C:** Output length does not add current information.
- **D:** Conversation memory is not an authoritative document repository.

---

# 11. Quick Revision Sheet

- Foundry supports the AI app and agent lifecycle from model discovery to production monitoring.
- A project organizes artifacts for an AI solution.
- The model catalog helps compare and select models.
- Application code commonly calls a deployment name.
- A prompt-based agent offers managed, configuration-first development.
- A voice-based prompt agent supports real-time spoken interaction.
- A hosted agent supports custom code and frameworks with managed hosting.
- Agent = model + instructions + tools + knowledge + state + guardrails.
- Knowledge provides facts; memory preserves interaction state.
- A tool performs an operation; a toolbox centralizes reusable governed tools.
- RAG supports current/private knowledge and citations.
- Evaluation measures quality and safety.
- Tracing explains an execution.
- Monitoring tracks production behavior over time.
- Managed identity avoids stored credentials; RBAC grants permissions.
- Sensitive tool actions require validation, authorization, and often human approval.

---

# 12. Self-Check

You are ready to move to the next topic when you can explain:

- [ ] What Microsoft Foundry provides
- [ ] Foundry resource versus project
- [ ] Model versus deployment
- [ ] Model catalog selection factors
- [ ] Basic app versus agent
- [ ] Prompt-based, voice-based, and hosted agents
- [ ] Instructions, knowledge, memory, tools, and toolboxes
- [ ] RAG versus fine-tuning
- [ ] Evaluation versus tracing versus monitoring
- [ ] Development-to-production agent lifecycle
- [ ] Managed identity and RBAC
- [ ] Why tool calls require external authorization and validation

---

# 13. Official References

- [Microsoft Foundry documentation](https://learn.microsoft.com/en-us/azure/foundry/)
- [Microsoft Foundry training](https://learn.microsoft.com/en-us/training/azure/ai-foundry)
- [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview)
- [Agent development lifecycle](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/development-lifecycle)
- [Evaluation in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)

---

## Recommended next concept

**Model selection: LLM vs SLM vs reasoning, multimodal, embedding, and generation models**

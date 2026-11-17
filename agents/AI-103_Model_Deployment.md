# AI-103: Model Deployment

> Exam-focused notes on deploying models in Microsoft Foundry, including deployment options, deployment names, capacity, quotas, regions, security, monitoring, and practice questions.

---

## 1. What Is Model Deployment?

Model deployment makes a selected AI model available to an application through an endpoint or inference API.

A deployment connects:

- A model and model version
- A deployment name
- An Azure region or deployment scope
- A deployment type
- Capacity and quota
- Authentication and authorization
- Monitoring and lifecycle settings

### Core exam rule

> Selecting a model from the catalog does not by itself make it callable. The model must be deployed using a supported deployment option and configuration.

---

## 2. Model Name vs Model Version vs Deployment Name

### Model name

Identifies the model family, such as a language, embedding, reasoning, or multimodal model.

### Model version

Identifies a specific release of the model. Versions can differ in quality, capabilities, limits, behavior, and lifecycle dates.

### Deployment name

A user-defined name assigned to the deployed model configuration. Application code commonly references this deployment name.

### Example

```text
Model family:     chat-model
Model version:    2026-xx-xx
Deployment name:  support-prod
```

### Exam trap

If an SDK parameter asks for the deployed model identifier, the expected value may be the **deployment name**, not simply the catalog model name.

---

## 3. Main Deployment Options

The exact choices depend on the model and current Microsoft Foundry availability.

## 3.1 Serverless API deployment

A serverless API deployment provides managed inference without requiring the team to manage the underlying compute infrastructure.

### Choose it when

- Rapid deployment is required
- The team wants minimal infrastructure management
- Usage is variable
- The selected model supports serverless deployment
- Consumption-based access is suitable

### Benefits

- Faster setup
- Managed scaling
- No direct VM management
- Convenient development and production integration

### Considerations

- Model and regional availability
- Quota and rate limits
- Pricing model
- Less control over underlying compute

---

## 3.2 Managed compute deployment

Managed compute uses dedicated or configured compute resources to host a model.

### Choose it when

- The model requires managed compute
- Custom compute configuration is needed
- Dedicated infrastructure is required
- A model is not available through serverless deployment
- The workload needs greater runtime or hosting control

### Considerations

- Compute sizing
- Provisioning time
- Scaling
- Endpoint management
- Cost while resources are allocated
- Container/runtime compatibility

---

## 3.3 Local or edge deployment

A local deployment runs a compatible model on local, edge, or on-premises infrastructure.

### Choose it when

- Offline processing is required
- Cloud connectivity is unreliable
- Data must remain local
- Very low local latency is required
- Available hardware supports the model

### Strong candidate

Small language models are often better suited to constrained local hardware than very large models.

### Important caution

Local deployment does not automatically guarantee security. The system still requires access control, patching, encryption, monitoring, and secure model distribution.

---

## 4. Deployment Types and Processing Scope

Supported choices vary by model and service. Exam questions may describe global, data-zone, or regional processing requirements.

## 4.1 Global deployment

Global deployments can route inference processing across a broader Microsoft-managed geography to improve capacity and availability.

### Best fit

- Highest capacity flexibility
- No strict requirement to keep inference processing inside one region or approved data zone
- Broad production availability

### Trade-off

It may not satisfy requirements that restrict processing to a specific geography or region.

---

## 4.2 Data-zone deployment

Data-zone deployments keep inference processing within a defined geographic data zone, subject to the supported service configuration.

### Best fit

- The organization needs geographic processing boundaries
- A broader zone is acceptable, but global processing is not
- The selected model and deployment type support the required zone

---

## 4.3 Regional deployment

Regional deployments process requests in a selected Azure region when supported.

### Best fit

- Processing must remain in a particular region
- Regional availability and capacity are sufficient
- The compliance or architecture requirement is region-specific

### Exam trap

A region supporting Microsoft Foundry does not mean every model, version, deployment type, or related feature is available in that region.

---

## 5. Standard, Provisioned, and Batch Patterns

## 5.1 Standard deployment

Standard deployment is commonly used for online, real-time inference with consumption-oriented capacity and quota.

### Choose it when

- Traffic is interactive
- Usage can vary
- A general-purpose online endpoint is needed
- Provisioned throughput is unnecessary

---

## 5.2 Provisioned deployment

Provisioned deployment reserves capacity for more predictable throughput and performance.

### Choose it when

- Traffic is stable and substantial
- Predictable throughput is required
- The organization can forecast capacity
- Production performance consistency justifies reserved capacity

### Trade-offs

- Requires capacity planning
- Can cost more if underused
- Availability depends on model, region, and capacity

---

## 5.3 Batch deployment or batch inference

Batch processing is designed for asynchronous, non-interactive workloads.

### Choose it when

- Immediate responses are unnecessary
- A large dataset must be processed
- Offline evaluation or enrichment is required
- Throughput and cost matter more than interactive latency

### Example workloads

- Summarizing a document archive
- Classifying historical tickets
- Generating embeddings for a corpus
- Evaluating many prompts and responses

---

## 6. Quota, Capacity, and Rate Limits

## 6.1 Quota

Quota is the allowed service capacity assigned at a subscription, region, model, or deployment-type scope, depending on the service.

Quota does not necessarily mean the application is currently consuming that capacity. It defines an allowed ceiling or allocation boundary.

## 6.2 Capacity

Capacity is the processing capability assigned or available to a deployment.

## 6.3 Common rate-limit concepts

- Requests per minute (RPM)
- Tokens per minute (TPM)
- Concurrent requests
- Input and output token limits
- Batch-job limits

### Important relationship

A workload can hit a token limit even when its request count is low if each request contains a large prompt or generates a long answer.

---

## 7. Handling HTTP 429 Throttling

HTTP 429 generally indicates that a request exceeded an applicable rate or capacity limit.

### Recommended responses

1. Respect any retry guidance returned by the service.
2. Use exponential backoff with jitter.
3. Avoid immediate retry loops.
4. Reduce request bursts.
5. Reduce unnecessary prompt and output tokens.
6. Queue work when immediate processing is unnecessary.
7. Review quota and capacity.
8. Add controlled fallback where appropriate.

### Exam trap

Creating aggressive retries can worsen throttling. The correct pattern is controlled retry with exponential backoff and capacity-aware design.

---

## 8. Capacity Planning

Capacity planning should use measured workload characteristics.

### Collect

- Expected requests per minute
- Average and peak input tokens
- Average and peak output tokens
- Concurrent users
- Response-time target
- Retry rate
- Tool-call count
- Growth forecast

### Worked example

Assume:

- 100 requests per minute
- Average 1,500 input tokens
- Average 500 output tokens

Estimated token demand:

```text
100 × (1,500 + 500) = 200,000 tokens per minute
```

Add a reasonable peak and failure margin based on load testing rather than deploying exactly at the average.

### Important caution

The calculation estimates workload demand. Actual quota accounting and capacity units depend on the selected model and deployment type.

---

## 9. Regional Availability

Before deployment, verify:

- Model availability
- Model-version availability
- Deployment-type availability
- Regional capacity
- Subscription quota
- Data-residency requirements
- Agent or tool availability, if applicable

### Good design process

1. Identify allowed regions.
2. Check whether the required model/version is available.
3. Check whether the required deployment type is supported.
4. Confirm quota and capacity.
5. Test latency from the application's location.
6. Create a fallback or migration plan.

---

## 10. Model Lifecycle and Version Management

Models can be updated, deprecated, or retired.

### Production practices

- Track version and retirement notices
- Avoid untested automatic production changes
- Evaluate replacement versions
- Run regression and safety tests
- Maintain a rollback strategy
- Update application configuration deliberately
- Revalidate tool calling and structured output

### Exam rule

Before moving to a new model version, compare it using representative prompts and measurable quality, safety, latency, and cost criteria.

---

## 11. Resilience and High Availability

A resilient deployment may include:

- Retry with exponential backoff
- Request queuing
- Circuit-breaker logic
- Regional failover
- Alternative deployment or model fallback
- Health monitoring
- Graceful degradation

### Fallback example

```text
Primary deployment unavailable
  -> retry with backoff
  -> use approved secondary regional deployment
  -> if unavailable, queue request or return a controlled response
```

### Caution

Fallback models can behave differently. Evaluate output quality, safety, structured-output compatibility, and tool support before enabling them.

---

## 12. Security

## 12.1 Microsoft Entra ID and managed identity

When supported, use identity-based authentication rather than embedding API keys in application code.

## 12.2 Azure RBAC

Assign only the permissions needed to deploy, invoke, monitor, or administer models.

## 12.3 Network controls

Depending on service support and architecture, use:

- Private endpoints
- Virtual network controls
- Firewall restrictions
- Controlled outbound access

## 12.4 Secrets

If a secret is unavoidable:

- Store it in Azure Key Vault
- Rotate it
- Do not commit it to source code
- Restrict access using identity and RBAC

---

## 13. Monitoring a Deployment

Monitor:

- Request count
- Error rate
- HTTP 429 responses
- Latency
- Token consumption
- Cost
- Availability
- Content-safety signals
- Quality trends
- Model-version behavior

### Tracing vs monitoring

- **Tracing:** Explains a particular execution.
- **Monitoring:** Tracks deployment health and behavior over time.

---

## 14. CI/CD for Model Deployments

A deployment pipeline can manage:

- Infrastructure as code
- Environment-specific configuration
- Deployment names
- Model/version selection
- Identity and RBAC
- Network configuration
- Automated evaluation gates
- Smoke tests
- Rollback

### Recommended flow

```text
Code/config change
 -> deploy to development
 -> run functional, quality, and safety tests
 -> deploy to staging
 -> run load and regression tests
 -> approval
 -> deploy to production
 -> monitor
```

---

## 15. High-Value Decision Table

| Requirement | Strong candidate |
|---|---|
| Rapid managed inference with minimal infrastructure | Serverless API |
| Dedicated/custom model hosting | Managed compute |
| Offline or local processing | Local/edge deployment |
| Interactive variable traffic | Standard deployment |
| Stable demand and predictable throughput | Provisioned deployment |
| Large asynchronous workload | Batch processing |
| Broad capacity flexibility | Global deployment, if permitted |
| Processing restricted to an approved geographic zone | Data-zone deployment |
| Processing restricted to one supported region | Regional deployment |
| Avoid credentials in code | Managed identity and RBAC |
| HTTP 429 | Exponential backoff, traffic control, and quota review |

---

## 16. Common Exam Traps

1. Confusing the model name with the deployment name.
2. Assuming every model supports every deployment option.
3. Assuming every Foundry region supports every model and feature.
4. Treating quota as unlimited guaranteed performance.
5. Using standard deployment when predictable reserved throughput is explicitly required.
6. Using provisioned capacity for a small unpredictable workload without cost analysis.
7. Using interactive endpoints for large non-urgent batch jobs.
8. Retrying HTTP 429 immediately in a tight loop.
9. Selecting global processing when compliance requires regional or data-zone processing.
10. Hard-coding API keys instead of using managed identity where supported.
11. Updating model versions without regression evaluation.
12. Enabling a fallback model without testing behavior and API compatibility.

---

# 17. Practice Questions

## Question 1: Deployment name

A developer deploys a model with the deployment name `claims-prod`. Which value should application configuration commonly use when invoking that deployed model?

**A.** Only the publisher name  
**B.** `claims-prod`  
**C.** The Azure subscription display name  
**D.** The resource-group location

### Correct answer

**B. `claims-prod`**

### Why B is correct

The deployment name identifies the configured model deployment that the application invokes.

### Why the other options are incorrect

- **A:** A publisher name does not identify the organization's deployment.
- **C:** A subscription display name is not an inference deployment identifier.
- **D:** A region does not uniquely identify a deployment.

---

## Question 2: Minimal infrastructure

A team wants to deploy a supported catalog model quickly without managing virtual machines or model-serving containers.

**A.** Serverless API deployment  
**B.** Self-managed virtual-machine cluster  
**C.** Local deployment only  
**D.** DNS zone

### Correct answer

**A. Serverless API deployment**

### Why A is correct

Serverless deployment provides managed inference and removes direct compute-management work.

### Why the other options are incorrect

- **B:** Requires more infrastructure management.
- **C:** Does not satisfy the stated desire for managed cloud inference.
- **D:** DNS does not host a model.

---

## Question 3: Custom hosting requirements

A model is not offered through serverless inference and requires configured compute resources.

**A.** Managed compute deployment  
**B.** Increase prompt temperature  
**C.** Create an embedding index only  
**D.** Use a DNS record as inference compute

### Correct answer

**A. Managed compute deployment**

### Why A is correct

Managed compute supports models or configurations that require provisioned hosting resources.

### Why the other options are incorrect

- **B:** Temperature does not host a model.
- **C:** An index is not a model endpoint.
- **D:** DNS provides name resolution only.

---

## Question 4: Predictable production throughput

A production assistant receives stable, high-volume traffic and requires predictable throughput.

**A.** Provisioned deployment, if supported  
**B.** A developer laptop  
**C.** Batch processing only  
**D.** Higher temperature

### Correct answer

**A. Provisioned deployment, if supported**

### Why A is correct

Provisioned capacity is designed for workloads that benefit from reserved, predictable throughput.

### Why the other options are incorrect

- **B:** A laptop is not an appropriate managed production design.
- **C:** Batch is not suitable for interactive conversations.
- **D:** Temperature changes output variation, not throughput allocation.

---

## Question 5: Batch workload

A company needs to summarize two million archived records. Results are required within two days, not interactively.

**A.** Batch processing  
**B.** Real-time voice deployment  
**C.** One interactive request from a browser  
**D.** Increase maximum output tokens without batching

### Correct answer

**A. Batch processing**

### Why A is correct

The workload is large, asynchronous, and does not require immediate responses.

### Why the other options are incorrect

- **B:** Voice interaction is unrelated.
- **C:** A single interactive request is unsuitable for a large archive.
- **D:** Token limits do not create a scalable batch workflow.

---

## Question 6: Regional processing

A regulated workload requires inference processing to remain in one specific supported Azure region.

**A.** Regional deployment  
**B.** Global deployment regardless of policy  
**C.** Public anonymous endpoint  
**D.** Any model without checking availability

### Correct answer

**A. Regional deployment**

### Why A is correct

A regional deployment is the correct starting choice when processing must remain in a particular supported region.

### Why the other options are incorrect

- **B:** Global processing can violate the stated requirement.
- **C:** Anonymous access is insecure and does not enforce processing location.
- **D:** Model and deployment availability must be verified.

---

## Question 7: Region availability

A Foundry project exists in an Azure region. The team assumes every catalog model can therefore be deployed there.

Which statement is correct?

**A.** Every model is automatically available in every Foundry region.  
**B.** Model, version, deployment type, and capacity availability must be checked separately.  
**C.** Region never affects deployment.  
**D.** Quota is shared globally without constraints.

### Correct answer

**B. Model, version, deployment type, and capacity availability must be checked separately.**

### Why B is correct

Foundry service availability does not guarantee that every model and deployment configuration is available in that region.

### Why the other options are incorrect

- **A:** Availability varies.
- **C:** Region affects availability, data processing, latency, and capacity.
- **D:** Quota scope depends on the service and deployment type.

---

## Question 8: HTTP 429

An application receives HTTP 429 responses during traffic bursts.

**A.** Retry continuously without delay  
**B.** Use exponential backoff with jitter, control bursts, and review quota  
**C.** Disable authentication  
**D.** Increase temperature

### Correct answer

**B. Use exponential backoff with jitter, control bursts, and review quota**

### Why B is correct

This pattern reduces retry storms and addresses capacity or rate-limit pressure.

### Why the other options are incorrect

- **A:** Tight retries can worsen throttling.
- **C:** Authentication is unrelated and must remain enabled.
- **D:** Temperature does not increase quota.

---

## Question 9: Token limits

An application sends only 20 requests per minute but each request contains a very large prompt. It receives throttling errors.

What is the most likely explanation?

**A.** Tokens-per-minute limits can be reached even when request count is low.  
**B.** RPM is the only possible limit.  
**C.** Prompt size never affects capacity.  
**D.** Authentication always causes HTTP 429.

### Correct answer

**A. Tokens-per-minute limits can be reached even when request count is low.**

### Why A is correct

Large prompts and responses can consume substantial token capacity with relatively few requests.

### Why the other options are incorrect

- **B:** Both request and token limits may apply.
- **C:** Prompt size directly affects token consumption.
- **D:** Authentication failures normally use different status codes.

---

## Question 10: Secure authentication

An Azure-hosted application must invoke a supported model deployment without storing a key in code.

**A.** Managed identity with appropriate RBAC  
**B.** Hard-coded API key  
**C.** Developer password in the prompt  
**D.** Anonymous public access

### Correct answer

**A. Managed identity with appropriate RBAC**

### Why A is correct

Managed identity avoids embedded credentials, and RBAC grants only the required permissions.

### Why the other options are incorrect

- **B:** Hard-coded keys create secret-exposure risk.
- **C:** Prompts are not secure secret stores.
- **D:** Anonymous access violates least privilege.

---

## Question 11: Version upgrade

A new model version is available. What should the production team do before switching traffic?

**A.** Switch immediately without testing  
**B.** Run representative quality, safety, latency, cost, and compatibility evaluations  
**C.** Delete the existing deployment first  
**D.** Compare only the model name

### Correct answer

**B. Run representative quality, safety, latency, cost, and compatibility evaluations**

### Why B is correct

Model versions can change behavior and supported capabilities. Regression testing reduces production risk.

### Why the other options are incorrect

- **A:** Untested changes can cause regressions.
- **C:** Removing the current deployment first eliminates rollback.
- **D:** The name does not prove equivalent behavior.

---

## Question 12: Offline requirement

A factory must run inference during internet outages and keep sensitive input onsite.

**A.** Compatible local/edge deployment  
**B.** Cloud-only endpoint with no fallback  
**C.** Global endpoint regardless of connectivity  
**D.** Public image hosting

### Correct answer

**A. Compatible local/edge deployment**

### Why A is correct

Local deployment supports offline processing and onsite data handling when hardware and model compatibility are sufficient.

### Why the other options are incorrect

- **B:** It fails during connectivity loss.
- **C:** It still depends on connectivity.
- **D:** It does not provide model inference.

---

## Question 13: Cost optimization

A provisioned deployment is used at only 5% of its reserved capacity, and traffic is highly unpredictable.

What should the team evaluate?

**A.** Whether a standard consumption-oriented deployment is more cost effective  
**B.** Increasing provisioned capacity further  
**C.** Disabling monitoring  
**D.** Increasing every prompt's length

### Correct answer

**A. Whether a standard consumption-oriented deployment is more cost effective**

### Why A is correct

Low utilization and unpredictable demand can make reserved capacity inefficient.

### Why the other options are incorrect

- **B:** More unused capacity increases inefficiency.
- **C:** Monitoring is needed to make the decision.
- **D:** Longer prompts increase token use.

---

## Question 14: Failover

A critical application requires regional resilience.

Which design is most appropriate?

**A.** An evaluated secondary deployment with controlled failover and health monitoring  
**B.** One deployment with no retry or fallback  
**C.** An untested random model  
**D.** Store credentials in source control

### Correct answer

**A. An evaluated secondary deployment with controlled failover and health monitoring**

### Why A is correct

A tested secondary deployment supports continuity while controlling behavioral and compatibility risks.

### Why the other options are incorrect

- **B:** Provides no resilience.
- **C:** An untested fallback can produce incompatible or unsafe behavior.
- **D:** Exposes secrets and does not improve availability.

---

## Question 15: Multi-select deployment checks

Before deploying a model to production, which three items should the team verify? **Select three.**

**A.** Model/version and deployment-type availability in the required region  
**B.** Quota, capacity, and expected workload  
**C.** Security, evaluation, monitoring, and lifecycle plans  
**D.** The color of the model-provider logo  
**E.** Whether the deployment name is fashionable

### Correct answers

**A, B, and C**

### Why they are correct

- **A:** Deployment feasibility depends on supported combinations.
- **B:** Capacity must satisfy expected traffic and token demand.
- **C:** Production readiness includes security, quality, operations, and retirement planning.

### Why the other options are incorrect

- **D:** Branding has no technical relevance.
- **E:** A deployment name must be valid and manageable, not fashionable.

---

# 18. One-Minute Revision Sheet

- A selected model must be deployed before application inference.
- Application code commonly uses the deployment name.
- Serverless API minimizes infrastructure management.
- Managed compute provides more hosting control.
- Local deployment supports offline and onsite processing.
- Standard deployment fits variable interactive traffic.
- Provisioned deployment fits stable workloads requiring predictable throughput.
- Batch fits large non-interactive workloads.
- Global, data-zone, and regional choices differ in processing scope.
- Model availability varies by model, version, region, and deployment type.
- TPM and RPM are different limits.
- Handle HTTP 429 using exponential backoff, traffic control, and quota review.
- Use managed identity and RBAC where supported.
- Evaluate new model versions before production rollout.
- Monitor latency, errors, throttling, tokens, cost, safety, and quality.

---

# 19. Self-Check

- [ ] I can distinguish model name, version, and deployment name.
- [ ] I can compare serverless, managed compute, and local deployment.
- [ ] I can compare standard, provisioned, and batch processing.
- [ ] I understand global, data-zone, and regional processing choices.
- [ ] I understand RPM, TPM, quota, and capacity.
- [ ] I know how to handle HTTP 429.
- [ ] I can perform a basic token-demand estimate.
- [ ] I know why regional availability must be checked.
- [ ] I understand model-version lifecycle planning.
- [ ] I can describe secure authentication and resilient failover.

---

## Recommended Next Concept

**Prompt engineering: system instructions, few-shot examples, structured output, parameters, and prompt-injection protection.**

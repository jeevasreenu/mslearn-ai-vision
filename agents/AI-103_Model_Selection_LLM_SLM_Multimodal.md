# AI-103: Model Selection - LLM, SLM, and Multimodal Models

> Concept-wise exam notes with selection rules, comparisons, traps, and 15 practice questions.
>
> Updated: November 2026

---

# 1. Why Model Selection Matters

Model selection is the process of choosing the model that meets the application's quality requirements while satisfying constraints such as:

- Input and output modality
- Reasoning complexity
- Accuracy and task quality
- Latency
- Throughput
- Cost
- Context-window requirements
- Tool/function-calling support
- Structured-output support
- Deployment location
- Data privacy and compliance
- Regional availability
- Model lifecycle and support

## Core exam rule

> Choose the smallest and least expensive model that satisfies the measured quality, safety, latency, and capability requirements.

Do not select the largest model automatically. First identify the required capability, then compare candidate models using representative application data.

---

# 2. Model Categories

## 2.1 Large Language Model (LLM)

An LLM is a general-purpose language model trained on large amounts of data and designed to understand or generate language, code, and sometimes other modalities.

### Typical strengths

- Broad language understanding
- Complex instruction following
- Reasoning and planning
- Long-form generation
- Summarization
- Question answering
- Code generation and explanation
- Tool selection and function calling
- Handling ambiguous or diverse inputs

### Typical limitations

- Higher inference cost than smaller models
- Higher latency and compute requirements
- Can produce unsupported information
- May be unnecessary for narrow, repetitive tasks
- Requires evaluation and safety controls

### Choose an LLM when

- The task requires broad knowledge or flexible language understanding.
- Inputs are varied and difficult to predict.
- Complex reasoning or multistep planning is needed.
- The application must generate high-quality long-form content.
- The agent must understand complicated instructions and select tools.

### Avoid defaulting to an LLM when

- The task is simple classification or extraction.
- Rules can solve the problem reliably.
- A smaller model meets the tested quality threshold.
- The workload has strict edge, latency, or cost constraints.

---

## 2.2 Small Language Model (SLM)

An SLM is a compact language model optimized for efficiency. Exact parameter boundaries vary, but SLMs generally require less compute and memory than LLMs.

### Typical strengths

- Lower latency
- Lower inference cost
- Higher throughput per compute unit
- Smaller memory footprint
- Better suitability for local, edge, or on-premises execution
- Strong performance on focused tasks when properly selected or adapted

### Typical limitations

- Less broad world knowledge
- Lower performance on highly complex or ambiguous reasoning
- May need carefully designed prompts, task-specific examples, RAG, or fine-tuning
- Capability support differs by model, runtime, and deployment option

### Choose an SLM when

- The task is focused and well-defined.
- Low latency is important.
- The application handles high request volume.
- Cost must be minimized.
- The model must run on constrained hardware or locally.
- Data must remain on a device or local environment.
- Evaluation shows that the SLM meets the quality target.

### Typical SLM workloads

- Intent classification
- Routing
- Focused extraction
- Template-based generation
- Simple summarization
- Local assistance
- Domain-specific chat when combined with RAG
- Repetitive tool-selection tasks

---

## 2.3 Multimodal Model

A multimodal model processes or generates more than one type of data, such as:

- Text
- Images
- Audio
- Video

A common multimodal model accepts text and images and returns text. Other models may support audio input, voice interaction, image generation, or video generation.

### Choose a multimodal model when

- The application must answer questions about an image.
- A document's layout, chart, diagram, or visual structure matters.
- The application must compare multiple images.
- Audio or video forms part of the reasoning context.
- A conversational interface must combine text, image, or voice.

### Examples

- Analyze damage in a photograph.
- Explain a chart supplied as an image.
- Extract meaning from a screenshot.
- Generate alt text.
- Compare two product images.
- Analyze a video segment.
- Reason over audio plus text instructions.

### Common limitation

A model being multimodal does not mean that it supports every modality or every input/output combination. Always verify its model card, API, deployment type, region, and supported payloads.

---

# 3. Related Model Types You Must Distinguish

## 3.1 Reasoning model

A reasoning model is optimized for complex problem solving and multistep reasoning.

Choose it for:

- Difficult planning
- Complex mathematical or logical problems
- Deep code analysis
- Tasks where accuracy is more important than minimum latency

Do not choose it automatically for simple extraction, classification, or low-latency routing.

---

## 3.2 Embedding model

An embedding model converts text or other supported content into numeric vectors.

Use it for:

- Vector search
- Semantic similarity
- RAG retrieval
- Clustering
- Recommendation
- Duplicate detection

An embedding model does not normally generate a natural-language answer.

---

## 3.3 Image-generation model

An image-generation model creates or edits images from prompts or reference images.

Use it for:

- Text-to-image generation
- Inpainting
- Image variation
- Prompt-driven visual editing

Do not use it merely to understand an existing image. Image understanding requires a compatible multimodal understanding model.

---

## 3.4 Speech model

A speech model may provide:

- Speech-to-text
- Text-to-speech
- Speech translation
- Voice interaction

Do not assume a text LLM automatically provides production speech recognition or speech synthesis.

---

## 3.5 Domain-specific model

A domain-specific model is optimized for a specialized area, task, or industry.

Potential benefits:

- Better specialized vocabulary
- Better task accuracy
- Lower prompt complexity
- Smaller deployment footprint

It still requires evaluation with the organization's data and safety requirements.

---

# 4. LLM vs SLM vs Multimodal

| Dimension | LLM | SLM | Multimodal model |
|---|---|---|---|
| Main purpose | Broad language and reasoning | Efficient focused language tasks | Understand or generate multiple data types |
| Typical inputs | Text, sometimes other modalities | Usually text, depending on model | Text plus image/audio/video, depending on model |
| Typical cost | Higher | Lower | Varies, often higher with rich media |
| Typical latency | Higher than comparable SLM | Lower | Varies by modality and payload size |
| General knowledge | Broad | More limited | Depends on underlying model |
| Edge/local suitability | Less suitable for constrained devices | Often suitable | Depends heavily on model and runtime |
| Complex reasoning | Usually stronger | May be weaker | Depends on model class |
| High-volume focused workload | May be excessive | Strong candidate | Use only if multiple modalities are required |
| Image understanding | Only if the model explicitly supports vision | Only if supported | Primary use case for vision-capable models |

## Important point

“Multimodal” describes supported data modalities. It does not tell you whether the model is large or small. A model can be both small and multimodal, or large and multimodal.

---

# 5. A Practical Model-Selection Framework

Use this sequence in exam scenarios.

## Step 1: Identify the task

Examples:

- Generate or summarize text
- Classify intent
- Extract structured fields
- Reason over complex instructions
- Understand an image
- Generate an image
- Create embeddings
- Transcribe speech

## Step 2: Identify modalities

Ask:

- Is input text only?
- Are images, audio, or video included?
- What output type is required?

If visual or audio context must be reasoned over, select a compatible multimodal model or a specialized service.

## Step 3: Determine reasoning complexity

- Simple, narrow, repeatable: evaluate an SLM first.
- Broad, ambiguous, or complex: evaluate an LLM.
- Deep multistep reasoning: consider a reasoning model.

## Step 4: Identify operational constraints

- Maximum acceptable latency
- Requests per minute
- Tokens per minute
- Budget
- Hardware
- Online versus offline operation
- Data residency
- Region availability

## Step 5: Verify required capabilities

Check the model card for:

- Supported modalities
- Context window
- Maximum output
- Tool/function calling
- Structured output or JSON
- Fine-tuning support
- Safety information
- Languages
- Deployment options

## Step 6: Compare candidates empirically

Use representative data and measure:

- Task accuracy
- Groundedness
- Relevance
- Safety
- Latency
- Throughput
- Token usage
- Cost per successful task

## Step 7: Choose based on total value

Do not optimize a single benchmark. Select the model with the best overall trade-off for the application.

---

# 6. Microsoft Foundry Model Catalog

The Foundry model catalog enables teams to discover, compare, evaluate, and deploy models from Microsoft and supported providers.

Use the catalog to inspect:

- Model provider
- Model family and version
- Task type
- Supported modalities
- Context and output limits
- Tool-calling support
- Structured-output support
- Deployment options
- Regional availability
- Benchmark information
- Model card and limitations

## Models sold by Azure vs partner/community models

### Models sold by Azure

Typically provide deep Azure integration, Microsoft commercial terms/support, and enterprise-focused deployment and operational capabilities.

### Partner and community models

Increase model choice and may support specialized tasks or deployment patterns. Review provider terms, model cards, support, licensing, security, and deployment requirements.

### Exam rule

The organization remains responsible for selecting an appropriate model and implementing safety, legal, and governance controls.

---

# 7. Quality, Cost, Latency, and Throughput

## 7.1 Quality

Quality must be measured on representative examples, not inferred from parameter count alone.

Evaluate:

- Accuracy
- Relevance
- Groundedness
- Instruction following
- Format compliance
- Tool-call correctness
- Safety

## 7.2 Cost

Cost can be affected by:

- Input tokens
- Output tokens
- Model price
- Number of model calls
- Retries
- Tool calls
- Image/audio/video payloads
- Provisioned capacity

### Cost-reduction approaches

- Use an SLM when it meets quality needs.
- Reduce unnecessary prompt context.
- Retrieve only relevant chunks.
- Limit output length.
- Cache repeated deterministic results where appropriate.
- Route easy and difficult requests to different models.

## 7.3 Latency

Latency can increase because of:

- Larger models
- Long input context
- Long generated output
- Complex reasoning
- Multiple agent/tool calls
- Large image, audio, or video input
- Network or regional distance

## 7.4 Throughput

Throughput is the amount of work completed in a period. Smaller models often support greater throughput on equivalent compute, but actual performance must be measured for the chosen deployment.

---

# 8. Model Routing and Cascading

A production application can use multiple models.

## Routing pattern

1. Use a small/fast model or deterministic logic to classify the request.
2. Send simple requests to an SLM.
3. Send difficult requests to an LLM or reasoning model.
4. Send image-based requests to a multimodal model.

## Cascading pattern

1. Attempt the task with a lower-cost model.
2. Evaluate confidence or validation checks.
3. Escalate to a more capable model if needed.

### Benefits

- Lower average cost
- Lower latency for simple requests
- Better quality for difficult tasks

### Risks

- Incorrect routing
- Added architecture complexity
- More testing requirements
- Inconsistent behavior

---

# 9. RAG and Model Size

RAG and model size solve different problems.

- **RAG** supplies current or private knowledge.
- **Model size/capability** affects reasoning and generation quality.

An SLM combined with high-quality RAG may outperform an ungrounded LLM for a narrow domain. However, RAG cannot compensate for a model that lacks the required reasoning or modality capability.

### Exam trap

If the requirement says “latest internal documents,” the answer is usually RAG/grounding, not simply “choose a larger model.”

---

# 10. Deployment Considerations

## Cloud/serverless deployment

Useful when the team wants managed inference and reduced infrastructure management.

## Managed compute

Useful when the selected model requires dedicated/custom compute, custom runtime control, or a deployment option not available through serverless inference.

## Local/edge deployment

Useful when:

- Connectivity is limited
- Offline operation is required
- Very low local latency is needed
- Data must be processed locally
- Hardware can support the selected model

SLMs are usually stronger candidates for constrained local hardware.

### Always verify

- Regional availability
- Quota
- Supported deployment type
- Model version lifecycle
- Deprecation/retirement dates
- Hardware requirements

---

# 11. Responsible AI and Security

Model selection must consider more than quality.

Review:

- Model card and intended uses
- Known limitations
- Safety evaluations
- Content filtering compatibility
- Data handling and privacy
- Provider and licensing terms
- Regional and compliance requirements
- Bias and harmful-output risks
- Prompt injection risks for multimodal inputs

## Multimodal-specific risks

- Hidden or embedded instructions in images
- Sensitive information exposed in photographs
- Incorrect visual interpretations
- Unsafe generated media
- Copyright, brand, and watermark concerns

Treat text extracted from images as untrusted input and apply appropriate validation and guardrails.

---

# 12. High-Value Exam Decision Table

| Scenario clue | Strong candidate |
|---|---|
| Broad language tasks and complex reasoning | LLM |
| Focused high-volume classification | SLM |
| Low-cost, low-latency narrow task | SLM |
| On-device or constrained hardware | SLM/local-capable model |
| Question about an uploaded image | Multimodal vision-capable model |
| Create an image from text | Image-generation model |
| Search by semantic similarity | Embedding model |
| Difficult multistep logical planning | Reasoning model |
| Latest private company documents | RAG plus an appropriate language model |
| Audio transcription | Speech-to-text model/service |
| Predictable rule-based decision | Deterministic code/rules, not necessarily a generative model |

---

# 13. Common Exam Traps

1. **Choosing the largest model automatically:** Select by measured requirements.
2. **Using an LLM for embeddings:** Use an embedding model for vector representation.
3. **Using image generation for image understanding:** These are different capabilities.
4. **Assuming every multimodal model supports all media:** Verify exact modalities and API.
5. **Treating multimodal as a size category:** It is a modality category.
6. **Using a larger model for current private knowledge:** Use RAG/grounding.
7. **Ignoring latency and cost:** Quality is only one selection dimension.
8. **Assuming benchmark leadership guarantees application success:** Evaluate with representative data.
9. **Ignoring region and deployment support:** A suitable model may not be deployable in the required configuration or region.
10. **Assuming SLM means poor quality:** SLMs can perform strongly on focused tasks.
11. **Assuming local deployment guarantees security:** Local systems still need access control, patching, encryption, and monitoring.
12. **Using AI where deterministic rules are sufficient:** Prefer predictable code for exact business rules.

---

# 14. Practice Questions

## Question 1: Focused high-volume workload

A company must classify millions of short support requests into 12 stable categories. The target accuracy is achievable with several candidate models, but the application requires low latency and low cost.

Which model should the team evaluate first?

**A.** The largest available reasoning model  
**B.** A suitable SLM  
**C.** An image-generation model  
**D.** A speech-synthesis model

### Correct answer

**B. A suitable SLM**

### Why B is correct

The task is narrow, stable, high-volume, and latency/cost sensitive. An SLM is the most appropriate starting candidate if it meets the measured accuracy target.

### Why the other options are incorrect

- **A:** A large reasoning model adds cost and latency without a stated need for complex reasoning.
- **C:** Image generation does not classify text requests.
- **D:** Speech synthesis converts text to audio.

### Exam rule

For focused high-volume language tasks, evaluate an SLM before choosing a larger model.

---

## Question 2: Complex contract reasoning

An application must analyze lengthy contracts, reconcile clauses across sections, identify conflicting obligations, and explain its reasoning to legal reviewers.

Which model category is the strongest starting point?

**A.** A capable LLM or reasoning model with an adequate context window  
**B.** An embedding model only  
**C.** An image-generation model  
**D.** A speech-to-text model

### Correct answer

**A. A capable LLM or reasoning model with an adequate context window**

### Why A is correct

The workload requires broad language understanding, long-context processing, and complex multistep reasoning.

### Why the other options are incorrect

- **B:** Embeddings retrieve similar content but do not perform the required analysis by themselves.
- **C:** Image generation creates visuals.
- **D:** Speech-to-text transcribes audio.

### Exam trap

An embedding model may support retrieval, but it does not replace the generative/reasoning model.

---

## Question 3: Image question answering

Users upload equipment photographs and ask the application to identify visible damage and explain recommended inspection steps.

Which model capability is required?

**A.** Text-only completion  
**B.** Multimodal image understanding  
**C.** Text embedding only  
**D.** Text-to-speech only

### Correct answer

**B. Multimodal image understanding**

### Why B is correct

The model must interpret visual content and combine it with a text question.

### Why the other options are incorrect

- **A:** A text-only model cannot directly inspect the photograph.
- **C:** Embeddings support similarity, not detailed visual reasoning and answer generation alone.
- **D:** Text-to-speech produces audio output.

---

## Question 4: Multimodal meaning

Which statement about multimodal models is correct?

**A.** Every multimodal model supports text, image, audio, and video inputs and outputs.  
**B.** Multimodal means the model supports more than one data modality, but exact combinations vary.  
**C.** Multimodal always means the model is an LLM with hundreds of billions of parameters.  
**D.** Multimodal models cannot be used in agents.

### Correct answer

**B. Multimodal means the model supports more than one data modality, but exact combinations vary.**

### Why B is correct

Multimodality describes supported data types. The model card must be checked for exact input/output combinations.

### Why the other options are incorrect

- **A:** Different models support different combinations.
- **C:** Multimodal is not a parameter-count category.
- **D:** Compatible multimodal models can support agent scenarios.

---

## Question 5: Edge deployment

A factory requires an offline assistant on local hardware. The task is focused, and cloud connectivity is unreliable.

Which model characteristic should be prioritized?

**A.** A compact SLM compatible with the available local runtime and hardware  
**B.** The largest cloud-only model  
**C.** An image generator, even though all inputs are text  
**D.** A model selected only by popularity

### Correct answer

**A. A compact SLM compatible with the available local runtime and hardware**

### Why A is correct

SLMs have lower memory and compute requirements and are stronger candidates for local/offline deployment. Runtime and hardware compatibility must still be verified.

### Why the other options are incorrect

- **B:** A cloud-only model does not satisfy offline operation.
- **C:** The workload does not require image generation.
- **D:** Popularity does not prove compatibility or quality.

---

## Question 6: Latest company knowledge

A chatbot must answer from policies updated every week and cite the relevant sections. The current model gives outdated answers.

What should the team do first?

**A.** Replace the model with the largest LLM only  
**B.** Implement RAG over an updated policy index  
**C.** Increase temperature  
**D.** Increase output tokens

### Correct answer

**B. Implement RAG over an updated policy index**

### Why B is correct

RAG supplies current policy content at runtime and can preserve source information for citations.

### Why the other options are incorrect

- **A:** A larger model still may not know private or recently updated policies.
- **C:** Temperature affects variation, not knowledge freshness.
- **D:** Output length does not add current facts.

### Exam rule

Current private knowledge requires grounding, not merely a larger model.

---

## Question 7: Semantic retrieval

A RAG pipeline needs to retrieve passages that are conceptually similar to a user's question even when different terminology is used.

Which model type is required for vectorization?

**A.** Embedding model  
**B.** Image-generation model  
**C.** Text-to-speech model  
**D.** Video-generation model

### Correct answer

**A. Embedding model**

### Why A is correct

Embedding models convert passages and queries into vectors for semantic similarity search.

### Why the other options are incorrect

- **B:** Generates images.
- **C:** Synthesizes speech.
- **D:** Generates video.

---

## Question 8: Image generation versus understanding

A marketing application must create new product-background concepts from text prompts.

Which model type should be used?

**A.** Image-generation model  
**B.** Text embedding model  
**C.** Speech recognition model  
**D.** Text-only classification SLM

### Correct answer

**A. Image-generation model**

### Why A is correct

The requirement is to create new visual content from text.

### Why the other options are incorrect

- **B:** Produces vectors.
- **C:** Converts speech to text.
- **D:** Classifies text and does not generate images.

### Exam trap

“Create an image” indicates generation. “Explain an image” indicates multimodal understanding.

---

## Question 9: Representative evaluation

Two models perform similarly on public benchmarks. The team must choose one for an internal medical-document summarization application.

What is the best next action?

**A.** Select the model with the largest parameter count  
**B.** Evaluate both models with representative, approved application data and relevant quality/safety metrics  
**C.** Select randomly  
**D.** Use the lowest temperature as the only evaluation

### Correct answer

**B. Evaluate both models with representative, approved application data and relevant quality/safety metrics**

### Why B is correct

Public benchmarks may not reflect the application's terminology, safety risks, latency, format, or quality requirements.

### Why the other options are incorrect

- **A:** Parameter count does not guarantee application quality.
- **C:** Random selection is not evidence based.
- **D:** Temperature is a configuration parameter, not a complete evaluation method.

---

## Question 10: Model routing

A support assistant receives mostly simple FAQ requests but occasionally receives complex troubleshooting cases. The company wants to minimize average cost without reducing quality for difficult cases.

Which design is most appropriate?

**A.** Send all requests to the most expensive model  
**B.** Route simple requests to an SLM and complex requests to a capable LLM, with routing evaluation and fallback  
**C.** Use an image model for every request  
**D.** Remove all validation to reduce latency

### Correct answer

**B. Route simple requests to an SLM and complex requests to a capable LLM, with routing evaluation and fallback**

### Why B is correct

Model routing balances cost and latency while preserving stronger reasoning for difficult requests.

### Why the other options are incorrect

- **A:** It does not optimize average cost.
- **C:** Most requests are text FAQ questions.
- **D:** Removing validation creates reliability and security risks.

---

## Question 11: Structured output

An application requires valid JSON that conforms to a specified schema and also needs tool calling. What should the team do during model selection?

**A.** Assume every language model supports both features identically  
**B.** Verify structured-output and tool-calling support in the model card/API, then test schema compliance  
**C.** Select an embedding model  
**D.** Increase image resolution

### Correct answer

**B. Verify structured-output and tool-calling support in the model card/API, then test schema compliance**

### Why B is correct

Support differs across model families, versions, APIs, and deployment options. Compliance must be tested.

### Why the other options are incorrect

- **A:** Capabilities are not identical.
- **C:** An embedding model does not generate the required JSON response.
- **D:** Image resolution is unrelated.

---

## Question 12: Simple deterministic rule

A loan-processing workflow must reject an application when a required legal checkbox is false. The rule is exact and must always behave deterministically.

What is the best implementation?

**A.** Deterministic application code or a rules engine  
**B.** A creative LLM prompt with high temperature  
**C.** An image-generation model  
**D.** A multimodal model solely because it is more capable

### Correct answer

**A. Deterministic application code or a rules engine**

### Why A is correct

An exact legal condition should be enforced predictably outside a generative model.

### Why the other options are incorrect

- **B:** Generative output is probabilistic and high temperature increases variation.
- **C:** Image generation is irrelevant.
- **D:** Additional model capability does not improve an exact Boolean rule.

---

## Question 13: Cost comparison

Model A costs less per token but needs repeated retries and produces longer outputs. Model B costs more per token but completes the task correctly in one short response.

Which metric should guide the decision?

**A.** Price per token only  
**B.** Total cost per successful task together with quality and latency  
**C.** Model-name length  
**D.** Number of provider logos

### Correct answer

**B. Total cost per successful task together with quality and latency**

### Why B is correct

Real application cost includes token volume, retries, number of calls, and successful completion rate.

### Why the other options are incorrect

- **A:** It ignores retries and output volume.
- **C:** Naming has no operational relevance.
- **D:** Branding does not measure performance.

---

## Question 14: Multimodal prompt injection

A vision-enabled agent processes screenshots submitted by users. Some screenshots may contain malicious text instructing the agent to reveal secrets.

What should the team do?

**A.** Treat embedded image text as trusted system instructions  
**B.** Treat image content as untrusted input and apply prompt-injection defenses, access controls, and tool authorization  
**C.** Disable authentication  
**D.** Store credentials in the prompt for convenience

### Correct answer

**B. Treat image content as untrusted input and apply prompt-injection defenses, access controls, and tool authorization**

### Why B is correct

Multimodal inputs can carry indirect prompt-injection attacks. Deterministic authorization must protect data and tools.

### Why the other options are incorrect

- **A:** User-provided content must not override trusted instructions.
- **C:** Removing authentication increases risk.
- **D:** Prompts are not secure secret stores.

---

## Question 15: Multi-select model criteria

A team is selecting a model for a production agent. Which three factors should it evaluate? **Select three.**

**A.** Required modalities and tool support  
**B.** Quality on representative application data  
**C.** Latency, throughput, and total cost  
**D.** The model with the most fashionable name  
**E.** Provider logo color

### Correct answers

**A, B, and C**

### Why they are correct

- **A:** The model must support the required inputs, outputs, and agent capabilities.
- **B:** Application-specific evaluation verifies actual quality and safety.
- **C:** Production feasibility depends on operational performance and economics.

### Why the other options are incorrect

- **D:** Popularity or naming does not verify suitability.
- **E:** Branding is irrelevant to technical selection.

---

# 15. One-Minute Revision Sheet

- Use an **LLM** for broad language tasks, complex instructions, and sophisticated reasoning.
- Use an **SLM** for focused, high-volume, low-cost, low-latency, local, or edge workloads when evaluation confirms quality.
- Use a **multimodal model** when the task requires reasoning over multiple data types.
- Multimodal is a modality category, not a parameter-size category.
- Use an **embedding model** for vector representation and semantic retrieval.
- Use an **image-generation model** to create/edit images, not just to understand them.
- Use a **reasoning model** for difficult multistep problems when the quality benefit justifies latency/cost.
- For changing private knowledge, add **RAG** rather than only increasing model size.
- Check model cards for modalities, limits, tools, structured output, regions, and deployment options.
- Compare candidate models using representative data.
- Measure total cost per successful task, not only price per token.
- Use routing or cascading to balance simple and difficult workloads.
- Prefer deterministic code for exact business rules.
- Treat image/audio/video inputs as untrusted content.

---

# 16. Self-Check

- [ ] I can explain LLM, SLM, and multimodal models.
- [ ] I understand that multimodal does not mean large.
- [ ] I can select an SLM for focused, cost-sensitive workloads.
- [ ] I can select an LLM/reasoning model for complex tasks.
- [ ] I can distinguish image understanding from image generation.
- [ ] I can distinguish language generation from embeddings.
- [ ] I understand model routing and cascading.
- [ ] I can evaluate quality, latency, throughput, safety, and cost.
- [ ] I know why RAG is used for current private knowledge.
- [ ] I know to verify model-card capabilities and regional deployment support.

---

# 17. Official References

- [Microsoft Foundry Models overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/foundry-models-overview)
- [Select, deploy, and evaluate Microsoft Foundry models](https://learn.microsoft.com/en-us/training/modules/model-catalog-evaluate/)
- [Microsoft Foundry documentation](https://learn.microsoft.com/en-us/azure/foundry/)
- [Small language models in Foundry Local](https://learn.microsoft.com/en-us/azure/azure-sovereign-clouds/private/foundry-local/concept-models)

---

## Recommended Next Concept

**Model deployment options, deployment names, quota, capacity, and regional availability**

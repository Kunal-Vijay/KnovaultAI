# AI Engineering Knowledge Assistant

## Phased Development Plan & Cursor Development Protocol

You are the lead software architect and senior engineer for this project.

We are building a production-style **AI Engineering Knowledge Assistant** that allows users to ask engineering questions and receive answers grounded in:

1. System/company documentation
2. Git repositories
3. API documentation
4. Runbooks
5. Incident reports
6. User-uploaded documents
7. URLs/web content, where supported

The project should demonstrate:

* RAG
* Semantic search
* Hybrid search
* Vector databases
* LLM Gateway
* Multi-provider LLM support
* LLM observability
* Distributed tracing
* Token/cost tracking
* Prompt versioning
* LLM regression testing
* CI/CD
* Authentication/authorization
* User-specific knowledge bases
* Production-oriented architecture

---

# CRITICAL DEVELOPMENT RULE

You MUST develop this project one phase at a time.

DO NOT implement multiple phases in one iteration.

For every phase, follow this exact workflow:

### Step 1 — Inspect

Inspect:

* existing repository
* current code
* database schema
* configuration
* Docker setup
* tests
* dependencies
* architecture
* previous phase implementation

Do not assume anything that already exists.

### Step 2 — Explain

Explain:

* what this phase is solving
* why we need it
* how it fits into the overall architecture
* components involved
* APIs/interfaces
* database changes
* infrastructure changes
* security considerations
* testing strategy

### Step 3 — Propose

Before writing implementation code, propose:

* architecture
* directory structure
* interfaces
* data models
* APIs
* dependencies
* configuration
* sequence/data flow

If there are multiple reasonable approaches, show me the options and recommend one based on:

* simplicity
* low cost
* maintainability
* learning value
* production realism

### Step 4 — Ask for my decisions

Ask me the important questions before implementation.

Examples:

* Which database?
* Which embedding model?
* Which LLM provider?
* Which authentication approach?
* Should this component be synchronous or asynchronous?
* Should we use Redis?
* Should we introduce a queue now or later?
* Should user documents be private or shared?
* Should we support multiple tenants?

Do NOT silently make major architectural decisions.

For minor implementation details, use your judgment.

### Step 5 — Wait

STOP.

Do not write implementation code until I approve the architecture and answer the required questions.

### Step 6 — Implement

After I approve:

* implement ONLY the current phase
* keep changes focused
* don't implement future phases
* don't prematurely optimize
* don't introduce unnecessary infrastructure

### Step 7 — Test

After implementation:

* run unit tests
* run integration tests where applicable
* run lint/type checks
* verify APIs
* verify database migrations
* verify Docker services
* test failure cases

### Step 8 — Review

Explain:

* what was implemented
* files changed
* architectural decisions
* tests added
* known limitations
* technical debt
* what is intentionally NOT implemented yet

### Step 9 — Phase checkpoint

Provide:

```text
PHASE STATUS
-------------
Phase: X
Status: COMPLETE

Implemented:
- ...

Tests:
- ...

Architecture changes:
- ...

Known limitations:
- ...

Next phase:
- ...

Awaiting approval:
YES
```

DO NOT automatically start the next phase.

---

# Overall Architecture

The target architecture is:

```text
                        USERS / CLIENTS
                              |
             +----------------+----------------+
             |                |                |
           Web UI          API Client       Slack
             |                |                |
             +----------------+----------------+
                              |
                              v
                     +----------------+
                     |    FastAPI     |
                     |    API Layer   |
                     +-------+--------+
                             |
                +------------+-------------+
                |                          |
                v                          v
         Query/RAG Pipeline          Document Upload
                |                          |
                |                          v
                |                  Ingestion Pipeline
                |                          |
                |                    Parse / Chunk
                |                          |
                |                      Embeddings
                |                          |
                |                          v
                |                 +----------------+
                |                 | PostgreSQL     |
                |                 | + pgvector     |
                |                 +----------------+
                |                          ^
                |                          |
                +-----------> Semantic Search
                                      |
                                      v
                                Hybrid Search
                                      |
                                      v
                                  Reranking
                                      |
                                      v
                              Context Assembly
                                      |
                                      v
                              +---------------+
                              |  LLM Gateway  |
                              +-------+-------+
                                      |
                     +----------------+----------------+
                     |                |                |
                     v                v                v
                  OpenAI           Gemini          Anthropic
                     |                |                |
                     +----------------+----------------+
                                      |
                                      v
                                   Answer
                                      |
                                      v
                                  User


        +----------------------------------------------------+
        |              OBSERVABILITY                          |
        | OpenTelemetry | Prometheus | Grafana | Logs        |
        +----------------------------------------------------+

        +----------------------------------------------------+
        |              LLM REGRESSION                        |
        | Dataset | Evaluator | Baseline | CI/CD | Threshold |
        +----------------------------------------------------+
```

---

# PHASE 1 — Project Foundation

## Goal

Create the initial project foundation without implementing RAG or LLM functionality.

## Build

Set up:

* Python
* FastAPI
* PostgreSQL
* Docker Compose
* environment configuration
* dependency management
* logging
* health checks
* basic testing
* project structure
* database connection

Suggested structure:

```text
ai-engineering-assistant/

├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
│
├── tests/
│
├── migrations/
│
├── scripts/
│
├── docker/
│
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── Makefile
```

## Deliverables

* FastAPI service
* PostgreSQL
* `/health`
* `/ready`
* structured logging
* configuration management
* database migration system
* basic CI

Do NOT implement:

* embeddings
* vector search
* LLM calls
* RAG
* gateway

---

# PHASE 2 — User & Knowledge Base Model

## Goal

Introduce users and isolated knowledge bases.

The system should support:

```text
User
  |
  +---- Knowledge Base A
  |
  +---- Knowledge Base B
```

A user should eventually be able to upload their own documents and query them.

## Design

Introduce concepts such as:

```text
User
KnowledgeBase
Document
DocumentChunk
```

Potential relationship:

```text
User
 |
 +-- KnowledgeBase
       |
       +-- Document
              |
              +-- DocumentChunk
```

Important design decision:

A document must belong to a knowledge base.

Every query must eventually be scoped to a knowledge base.

This prevents one user's documents from accidentally appearing in another user's results.

## Deliverables

* database models
* migrations
* CRUD APIs
* ownership model
* authorization boundaries
* tests

---

# PHASE 3 — Document Ingestion Pipeline

## Goal

Allow users to upload documents that become searchable knowledge.

Supported initial formats:

```text
PDF
TXT
Markdown
DOCX
```

Potential future support:

```text
GitHub
URLs
Confluence
Google Drive
Slack
```

Do NOT implement all future connectors now.

## Pipeline

```text
Upload
  |
  v
Document Storage
  |
  v
Parser
  |
  v
Text Extraction
  |
  v
Chunking
  |
  v
Metadata
  |
  v
Embedding
  |
  v
Vector Database
```

For every chunk store metadata such as:

```text
document_id
knowledge_base_id
chunk_id
content
source
page_number
section
created_at
embedding
```

## Important

Design the ingestion system so that adding new parsers later does not require rewriting the entire pipeline.

Use interfaces such as:

```python
DocumentParser
EmbeddingProvider
Chunker
DocumentStore
```

---

# PHASE 4 — Semantic Search

## Goal

Implement semantic search using embeddings and PostgreSQL + pgvector.

Pipeline:

```text
User Query
    |
    v
Embedding Model
    |
    v
Query Vector
    |
    v
pgvector
    |
    v
Top-K Similar Chunks
```

Implement:

```text
similarity search
top_k
knowledge_base filtering
metadata filtering
similarity threshold
```

API example:

```http
POST /api/v1/search
```

Request:

```json
{
  "knowledge_base_id": "...",
  "query": "How does evaluation retry work?",
  "top_k": 5
}
```

Response should include:

```text
chunk
document
score
metadata
```

---

# PHASE 5 — RAG Pipeline

## Goal

Turn semantic search into a complete question-answering system.

Pipeline:

```text
Question
   |
   v
Query Processing
   |
   v
Semantic Search
   |
   v
Top-K Chunks
   |
   v
Context Assembly
   |
   v
Prompt
   |
   v
LLM
   |
   v
Answer + Citations
```

The answer should reference the documents/chunks used.

Example:

```text
Answer:
The evaluation retry mechanism retries failed evaluations
up to 3 times.

Sources:
- evaluation-runbook.md
- architecture.md
```

Implement clear separation between:

```text
Retriever
ContextBuilder
PromptBuilder
LLMClient
RAGService
```

Do not tightly couple everything together.

---

# PHASE 6 — LLM Gateway

## Goal

Create a provider-independent LLM gateway.

The application should NOT directly call OpenAI/Gemini/Anthropic.

Architecture:

```text
RAG Service
     |
     v
LLM Gateway
     |
     +------ OpenAI
     |
     +------ Gemini
     |
     +------ Anthropic
```

Gateway responsibilities:

* provider abstraction
* model routing
* authentication
* retries
* timeout
* fallback
* rate limiting
* request IDs
* token tracking
* cost calculation
* structured request/response logging

Create a common interface:

```python
LLMProvider
```

Possible implementations:

```python
OpenAIProvider
GeminiProvider
AnthropicProvider
```

Gateway:

```python
LLMGateway
```

The RAG layer should depend only on:

```python
LLMGateway
```

and never directly on a provider SDK.

---

# PHASE 7 — Hybrid Search + Reranking

## Goal

Improve retrieval quality.

Instead of:

```text
Semantic Search only
```

implement:

```text
                   Query
                     |
             +-------+-------+
             |               |
             v               v
       Vector Search     Keyword Search
        pgvector             BM25
             |               |
             +-------+-------+
                     |
                     v
               Candidate Set
                     |
                     v
                  Reranker
                     |
                     v
                Top-K Chunks
```

Support:

* semantic similarity
* keyword relevance
* score normalization
* weighted combination
* reranking

Make the retrieval pipeline configurable.

For example:

```text
semantic_weight
keyword_weight
top_k
rerank_top_n
```

This configuration will later be important for regression testing.

---

# PHASE 8 — Observability

## Goal

Make the AI system observable end-to-end.

Use:

```text
OpenTelemetry
Prometheus
Grafana
Structured Logs
```

Trace:

```text
HTTP Request
   |
   +-- Query processing
   |
   +-- Embedding
   |
   +-- Vector search
   |
   +-- Keyword search
   |
   +-- Reranking
   |
   +-- Context assembly
   |
   +-- LLM Gateway
          |
          +-- Provider request
          |
          +-- Provider response
```

Track:

### Application metrics

```text
request_count
error_count
request_latency
p50
p95
p99
```

### Retrieval metrics

```text
retrieval_count
similarity_score
top_k
reranking_latency
```

### LLM metrics

```text
input_tokens
output_tokens
total_tokens
model
provider
latency
errors
```

### Cost

Track estimated:

```text
cost per request
cost per model
cost per user
cost per knowledge base
```

Create Grafana dashboards.

---

# PHASE 9 — LLM Regression Testing

## Goal

Prevent changes to prompts, models, embeddings, or retrieval from silently reducing answer quality.

Create an evaluation dataset:

```text
evals/
    dataset.json
    expected_answers.json
```

Each test should contain:

```json
{
  "question": "...",
  "knowledge_base": "...",
  "expected_sources": [],
  "expected_answer": "...",
  "criteria": {}
}
```

Evaluate:

```text
Retrieval Recall
Context Precision
Context Recall
Answer Relevance
Faithfulness
Latency
Token Usage
Cost
```

Create a baseline:

```text
baseline/
    results.json
```

Pipeline:

```text
Code Change
    |
    v
Run Regression Tests
    |
    v
Compare Baseline
    |
    +------ Quality improved
    |
    +------ Quality unchanged
    |
    +------ Quality degraded
                  |
                  v
              CI Failure
```

Define configurable thresholds.

Example:

```text
faithfulness must not decrease > 5%
retrieval recall must not decrease > 5%
latency must not increase > 30%
```

Do not hardcode these thresholds without discussing them with me first.

---

# PHASE 10 — Production Hardening

## Goal

Turn the project into something that demonstrates production engineering.

Implement only after the previous phases are stable.

Potential features:

### Authentication

```text
JWT/OAuth
```

### Authorization

```text
User
 |
 +-- Knowledge Base
       |
       +-- Documents
```

Ensure users cannot access another user's data.

### Security

* API key management
* secrets management
* input validation
* file validation
* file size limits
* prompt injection defenses
* audit logging

### Reliability

* retries
* timeouts
* circuit breakers
* provider fallback
* idempotent ingestion
* dead-letter handling where appropriate

### Performance

* caching
* connection pooling
* batch embeddings
* async processing

### Deployment

Start simple.

Possible deployment:

```text
Docker
   |
   +-- FastAPI
   |
   +-- PostgreSQL
   |
   +-- Prometheus
   |
   +-- Grafana
```

Then optionally deploy to AWS.

Do NOT introduce Kubernetes unless there is a clear learning or architecture reason.

---

# OPTIONAL PHASE 11 — User Experience

Only implement after the backend is stable.

Create a simple UI:

```text
+---------------------------------------+
| AI Engineering Knowledge Assistant    |
+---------------------------------------+
| Knowledge Base: My Engineering Docs   |
|                                       |
| Ask a question...                     |
|                                       |
| [ Why does evaluation retry fail? ]   |
|                                       |
+---------------------------------------+
| Answer                                |
|                                       |
| ...                                   |
|                                       |
| Sources                               |
| [evaluation-runbook.md]               |
| [architecture.md]                     |
+---------------------------------------+
```

Include:

* document upload
* knowledge-base selection
* chat
* source citations
* retrieval scores
* request/trace ID
* optional "view retrieved context"

---

# IMPORTANT ARCHITECTURAL PRINCIPLES

Throughout the project:

## 1. Keep provider code isolated

Bad:

```text
RAGService -> OpenAI SDK
```

Good:

```text
RAGService
    ↓
LLMGateway
    ↓
LLMProvider
    ↓
OpenAI/Gemini/Anthropic
```

## 2. Keep retrieval independent from generation

```text
Retriever
```

must be usable independently of:

```text
LLM
```

This allows us to test retrieval quality separately.

## 3. User documents are first-class knowledge

A user's uploaded document must go through the same ingestion pipeline as other knowledge sources:

```text
User Upload
    ↓
Parse
    ↓
Chunk
    ↓
Embed
    ↓
Store
    ↓
Search
    ↓
RAG
```

But it must retain ownership:

```text
knowledge_base_id
user_id
document_id
```

## 4. Every request needs correlation

Use:

```text
request_id
trace_id
user_id
knowledge_base_id
```

where appropriate.

This should allow us to answer:

> "Why did this particular AI response happen?"

by tracing:

```text
Request
 ↓
Retrieval
 ↓
Documents
 ↓
Prompt
 ↓
Model
 ↓
Response
 ↓
Cost
```

## 5. Configuration over hardcoding

Make these configurable:

```text
embedding_model
llm_provider
llm_model
top_k
semantic_weight
keyword_weight
reranker
temperature
max_tokens
prompt_version
```

## 6. Tests are part of every phase

Every phase must include appropriate tests.

Do not postpone testing until the end.

---

# COST CONSTRAINT

This is a portfolio project.

Prefer low-cost architecture.

Initial target:

```text
PostgreSQL + pgvector
Docker Compose
Local development
One embedding provider
One primary LLM
One fallback LLM
OpenTelemetry
Prometheus
Grafana
GitHub Actions
```

Do not introduce paid infrastructure unless necessary.

Ask before adding services that create recurring costs.

---

# ENGINEERING QUALITY EXPECTATIONS

Write production-quality code.

Follow:

* clean architecture where useful
* SOLID principles where appropriate
* type hints
* dependency injection
* clear interfaces
* small services
* meaningful error handling
* structured logging
* tests
* configuration management
* database migrations
* API versioning

Avoid:

* overengineering
* unnecessary microservices
* unnecessary Kubernetes
* giant classes
* tightly coupled provider SDKs
* hardcoded credentials
* hardcoded prompts
* global mutable state

---

# REQUIRED DEVELOPMENT BEHAVIOR

At the beginning of EVERY phase, say:

```text
PHASE X — ARCHITECTURE REVIEW

Current system:
...

Goal:
...

Changes proposed:
...

Components affected:
...

Database changes:
...

API changes:
...

Infrastructure changes:
...

Risks:
...

Architecture decisions requiring your input:
1.
2.
3.
```

Then WAIT for my response.

After I provide the decisions, show me the final architecture for the phase and ask:

```text
Do you approve this architecture for Phase X?
```

Only after I explicitly approve should you implement.

---

# IMPORTANT

Never assume that because a later phase is described here, you should implement it now.

For example:

If we are in Phase 3, do NOT implement:

* semantic search
* RAG
* LLM gateway
* observability
* regression testing

unless a minimal interface is absolutely required for Phase 3.

If a future-phase interface is needed, create only the smallest abstraction necessary and clearly mark it as future integration.

---

# DEFINITION OF DONE

A phase is complete only when:

1. Implementation exists
2. Tests exist
3. Tests pass
4. Configuration is documented
5. APIs are documented
6. Database migrations work
7. Docker setup works where applicable
8. README is updated
9. Architecture decisions are documented
10. Known limitations are documented

Then stop and wait for approval before continuing.

---

# START

Start with **PHASE 1 — Project Foundation**.

Do NOT write code yet.

First inspect the repository and then provide:

1. Current repository assessment
2. Proposed Phase 1 architecture
3. Proposed directory structure
4. Technology choices
5. Dependencies
6. Docker architecture
7. Database architecture
8. Testing strategy
9. Architecture decisions requiring my input

Then wait for my response.

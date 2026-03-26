# OmniSkill Framework Design

This is an extremely valuable direction for exploration. Combined with deep understanding of projects like `ui-ux-pro-max-skill` and `qmd`, we can extract a **universal Agentic-RAG Skill framework**.

This universal framework is named **"OmniSkill Framework" (Universal Agentic Skill Framework)**. Its core goal is: **provide a standard scaffolding that lets developers "fill in the blanks" with CSV or Markdown data to generate super Skills with dynamic retrieval and on-demand assembly capabilities.**

Here is the in-depth design of the framework:

---

## 1. OmniSkill Framework Architecture (Mermaid)

```mermaid
graph TD
    subgraph 1. AI IDE / Agent Layer
        A[User Input: "Help me design a high-concurrency flash sale API"] --> B[AI Intercept Request]
        B --> |Read| C(Domain SKILL.md)
        C -. Invoke .-> D[Execution Engine core.py]
    end

    subgraph 2. OmniSkill Core (Universal Search Engine)
        D --> E{Request Parser}
        E --> |Extract keywords, intent, domain| F(Universal Search Module BM25/Regex)
    end

    subgraph 3. Hybrid Dataset Layer
        F -->|Structured Search| G[(CSV Datasets)]
        G --> |Row level: API specs, status codes, field mappings| G1
        F --> |Document Chunk Search| H[(Markdown Datasets)]
        H --> |Chunk level H2/H3: Architecture, best practices, code examples| H1
    end

    subgraph 4. Dynamic Assembly Layer
        G1 --> I[Prompt Assembler]
        H1 --> I
        I --> |Formatted output| J[Assembled System Prompt Context]
    end

    J -. Inject context .-> B
    B --> K[High-quality, constrained code/solution output]
```

---

## 2. Framework Directory Structure

The framework uses an "engine and data separation" design. Developers only need to create directories and drop files under `datasets/`, and the framework automatically turns them into a Skill.

```text
omni-skill/
│
├── src/omniskill/
│   ├── core/
│   │   ├── indexer.py       # Automatic index generator (supports chunked MD parsing, CSV parsing)
│   │   ├── search.py        # Pure Python local search engine using BM25
│   │   └── assembler.py     # Prompt dynamic assembly template engine
│   ├── cli.py               # CLI entry point
│   ├── config.py            # Configuration management
│   ├── exceptions.py        # Exception hierarchy
│   ├── protocols.py         # Protocol interfaces
│   └── models/              # Data models
│       ├── __init__.py
│       └── ...
│
├── examples/                # Example skills
│   └── backend-api-master/  # Example: Backend API Architect Skill
│       ├── datasets/
│       │   ├── api_standards.csv   # Structured data (status codes, naming conventions)
│       │   ├── auth_patterns.md    # Unstructured docs (auth code examples)
│       │   └── db_best_practices.md # Database best practices
│       └── SKILL.md
│
├── features/                # BDD feature files
│   ├── indexing.feature
│   ├── search.feature
│   └── steps/
│
└── tests/                   # Unit tests
```

---

## 3. Core Module Design

### ① Intelligent Parsing and Indexing Module (`indexer.py`)

This is the key to supporting **hybrid datasets (CSV + Markdown)**. At startup or build time, it consolidates files of different formats into unified searchable units (Documents).

- **CSV Processing**: Converts each row into a Document. For example, `api_standards.csv` has fields `Pattern, Description, Example`. The framework automatically uses `Pattern` + `Description` as search index columns, and outputs `Example` when a search matches.
- **Markdown Processing (Chunking)**: Uses regex to extract header levels (`##` or `###`), splitting each subsection into an independent Document.
  - *Design purpose*: Markdown contains detailed code implementations and explanations that would overflow the context window. By chunking at headers, searching "JWT" only returns the `## JWT Authentication Best Practices` section.

### ② Pure Local Hybrid Search Engine (`search.py`)

No need for ChromaDB or any complex vector database.

- **BM25 Scoring**: Uses the open-source `rank_bm25` library to tokenize and score user queries.
- **Precise Routing with Tags**: When the LLM invokes the script, it can pass `--type csv` or `--tag auth`, and the engine prioritizes searching within the specified subset, improving accuracy.

### ③ Dynamic Prompt Assembler (`assembler.py`)

Takes the Top-K search results (which may be a few CSV rules plus a Markdown best practice code snippet) and assembles them into LLM-friendly XML or Markdown format.

The assembler outputs structured context like this (example in XML format):

```xml
<context_injection>
  <rules source="api_standards.csv">
    - Constraint: POST endpoints must return 201 Created.
    - Naming convention: Use snake_case for JSON response fields.
  </rules>
  <reference source="auth_patterns.md">
    See JWT Authentication section for implementation details.
  </reference>
</context_injection>
```

---

## 4. SKILL Auto-Generation Mechanism (CLI)

This is the experience a real framework should provide. To create a Skill in a new domain (e.g., "Game Development Guide"), you don't need to write any code—just use the CLI:

**Step 1: Run the command**

```bash
omniskill create game-dev-pro
```

**Step 2: CLI auto-generates the default `SKILL.md` (instruction file for LLMs)**

The generated SKILL.md contains sections for Role, Knowledge Retrieval Action with the search command, and step-by-step Instructions for the LLM to follow.

**Step 3: Populate the dataset**

Drop your accumulated `game_patterns.csv` into `datasets/`, split your purchased tutorial documents by `##` headers into `datasets/`. **A privatized AI expert that understands all your coding habits is born.**

---

## 5. Core Advantages of This Framework Design

1. **Extremely Efficient Token Usage**: Traditional approaches put 100,000 words of architecture specs into the prompt—extremely expensive and prone to "Lost in the middle." This framework makes the AI **actively look things up (on-demand retrieval)**, with each retrieval returning only ~1000 tokens of context.

2. **Unlimited Knowledge Base Expansion**: Whether you use CSV (suitable for strict rules, mapping tables) or Markdown (suitable for long code, complex logic explanations), the framework's adapters can handle it.

3. **Zero External Dependencies (Zero-Dependency RAG)**: No network dependency, no cloud vector database—all local pure text retrieval, greatly reducing security compliance risk and deployment barriers.

4. **Eliminates AI "Slop" (Mediocrity)**: Since every generation is forced to inject specific, domain-vertical CSV parameters or private Markdown code blocks, the AI cannot output generic, mediocre code.

---

## Summary

The **OmniSkill (Search + Dataset + Dynamic Assembly)** framework is essentially an **"external data bus" for LLMs**.

You only need to maintain your **CSV (structured standards)** and **Markdown (best practice artifacts)**, and through this framework, any junior programmer using Cursor/Claude can write code that fully meets your company's senior architect standards. This is absolutely the killer pattern for developing high-level AI Agent productivity tools in 2025-2026.

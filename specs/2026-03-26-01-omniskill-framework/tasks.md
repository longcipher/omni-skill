# OmniSkill Framework — Tasks

| Metadata | Details |
| :--- | :--- |
| **Design Doc** | specs/2026-03-26-01-omniskill-framework/design.md |
| **Status** | Planning |

---

## Summary & Timeline

| Phase | Tasks | Duration | Deliverable |
|-------|-------|----------|-------------|
| Phase 1: Foundation | 1.1-1.4 | 2 days | Core models, indexing |
| Phase 2: Search | 2.1-2.3 | 2 days | BM25 search engine |
| Phase 3: Assembly | 3.1-3.2 | 1 day | Prompt assembler |
| Phase 4: CLI | 4.1-4.3 | 1 day | CLI scaffolding |
| Phase 5: Integration | 5.1-5.3 | 2 days | Integration, tests |
| **Total** | **14 tasks** | **9 days** | **Complete Framework** |

---

## Phase 1: Foundation

### Task 1.1: Project Identity Alignment — Rename Placeholders

> **Context:** The current project uses generic placeholder names (`uv-app`, `uv_app`) that don't match the project identity (`omniskill`). This task renames all placeholders to project-matching identities before feature work proceeds.
>
> **Verification:** All imports, CLI commands, and package references use `omniskill` instead of `uv_app` or `uv-app`.
>
> **Requirement Coverage:** N/A (Infrastructure)
>
> **Scenario Coverage:** N/A

- **Loop Type:** TDD-only
- **Behavioral Contract:** No behavior change - pure rename
- **Simplification Focus:** Consolidate identity to single canonical name
- **Advanced Test Coverage:** Example-based only
- **Status:** 🟢 DONE
- [x] Step 1: Rename `src/uv_app/` to `src/omniskill/`
- [x] Step 2: Update `pyproject.toml` project name from `uv-app` to `omniskill`
- [x] Step 3: Update `pyproject.toml` script entry from `uv-app` to `omniskill`
- [x] Step 4: Update all internal imports in source files
- [x] Step 5: Update all test imports
- [x] Step 6: Update `features/steps/` imports if any
- [x] Step 7: Run `uv sync --all-groups` to regenerate lock file
- [x] Step 8: Verification: `uv run omniskill --help` works
- [x] Step 9: Verification: `uv run pytest tests/` passes
- [x] Step 10: Verification: `uv run behave features/` passes
- [ ] BDD Verification: N/A (no behavior change)
- [ ] Verification: All tests pass after rename
- [ ] Advanced Test Verification: N/A
- [ ] Runtime Verification: N/A

---

### Task 1.2: Core Data Models — Document, Chunk, SearchResult

> **Context:** Define the foundational data structures used throughout the framework. These immutable dataclasses represent documents (from CSV and Markdown files), chunks (sub-sections of Markdown), and search results (with BM25 scores).
>
> **Verification:** All models can be instantiated, are immutable (frozen), have proper type annotations, and support JSON serialization via `msgspec`.
>
> **Requirement Coverage:** R1, R2, R3, R10
>
> **Scenario Coverage:** `indexing.feature` (all scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - model definitions
- **Simplification Focus:** Clear, explicit dataclass definitions with slots
- **Advanced Test Coverage:** Property tests for model instantiation
- **Status:** 🟢 DONE
- [x] Step 1: Create `src/omniskill/models/__init__.py`
- [x] Step 2: Define `Document` dataclass with slots=True, frozen=True
- [x] Step 3: Define `Chunk` dataclass with slots=True, frozen=True
- [x] Step 4: Define `SearchResult` dataclass with slots=True, frozen=True
- [x] Step 5: Add type annotations for all fields
- [x] Step 6: Add docstrings for all classes
- [x] Step 7: Create `tests/test_models.py` with unit tests
- [x] Step 8: Write test for Document instantiation
- [x] Step 9: Write test for Chunk instantiation
- [x] Step 10: Write test for SearchResult instantiation
- [x] Step 11: Write test for immutability (frozen dataclass)
- [x] Step 12: Write property test with Hypothesis for arbitrary data
- [x] Step 13: Write `features/indexing.feature` Gherkin scenarios
- [x] Step 14: Create `features/steps/indexing_steps.py` with step definitions
- [x] BDD Verification: `uv run behave features/indexing.feature` passes
- [x] Verification: `uv run pytest tests/test_models.py -v` passes
- [x] Advanced Test Verification: `uv run pytest tests/test_models.py::test_document_hypothesis -v` passes
- [x] Runtime Verification: N/A (no runtime service)

---

### Task 1.3: Document Indexer — CSV and Markdown Indexing

> **Context:** Implement the `Indexer` class that converts CSV and Markdown files into searchable `Document` and `Chunk` objects. CSV files are indexed row-by-row; Markdown files are chunked by H2/H3 headers.
>
> **Verification:** Indexer correctly parses CSV files (headers → document fields), chunks Markdown by headers, handles edge cases (empty files, malformed CSV, missing headers), and returns proper Document/Chunk objects.
>
> **Requirement Coverage:** R1, R2, R3, R9, R10
>
> **Scenario Coverage:** `indexing.feature` (all scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - indexing implementation
- **Simplification Focus:** Clear separation between CSV and Markdown indexing strategies
- **Advanced Test Coverage:** Property tests for CSV/Markdown parsing
- **Status:** 🟢 DONE
- [x] Step 1: Create `src/omniskill/core/__init__.py`
- [x] Step 2: Create `src/omniskill/core/indexer.py`
- [x] Step 3: Define `IndexerProtocol` (or import from protocols.py)
- [x] Step 4: Implement `CsvIndexer` class with `index_file` method
- [x] Step 5: Parse CSV with `csv.DictReader` for header support
- [x] Step 6: Create Document per row with row data as metadata
- [x] Step 7: Implement `MarkdownIndexer` class
- [x] Step 8: Parse Markdown headers with regex (H2: `##`, H3: `###`)
- [x] Step 9: Chunk content between headers into Chunk objects
- [x] Step 10: Implement `Indexer` router class that selects appropriate indexer
- [x] Step 11: Add file extension detection and indexer selection
- [x] Step 12: Add error handling for malformed files
- [x] Step 13: Create `tests/test_indexer.py` with unit tests
- [x] Step 14: Write test for CSV indexing with sample data
- [x] Step 15: Write test for Markdown H2 chunking
- [x] Step 16: Write test for Markdown H3 chunking
- [x] Step 17: Write test for mixed content handling
- [x] Step 18: Write test for error handling (malformed CSV)
- [x] Step 19: Write property test with Hypothesis for CSV content
- [x] Step 20: Write property test with Hypothesis for Markdown content
- [x] Step 21: Update `features/steps/indexing_steps.py` with step implementations
- [x] BDD Verification: `uv run behave features/indexing.feature` passes
- [x] Verification: `uv run pytest tests/test_indexer.py -v` passes
- [x] Advanced Test Verification: `uv run pytest tests/test_indexer.py -k hypothesis -v` passes
- [x] Runtime Verification: N/A

---

### Task 1.4: Protocol Definitions — indexer, searcher, assembler

> **Context:** Define the protocol interfaces (typing.Protocol) that establish contracts between core modules. These protocols enable dependency injection, testing with mocks, and future extensibility.
>
> **Verification:** All protocols are runtime-checkable, have complete type annotations, and cover all required methods. Protocols are used correctly in core module signatures.
>
> **Requirement Coverage:** R10 (Type annotations)
>
> **Scenario Coverage:** N/A (Infrastructure)

- **Loop Type:** TDD-only
- **Behavioral Contract:** New behavior - protocol definitions
- **Simplification Focus:** Clear, minimal protocol definitions
- **Advanced Test Coverage:** Example-based only
- **Status:** 🟢 DONE
- [x] Step 1: Create `src/omniskill/protocols.py`
- [x] Step 2: Import `Protocol`, `runtime_checkable` from `typing`
- [x] Step 3: Define `IndexerProtocol` with `index_file`, `index_directory`, `supports_file` methods
- [x] Step 4: Add complete type annotations to `IndexerProtocol`
- [x] Step 5: Add docstrings to `IndexerProtocol` methods
- [x] Step 6: Define `SearcherProtocol` with `search`, `add_documents` methods
- [x] Step 7: Add complete type annotations to `SearcherProtocol`
- [x] Step 8: Add docstrings to `SearcherProtocol` methods
- [x] Step 9: Define `AssemblerProtocol` with `assemble` method
- [x] Step 10: Add complete type annotations to `AssemblerProtocol`
- [x] Step 11: Add docstrings to `AssemblerProtocol` methods
- [x] Step 12: Apply `@runtime_checkable` decorator to all protocols
- [x] Step 13: Create `tests/test_protocols.py` with unit tests
- [x] Step 14: Write test that verifies `IndexerProtocol` is runtime-checkable
- [x] Step 15: Write test that verifies `SearcherProtocol` is runtime-checkable
- [x] Step 16: Write test that verifies `AssemblerProtocol` is runtime-checkable
- [x] Step 17: Write test that verifies a conforming class passes protocol check
- [x] Step 18: Write test that verifies a non-conforming class fails protocol check
- [x] Step 19: Export protocols from `src/omniskill/__init__.py`
- [x] BDD Verification: N/A (no user-visible behavior)
- [x] Verification: `uv run pytest tests/test_protocols.py -v` passes
- [x] Advanced Test Verification: N/A
- [x] Runtime Verification: N/A

---

## Phase 2: Search

### Task 2.1: BM25 Search Engine Implementation

> **Context:** Implement the BM25 search engine using the `rank-bm25` library (or pure Python implementation if preferred). The searcher must index documents, accept queries, and return ranked results with BM25 scores.
>
> **Verification:** Searcher correctly indexes documents, performs BM25 scoring, returns ranked results by relevance, and handles edge cases (empty queries, no matches).
>
> **Requirement Coverage:** R4, R9, R10
>
> **Scenario Coverage:** `search.feature` (BM25 search scenario)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - search implementation
- **Simplification Focus:** Clear BM25 implementation with configurable parameters
- **Advanced Test Coverage:** Property tests for search ranking consistency
- **Status:** 🟡 IN PROGRESS
- [ ] Step 1: Add `rank-bm25` dependency via `uv add rank-bm25`
- [ ] Step 2: Create `src/omniskill/core/search.py`
- [ ] Step 3: Import `BM25Okapi` from `rank_bm25`
- [ ] Step 4: Define `BM25Searcher` class implementing `SearcherProtocol`
- [ ] Step 5: Implement `__init__` with `k1`, `b` parameter configuration
- [ ] Step 6: Implement `add_documents` method to index documents
- [ ] Step 7: Tokenize document content for BM25 indexing
- [ ] Step 8: Store documents in internal list
- [ ] Step 9: Implement `search` method with query parameter
- [ ] Step 10: Tokenize query for BM25 scoring
- [ ] Step 11: Get BM25 scores from `BM25Okapi`
- [ ] Step 12: Sort results by score (descending)
- [ ] Step 13: Return `SearchResult` objects with document and score
- [ ] Step 14: Add error handling for empty index
- [ ] Step 15: Add error handling for empty query
- [ ] Step 16: Create `tests/test_search.py` with unit tests
- [ ] Step 17: Write test for document indexing
- [ ] Step 18: Write test for BM25 search with known results
- [ ] Step 19: Write test for empty query handling
- [ ] Step 20: Write test for empty index handling
- [ ] Step 21: Write test for ranking order (highest score first)
- [ ] Step 22: Write property test for search consistency (same query = same ranking)
- [ ] Step 23: Create `features/search.feature` with Gherkin scenarios
- [ ] Step 24: Create `features/steps/search_steps.py` with step implementations
- [ ] BDD Verification: `uv run behave features/search.feature` passes
- [ ] Verification: `uv run pytest tests/test_search.py -v` passes
- [ ] Advanced Test Verification: `uv run pytest tests/test_search.py -k hypothesis -v` passes
- [ ] Runtime Verification: N/A

---

### Task 2.2: Tag-Based Filtering Implementation

> **Context:** Extend the BM25 search engine to support tag-based filtering. Tags can filter by document type (`csv`, `markdown`) and custom tags extracted from file paths or metadata.
>
> **Verification:** Searcher correctly filters results by `doc_type`, custom tags, and supports combining tag filters with text search.
>
> **Requirement Coverage:** R5, R10
>
> **Scenario Coverage:** `search.feature` (tag filtering scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - tag filtering
- **Simplification Focus:** Clear tag extraction and filtering logic
- **Advanced Test Coverage:** Property tests for tag filtering consistency
- **Status:** 🔴 TODO
- [ ] Step 1: Update `Document` dataclass to include `tags` field
- [ ] Step 2: Update `Chunk` dataclass to include `tags` field
- [ ] Step 3: Update `CsvIndexer` to extract tags from file path
- [ ] Step 4: Update `MarkdownIndexer` to extract tags from file path
- [ ] Step 5: Update `BM25Searcher` class with tag filtering
- [ ] Step 6: Add `doc_type` parameter to `search` method signature
- [ ] Step 7: Add `tags` parameter to `search` method signature
- [ ] Step 8: Implement tag matching logic (all tags must match)
- [ ] Step 9: Implement doc_type filtering logic
- [ ] Step 10: Apply filters before BM25 scoring for efficiency
- [ ] Step 11: Create `tests/test_search_filters.py` with unit tests
- [ ] Step 12: Write test for doc_type filtering (csv vs markdown)
- [ ] Step 13: Write test for single tag filtering
- [ ] Step 14: Write test for multiple tag filtering (AND logic)
- [ ] Step 15: Write test for combined text search + tag filter
- [ ] Step 16: Write test for no matches with filter
- [ ] Step 17: Write property test for tag filtering consistency
- [ ] Step 18: Update `features/search.feature` with tag filtering scenarios
- [ ] Step 19: Update `features/steps/search_steps.py` with filter step implementations
- [ ] BDD Verification: `uv run behave features/search.feature` passes
- [ ] Verification: `uv run pytest tests/test_search_filters.py -v` passes
- [ ] Advanced Test Verification: `uv run pytest tests/test_search_filters.py -k hypothesis -v` passes
- [ ] Runtime Verification: N/A

---

### Task 2.3: Search Integration with Indexer

> **Context:** Wire the `Indexer` and `BM25Searcher` together so that indexed documents are automatically added to the search index. This creates the complete indexing → search pipeline.
>
> **Verification:** Documents indexed from CSV/Markdown files are immediately searchable via BM25 search, with proper ranking and filtering.
>
> **Requirement Coverage:** R1, R4, R10
>
> **Scenario Coverage:** `search.feature` (end-to-end search scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - integrated pipeline
- **Simplification Focus:** Clear integration point between components
- **Advanced Test Coverage:** End-to-end property tests
- **Status:** 🔴 TODO
- [ ] Step 1: Create `src/omniskill/core/engine.py` integration module
- [ ] Step 2: Define `SearchEngine` class that combines Indexer + Searcher
- [ ] Step 3: Add `__init__` with `Indexer` and `BM25Searcher` injection
- [ ] Step 4: Add `index_directory` method that indexes and adds to search
- [ ] Step 5: Add `search` method that delegates to searcher
- [ ] Step 6: Add `index_and_search` convenience method
- [ ] Step 7: Add error handling for index → search pipeline
- [ ] Step 8: Add logging for pipeline stages
- [ ] Step 9: Create `tests/test_engine.py` with integration tests
- [ ] Step 10: Write test for CSV → index → search pipeline
- [ ] Step 11: Write test for Markdown → index → search pipeline
- [ ] Step 12: Write test for mixed CSV + Markdown pipeline
- [ ] Step 13: Write test for search ranking quality
- [ ] Step 14: Write test for error handling in pipeline
- [ ] Step 15: Write end-to-end property test with Hypothesis
- [ ] Step 16: Update `features/search.feature` with end-to-end scenarios
- [ ] Step 17: Update `features/steps/search_steps.py` with pipeline steps
- [ ] BDD Verification: `uv run behave features/search.feature` passes
- [ ] Verification: `uv run pytest tests/test_engine.py -v` passes
- [ ] Advanced Test Verification: `uv run pytest tests/test_engine.py -k hypothesis -v` passes
- [ ] Runtime Verification: N/A

---

## Phase 3: Assembly

### Task 3.1: Prompt Assembler Core

> **Context:** Implement the `Assembler` class that takes search results and formats them into LLM-friendly context. Support XML and Markdown output formats with proper structure and metadata.
>
> **Verification:** Assembler correctly formats search results, includes source attribution, handles both CSV and Markdown results, and produces valid XML/Markdown output.
>
> **Requirement Coverage:** R6, R10
>
> **Scenario Coverage:** `assembly.feature` (all scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - assembler implementation
- **Simplification Focus:** Clear formatting functions, template-based output
- **Advanced Test Coverage:** Property tests for format consistency
- **Status:** 🔴 TODO
- [ ] Step 1: Create `src/omniskill/core/assembler.py`
- [ ] Step 2: Define `OutputFormat` Enum with XML and MARKDOWN values
- [ ] Step 3: Define `AssemblerProtocol` (or import from protocols.py)
- [ ] Step 4: Implement `PromptAssembler` class
- [ ] Step 5: Add `assemble` method with `results` and `format` parameters
- [ ] Step 6: Implement XML format method
- [ ] Step 7: XML structure: `<context_injection>` root with `<rules>` and `<reference>` children
- [ ] Step 8: Implement Markdown format method
- [ ] Step 9: Markdown structure: `## Context` with `### Rules` and `### References`
- [ ] Step 10: Add source attribution in both formats
- [ ] Step 11: Handle CSV results (show as rules/constraints)
- [ ] Step 12: Handle Markdown results (show as reference code)
- [ ] Step 13: Add error handling for empty results
- [ ] Step 14: Add max context length enforcement
- [ ] Step 15: Create `tests/test_assembler.py` with unit tests
- [ ] Step 16: Write test for XML format output
- [ ] Step 17: Write test for Markdown format output
- [ ] Step 18: Write test for mixed CSV + Markdown assembly
- [ ] Step 19: Write test for empty results handling
- [ ] Step 20: Write test for context length enforcement
- [ ] Step 21: Write test for source attribution presence
- [ ] Step 22: Write property test for format consistency
- [ ] Step 23: Create `features/assembly.feature` with Gherkin scenarios
- [ ] Step 24: Create `features/steps/assembly_steps.py` with step definitions
- [ ] BDD Verification: `uv run behave features/assembly.feature` passes
- [ ] Verification: `uv run pytest tests/test_assembler.py -v` passes
- [ ] Advanced Test Verification: `uv run pytest tests/test_assembler.py -k hypothesis -v` passes
- [ ] Runtime Verification: N/A

---

### Task 3.2: Assembler Integration with Search

> **Context:** Wire the `Assembler` with the `SearchEngine` to create the complete search → assemble pipeline. This enables end-to-end functionality from indexing through search to formatted prompt context.
>
> **Verification:** The complete pipeline works: index documents → search → assemble results into formatted context (XML or Markdown).
>
> **Requirement Coverage:** R6, R10
>
> **Scenario Coverage:** `assembly.feature` (end-to-end scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - integrated pipeline
- **Simplification Focus:** Clear pipeline flow with proper error handling
- **Advanced Test Coverage:** End-to-end property tests
- **Status:** 🔴 TODO
- [ ] Step 1: Update `src/omniskill/core/engine.py` SearchEngine class
- [ ] Step 2: Add `assembler` parameter to `SearchEngine.__init__`
- [ ] Step 3: Import `PromptAssembler` and `OutputFormat`
- [ ] Step 4: Add `search_and_assemble` method to SearchEngine
- [ ] Step 5: Method signature: `search_and_assemble(query, format, limit, ...)`
- [ ] Step 6: Implementation: search → get results → assemble → return formatted string
- [ ] Step 7: Add convenience method for XML output
- [ ] Step 8: Add convenience method for Markdown output
- [ ] Step 9: Add error handling for assembly failures
- [ ] Step 10: Add logging for pipeline stages
- [ ] Step 11: Update `SearchEngine.index_directory` to log progress
- [ ] Step 12: Update `SearchEngine.search` to log query and result count
- [ ] Step 13: Create `tests/test_engine_integration.py` with integration tests
- [ ] Step 14: Write test for full pipeline: CSV index → search → XML assembly
- [ ] Step 15: Write test for full pipeline: Markdown index → search → Markdown assembly
- [ ] Step 16: Write test for mixed pipeline: CSV + Markdown → search → assembly
- [ ] Step 17: Write test for `search_and_assemble` convenience method
- [ ] Step 18: Write test for error handling in pipeline
- [ ] Step 19: Write end-to-end property test with Hypothesis
- [ ] Step 20: Update `features/assembly.feature` with end-to-end scenarios
- [ ] Step 21: Update `features/steps/assembly_steps.py` with pipeline step definitions
- [ ] BDD Verification: `uv run behave features/assembly.feature` passes
- [ ] Verification: `uv run pytest tests/test_engine_integration.py -v` passes
- [ ] Advanced Test Verification: `uv run pytest tests/test_engine_integration.py -k hypothesis -v` passes
- [ ] Runtime Verification: N/A

---

## Phase 4: CLI

### Task 4.1: CLI Framework Setup

> **Context:** Set up the Click-based CLI framework with command structure, help text, and argument parsing. This is the foundation for all CLI commands.
>
> **Verification:** CLI can be invoked with `omniskill --help`, shows proper command structure, and handles argument parsing correctly.
>
> **Requirement Coverage:** R7, R10
>
> **Scenario Coverage:** `cli.feature` (help and structure scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - CLI framework
- **Simplification Focus:** Clear Click command structure
- **Advanced Test Coverage:** Example-based only
- **Status:** 🔴 TODO
- [ ] Step 1: Update `src/omniskill/cli.py` (or create if doesn't exist)
- [ ] Step 2: Import `click` library
- [ ] Step 3: Define main CLI group with `@click.group()`
- [ ] Step 4: Add `--version` option that prints version from `__version__`
- [ ] Step 5: Add `--verbose` / `-v` option for verbose output
- [ ] Step 6: Add `--config` option for custom config file path
- [ ] Step 7: Create `src/omniskill/__main__.py` for `python -m omniskill` support
- [ ] Step 8: In `__main__.py`, import and call CLI main function
- [ ] Step 9: Add `__version__` to `src/omniskill/__init__.py`
- [ ] Step 10: Update `pyproject.toml` to point to correct CLI entry point
- [ ] Step 11: Create `tests/test_cli.py` with unit tests
- [ ] Step 12: Write test for `--help` output
- [ ] Step 13: Write test for `--version` output
- [ ] Step 14: Write test for `--verbose` flag
- [ ] Step 15: Write test for main command group structure
- [ ] Step 16: Write test for `python -m omniskill` invocation
- [ ] Step 17: Create `features/cli.feature` with Gherkin scenarios
- [ ] Step 18: Create `features/steps/cli_steps.py` with step definitions
- [ ] BDD Verification: `uv run behave features/cli.feature` passes
- [ ] Verification: `uv run pytest tests/test_cli.py -v` passes
- [ ] Advanced Test Verification: N/A
- [ ] Runtime Verification: `uv run omniskill --help` works correctly

---

### Task 4.2: Skill Creation CLI Command

> **Context:** Implement the `omniskill create <skill-name>` command that generates a new skill directory structure with proper files and templates.
>
> **Verification:** CLI command creates skill directory with `SKILL.md`, `datasets/` folder, and proper structure. Handles existing directories gracefully.
>
> **Requirement Coverage:** R7, R8, R10
>
> **Scenario Coverage:** `cli.feature` (skill creation scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - skill creation command
- **Simplification Focus:** Clear directory creation and template rendering
- **Advanced Test Coverage:** Example-based only
- **Status:** 🔴 TODO
- [ ] Step 1: Create `src/omniskill/commands/` directory
- [ ] Step 2: Create `src/omniskill/commands/__init__.py`
- [ ] Step 3: Create `src/omniskill/commands/create.py`
- [ ] Step 4: Import `click` and define `create` command function
- [ ] Step 5: Add `@click.argument('skill_name')` decorator
- [ ] Step 6: Add `--template` option for custom templates
- [ ] Step 7: Add `--force` / `-f` option to overwrite existing
- [ ] Step 8: Implement skill directory creation logic
- [ ] Step 9: Create `skills/{skill_name}/` directory
- [ ] Step 10: Create `skills/{skill_name}/datasets/` subdirectory
- [ ] Step 11: Create default `SKILL.md` template file
- [ ] Step 12: Template includes: Role, Knowledge Retrieval Action, Command, Instructions
- [ ] Step 13: Create `__init__.py` stub in skill directory
- [ ] Step 14: Add success message with path output
- [ ] Step 15: Add error handling for existing directory (without --force)
- [ ] Step 16: Add error handling for invalid skill names
- [ ] Step 17: Register `create` command in main CLI group
- [ ] Step 18: Create `tests/commands/test_create.py` with unit tests
- [ ] Step 19: Write test for successful skill creation
- [ ] Step 20: Write test for directory structure creation
- [ ] Step 21: Write test for SKILL.md content generation
- [ ] Step 22: Write test for existing directory handling (with --force)
- [ ] Step 23: Write test for existing directory error (without --force)
- [ ] Step 24: Write test for invalid skill name handling
- [ ] Step 25: Update `features/cli.feature` with skill creation scenarios
- [ ] Step 26: Update `features/steps/cli_steps.py` with creation step definitions
- [ ] BDD Verification: `uv run behave features/cli.feature` passes
- [ ] Verification: `uv run pytest tests/commands/test_create.py -v` passes
- [ ] Advanced Test Verification: N/A
- [ ] Runtime Verification: `uv run omniskill create test-skill` creates skill correctly

---

### Task 4.3: SKILL.md Template and Generation

> **Context:** Create the SKILL.md template that is generated for new skills. This file contains instructions for LLMs on how to use the skill, including the knowledge retrieval action and command execution instructions.
>
> **Verification:** Generated SKILL.md contains proper Role definition, Knowledge Retrieval Action with command template, step-by-step Instructions, and is formatted for LLM consumption.
>
> **Requirement Coverage:** R8, R10
>
> **Scenario Coverage:** `cli.feature` (SKILL.md generation scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - SKILL.md template
- **Simplification Focus:** Clear, comprehensive template with all required sections
- **Advanced Test Coverage:** Example-based only
- **Status:** 🔴 TODO
- [ ] Step 1: Create `src/omniskill/templates/` directory
- [ ] Step 2: Create `src/omniskill/templates/__init__.py`
- [ ] Step 3: Create `src/omniskill/templates/skill_md.py`
- [ ] Step 4: Define `SKILL_MD_TEMPLATE` constant with Jinja2-style template
- [ ] Step 5: Template Section: `# Role` - skill role definition
- [ ] Step 6: Template Section: `# Knowledge Retrieval Action` - core instruction
- [ ] Step 7: Template includes command template: `python -m omniskill search --query ...`
- [ ] Step 8: Template Section: `# Instructions` - step-by-step usage
- [ ] Step 9: Template includes instruction for extracting keywords
- [ ] Step 10: Template includes instruction for executing command
- [ ] Step 11: Template includes instruction for reading context injection
- [ ] Step 12: Template includes instruction for generating final output
- [ ] Step 13: Define `generate_skill_md(skill_name: str, skill_dir: str) -> str` function
- [ ] Step 14: Function fills template with skill-specific values
- [ ] Step 15: Function returns rendered SKILL.md content
- [ ] Step 16: Update `src/omniskill/commands/create.py` to use template function
- [ ] Step 17: Import `generate_skill_md` in create command
- [ ] Step 18: Use `generate_skill_md` when creating SKILL.md file
- [ ] Step 19: Create `tests/templates/test_skill_md.py` with unit tests
- [ ] Step 20: Write test for `generate_skill_md` function
- [ ] Step 21: Write test for template contains Role section
- [ ] Step 22: Write test for template contains Knowledge Retrieval Action section
- [ ] Step 23: Write test for template contains Instructions section
- [ ] Step 24: Write test for template contains command template
- [ ] Step 25: Write test for skill name substitution in output
- [ ] Step 26: Update `features/cli.feature` with SKILL.md content scenarios
- [ ] Step 27: Update `features/steps/cli_steps.py` with content checking steps
- [ ] BDD Verification: `uv run behave features/cli.feature` passes
- [ ] Verification: `uv run pytest tests/templates/test_skill_md.py -v` passes
- [ ] Advanced Test Verification: N/A
- [ ] Runtime Verification: `cat skills/test-skill/SKILL.md` shows properly formatted content

---

## Phase 5: Integration

### Task 5.1: Main Entry Point and Wiring

> **Context:** Wire all components together in a cohesive main entry point. This includes the full pipeline: CLI → Indexer → Searcher → Assembler → Output. Create the `omniskill search` command that orchestrates the entire flow.
>
> **Verification:** Running `omniskill search --query "..." --skill-dir ...` executes the full pipeline: indexes files, searches, assembles, and outputs formatted context.
>
> **Requirement Coverage:** R7, R10
>
> **Scenario Coverage:** `cli.feature` (end-to-end search scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - integrated entry point
- **Simplification Focus:** Clear orchestration of components
- **Advanced Test Coverage:** End-to-end property tests
- **Status:** 🔴 TODO
- [ ] Step 1: Create `src/omniskill/commands/search.py`
- [ ] Step 2: Import `click` and define `search` command function
- [ ] Step 3: Add `@click.argument('query')` decorator
- [ ] Step 4: Add `--skill-dir` option with required=True
- [ ] Step 5: Add `--format` option with choices=['xml', 'markdown'], default='xml'
- [ ] Step 6: Add `--limit` option with default=10
- [ ] Step 7: Add `--type` option for doc_type filtering
- [ ] Step 8: Add `--tag` option (multiple=True) for tag filtering
- [ ] Step 9: Implement search command logic
- [ ] Step 10: Validate skill_dir exists and is a directory
- [ ] Step 11: Create `OmniSkillConfig` with default settings
- [ ] Step 12: Instantiate `Indexer` (router with CSV and Markdown indexers)
- [ ] Step 13: Instantiate `BM25Searcher` with config
- [ ] Step 14: Instantiate `PromptAssembler`
- [ ] Step 15: Instantiate `SearchEngine` with all components
- [ ] Step 16: Call `search_engine.index_directory(skill_dir)`
- [ ] Step 17: Call `search_engine.search_and_assemble(query, format, limit, ...)`
- [ ] Step 18: Print assembled context to stdout
- [ ] Step 19: Add progress logging with `structlog`
- [ ] Step 20: Add error handling with proper exit codes
- [ ] Step 21: Register `search` command in main CLI group
- [ ] Step 22: Create `tests/commands/test_search.py` with integration tests
- [ ] Step 23: Write test for search command with CSV data
- [ ] Step 24: Write test for search command with Markdown data
- [ ] Step 25: Write test for search command with XML output
- [ ] Step 26: Write test for search command with Markdown output
- [ ] Step 27: Write test for search command with tag filtering
- [ ] Step 28: Write test for search command with doc_type filtering
- [ ] Step 29: Write test for search command error handling
- [ ] Step 30: Write end-to-end property test with Hypothesis
- [ ] Step 31: Update `features/cli.feature` with search command scenarios
- [ ] Step 32: Update `features/steps/cli_steps.py` with search command steps
- [ ] BDD Verification: `uv run behave features/cli.feature` passes
- [ ] Verification: `uv run pytest tests/commands/test_search.py -v` passes
- [ ] Advanced Test Verification: `uv run pytest tests/commands/test_search.py -k hypothesis -v` passes
- [ ] Runtime Verification: `uv run omniskill search "test query" --skill-dir skills/test-skill/` outputs formatted context

---

### Task 5.2: Configuration and Error Handling

> **Context:** Implement comprehensive configuration management and error handling across the framework. This includes config file support, environment variable integration, and consistent error handling with meaningful messages.
>
> **Verification:** Configuration loads from files and environment variables, error handling catches and reports all error conditions with helpful messages, and the framework degrades gracefully under error conditions.
>
> **Requirement Coverage:** R10 (Configuration), Error handling
>
> **Scenario Coverage:** `cli.feature` (error handling scenarios)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** New behavior - configuration and error handling
- **Simplification Focus:** Clear configuration hierarchy, explicit error types
- **Advanced Test Coverage:** Property tests for configuration validation
- **Status:** 🔴 TODO
- [ ] Step 1: Create `src/omniskill/config.py`
- [ ] Step 2: Import `msgspec` for configuration struct
- [ ] Step 3: Define `OmniSkillConfig` struct with `msgspec.Struct`
- [ ] Step 4: Add indexing settings: `csv_extensions`, `markdown_extensions`, `max_file_size_mb`
- [ ] Step 5: Add search settings: `default_search_limit`, `bm25_k1`, `bm25_b`
- [ ] Step 6: Add assembly settings: `default_output_format`, `max_context_length`
- [ ] Step 7: Add path settings: `skills_dir`, `core_dir`
- [ ] Step 8: Add `from_file(path: Path) -> OmniSkillConfig` class method
- [ ] Step 9: Add `from_env() -> OmniSkillConfig` class method
- [ ] Step 10: Add `merge(other: OmniSkillConfig) -> OmniSkillConfig` method
- [ ] Step 11: Define default config file locations: `./omniskill.toml`, `~/.config/omniskill/config.toml`
- [ ] Step 12: Use `toml` library for config file parsing
- [ ] Step 13: Create `src/omniskill/exceptions.py`
- [ ] Step 14: Define `OmniSkillError` base exception class
- [ ] Step 15: Define `ConfigurationError` for config-related errors
- [ ] Step 16: Define `IndexingError` for indexing failures
- [ ] Step 17: Define `SearchError` for search failures
- [ ] Step 18: Define `AssemblyError` for assembly failures
- [ ] Step 19: Define `FileError` for file operation failures
- [ ] Step 20: Add meaningful error messages to all exception classes
- [ ] Step 21: Create `tests/test_config.py` with unit tests
- [ ] Step 22: Write test for default config values
- [ ] Step 23: Write test for config file loading
- [ ] Step 24: Write test for environment variable loading
- [ ] Step 25: Write test for config merging
- [ ] Step 26: Write test for invalid config file handling
- [ ] Step 27: Write property test for config validation
- [ ] Step 28: Create `tests/test_exceptions.py` with unit tests
- [ ] Step 29: Write test for exception hierarchy
- [ ] Step 30: Write test for error message formatting
- [ ] Step 31: Write test for exception raising and catching
- [ ] Step 32: Update CLI commands to use new config system
- [ ] Step 33: Update CLI commands to use proper exception handling
- [ ] Step 34: Update `features/cli.feature` with config and error scenarios
- [ ] Step 35: Update `features/steps/cli_steps.py` with error handling steps
- [ ] BDD Verification: `uv run behave features/cli.feature` passes
- [ ] Verification: `uv run pytest tests/test_config.py tests/test_exceptions.py -v` passes
- [ ] Advanced Test Verification: `uv run pytest tests/test_config.py -k hypothesis -v` passes
- [ ] Runtime Verification: `uv run omniskill --config custom.toml search ...` uses custom config

---

### Task 5.3: End-to-End Testing and Documentation

> **Context:** Complete the framework with comprehensive end-to-end tests, documentation, and examples. This includes example skills, full integration tests, README documentation, and benchmark tests.
>
> **Verification:** All tests pass, example skills work correctly, documentation is complete, and benchmarks show acceptable performance.
>
> **Requirement Coverage:** All requirements (R1-R10)
>
> **Scenario Coverage:** All feature files (complete test suite)

- **Loop Type:** BDD+TDD
- **Behavioral Contract:** Complete framework validation
- **Simplification Focus:** Clear examples, comprehensive docs
- **Advanced Test Coverage:** Full test suite + benchmarks
- **Status:** 🔴 TODO
- [ ] Step 1: Create `examples/` directory
- [ ] Step 2: Create `examples/backend-api-master/` example skill
- [ ] Step 3: Add sample `api_standards.csv` with API conventions
- [ ] Step 4: Add sample `auth_patterns.md` with authentication examples
- [ ] Step 5: Add sample `db_best_practices.md` with database guidelines
- [ ] Step 6: Generate `SKILL.md` for backend-api-master example
- [ ] Step 7: Create `examples/README.md` explaining examples
- [ ] Step 8: Create `tests/test_e2e.py` with end-to-end tests
- [ ] Step 9: Write E2E test for backend-api-master skill indexing
- [ ] Step 10: Write E2E test for backend-api-master skill search
- [ ] Step 11: Write E2E test for backend-api-master skill assembly
- [ ] Step 12: Write E2E test for full CLI workflow
- [ ] Step 13: Add benchmark tests with `pytest-benchmark`
- [ ] Step 14: Write benchmark for CSV indexing (target: <100ms for 1000 rows)
- [ ] Step 15: Write benchmark for Markdown chunking (target: <100ms for 100KB)
- [ ] Step 16: Write benchmark for BM25 search (target: <50ms for 1000 docs)
- [ ] Step 17: Write benchmark for assembly (target: <20ms for 10 results)
- [ ] Step 18: Update `README.md` with framework documentation
- [ ] Step 19: Add Overview section explaining OmniSkill
- [ ] Step 20: Add Installation section with `pip install` or `uv` instructions
- [ ] Step 21: Add Quick Start section with basic usage example
- [ ] Step 22: Add Architecture section with diagram
- [ ] Step 23: Add CLI Reference section with all commands
- [ ] Step 24: Add Python API Reference section with examples
- [ ] Step 25: Add Contributing section with development setup
- [ ] Step 26: Add License section
- [ ] Step 27: Create `docs/` directory with additional documentation
- [ ] Step 28: Create `docs/architecture.md` with detailed architecture docs
- [ ] Step 29: Create `docs/api.md` with API documentation
- [ ] Step 30: Create `docs/tutorials.md` with step-by-step tutorials
- [ ] Step 31: Run full test suite: `just test-all`
- [ ] Step 32: Verify all tests pass
- [ ] Step 33: Run linting: `just lint`
- [ ] Step 34: Verify no lint errors
- [ ] Step 35: Run type checking: `ty check`
- [ ] Step 36: Verify no type errors
- [ ] Step 37: Run benchmarks: `uv run pytest tests/test_benchmarks.py`
- [ ] Step 38: Verify all benchmarks meet performance targets
- [ ] Step 39: Update `features/` with any missing scenarios
- [ ] Step 40: Run BDD tests: `uv run behave features/`
- [ ] Step 41: Verify all BDD tests pass
- [ ] BDD Verification: `uv run behave features/` passes (all features)
- [ ] Verification: `uv run pytest tests/ -v` passes (all tests)
- [ ] Advanced Test Verification: `uv run pytest tests/test_benchmarks.py` passes
- [ ] Runtime Verification: `uv run omniskill create my-skill && uv run omniskill search "test" --skill-dir skills/my-skill/` works end-to-end

---

## Definition of Done

The OmniSkill Framework implementation is complete when:

1. **All Tasks Complete**: Every task above is marked `🟢 DONE`
2. **All Tests Pass**: `pytest`, `behave`, and property tests all pass
3. **Type Safe**: `ty check` passes with zero errors
4. **Lint Clean**: `ruff check` passes with zero errors
5. **Formatted**: `ruff format` has been applied
6. **Documented**: All public APIs have docstrings, README is complete
7. **BDD Complete**: All Gherkin scenarios pass
8. **Performance**: Search latency <100ms for 10MB datasets
9. **CLI Working**: `omniskill create <skill-name>` generates valid skill structure
10. **Identity Aligned**: All placeholder names replaced with `omniskill`
11. **Examples Working**: Example skills (`backend-api-master`) work correctly
12. **Benchmarks Met**: All performance benchmarks meet targets

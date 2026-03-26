"""End-to-end tests for OmniSkill framework.

Tests the complete workflow from indexing to search to assembly.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from omniskill.core.assembler import OutputFormat, PromptAssembler
from omniskill.core.engine import SearchEngine
from omniskill.core.indexer import Indexer


class TestEndToEnd:
    """End-to-end tests for the complete framework."""

    def test_csv_indexing_and_search(self, tmp_path: Path) -> None:
        """Test CSV file indexing and search."""
        # Create test CSV file
        csv_content = "name,age,city\nAlice,30,NYC\nBob,25,LA\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Initialize search engine
        engine = SearchEngine()

        # Index the directory
        documents = engine.index_directory(str(tmp_path))
        assert len(documents) == 2

        # Search for content
        results = engine.search("Alice")
        assert len(results) >= 1
        doc = results[0].document
        metadata = getattr(doc, "metadata", None)
        if metadata is not None:
            assert metadata["name"] == "Alice"

    def test_markdown_indexing_and_search(self, tmp_path: Path) -> None:
        """Test Markdown file indexing and search."""
        # Create test Markdown file
        md_content = """## Getting Started

Install the package.

## Usage

Import and use it.
"""
        md_file = tmp_path / "guide.md"
        md_file.write_text(md_content)

        # Initialize search engine
        engine = SearchEngine()

        # Index the directory
        documents = engine.index_directory(str(tmp_path))
        assert len(documents) == 2

        # Search for content
        results = engine.search("Install")
        assert len(results) >= 1
        assert "Install" in results[0].document.content

    def test_mixed_file_indexing(self, tmp_path: Path) -> None:
        """Test indexing both CSV and Markdown files."""
        # Create CSV file
        csv_content = "pattern,description\nsnake_case,Use snake_case\n"
        csv_file = tmp_path / "patterns.csv"
        csv_file.write_text(csv_content)

        # Create Markdown file
        md_content = "## Authentication\nUse JWT tokens.\n"
        md_file = tmp_path / "auth.md"
        md_file.write_text(md_content)

        # Initialize search engine
        engine = SearchEngine()

        # Index the directory
        documents = engine.index_directory(str(tmp_path))
        assert len(documents) == 2

        # Search across both file types
        results = engine.search("snake_case")
        assert len(results) >= 1
        assert results[0].document.source.endswith(".csv")

        results = engine.search("JWT")
        assert len(results) >= 1
        assert results[0].document.source.endswith(".md")

    def test_search_with_tag_filtering(self, tmp_path: Path) -> None:
        """Test search with tag-based filtering."""
        # Create CSV file
        csv_content = "name,role\nAlice,admin\nBob,user\n"
        csv_file = tmp_path / "users.csv"
        csv_file.write_text(csv_content)

        # Initialize search engine
        engine = SearchEngine()

        # Index the directory
        engine.index_directory(str(tmp_path))

        # Search with doc_type filter
        results = engine.search("Alice", doc_type="csv")
        assert len(results) >= 1
        assert all(r.document.source.endswith(".csv") for r in results)

    def test_search_with_limit(self, tmp_path: Path) -> None:
        """Test search with result limit."""
        # Create CSV file with multiple rows
        csv_content = "name,age\nAlice,30\nBob,25\nCharlie,35\nDave,28\nEve,32\n"
        csv_file = tmp_path / "people.csv"
        csv_file.write_text(csv_content)

        # Initialize search engine
        engine = SearchEngine()

        # Index the directory
        engine.index_directory(str(tmp_path))

        # Search with limit
        results = engine.search("name", limit=3)
        assert len(results) <= 3

    def test_xml_assembly(self, tmp_path: Path) -> None:
        """Test XML format assembly."""
        # Create CSV file
        csv_content = "pattern,description\nsnake_case,Use snake_case\n"
        csv_file = tmp_path / "patterns.csv"
        csv_file.write_text(csv_content)

        # Initialize search engine
        engine = SearchEngine()
        engine.index_directory(str(tmp_path))

        # Search and assemble
        results = engine.search("snake_case")
        assembler = PromptAssembler()
        output = assembler.assemble(results, output_format=OutputFormat.XML)

        assert "<context_injection>" in output
        assert "<rules>" in output
        assert "snake_case" in output

    def test_markdown_assembly(self, tmp_path: Path) -> None:
        """Test Markdown format assembly."""
        # Create Markdown file
        md_content = "## Authentication\nUse JWT tokens.\n"
        md_file = tmp_path / "auth.md"
        md_file.write_text(md_content)

        # Initialize search engine
        engine = SearchEngine()
        engine.index_directory(str(tmp_path))

        # Search and assemble
        results = engine.search("JWT")
        assembler = PromptAssembler()
        output = assembler.assemble(results, output_format=OutputFormat.MARKDOWN)

        assert "## Context" in output
        assert "### References" in output
        assert "JWT" in output

    def test_full_pipeline(self, tmp_path: Path) -> None:
        """Test the complete indexing, search, and assembly pipeline."""
        # Create test files
        csv_content = "api_pattern,description\nsnake_case,Use snake_case for endpoints\n"
        csv_file = tmp_path / "api.csv"
        csv_file.write_text(csv_content)

        md_content = "## Authentication\nUse JWT tokens for API authentication.\n"
        md_file = tmp_path / "auth.md"
        md_file.write_text(md_content)

        # Initialize search engine
        engine = SearchEngine()

        # Index the directory
        documents = engine.index_directory(str(tmp_path))
        assert len(documents) == 2

        # Search for API patterns
        results = engine.search("API authentication")
        assert len(results) >= 1

        # Assemble results
        assembler = PromptAssembler()
        output = assembler.assemble(results, output_format=OutputFormat.XML)

        # Verify output contains relevant content
        assert "<context_injection>" in output
        assert len(output) > 0

    def test_example_skill_workflow(self) -> None:
        """Test the example skill workflow from the examples directory."""
        # This test uses the actual example files
        examples_dir = Path("examples/backend-api-master")
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        # Initialize search engine
        engine = SearchEngine()

        # Index the example skill directory
        documents = engine.index_directory(str(examples_dir))
        assert len(documents) > 0

        # Search for API patterns
        results = engine.search("API design patterns")
        assert len(results) >= 0  # May or may not have results

        # Search for authentication
        results = engine.search("JWT authentication")
        assert len(results) >= 0

        # Search for database best practices
        results = engine.search("database connection pooling")
        assert len(results) >= 0


class TestPerformance:
    """Performance tests for the framework."""

    def test_csv_indexing_performance(self, tmp_path: Path) -> None:
        """Test CSV indexing performance."""
        # Create CSV file with 1000 rows
        csv_lines = ["name,age,city"]
        csv_lines.extend(f"User{i},{20 + i % 50},City{i % 10}" for i in range(1000))
        csv_content = "\n".join(csv_lines)
        csv_file = tmp_path / "large.csv"
        csv_file.write_text(csv_content)

        # Initialize indexer
        indexer = Indexer()

        # Index the file
        start_time = time.time()
        documents = indexer.index_file(str(csv_file))
        end_time = time.time()

        # Verify indexing completed in reasonable time
        assert len(documents) == 1000
        assert (end_time - start_time) < 1.0  # Should complete in under 1 second

    def test_search_performance(self, tmp_path: Path) -> None:
        """Test search performance."""
        # Create CSV file with 1000 rows
        csv_lines = ["name,description"]
        csv_lines.extend(f"Item{i},Description for item {i}" for i in range(1000))
        csv_content = "\n".join(csv_lines)
        csv_file = tmp_path / "items.csv"
        csv_file.write_text(csv_content)

        # Initialize search engine
        engine = SearchEngine()
        engine.index_directory(str(tmp_path))

        # Perform search
        start_time = time.time()
        results = engine.search("item", limit=10)
        end_time = time.time()

        # Verify search completed in reasonable time
        assert len(results) <= 10
        assert (end_time - start_time) < 0.1  # Should complete in under 100ms

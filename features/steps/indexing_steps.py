"""Step definitions for indexing.feature."""

from __future__ import annotations

import contextlib
import tempfile
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import msgspec
import pytest
from behave import given, then, when

from omniskill.core.indexer import CsvIndexer, Indexer, MarkdownIndexer
from omniskill.models import Chunk, Document, SearchResult


# Shared context for storing created objects
@given("the core data models are defined")
def step_core_models_defined(context: Any) -> None:
    """Verify that the core data models are available."""
    assert Document is not None
    assert Chunk is not None
    assert SearchResult is not None
    context.documents = {}
    context.chunks = {}
    context.search_results = []


@when("I create a Document with:")
def step_create_document(context: Any) -> None:
    """Create a Document from table data."""
    table = context.table
    data: dict[str, Any] = {}

    for row in table:
        key = row["field"]
        value = row["value"]

        # Convert Python literals
        if value == "{}":
            value = {}
        elif value == "()":
            value = ()
        elif value.startswith("(") and value.endswith(")"):
            # Handle tuple with values like ("tag1", "tag2")
            with contextlib.suppress(SyntaxError, NameError):
                value = eval(value)  # noqa: S307
        else:
            with contextlib.suppress(SyntaxError, NameError):
                value = eval(value)  # noqa: S307

        data[key] = value

    document = Document(
        id=data["id"],
        source=data["source"],
        content=data["content"],
        metadata=data.get("metadata", {}),
        tags=data.get("tags", ()),
    )

    context.current_document = document
    context.documents[document.id] = document


@then("the Document should be created successfully")
def step_document_created(context: Any) -> None:
    """Verify that a Document was created."""
    assert hasattr(context, "current_document")
    assert isinstance(context.current_document, Document)


@then("the Document should be immutable")
def step_document_immutable(context: Any) -> None:
    """Verify that Document cannot be modified."""
    doc = context.current_document
    with pytest.raises(FrozenInstanceError):
        doc.content = "new content"


@when("I create a Chunk with:")
def step_create_chunk(context: Any) -> None:
    """Create a Chunk from table data."""
    table = context.table
    data: dict[str, Any] = {}

    for row in table:
        key = row["field"]
        value = row["value"]

        if value == "None":
            value = None
        elif value == "()":
            value = ()
        elif value.startswith("(") and value.endswith(")"):
            with contextlib.suppress(SyntaxError, NameError):
                value = eval(value)  # noqa: S307
        else:
            with contextlib.suppress(SyntaxError, NameError):
                value = eval(value)  # noqa: S307

        data[key] = value

    chunk = Chunk(
        id=data["id"],
        source=data["source"],
        content=data["content"],
        header_level=data.get("header_level"),
        header_text=data.get("header_text"),
        tags=data.get("tags", ()),
    )

    context.current_chunk = chunk
    context.chunks[chunk.id] = chunk


@then("the Chunk should be created successfully")
def step_chunk_created(context: Any) -> None:
    """Verify that a Chunk was created."""
    assert hasattr(context, "current_chunk")
    assert isinstance(context.current_chunk, Chunk)


@then("the Chunk should be immutable")
def step_chunk_immutable(context: Any) -> None:
    """Verify that Chunk cannot be modified."""
    chunk = context.current_chunk
    with pytest.raises(FrozenInstanceError):
        chunk.content = "new content"


@given('a Document exists with id "{doc_id}"')
def step_given_document_exists(context: Any, doc_id: str) -> None:
    """Create a Document with the given ID if it doesn't exist."""
    if not hasattr(context, "documents"):
        context.documents = {}

    if doc_id not in context.documents:
        doc = Document(
            id=doc_id,
            source=f"data/{doc_id}.csv",
            content=f"Content for {doc_id}",
            metadata={},
            tags=(),
        )
        context.documents[doc_id] = doc


@given('a Chunk exists with id "{chunk_id}"')
def step_given_chunk_exists(context: Any, chunk_id: str) -> None:
    """Create a Chunk with the given ID if it doesn't exist."""
    if not hasattr(context, "chunks"):
        context.chunks = {}

    if chunk_id not in context.chunks:
        chunk = Chunk(
            id=chunk_id,
            source=f"docs/{chunk_id}.md",
            content=f"Content for {chunk_id}",
            header_level=1,
            header_text=f"Header for {chunk_id}",
            tags=(),
        )
        context.chunks[chunk_id] = chunk


@when("I create a SearchResult with:")
def step_create_search_result(context: Any) -> None:
    """Create a SearchResult from table data."""
    table = context.table
    data: dict[str, Any] = {}

    for row in table:
        key = row["field"]
        value = row["value"]

        if key == "score":
            value = float(value)
        elif key == "document":
            # Look up document or chunk by ID
            doc_id = value
            if hasattr(context, "documents") and doc_id in context.documents:
                value = context.documents[doc_id]
            elif hasattr(context, "chunks") and doc_id in context.chunks:
                value = context.chunks[doc_id]
            else:
                msg = f"Document or Chunk with id {doc_id} not found"
                raise ValueError(msg)

        data[key] = value

    result = SearchResult(
        document=data["document"],
        score=data["score"],
    )

    context.current_search_result = result
    if not hasattr(context, "search_results"):
        context.search_results = []
    context.search_results.append(result)


@then("the SearchResult should be created successfully")
def step_search_result_created(context: Any) -> None:
    """Verify that a SearchResult was created."""
    assert hasattr(context, "current_search_result")
    assert isinstance(context.current_search_result, SearchResult)


@then("the SearchResult should reference the Document")
def step_search_result_references_document(context: Any) -> None:
    """Verify that SearchResult references a Document."""
    result = context.current_search_result
    assert isinstance(result.document, Document)


@then("the SearchResult should reference the Chunk")
def step_search_result_references_chunk(context: Any) -> None:
    """Verify that SearchResult references a Chunk."""
    result = context.current_search_result
    assert isinstance(result.document, Chunk)


@given("multiple Documents exist")
def step_multiple_documents_exist(context: Any) -> None:
    """Create multiple documents for hash testing."""
    if not hasattr(context, "documents"):
        context.documents = {}

    for i in range(3):
        doc_id = f"doc-{i:03d}"
        doc = Document(
            id=doc_id,
            source=f"data/{doc_id}.csv",
            content=f"Content for {doc_id}",
            metadata={"index": i},
            tags=("tag1", "tag2"),
        )
        context.documents[doc_id] = doc


@when("I add them to a set")
def step_add_to_set(context: Any) -> None:
    """Add documents to a set."""
    doc_set = set(context.documents.values())
    context.document_set = doc_set


@then("the set should contain all unique Documents")
def step_set_contains_documents(context: Any) -> None:
    """Verify that all documents are in the set."""
    assert len(context.document_set) == len(context.documents)
    for doc in context.documents.values():
        assert doc in context.document_set


@given("multiple Chunks exist")
def step_multiple_chunks_exist(context: Any) -> None:
    """Create multiple chunks for hash testing."""
    if not hasattr(context, "chunks"):
        context.chunks = {}

    for i in range(3):
        chunk_id = f"chunk-{i:03d}"
        chunk = Chunk(
            id=chunk_id,
            source=f"docs/{chunk_id}.md",
            content=f"Content for {chunk_id}",
            header_level=(i % 6) + 1,
            header_text=f"Header {i}",
            tags=(),
        )
        context.chunks[chunk_id] = chunk


@then("the set should contain all unique Chunks")
def step_set_contains_chunks(context: Any) -> None:
    """Verify that all chunks are in the set."""
    chunk_set = set(context.chunks.values())
    assert len(chunk_set) == len(context.chunks)
    for chunk in context.chunks.values():
        assert chunk in chunk_set


@given("a Document exists with metadata")
def step_document_with_metadata(context: Any) -> None:
    """Create a document with metadata for JSON testing."""
    if not hasattr(context, "documents"):
        context.documents = {}

    doc = Document(
        id="doc-json-test",
        source="data/test.csv",
        content="Test content for JSON",
        metadata={"author": "Test Author", "version": 1, "draft": True},
        tags=("json", "test"),
    )
    context.documents[doc.id] = doc
    context.current_document = doc


@when("I serialize the Document to JSON")
def step_serialize_document(context: Any) -> None:
    """Serialize document to JSON using msgspec."""
    doc = context.current_document
    # Convert to dict then encode
    doc_dict = {
        "id": doc.id,
        "source": doc.source,
        "content": doc.content,
        "metadata": doc.metadata,
        "tags": doc.tags,
    }
    context.json_bytes = msgspec.json.encode(doc_dict)


@then("the JSON should contain all Document fields")
def step_json_contains_fields(context: Any) -> None:
    """Verify JSON contains all document fields."""
    decoded = msgspec.json.decode(context.json_bytes)
    doc = context.current_document

    assert decoded["id"] == doc.id
    assert decoded["source"] == doc.source
    assert decoded["content"] == doc.content
    assert decoded["metadata"] == doc.metadata
    assert decoded["tags"] == list(doc.tags)


@given("a Chunk exists with header information")
def step_chunk_with_header(context: Any) -> None:
    """Create a chunk with header for JSON testing."""
    if not hasattr(context, "chunks"):
        context.chunks = {}

    chunk = Chunk(
        id="chunk-json-test",
        source="docs/test.md",
        content="Chunk content for JSON",
        header_level=2,
        header_text="Test Header",
        tags=("json", "chunk"),
    )
    context.chunks[chunk.id] = chunk
    context.current_chunk = chunk


@when("I serialize the Chunk to JSON")
def step_serialize_chunk(context: Any) -> None:
    """Serialize chunk to JSON using msgspec."""
    chunk = context.current_chunk
    chunk_dict = {
        "id": chunk.id,
        "source": chunk.source,
        "content": chunk.content,
        "header_level": chunk.header_level,
        "header_text": chunk.header_text,
        "tags": chunk.tags,
    }
    context.json_bytes = msgspec.json.encode(chunk_dict)


@then("the JSON should contain all Chunk fields")
def step_json_contains_chunk_fields(context: Any) -> None:
    """Verify JSON contains all chunk fields."""
    decoded = msgspec.json.decode(context.json_bytes)
    chunk = context.current_chunk

    assert decoded["id"] == chunk.id
    assert decoded["source"] == chunk.source
    assert decoded["content"] == chunk.content
    assert decoded["header_level"] == chunk.header_level
    assert decoded["header_text"] == chunk.header_text
    assert decoded["tags"] == list(chunk.tags)


@given("multiple SearchResults exist with different scores")
def step_multiple_search_results(context: Any) -> None:
    """Create multiple search results for sorting."""
    if not hasattr(context, "documents"):
        context.documents = {}

    # Create documents with different scores
    results = []
    for i, score in enumerate([0.75, 0.95, 0.5, 0.85]):
        doc = Document(
            id=f"doc-sort-{i}",
            source=f"data/doc{i}.csv",
            content=f"Content {i}",
            metadata={},
            tags=(),
        )
        context.documents[doc.id] = doc
        results.append(SearchResult(document=doc, score=score))

    context.search_results = results


@when("I sort them by score")
def step_sort_by_score(context: Any) -> None:
    """Sort search results by score."""
    context.sorted_results = sorted(
        context.search_results,
        key=lambda r: r.score,
        reverse=True,
    )


@then("they should be ordered from highest to lowest score")
def step_verify_score_order(context: Any) -> None:
    """Verify results are sorted by score descending."""
    scores = [r.score for r in context.sorted_results]
    assert scores == sorted(scores, reverse=True)


# --- Indexer step definitions ---


@given('a CSV file "{filename}" with content:')
def step_csv_file_with_content(context: Any, filename: str) -> None:
    """Create a temporary CSV file with given content."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="behave_indexer_"))
    file_path = tmp_dir / filename
    file_path.write_text(context.text or "")
    context.index_file_path = str(file_path)


@given('a Markdown file "{filename}" with content:')
def step_markdown_file_with_content(context: Any, filename: str) -> None:
    """Create a temporary Markdown file with given content."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="behave_indexer_"))
    file_path = tmp_dir / filename
    file_path.write_text(context.text or "")
    context.index_file_path = str(file_path)


@given('an unsupported file "{filename}" with content "{content}"')
def step_unsupported_file(context: Any, filename: str, content: str) -> None:
    """Create a temporary unsupported file."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="behave_indexer_"))
    file_path = tmp_dir / filename
    file_path.write_text(content)
    context.index_file_path = str(file_path)


@when("I index the file with CsvIndexer")
def step_index_with_csv_indexer(context: Any) -> None:
    """Index file with CsvIndexer."""
    indexer = CsvIndexer()
    context.index_results = indexer.index_file(context.index_file_path)


@when("I index the file with MarkdownIndexer")
def step_index_with_markdown_indexer(context: Any) -> None:
    """Index file with MarkdownIndexer."""
    indexer = MarkdownIndexer()
    context.index_results = indexer.index_file(context.index_file_path)


@when("I index the file with Indexer")
def step_index_with_router(context: Any) -> None:
    """Index file with the Indexer router."""
    indexer = Indexer()
    try:
        context.index_results = indexer.index_file(context.index_file_path)
        context.index_error = None
    except ValueError as e:
        context.index_error = e
        context.index_results = []


@then("I should get {count:d} Documents")
def step_should_get_documents(context: Any, count: int) -> None:
    """Verify document count."""
    assert len(context.index_results) == count
    for item in context.index_results:
        assert isinstance(item, Document)


@then("I should get {count:d} Chunks")
def step_should_get_chunks(context: Any, count: int) -> None:
    """Verify chunk count."""
    assert len(context.index_results) == count
    for item in context.index_results:
        assert isinstance(item, Chunk)


@then('Document {idx:d} should have metadata key "{key}" with value "{value}"')
def step_document_metadata(context: Any, idx: int, key: str, value: str) -> None:
    """Verify document metadata."""
    doc = context.index_results[idx]
    assert isinstance(doc, Document)
    assert doc.metadata[key] == value


@then('Chunk {idx:d} should have header_text "{text}"')
def step_chunk_header_text(context: Any, idx: int, text: str) -> None:
    """Verify chunk header text."""
    chunk = context.index_results[idx]
    assert isinstance(chunk, Chunk)
    assert chunk.header_text == text


@then("Chunk {idx:d} should have header_level {level:d}")
def step_chunk_header_level(context: Any, idx: int, level: int) -> None:
    """Verify chunk header level."""
    chunk = context.index_results[idx]
    assert isinstance(chunk, Chunk)
    assert chunk.header_level == level


@then("the results should be Documents")
def step_results_are_documents(context: Any) -> None:
    """Verify results are Documents."""
    assert len(context.index_results) > 0
    for item in context.index_results:
        assert isinstance(item, Document)


@then("the results should be Chunks")
def step_results_are_chunks(context: Any) -> None:
    """Verify results are Chunks."""
    assert len(context.index_results) > 0
    for item in context.index_results:
        assert isinstance(item, Chunk)


@then("a ValueError should be raised")
def step_value_error_raised(context: Any) -> None:
    """Verify ValueError was raised."""
    assert context.index_error is not None
    assert isinstance(context.index_error, ValueError)

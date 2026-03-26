"""Tests for core data models."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given
from hypothesis.strategies import (
    dictionaries,
    floats,
    integers,
    none,
    one_of,
    text,
    tuples,
)

from omniskill.models import Chunk, Document, SearchResult


class TestDocument:
    """Tests for Document dataclass."""

    def test_document_instantiation(self) -> None:
        """Test that a Document can be created with all required fields."""
        doc = Document(
            id="doc-001",
            source="data/docs.csv",
            content="This is a test document.",
            metadata={"author": "Test Author", "date": "2024-01-01"},
            tags=("tag1", "tag2"),
        )

        assert doc.id == "doc-001"
        assert doc.source == "data/docs.csv"
        assert doc.content == "This is a test document."
        assert doc.metadata == {"author": "Test Author", "date": "2024-01-01"}
        assert doc.tags == ("tag1", "tag2")

    def test_document_empty_metadata(self) -> None:
        """Test Document with empty metadata."""
        doc = Document(
            id="doc-002",
            source="data/docs.csv",
            content="Test content",
            metadata={},
            tags=(),
        )

        assert doc.metadata == {}
        assert doc.tags == ()

    def test_document_immutable(self) -> None:
        """Test that Document is immutable (frozen dataclass)."""
        doc = Document(
            id="doc-003",
            source="data/docs.csv",
            content="Test",
            metadata={},
            tags=(),
        )

        with pytest.raises(FrozenInstanceError):
            setattr(doc, "id", "new-id")  # noqa: B010

    def test_document_hashable(self) -> None:
        """Test that Document can be used in sets and as dict keys."""
        doc1 = Document(
            id="doc-001",
            source="data/docs.csv",
            content="Test",
            metadata={},
            tags=(),
        )
        doc2 = Document(
            id="doc-002",
            source="data/docs.csv",
            content="Test 2",
            metadata={},
            tags=(),
        )

        doc_set = {doc1, doc2}
        assert len(doc_set) == 2

        doc_dict = {doc1: "value1", doc2: "value2"}
        assert doc_dict[doc1] == "value1"


class TestChunk:
    """Tests for Chunk dataclass."""

    def test_chunk_instantiation(self) -> None:
        """Test that a Chunk can be created with all required fields."""
        chunk = Chunk(
            id="chunk-001",
            source="docs/guide.md",
            content="This is a chunk of content.",
            header_level=2,
            header_text="Getting Started",
            tags=("guide", "tutorial"),
        )

        assert chunk.id == "chunk-001"
        assert chunk.source == "docs/guide.md"
        assert chunk.content == "This is a chunk of content."
        assert chunk.header_level == 2
        assert chunk.header_text == "Getting Started"
        assert chunk.tags == ("guide", "tutorial")

    def test_chunk_no_header(self) -> None:
        """Test Chunk without header information."""
        chunk = Chunk(
            id="chunk-002",
            source="docs/guide.md",
            content="Content without header.",
            header_level=None,
            header_text=None,
            tags=(),
        )

        assert chunk.header_level is None
        assert chunk.header_text is None

    def test_chunk_immutable(self) -> None:
        """Test that Chunk is immutable (frozen dataclass)."""
        chunk = Chunk(
            id="chunk-003",
            source="docs/guide.md",
            content="Test",
            header_level=None,
            header_text=None,
            tags=(),
        )

        with pytest.raises(FrozenInstanceError):
            setattr(chunk, "content", "new content")  # noqa: B010

    def test_chunk_hashable(self) -> None:
        """Test that Chunk can be used in sets and as dict keys."""
        chunk1 = Chunk(
            id="chunk-001",
            source="docs/guide.md",
            content="Test",
            header_level=None,
            header_text=None,
            tags=(),
        )

        chunk_set = {chunk1}
        assert len(chunk_set) == 1

        chunk_dict = {chunk1: "value"}
        assert chunk_dict[chunk1] == "value"


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_search_result_with_document(self) -> None:
        """Test SearchResult with Document."""
        doc = Document(
            id="doc-001",
            source="data/docs.csv",
            content="Test document content.",
            metadata={},
            tags=(),
        )

        result = SearchResult(
            document=doc,
            score=0.95,
        )

        assert result.document == doc
        assert result.score == 0.95

    def test_search_result_with_chunk(self) -> None:
        """Test SearchResult with Chunk."""
        chunk = Chunk(
            id="chunk-001",
            source="docs/guide.md",
            content="Chunk content.",
            header_level=1,
            header_text="Introduction",
            tags=(),
        )

        result = SearchResult(
            document=chunk,
            score=0.87,
        )

        assert result.document == chunk
        assert result.score == 0.87

    def test_search_result_zero_score(self) -> None:
        """Test SearchResult with zero score."""
        doc = Document(
            id="doc-001",
            source="data/docs.csv",
            content="Test",
            metadata={},
            tags=(),
        )

        result = SearchResult(document=doc, score=0.0)
        assert result.score == 0.0

    def test_search_result_immutable(self) -> None:
        """Test that SearchResult is immutable (frozen dataclass)."""
        doc = Document(
            id="doc-001",
            source="data/docs.csv",
            content="Test",
            metadata={},
            tags=(),
        )

        result = SearchResult(document=doc, score=0.5)

        with pytest.raises(FrozenInstanceError):
            setattr(result, "score", 0.8)  # noqa: B010

    def test_search_result_hashable(self) -> None:
        """Test that SearchResult can be used in sets and as dict keys."""
        doc = Document(
            id="doc-001",
            source="data/docs.csv",
            content="Test",
            metadata={},
            tags=(),
        )

        result = SearchResult(document=doc, score=0.5)

        result_set = {result}
        assert len(result_set) == 1

        result_dict = {result: "value"}
        assert result_dict[result] == "value"


# Property-based tests using Hypothesis


class TestDocumentProperties:
    """Property-based tests for Document."""

    @given(
        doc_id=text(min_size=1),
        source=text(min_size=1),
        content=text(),
        metadata=dictionaries(text(), text() | integers() | none()),
        tags=tuples(text(min_size=1)),
    )
    def test_document_properties(
        self,
        doc_id: str,
        source: str,
        content: str,
        metadata: dict,
        tags: tuple,
    ) -> None:
        """Test Document can be created with arbitrary valid data."""
        doc = Document(
            id=doc_id,
            source=source,
            content=content,
            metadata=metadata,
            tags=tags,
        )

        assert doc.id == doc_id
        assert doc.source == source
        assert doc.content == content
        assert doc.metadata == metadata
        assert doc.tags == tags


class TestChunkProperties:
    """Property-based tests for Chunk."""

    @given(
        chunk_id=text(min_size=1),
        source=text(min_size=1),
        content=text(),
        header_level=one_of(none(), integers(min_value=1, max_value=6)),
        header_text=one_of(none(), text()),
        tags=tuples(text(min_size=1)),
    )
    def test_chunk_properties(
        self,
        chunk_id: str,
        source: str,
        content: str,
        header_level: int | None,
        header_text: str | None,
        tags: tuple,
    ) -> None:
        """Test Chunk can be created with arbitrary valid data."""
        chunk = Chunk(
            id=chunk_id,
            source=source,
            content=content,
            header_level=header_level,
            header_text=header_text,
            tags=tags,
        )

        assert chunk.id == chunk_id
        assert chunk.source == source
        assert chunk.content == content
        assert chunk.header_level == header_level
        assert chunk.header_text == header_text
        assert chunk.tags == tags


class TestSearchResultProperties:
    """Property-based tests for SearchResult."""

    @given(
        score=floats(min_value=0.0, max_value=1.0),
    )
    def test_search_result_with_document(self, score: float) -> None:
        """Test SearchResult can be created with Document."""
        doc = Document(
            id="doc-test",
            source="test.csv",
            content="Test content",
            metadata={},
            tags=(),
        )

        result = SearchResult(document=doc, score=score)

        assert result.document == doc
        assert result.score == score

    @given(
        score=floats(min_value=0.0, max_value=1.0),
    )
    def test_search_result_with_chunk(self, score: float) -> None:
        """Test SearchResult can be created with Chunk."""
        chunk = Chunk(
            id="chunk-test",
            source="test.md",
            content="Test chunk content",
            header_level=1,
            header_text="Header",
            tags=(),
        )

        result = SearchResult(document=chunk, score=score)

        assert result.document == chunk
        assert result.score == score

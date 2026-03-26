"""Tests for protocol definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from omniskill.models import Chunk, Document, SearchResult
from omniskill.protocols import AssemblerProtocol, IndexerProtocol, SearcherProtocol

if TYPE_CHECKING:
    from pathlib import Path


# ---------------------------------------------------------------------------
# Runtime checkability tests
# ---------------------------------------------------------------------------


class TestProtocolRuntimeCheckable:
    """Verify all protocols are runtime-checkable via isinstance."""

    def test_indexer_protocol_is_runtime_checkable(self) -> None:
        """IndexerProtocol must support isinstance() checks."""

        class ConformingIndexer:
            def index_file(self, path: Path) -> list[Document | Chunk]:
                return []

            def index_directory(self, path: Path) -> list[Document | Chunk]:
                return []

            def supports_file(self, path: Path) -> bool:
                return True

        obj = ConformingIndexer()
        assert isinstance(obj, IndexerProtocol)

    def test_searcher_protocol_is_runtime_checkable(self) -> None:
        """SearcherProtocol must support isinstance() checks."""

        class ConformingSearcher:
            def add_documents(self, documents: list[Document | Chunk]) -> None:
                pass

            def search(self, query: str, limit: int = 10) -> list[SearchResult]:
                return []

        obj = ConformingSearcher()
        assert isinstance(obj, SearcherProtocol)

    def test_assembler_protocol_is_runtime_checkable(self) -> None:
        """AssemblerProtocol must support isinstance() checks."""

        class ConformingAssembler:
            def assemble(self, results: list[SearchResult], output_format: str = "xml") -> str:
                return ""

        obj = ConformingAssembler()
        assert isinstance(obj, AssemblerProtocol)


# ---------------------------------------------------------------------------
# Conforming class passes protocol check
# ---------------------------------------------------------------------------


class TestProtocolConformance:
    """Verify conforming classes pass isinstance checks."""

    def test_full_indexer_conforms(self) -> None:
        """A class with all required methods passes isinstance check."""

        class FullIndexer:
            def index_file(self, path: Path) -> list[Document | Chunk]:
                return [
                    Document(
                        id="1",
                        source=str(path),
                        content="test",
                        metadata={},
                        tags=(),
                    )
                ]

            def index_directory(self, path: Path) -> list[Document | Chunk]:
                return []

            def supports_file(self, path: Path) -> bool:
                return path.suffix in {".csv", ".md"}

        assert isinstance(FullIndexer(), IndexerProtocol)

    def test_full_searcher_conforms(self) -> None:
        """A class with all required methods passes isinstance check."""

        class FullSearcher:
            def add_documents(self, documents: list[Document | Chunk]) -> None:
                pass

            def search(self, query: str, limit: int = 10) -> list[SearchResult]:
                return [
                    SearchResult(
                        document=Document(
                            id="1",
                            source="test",
                            content=query,
                            metadata={},
                            tags=(),
                        ),
                        score=1.0,
                    )
                ]

        assert isinstance(FullSearcher(), SearcherProtocol)

    def test_full_assembler_conforms(self) -> None:
        """A class with all required methods passes isinstance check."""

        class FullAssembler:
            def assemble(self, results: list[SearchResult], output_format: str = "xml") -> str:
                return f"<results count='{len(results)}'/>"

        assert isinstance(FullAssembler(), AssemblerProtocol)


# ---------------------------------------------------------------------------
# Non-conforming class fails protocol check
# ---------------------------------------------------------------------------


class TestProtocolNonConformance:
    """Verify non-conforming classes fail isinstance checks."""

    def test_missing_index_file_fails(self) -> None:
        """A class missing index_file does not conform to IndexerProtocol."""

        class PartialIndexer:
            def index_directory(self, path: Path) -> list[Document | Chunk]:
                return []

            def supports_file(self, path: Path) -> bool:
                return True

        assert not isinstance(PartialIndexer(), IndexerProtocol)

    def test_missing_index_directory_fails(self) -> None:
        """A class missing index_directory does not conform to IndexerProtocol."""

        class PartialIndexer:
            def index_file(self, path: Path) -> list[Document | Chunk]:
                return []

            def supports_file(self, path: Path) -> bool:
                return True

        assert not isinstance(PartialIndexer(), IndexerProtocol)

    def test_missing_supports_file_fails(self) -> None:
        """A class missing supports_file does not conform to IndexerProtocol."""

        class PartialIndexer:
            def index_file(self, path: Path) -> list[Document | Chunk]:
                return []

            def index_directory(self, path: Path) -> list[Document | Chunk]:
                return []

        assert not isinstance(PartialIndexer(), IndexerProtocol)

    def test_empty_class_fails_all_protocols(self) -> None:
        """An empty class does not conform to any protocol."""

        class Empty:
            pass

        obj = Empty()
        assert not isinstance(obj, IndexerProtocol)
        assert not isinstance(obj, SearcherProtocol)
        assert not isinstance(obj, AssemblerProtocol)

    def test_missing_add_documents_fails(self) -> None:
        """A class missing add_documents does not conform to SearcherProtocol."""

        class PartialSearcher:
            def search(self, query: str, limit: int = 10) -> list[SearchResult]:
                return []

        assert not isinstance(PartialSearcher(), SearcherProtocol)

    def test_missing_search_fails(self) -> None:
        """A class missing search does not conform to SearcherProtocol."""

        class PartialSearcher:
            def add_documents(self, documents: list[Document | Chunk]) -> None:
                pass

        assert not isinstance(PartialSearcher(), SearcherProtocol)

    def test_missing_assemble_fails(self) -> None:
        """A class without assemble does not conform to AssemblerProtocol."""

        class PartialAssembler:
            def other_method(self) -> None:
                pass

        assert not isinstance(PartialAssembler(), AssemblerProtocol)


# ---------------------------------------------------------------------------
# Protocol method signatures
# ---------------------------------------------------------------------------


class TestProtocolSignatures:
    """Verify protocols expose the expected method names."""

    def test_indexer_protocol_has_required_methods(self) -> None:
        assert hasattr(IndexerProtocol, "index_file")
        assert hasattr(IndexerProtocol, "index_directory")
        assert hasattr(IndexerProtocol, "supports_file")

    def test_searcher_protocol_has_required_methods(self) -> None:
        assert hasattr(SearcherProtocol, "add_documents")
        assert hasattr(SearcherProtocol, "search")

    def test_assembler_protocol_has_required_methods(self) -> None:
        assert hasattr(AssemblerProtocol, "assemble")

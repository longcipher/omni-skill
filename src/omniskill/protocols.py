"""Protocol interfaces for core modules.

Defines the contracts between indexer, searcher, and assembler components
using typing.Protocol for structural subtyping. All protocols are
runtime-checkable via @runtime_checkable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from pathlib import Path

    from omniskill.models import Chunk, Document, SearchResult


@runtime_checkable
class IndexerProtocol(Protocol):
    """Protocol for file indexers.

    Implementations parse files into Document or Chunk objects for
    downstream search and retrieval.
    """

    def index_file(self, path: Path) -> list[Document | Chunk]:
        """Index a single file.

        Args:
            path: Path to the file to index.

        Returns:
            A list of Document or Chunk objects extracted from the file.

        """
        ...

    def index_directory(self, path: Path) -> list[Document | Chunk]:
        """Index all supported files in a directory.

        Args:
            path: Path to the directory to index.

        Returns:
            A combined list of Document and Chunk objects from all
            supported files in the directory.

        """
        ...

    def supports_file(self, path: Path) -> bool:
        """Check whether the indexer can handle a given file.

        Args:
            path: Path to the file to check.

        Returns:
            True if this indexer supports the file type.

        """
        ...


@runtime_checkable
class SearcherProtocol(Protocol):
    """Protocol for document searchers.

    Implementations index documents for retrieval and execute ranked
    search queries against the indexed corpus.
    """

    def add_documents(self, documents: list[Document | Chunk]) -> None:
        """Add documents to the search index.

        Args:
            documents: Documents or chunks to make searchable.

        """
        ...

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search indexed documents by query string.

        Args:
            query: The search query.
            limit: Maximum number of results to return.

        Returns:
            A list of SearchResult objects ordered by relevance score.

        """
        ...


@runtime_checkable
class AssemblerProtocol(Protocol):
    """Protocol for result assemblers.

    Implementations format search results into structured output
    strings in various formats (e.g. XML, Markdown).
    """

    def assemble(self, results: list[SearchResult], output_format: str = "xml") -> str:
        """Assemble search results into a formatted string.

        Args:
            results: Search results to format.
            output_format: Output format identifier (e.g. "xml", "markdown").

        Returns:
            The formatted output string.

        """
        ...

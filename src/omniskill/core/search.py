"""BM25 search engine implementation.

Provides a BM25-based searcher that indexes Document and Chunk objects
and returns ranked results by relevance score.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from rank_bm25 import BM25Okapi

from omniskill.models import SearchResult

if TYPE_CHECKING:
    from collections.abc import Sequence

    from omniskill.models import Chunk, Document


_WORD_RE = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase word tokens.

    Args:
        text: The input text to tokenize.

    Returns:
        A list of lowercase word tokens.

    """
    return [t.lower() for t in _WORD_RE.findall(text)]


class BM25Searcher:
    """BM25-based document searcher.

    Indexes documents and performs ranked retrieval using BM25 scoring.
    Conforms to SearcherProtocol.

    Attributes:
        k1: Term frequency saturation parameter (default 1.5).
        b: Length normalization parameter (default 0.75).

    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        """Initialize the searcher with BM25 parameters.

        Args:
            k1: Controls term frequency saturation. Higher values make
                term frequency more important.
            b: Controls document length normalization. 1.0 means full
                normalization, 0.0 means none.

        """
        self.k1 = k1
        self.b = b
        self._documents: list[Document | Chunk] = []
        self._tokenized_corpus: list[list[str]] = []
        self._bm25: BM25Okapi | None = None

    def add_documents(self, documents: list[Document | Chunk] | Sequence[Document | Chunk]) -> None:
        """Add documents to the search index.

        Args:
            documents: Documents or chunks to make searchable.

        """
        if not documents:
            return

        self._documents.extend(documents)
        for doc in documents:
            self._tokenized_corpus.append(tokenize(doc.content))

        # Filter out empty token lists to avoid division by zero in BM25
        non_empty_corpus = [tokens for tokens in self._tokenized_corpus if tokens]
        if not non_empty_corpus:
            # If all documents have empty token lists, create a dummy corpus
            non_empty_corpus = [["__empty__"]]

        self._bm25 = BM25Okapi(
            non_empty_corpus,
            k1=self.k1,
            b=self.b,
        )
        self._apply_idf_floor()

    def _apply_idf_floor(self) -> None:
        """Apply epsilon floor to zero-IDF terms.

        When a term appears in exactly half the documents in a small corpus,
        BM25Okapi computes IDF=0.0, which makes the term contribute nothing
        to the score (due to ``idf.get(q) or 0``). This method replaces
        zero-IDF terms with epsilon * average_idf, matching the ATIRE BM25
        variant's handling of negative IDFs.
        """
        if self._bm25 is None:
            return

        eps = self._bm25.epsilon * max(self._bm25.average_idf, 0.25)
        for word, val in self._bm25.idf.items():
            if val == 0.0:
                self._bm25.idf[word] = eps

    def search(
        self,
        query: str,
        limit: int = 10,
        doc_type: str | None = None,
        tags: list[str] | None = None,
    ) -> list[SearchResult]:
        """Search indexed documents by query string.

        Args:
            query: The search query.
            limit: Maximum number of results to return.
            doc_type: Filter by document type ('csv' or 'markdown').
            tags: Filter by tags (all tags must match - AND logic).

        Returns:
            A list of SearchResult objects ordered by relevance score
            (highest first).

        Raises:
            ValueError: If the query is empty or whitespace-only.
            ValueError: If the index is empty (no documents added).

        """
        if not query or not query.strip():
            msg = "Query must not be empty"
            raise ValueError(msg)

        if self._bm25 is None or not self._documents:
            msg = "No documents indexed"
            raise ValueError(msg)

        tokenized_query = tokenize(query)
        if not tokenized_query:
            return []

        scores = self._bm25.get_scores(tokenized_query)

        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        results: list[SearchResult] = []
        has_positive_scores = any(s > 0 for _, s in indexed_scores)

        for idx, score in indexed_scores[:limit]:
            # Include results with positive scores
            # Also include negative scores when no positive scores exist
            # (happens when query term appears in all documents)
            # But exclude zero scores (no match at all)
            if score > 0 or (not has_positive_scores and score < 0):
                doc = self._documents[idx]

                # Apply doc_type filter
                if doc_type is not None:
                    # Determine doc_type from source file extension
                    if doc.source.endswith(".csv"):
                        actual_type = "csv"
                    elif doc.source.endswith(".md") or doc.source.endswith(".markdown"):
                        actual_type = "markdown"
                    else:
                        actual_type = "unknown"

                    if actual_type != doc_type:
                        continue

                # Apply tags filter (all tags must match - AND logic)
                if tags is not None and len(tags) > 0:
                    doc_tags = set(doc.tags)
                    if not all(tag in doc_tags for tag in tags):
                        continue

                results.append(SearchResult(document=doc, score=float(score)))

        return results

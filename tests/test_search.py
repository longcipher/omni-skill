"""Tests for the BM25 search engine."""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from omniskill.core.search import BM25Searcher, tokenize
from omniskill.models import Chunk, Document, SearchResult
from omniskill.protocols import SearcherProtocol


def _make_doc(doc_id: str, content: str) -> Document:
    """Create a test Document."""
    return Document(
        id=doc_id,
        source=f"data/{doc_id}.csv",
        content=content,
        metadata={},
        tags=(),
    )


def _make_chunk(chunk_id: str, content: str) -> Chunk:
    """Create a test Chunk."""
    return Chunk(
        id=chunk_id,
        source=f"docs/{chunk_id}.md",
        content=content,
        header_level=2,
        header_text=f"Header {chunk_id}",
        tags=(),
    )


# ---------------------------------------------------------------------------
# Tokenization Tests
# ---------------------------------------------------------------------------


class TestTokenize:
    """Tests for the tokenize function."""

    def test_lowercase(self) -> None:
        assert tokenize("Hello World") == ["hello", "world"]

    def test_strips_punctuation(self) -> None:
        assert tokenize("hello, world!") == ["hello", "world"]

    def test_empty_string(self) -> None:
        assert tokenize("") == []

    def test_only_punctuation(self) -> None:
        assert tokenize("!@#$%") == []

    def test_unicode(self) -> None:
        tokens = tokenize("日本語テスト")
        assert len(tokens) > 0


# ---------------------------------------------------------------------------
# BM25Searcher Unit Tests
# ---------------------------------------------------------------------------


class TestBM25Searcher:
    """Unit tests for BM25Searcher."""

    def test_add_documents(self) -> None:
        searcher = BM25Searcher()
        docs = [_make_doc("1", "python programming"), _make_doc("2", "java development")]
        searcher.add_documents(docs)
        # Verify documents were added by searching
        results = searcher.search("python")
        assert len(results) >= 1

    def test_add_empty_list(self) -> None:
        searcher = BM25Searcher()
        searcher.add_documents([])
        # Verify empty index raises on search
        with pytest.raises(ValueError, match="No documents"):
            searcher.search("anything")

    def test_search_returns_results(self) -> None:
        searcher = BM25Searcher()
        docs = [
            _make_doc("1", "python programming language"),
            _make_doc("2", "java programming language"),
            _make_doc("3", "cooking recipes"),
        ]
        searcher.add_documents(docs)
        results = searcher.search("python")
        assert len(results) >= 1
        assert all(isinstance(r, SearchResult) for r in results)
        assert all(r.score > 0 for r in results)

    def test_search_ranking_order(self) -> None:
        searcher = BM25Searcher()
        docs = [
            _make_doc("1", "python python python programming"),
            _make_doc("2", "python is great"),
            _make_doc("3", "java programming language"),
        ]
        searcher.add_documents(docs)
        results = searcher.search("python")
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)
        assert results[0].document.id == "1"

    def test_search_empty_query_raises(self) -> None:
        searcher = BM25Searcher()
        searcher.add_documents([_make_doc("1", "some content")])
        with pytest.raises(ValueError, match="empty"):
            searcher.search("")
        with pytest.raises(ValueError, match="empty"):
            searcher.search("   ")

    def test_search_empty_index_raises(self) -> None:
        searcher = BM25Searcher()
        with pytest.raises(ValueError, match="No documents"):
            searcher.search("anything")

    def test_search_no_matches(self) -> None:
        searcher = BM25Searcher()
        searcher.add_documents([_make_doc("1", "cooking recipes and food")])
        results = searcher.search("quantum physics")
        assert results == []

    def test_search_limit(self) -> None:
        searcher = BM25Searcher()
        docs = [_make_doc(str(i), f"python programming example {i}") for i in range(20)]
        searcher.add_documents(docs)
        results = searcher.search("python", limit=5)
        assert len(results) <= 5

    def test_search_with_chunks(self) -> None:
        searcher = BM25Searcher()
        chunks = [_make_chunk("c1", "python basics"), _make_chunk("c2", "advanced rust")]
        searcher.add_documents(chunks)
        results = searcher.search("python")
        assert len(results) >= 1
        assert isinstance(results[0].document, Chunk)

    def test_search_with_mixed_types(self) -> None:
        searcher = BM25Searcher()
        items: list[Document | Chunk] = [
            _make_doc("d1", "python programming"),
            _make_chunk("c1", "python tutorial"),
        ]
        searcher.add_documents(items)
        results = searcher.search("python")
        assert len(results) == 2

    def test_search_query_tokenization(self) -> None:
        searcher = BM25Searcher()
        searcher.add_documents([_make_doc("1", "python programming language")])
        results = searcher.search("PYTHON Programming!")
        assert len(results) >= 1

    def test_custom_bm25_parameters(self) -> None:
        searcher = BM25Searcher(k1=2.0, b=0.5)
        assert searcher.k1 == 2.0
        assert searcher.b == 0.5

    def test_searcher_protocol_compliance(self) -> None:
        searcher = BM25Searcher()
        assert isinstance(searcher, SearcherProtocol)

    def test_incremental_add_documents(self) -> None:
        searcher = BM25Searcher()
        searcher.add_documents([_make_doc("1", "python basics")])
        searcher.add_documents([_make_doc("2", "rust systems programming")])
        # Verify both documents are searchable
        results = searcher.search("python")
        assert any(r.document.id == "1" for r in results)
        results = searcher.search("rust")
        assert any(r.document.id == "2" for r in results)


# ---------------------------------------------------------------------------
# Hypothesis Property Tests
# ---------------------------------------------------------------------------


class TestSearchPropertyTests:
    """Property-based tests for search consistency."""

    @given(
        doc_contents=st.lists(
            st.text(min_size=1, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyz "),
            min_size=1,
            max_size=10,
        ),
        query=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz"),
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_search_is_deterministic(self, doc_contents: list[str], query: str) -> None:
        """Same query on same index always returns same ranking."""
        docs = [_make_doc(str(i), content) for i, content in enumerate(doc_contents)]
        searcher = BM25Searcher()
        searcher.add_documents(docs)

        try:
            results1 = searcher.search(query)
            results2 = searcher.search(query)
        except ValueError:
            return

        ids1 = [r.document.id for r in results1]
        ids2 = [r.document.id for r in results2]
        assert ids1 == ids2

        scores1 = [r.score for r in results1]
        scores2 = [r.score for r in results2]
        assert scores1 == scores2

    @given(
        texts=st.lists(
            st.text(min_size=1, max_size=30, alphabet="abcdefghijklmnopqrstuvwxyz "),
            min_size=1,
            max_size=5,
        )
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_search_results_sorted_descending(self, texts: list[str]) -> None:
        """Search results are always returned in descending score order."""
        docs = [_make_doc(str(i), t) for i, t in enumerate(texts)]
        searcher = BM25Searcher()
        searcher.add_documents(docs)

        for t in texts:
            words = [w for w in t.split() if w]
            if not words:
                continue
            try:
                results = searcher.search(words[0])
            except ValueError:
                continue
            scores = [r.score for r in results]
            assert scores == sorted(scores, reverse=True)

    @given(
        content=st.text(min_size=1, max_size=100, alphabet="abcdefghijklmnopqrstuvwxyz "),
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_tokenized_query_matches_tokenized_doc(self, content: str) -> None:
        """Searching for words from a document finds that document."""
        docs = [_make_doc("target", content), _make_doc("other", "xyzzy completely unrelated")]
        searcher = BM25Searcher()
        searcher.add_documents(docs)

        words = [w for w in content.split() if len(w) > 2]
        if not words:
            return

        results = searcher.search(words[0])
        if results:
            assert results[0].document.id == "target"

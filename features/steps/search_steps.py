"""Step definitions for search.feature."""

from __future__ import annotations

from typing import Any

from behave import given, then, when

from omniskill.core.search import BM25Searcher
from omniskill.models import Document


@given("a BM25 searcher is initialized")
def step_init_searcher(context: Any) -> None:
    """Initialize a BM25Searcher."""
    context.searcher = BM25Searcher()
    context.search_error = None


@given("the following documents are indexed:")
def step_index_documents(context: Any) -> None:
    """Index documents from a behave table."""
    docs = []
    for row in context.table:
        doc = Document(
            id=row["id"],
            source=f"data/{row['id']}.csv",
            content=row["content"],
            metadata={},
            tags=(),
        )
        docs.append(doc)
    context.searcher.add_documents(docs)
    context.indexed_docs = {d.id: d for d in docs}


@when('I search for "{query}"')
def step_search(context: Any, query: str) -> None:
    """Perform a search query."""
    context.search_error = None
    try:
        context.search_results = context.searcher.search(query)
    except ValueError as e:
        context.search_error = e
        context.search_results = []


@when('I search for ""')
def step_search_empty(context: Any) -> None:
    """Perform a search with empty query."""
    context.search_error = None
    try:
        context.search_results = context.searcher.search("")
    except ValueError as e:
        context.search_error = e
        context.search_results = []


@when('I search for "{query}" with limit {limit:d}')
def step_search_with_limit(context: Any, query: str, limit: int) -> None:
    """Perform a search with a result limit."""
    context.search_error = None
    try:
        context.search_results = context.searcher.search(query, limit=limit)
    except ValueError as e:
        context.search_error = e
        context.search_results = []


@when('I search for "{query}" twice')
def step_search_twice(context: Any, query: str) -> None:
    """Perform the same search twice for determinism testing."""
    try:
        context.search_results_1 = context.searcher.search(query)
        context.search_results_2 = context.searcher.search(query)
    except ValueError as e:
        context.search_error = e
        context.search_results_1 = []
        context.search_results_2 = []


@then("I should get at least {count:d} result")
@then("I should get at least {count:d} results")
def step_at_least_results(context: Any, count: int) -> None:
    """Verify minimum result count."""
    assert len(context.search_results) >= count


@then("I should get {count:d} results")
def step_exact_results(context: Any, count: int) -> None:
    """Verify exact result count."""
    assert len(context.search_results) == count


@then("I should get at most {count:d} results")
def step_at_most_results(context: Any, count: int) -> None:
    """Verify maximum result count."""
    assert len(context.search_results) <= count


@then('the top result should be document "{doc_id}"')
def step_top_result_is(context: Any, doc_id: str) -> None:
    """Verify the top result document ID."""
    assert len(context.search_results) > 0
    assert context.search_results[0].document.id == doc_id


@then("results should be sorted by score descending")
def step_sorted_descending(context: Any) -> None:
    """Verify results are sorted by score descending."""
    scores = [r.score for r in context.search_results]
    assert scores == sorted(scores, reverse=True)


@then('a ValueError should be raised with message "{msg}"')
def step_value_error_with_message(context: Any, msg: str) -> None:
    """Verify a ValueError was raised with expected message."""
    assert context.search_error is not None
    assert isinstance(context.search_error, ValueError)
    assert msg.lower() in str(context.search_error).lower()


@then("both result sets should be identical")
def step_results_identical(context: Any) -> None:
    """Verify two search result sets are identical."""
    ids1 = [r.document.id for r in context.search_results_1]
    ids2 = [r.document.id for r in context.search_results_2]
    assert ids1 == ids2

    scores1 = [r.score for r in context.search_results_1]
    scores2 = [r.score for r in context.search_results_2]
    assert scores1 == scores2

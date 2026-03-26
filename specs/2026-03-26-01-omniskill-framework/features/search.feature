Feature: BM25 Document Search
  As a developer using OmniSkill
  I want to search indexed documents using BM25 ranking
  So that I can retrieve the most relevant content for my queries

  Background:
    Given the OmniSkill framework is initialized
    And the following documents are indexed:
      | ID | Content                              | Doc Type | Tags        |
      | 1  | Python API design patterns          | markdown | python, api |
      | 2  | REST API authentication methods     | markdown | api, auth   |
      | 3  | Database indexing best practices    | markdown | db, perf    |
      | 4  | API rate limiting strategies        | markdown | api, perf   |
      | 5  | Python error handling patterns      | markdown | python      |

  Scenario: BM25 search returns ranked results
    When I search for "API design patterns"
    Then I should receive at least 3 results
    And the results should be ranked by relevance
    And result 1 should have higher score than result 2
    And the top result should contain "API" or "design" or "patterns"

  Scenario: Search for specific technical term
    When I search for "rate limiting"
    Then I should receive at least 1 result
    And the top result should have content containing "rate limiting"
    And the top result should have ID "4"

  Scenario: Search with no matching results
    When I search for "kubernetes orchestration containers"
    Then I should receive 0 results
    And no error should be raised
    And the search should complete successfully

  Scenario: Tag-based filtering narrows search scope
    When I search for "API" with tag filter "python"
    Then I should receive at least 1 result
    And all results should have tag "python"
    And result with ID "5" should not be in results

  Scenario: Multiple tag filtering (AND logic)
    When I search for "API" with tag filters "api, auth"
    Then I should receive at least 1 result
    And all results should have both tags "api" AND "auth"
    And result with ID "4" (api but not auth) should not be in results

  Scenario: Type-based filtering (CSV vs Markdown)
    Given the following additional CSV documents are indexed:
      | ID | Content                              | Doc Type | Tags        |
      | 6  | API status code reference           | csv      | api         |
      | 7  | Database connection pooling         | csv      | db          |
    When I search for "API" with type filter "markdown"
    Then I should receive at least 3 results
    And all results should have doc_type "markdown"
    And result with ID "6" (csv type) should not be in results

  Scenario: Combined text search and filter
    When I search for "database" with type filter "markdown" and tag filter "perf"
    Then I should receive at least 1 result
    And the top result should contain "database"
    And the top result should have doc_type "markdown"
    And the top result should have tag "perf"

  Scenario: Search with limit parameter
    When I search for "API" with limit 2
    Then I should receive exactly 2 results
    And the results should be the 2 most relevant matches

  Scenario: Empty query handling
    When I search for ""
    Then an appropriate error should be raised
    And the error message should indicate that query cannot be empty

---

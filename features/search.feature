Feature: BM25 Search Engine
  As a developer
  I want to search indexed documents using BM25 scoring
  So that I can retrieve relevant information by query

  Background:
    Given a BM25 searcher is initialized

  Scenario: Index documents and search
    Given the following documents are indexed:
      | id  | content                          |
      | d1  | python programming language      |
      | d2  | java programming tutorial        |
      | d3  | cooking recipes and food         |
    When I search for "python"
    Then I should get at least 1 result
    And the top result should be document "d1"

  Scenario: Search results are ranked by score
    Given the following documents are indexed:
      | id  | content                              |
      | d1  | python python programming basics     |
      | d2  | python is a great language           |
      | d3  | java programming language            |
    When I search for "python"
    Then results should be sorted by score descending

  Scenario: Search with no matches
    Given the following documents are indexed:
      | id  | content                      |
      | d1  | cooking recipes and food     |
    When I search for "quantum physics"
    Then I should get 0 results

  Scenario: Search with empty query raises error
    Given the following documents are indexed:
      | id  | content                  |
      | d1  | some searchable content  |
    When I search for ""
    Then a ValueError should be raised with message "empty"

  Scenario: Search on empty index raises error
    When I search for "anything"
    Then a ValueError should be raised with message "No documents"

  Scenario: Search with limit parameter
    Given the following documents are indexed:
      | id  | content                          |
      | d1  | python example one               |
      | d2  | python example two               |
      | d3  | python example three             |
      | d4  | python example four              |
      | d5  | python example five              |
    When I search for "python" with limit 3
    Then I should get at most 3 results

  Scenario: Search is deterministic
    Given the following documents are indexed:
      | id  | content                              |
      | d1  | machine learning with python         |
      | d2  | deep learning neural networks        |
    When I search for "learning" twice
    Then both result sets should be identical

Feature: Document Indexing and Search
  As a developer
  I want to index documents and search them
  So that I can retrieve relevant information

  Background:
    Given the core data models are defined

  Scenario: Create a Document instance
    When I create a Document with:
      | field      | value                 |
      | id         | doc-001               |
      | source     | data/docs.csv         |
      | content    | Test document content |
      | metadata   | {}                    |
      | tags       | ()                    |
    Then the Document should be created successfully
    And the Document should be immutable

  Scenario: Create a Chunk instance
    When I create a Chunk with:
      | field        | value               |
      | id           | chunk-001           |
      | source       | docs/guide.md       |
      | content      | Chunk content       |
      | header_level | 2                   |
      | header_text  | Getting Started     |
      | tags         | ("guide",)          |
    Then the Chunk should be created successfully
    And the Chunk should be immutable

  Scenario: Create a SearchResult instance with Document
    Given a Document exists with id "doc-001"
    When I create a SearchResult with:
      | field     | value   |
      | document  | doc-001 |
      | score     | 0.95    |
    Then the SearchResult should be created successfully
    And the SearchResult should reference the Document

  Scenario: Create a SearchResult instance with Chunk
    Given a Chunk exists with id "chunk-001"
    When I create a SearchResult with:
      | field     | value     |
      | document  | chunk-001 |
      | score     | 0.87      |
    Then the SearchResult should be created successfully
    And the SearchResult should reference the Chunk

  Scenario: Documents are hashable
    Given multiple Documents exist
    When I add them to a set
    Then the set should contain all unique Documents

  Scenario: Chunks are hashable
    Given multiple Chunks exist
    When I add them to a set
    Then the set should contain all unique Chunks

  Scenario: Documents support JSON serialization
    Given a Document exists with metadata
    When I serialize the Document to JSON
    Then the JSON should contain all Document fields

  Scenario: Chunks support JSON serialization
    Given a Chunk exists with header information
    When I serialize the Chunk to JSON
    Then the JSON should contain all Chunk fields

  Scenario: SearchResults are comparable by score
    Given multiple SearchResults exist with different scores
    When I sort them by score
    Then they should be ordered from highest to lowest score

  Scenario: Index a CSV file into Documents
    Given a CSV file "test.csv" with content:
      """
      name,age,city
      Alice,30,NYC
      Bob,25,LA
      """
    When I index the file with CsvIndexer
    Then I should get 2 Documents
    And Document 0 should have metadata key "name" with value "Alice"
    And Document 1 should have metadata key "name" with value "Bob"

  Scenario: Index a Markdown file by H2 headers into Chunks
    Given a Markdown file "guide.md" with content:
      """
      ## Getting Started

      Install the package.

      ## Usage

      Import and use it.
      """
    When I index the file with MarkdownIndexer
    Then I should get 2 Chunks
    And Chunk 0 should have header_text "Getting Started"
    And Chunk 1 should have header_text "Usage"

  Scenario: Index a Markdown file with mixed H2 and H3 headers
    Given a Markdown file "mixed.md" with content:
      """
      ## Main Section

      Overview.

      ### Detail A

      Details about A.

      ### Detail B

      Details about B.
      """
    When I index the file with MarkdownIndexer
    Then I should get 3 Chunks
    And Chunk 0 should have header_level 2
    And Chunk 1 should have header_level 3
    And Chunk 2 should have header_level 3

  Scenario: Index an empty CSV file
    Given a CSV file "empty.csv" with content:
      """
      """
    When I index the file with CsvIndexer
    Then I should get 0 Documents

  Scenario: Index an empty Markdown file
    Given a Markdown file "empty.md" with content:
      """
      """
    When I index the file with MarkdownIndexer
    Then I should get 0 Chunks

  Scenario: Indexer router selects correct indexer for CSV
    Given a CSV file "data.csv" with content:
      """
      x,y
      1,2
      """
    When I index the file with Indexer
    Then the results should be Documents

  Scenario: Indexer router selects correct indexer for Markdown
    Given a Markdown file "doc.md" with content:
      """
      ## Title

      Content.
      """
    When I index the file with Indexer
    Then the results should be Chunks

  Scenario: Indexer rejects unsupported file extension
    Given an unsupported file "notes.txt" with content "hello"
    When I index the file with Indexer
    Then a ValueError should be raised

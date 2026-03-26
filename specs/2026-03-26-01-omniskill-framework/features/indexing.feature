Feature: Document Indexing
  As a developer using OmniSkill
  I want to index CSV and Markdown files into searchable documents
  So that I can later search and retrieve relevant content

  Background:
    Given the OmniSkill framework is initialized

  Scenario: CSV file indexing creates searchable documents
    Given a CSV file "api_standards.csv" with the following content:
      | Pattern       | Description          | Example              |
      | snake_case    | Use snake_case       | user_name            |
      | camelCase     | Use camelCase        | userName             |
      | 201_Created   | POST returns 201     | HTTP 201             |
    When I index the CSV file
    Then 3 documents should be created
    And each document should have:
      | Field      | Value               |
      | doc_type   | csv                 |
      | source     | api_standards.csv   |
      | content    | <row content>       |
    And document 1 metadata should contain:
      | Key         | Value       |
      | Pattern     | snake_case  |
      | Description | Use snake_case |
      | Example     | user_name   |

  Scenario: Markdown file chunking by H2 headers
    Given a Markdown file "auth_patterns.md" with the following content:
      """
      # Authentication Patterns

      ## JWT Authentication
      Use JWT tokens for stateless auth.
      ```python
      token = jwt.encode(payload, secret)
      ```

      ## OAuth2 Flow
      Use OAuth2 for third-party auth.
      ```python
      oauth = OAuth2Session(client_id)
      ```

      ## Session-Based Auth
      Use sessions for traditional auth.
      """
    When I index the Markdown file with H2 chunking
    Then 3 chunks should be created
    And chunk 1 should have:
      | Field        | Value                  |
      | header_level | 2                      |
      | header_text  | JWT Authentication   |
      | content      | <JWT content>          |
    And chunk 2 should have:
      | Field        | Value                  |
      | header_level | 2                      |
      | header_text  | OAuth2 Flow            |
      | content      | <OAuth2 content>       |
    And chunk 3 should have:
      | Field        | Value                  |
      | header_level | 2                      |
      | header_text  | Session-Based Auth     |
      | content      | <Session content>      |

  Scenario: Markdown file chunking by H3 headers
    Given a Markdown file "db_best_practices.md" with the following content:
      """
      # Database Best Practices

      ## Indexing

      ### Single-Column Indexes
      Use for high-cardinality columns.

      ### Composite Indexes
      Use for multi-column queries.

      ## Query Optimization

      ### Avoid SELECT *
      Specify columns explicitly.
      """
    When I index the Markdown file with H3 chunking
    Then 4 chunks should be created
    And the chunks should include:
      | Header Text              | Header Level |
      | Single-Column Indexes    | 3            |
      | Composite Indexes        | 3            |
      | Avoid SELECT *           | 3            |
    And no H2 chunks should be created

  Scenario: Mixed content indexing
    Given a skill directory "backend-api-master" with the following files:
      | File                | Type       | Content Preview        |
      | api_standards.csv   | CSV        | Pattern,Description... |
      | auth_patterns.md    | Markdown   | # Auth Patterns...     |
      | db_best_practices.md| Markdown   | # DB Practices...      |
    When I index the entire skill directory
    Then documents should be created for all CSV rows
    And chunks should be created for all Markdown sections
    And all documents should have appropriate doc_type metadata
    And all documents should have source pointing to original file

  Scenario: Empty file handling
    Given an empty CSV file "empty.csv"
    And an empty Markdown file "empty.md"
    When I index the empty files
    Then no documents should be created for the empty CSV
    And no chunks should be created for the empty Markdown
    And no errors should be raised

  Scenario: Malformed CSV handling
    Given a malformed CSV file "malformed.csv" with:
      """
      Pattern,Description,Example
      snake_case,Use snake_case,user_name
      camelCase"Unclosed quote here
      """
    When I attempt to index the malformed CSV
    Then an `IndexingError` should be raised
    And the error message should indicate CSV parsing failure
    And partial documents before the error may be created

---

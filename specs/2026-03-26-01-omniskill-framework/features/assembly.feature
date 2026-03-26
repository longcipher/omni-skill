Feature: Prompt Assembly
  As a developer using OmniSkill
  I want to assemble search results into LLM-friendly prompt context
  So that I can inject relevant knowledge into AI conversations

  Background:
    Given the OmniSkill framework is initialized
    And the following search results are available:
      | Rank | Score | Content Source      | Content Type | Content Preview                                      |
      | 1    | 0.95  | api_standards.csv   | CSV          | Pattern: snake_case, Description: Use snake_case     |
      | 2    | 0.87  | auth_patterns.md    | Markdown     | ## JWT Authentication...                             |
      | 3    | 0.72  | api_standards.csv   | CSV          | Pattern: 201_Created, Description: POST returns 201  |

  Scenario: Search results assembled into XML format
    When I assemble the results into XML format
    Then the output should be valid XML
    And the root element should be <context_injection>
    And the XML should contain a <rules> section for CSV results
    And the XML should contain a <reference> section for Markdown results
    And the XML should include source attributes for each section
    And the XML should preserve the ranking order (highest score first)

  Scenario: Search results assembled into Markdown format
    When I assemble the results into Markdown format
    Then the output should be valid Markdown
    And the output should start with ## Context
    And the Markdown should contain a ### Rules section for CSV results
    And the Markdown should contain a ### References section for Markdown results
    And the Markdown should include source attribution for each section
    And the Markdown should preserve the ranking order (highest score first)

  Scenario: Mixed CSV and Markdown result assembly
    Given I have search results from both CSV and Markdown sources
    When I assemble the results
    Then CSV results should be formatted as rules/constraints
    And Markdown results should be formatted as reference code
    And both types should be included in the output
    And each result should be clearly labeled with its source

  Scenario: Empty result assembly
    Given I have no search results
    When I assemble the results
    Then an appropriate message should be returned
    And the output should indicate no results were found
    And no error should be raised

  Scenario: Maximum context length enforcement
    Given I have many search results that would exceed the maximum context length
    When I assemble the results with max_context_length=1000
    Then the output should be truncated to approximately 1000 characters
    And a truncation notice should be included
    And the most relevant results (highest score) should be prioritized

  Scenario: Source attribution in assembly
    When I assemble the results
    Then each section should include its source file path
    And CSV results should indicate they are from CSV files
    And Markdown results should indicate they are from Markdown files
    And the source attribution should be machine-parseable

  Scenario: Ranking preservation in assembly
    Given I have search results with varying scores
    When I assemble the results
    Then the highest scoring result should appear first
    And the second highest should appear second
    And the order should match the original ranking

  Scenario: XML format with nested sections
    When I assemble the results into XML format
    Then the XML structure should be:
      """
      <context_injection>
        <rules source="api_standards.csv">
          - Pattern: snake_case, Description: Use snake_case
          - Pattern: 201_Created, Description: POST returns 201
        </rules>
        <reference code source="auth_patterns.md">
          ## JWT Authentication...
        </reference>
      </context_injection>
      """

  Scenario: Markdown format with code blocks preserved
    Given a search result from Markdown containing code blocks
    When I assemble the results into Markdown format
    Then code blocks should be preserved with proper fencing
    And syntax highlighting hints should be retained
    And the Markdown should render correctly

  Scenario: Assembly with metadata inclusion
    When I assemble the results with include_metadata=True
    Then the output should include BM25 scores
    And the output should include result ranks
    And the output should include document IDs
    And the metadata should be structured and parseable

  Scenario: Assembly without metadata
    When I assemble the results with include_metadata=False
    Then the output should not include BM25 scores
    And the output should not include result ranks
    And the output should focus on content only

  Scenario: Error handling in assembly
    Given an invalid result object in the search results
    When I attempt to assemble the results
    Then an `AssemblyError` should be raised
    And the error message should indicate the assembly failure
    And details about the problematic result should be included

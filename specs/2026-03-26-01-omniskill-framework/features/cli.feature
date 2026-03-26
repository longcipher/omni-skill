Feature: CLI Commands
  As a developer using OmniSkill
  I want to use CLI commands to create skills and search knowledge
  So that I can interact with the framework from the command line

  Background:
    Given the OmniSkill CLI is installed
    And the command `omniskill` is available in the PATH

  Scenario: CLI help command
    When I run `omniskill --help`
    Then the output should contain "OmniSkill Framework"
    And the output should list available commands
    And the output should show global options like `--version` and `--verbose`
    And the exit code should be 0

  Scenario: CLI version command
    When I run `omniskill --version`
    Then the output should contain the version number
    And the output should match the pattern "omniskill, version X.Y.Z"
    And the exit code should be 0

  Scenario: CLI verbose mode
    When I run `omniskill --verbose search "test" --skill-dir ./test-skill`
    Then the output should contain debug information
    And the output should show indexing progress
    And the output should show search query details

  Scenario: Create new skill with CLI command
    When I run `omniskill create backend-api-master`
    Then a directory "skills/backend-api-master" should be created
    And the directory should contain "SKILL.md"
    And the directory should contain "datasets/" subdirectory
    And the directory should contain "__init__.py"
    And the exit code should be 0
    And the output should confirm successful creation

  Scenario: Create skill with force flag overwrites existing
    Given a skill "existing-skill" already exists
    When I run `omniskill create existing-skill --force`
    Then the existing skill directory should be overwritten
    And the exit code should be 0
    And a warning should be displayed about overwriting

  Scenario: Create skill without force fails on existing
    Given a skill "existing-skill" already exists
    When I run `omniskill create existing-skill`
    Then the command should fail
    And the exit code should be non-zero
    And the error message should indicate the skill already exists

  Scenario: Generated skill has correct directory structure
    When I run `omniskill create test-skill`
    Then the "skills/test-skill" directory should have the following structure:
      """
      test-skill/
      ├── SKILL.md
      ├── __init__.py
      └── datasets/
      """
    And the "datasets" directory should be empty
    And "SKILL.md" should be a valid Markdown file

  Scenario: Generated SKILL.md contains proper instructions
    When I run `omniskill create my-skill`
    Then the "skills/my-skill/SKILL.md" file should contain:
      | Section                      |
      | # Role                       |
      | # Knowledge Retrieval Action |
      | # Instructions               |
    And the file should contain the skill name "my-skill"
    And the file should contain a command template for search
    And the file should contain step-by-step instructions for LLM usage

  Scenario: Search command with query and skill directory
    Given a skill "test-skill" exists with indexed content
    When I run `omniskill search "API authentication" --skill-dir skills/test-skill`
    Then the command should succeed
    And the output should contain assembled context
    And the output should be valid XML by default
    And the exit code should be 0

  Scenario: Search command with format option
    Given a skill "test-skill" exists with indexed content
    When I run `omniskill search "API" --skill-dir skills/test-skill --format markdown`
    Then the output should be valid Markdown
    And the output should contain assembled context
    When I run the same search with `--format xml`
    Then the output should be valid XML

  Scenario: Search command with limit option
    Given a skill "test-skill" exists with many indexed documents
    When I run `omniskill search "API" --skill-dir skills/test-skill --limit 5`
    Then the output should contain at most 5 results
    And the most relevant 5 results should be included

  Scenario: Search command with type filter
    Given a skill "test-skill" exists with CSV and Markdown content
    When I run `omniskill search "API" --skill-dir skills/test-skill --type markdown`
    Then all results should be from Markdown documents
    And no CSV documents should appear in results

  Scenario: Search command with tag filter
    Given a skill "test-skill" exists with tagged documents
    When I run `omniskill search "API" --skill-dir skills/test-skill --tag auth --tag api`
    Then all results should have both "auth" AND "api" tags
    And results without both tags should not appear

  Scenario: Search command with non-existent skill directory
    When I run `omniskill search "API" --skill-dir skills/non-existent`
    Then the command should fail
    And the exit code should be non-zero
    And the error message should indicate the directory does not exist

  Scenario: Search command with empty skill directory
    Given an empty skill directory "empty-skill"
    When I run `omniskill search "API" --skill-dir skills/empty-skill`
    Then the command should succeed
    And the output should indicate no results found
    And the exit code should be 0

  Scenario: Search command with empty query
    Given a skill "test-skill" exists
    When I run `omniskill search "" --skill-dir skills/test-skill`
    Then the command should fail
    And the exit code should be non-zero
    And the error message should indicate query cannot be empty

  Scenario: Invalid format option
    Given a skill "test-skill" exists
    When I run `omniskill search "API" --skill-dir skills/test-skill --format invalid`
    Then the command should fail
    And the exit code should be non-zero
    And the error message should indicate invalid format option

  Scenario: Help for create command
    When I run `omniskill create --help`
    Then the output should contain "Create a new OmniSkill"
    And the output should show the SKILL_NAME argument
    And the output should show available options like `--force`

  Scenario: Help for search command
    When I run `omniskill search --help`
    Then the output should contain "Search skill knowledge"
    And the output should show the QUERY argument
    And the output should show options like `--skill-dir`, `--format`, `--limit`

  Scenario: Verbose output shows indexing progress
    Given a skill "test-skill" with multiple files
    When I run `omniskill search "API" --skill-dir skills/test-skill --verbose`
    Then the output should contain "Indexing files..."
    And the output should show progress for each file indexed
    And the output should contain "Search complete"

  Scenario: Configuration file usage
    Given a configuration file "custom.toml" with custom settings
    When I run `omniskill --config custom.toml search "API" --skill-dir skills/test`
    Then the custom configuration should be used
    And the search should respect custom settings

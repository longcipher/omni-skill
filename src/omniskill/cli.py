"""OmniSkill CLI entry point."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click
import structlog

from omniskill import __version__
from omniskill.core.assembler import PromptAssembler
from omniskill.core.engine import SearchEngine
from omniskill.core.generator import generate_skill

logger = structlog.get_logger()


@click.group()
@click.version_option(version=__version__, prog_name="omniskill")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output with debug information.",
)
@click.pass_context
def cli(ctx: click.Context, *, verbose: bool) -> None:
    """OmniSkill Framework - A universal Agentic-RAG skill framework."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    # Configure logging
    if verbose:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )


@cli.command()
@click.argument("skill_name")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing skill directory.",
)
@click.pass_context
def create(ctx: click.Context, skill_name: str, *, force: bool) -> None:  # noqa: ARG001
    """Create a new OmniSkill."""
    skills_dir = Path("skills")
    skill_dir = skills_dir / skill_name

    # Check if skill already exists
    if skill_dir.exists() and not force:
        click.echo(f"Error: Skill '{skill_name}' already exists. Use --force to overwrite.", err=True)
        sys.exit(1)

    # Create skill directory structure
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "datasets").mkdir(exist_ok=True)

    # Create __init__.py
    init_content = f'"""OmniSkill: {skill_name}."""\n'
    (skill_dir / "__init__.py").write_text(init_content)

    # Create SKILL.md template
    skill_md_content = f"""# {skill_name}

## Role

You are a specialized assistant with expertise in {skill_name.replace("-", " ")}.

## Knowledge Retrieval Action

When you need information to answer a question, execute the following command:

```bash
omniskill search "<your query>" --skill-dir skills/{skill_name} --format xml
```

This command will search the knowledge base and return relevant context.

## Instructions

1. **Extract Keywords**: Identify the key concepts and terms from the user's question.

2. **Execute Search**: Run the search command with extracted keywords
   to retrieve relevant context from the knowledge base.

3. **Read Context**: Parse the returned context (XML or Markdown format) to understand the available information.

4. **Generate Response**: Use the retrieved context to provide an
   accurate, helpful response. Always cite your sources when using
   information from the knowledge base.

5. **Handle Missing Information**: If the search returns no results or
   insufficient information, acknowledge what you don't know and
   suggest alternative approaches.

## Example Usage

User: "What are the best practices for API design?"

Action:
```bash
omniskill search "API design best practices" --skill-dir skills/{skill_name} --format xml
```

Then use the returned context to answer the question.
"""
    (skill_dir / "SKILL.md").write_text(skill_md_content)

    click.echo(f"✓ Created skill '{skill_name}' at {skill_dir}")
    click.echo(f"  - {skill_dir / 'SKILL.md'}")
    click.echo(f"  - {skill_dir / 'datasets'}/")


@cli.command()
@click.argument("query")
@click.option(
    "--skill-dir",
    "-d",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to the skill directory to search.",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["xml", "markdown"], case_sensitive=False),
    default="xml",
    help="Output format (default: xml).",
)
@click.option(
    "--limit",
    "-l",
    type=int,
    default=10,
    help="Maximum number of results to return (default: 10).",
)
@click.option(
    "--type",
    "-t",
    "doc_type",
    type=click.Choice(["csv", "markdown"], case_sensitive=False),
    help="Filter by document type.",
)
@click.option(
    "--tag",
    multiple=True,
    help="Filter by tag (can be used multiple times for AND logic).",
)
@click.option(
    "--metadata",
    is_flag=True,
    help="Include BM25 scores and metadata in output.",
)
@click.pass_context
def search(
    ctx: click.Context,
    query: str,
    skill_dir: Path,
    output_format: str,
    limit: int,
    doc_type: str | None,
    tag: tuple[str, ...],
    *,
    metadata: bool,
) -> None:
    """Search skill knowledge base."""
    verbose = ctx.obj.get("verbose", False)

    if not query.strip():
        click.echo("Error: Query cannot be empty.", err=True)
        sys.exit(1)

    try:
        # Initialize search engine
        engine = SearchEngine()

        # Index the skill directory
        if verbose:
            click.echo(f"Indexing {skill_dir}...", err=True)

        engine.index_directory(skill_dir)

        # Perform search
        tags_list = list(tag) if tag else None
        results = engine.search(
            query=query,
            limit=limit,
            doc_type=doc_type,
            tags=tags_list,
        )

        # Assemble results
        assembler = PromptAssembler()
        output = assembler.assemble(
            results=results,
            output_format=output_format,
            include_metadata=metadata,
        )

        # Output results
        click.echo(output)

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("search_failed")
        click.echo(f"Error: Search failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("dataset_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--name",
    "-n",
    "skill_name",
    default=None,
    help="Skill name. Defaults to the dataset directory name.",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    default=None,
    type=click.Path(path_type=Path),
    help="Output directory. Defaults to skills/<skill-name>/.",
)
@click.pass_context
def generate(
    ctx: click.Context,
    dataset_dir: Path,
    skill_name: str | None,
    output_dir: Path | None,
) -> None:
    """Generate a skill from a dataset directory.

    Analyzes CSV and Markdown files in DATASET_DIR and generates:
    - search.py: Python processing script using OmniSkill
    - SKILL.md: Skill specification document for LLMs
    """
    verbose = ctx.obj.get("verbose", False)

    try:
        analysis = generate_skill(
            dataset_dir=dataset_dir,
            skill_name=skill_name,
            output_dir=output_dir,
        )

        out = output_dir or Path("skills") / analysis.skill_name
        click.echo(f"Generated skill '{analysis.skill_name}' at {out}")
        click.echo(f"  - {out / 'SKILL.md'}")
        click.echo(f"  - {out / 'search.py'}")
        click.echo(f"  - {out / 'datasets'}/")

        if verbose:
            click.echo("\nDataset analysis:", err=True)
            click.echo(f"  CSV files: {len(analysis.csv_files)}", err=True)
            click.echo(f"  Markdown files: {len(analysis.markdown_files)}", err=True)
            click.echo(f"  Total documents: ~{analysis.total_documents}", err=True)

            for csv_info in analysis.csv_files:
                click.echo(f"  - {csv_info.path}: {csv_info.row_count} rows, columns={csv_info.columns}", err=True)
            for md_info in analysis.markdown_files:
                click.echo(f"  - {md_info.path}: {len(md_info.sections)} sections", err=True)

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("generate_failed")
        click.echo(f"Error: Generation failed: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Run the CLI application."""
    cli()


if __name__ == "__main__":
    main()

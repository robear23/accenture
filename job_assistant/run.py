"""CLI entry point for the Job Application Assistant."""

import sys
from pathlib import Path

import click
from rich.console import Console

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from job_assistant.config import settings
from job_assistant.orchestration.graph import build_graph
from job_assistant.rag.retriever import index_knowledge_base
from job_assistant.utils.display import (
    console,
    display_advisor_output,
    display_error,
    display_job_analysis,
    display_match_analysis,
    display_saved,
    display_writer_output,
)
from job_assistant.utils.logger import get_logger

logger = get_logger(__name__)


@click.command()
@click.option("--url", default=None, help="URL of the job posting to analyze.")
@click.option("--text", default=None, help="Job description text (inline).")
@click.option("--text-file", default=None, type=click.Path(exists=True),
              help="Path to a file containing the job description.")
@click.option("--reindex", is_flag=True, help="Force re-index the knowledge base.")
@click.option("--verbose", is_flag=True, help="Enable debug logging.")
def main(url, text, text_file, reindex, verbose):
    """Multi-Agent Job Application Assistant.

    Analyzes job postings and generates tailored application materials
    using LangGraph, RAG, and Google Gemini.
    """
    if verbose:
        import logging
        logging.getLogger("job_assistant").setLevel(logging.DEBUG)

    console.print("[bold blue]Job Application Assistant[/bold blue]")
    console.print("=" * 50)

    # Index knowledge base (always ensure it exists)
    with console.status("[bold green]Indexing knowledge base..."):
        count = index_knowledge_base(force=reindex)
        console.print(f"Knowledge base: {count} chunks indexed")

    if reindex and not url and not text and not text_file:
        console.print("[green]Knowledge base re-indexed successfully.[/green]")
        return

    # Determine job text source
    job_text = None
    if text:
        job_text = text
    elif text_file:
        job_text = Path(text_file).read_text(encoding="utf-8")
    elif not url:
        console.print("[red]Provide --url, --text, or --text-file[/red]")
        raise SystemExit(1)

    # Validate API key
    if not settings.google_api_key:
        console.print("[red]GOOGLE_API_KEY not set. Create a .env file.[/red]")
        raise SystemExit(1)

    # Build and run the pipeline
    console.print(f"\nModel: [cyan]{settings.gemini_model}[/cyan]")
    console.print()

    graph = build_graph()

    initial_state = {}
    if url:
        initial_state["job_url"] = url
    if job_text:
        initial_state["job_text"] = job_text

    steps = [
        "Scraping/validating",
        "Analyzing job posting",
        "Matching skills (RAG)",
        "Generating application materials",
        "Advising strategy",
        "Saving results",
    ]

    with console.status("") as status:
        step_idx = 0

        for event in graph.stream(initial_state):
            node_name = list(event.keys())[0]
            state = event[node_name]

            if step_idx < len(steps):
                status.update(f"[bold green]{steps[step_idx]}...")
            step_idx += 1

            # Check for error at each step
            if state.get("error"):
                display_error(state["error"])
                break

    # Display results
    final_state = state

    if final_state.get("job_analysis"):
        display_job_analysis(final_state["job_analysis"])

    if final_state.get("match_analysis"):
        display_match_analysis(final_state["match_analysis"])

    if final_state.get("writer_output"):
        display_writer_output(final_state["writer_output"])

    if final_state.get("advisor_output"):
        display_advisor_output(final_state["advisor_output"])

    if final_state.get("output_path"):
        display_saved(final_state["output_path"], final_state.get("db_id", 0))

    if final_state.get("error"):
        display_error(final_state["error"])


if __name__ == "__main__":
    main()

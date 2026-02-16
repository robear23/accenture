"""LangGraph StateGraph builder for the application pipeline."""

from langgraph.graph import END, StateGraph

from job_assistant.orchestration.nodes import (
    advise_strategy,
    analyze_job,
    generate_content,
    match_skills,
    save_results,
    scrape_or_validate,
)
from job_assistant.schemas.state import ApplicationState
from job_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def _has_error(state: ApplicationState) -> str:
    """Conditional edge: skip to save_results if error is set."""
    if state.get("error"):
        return "save_results"
    return "continue"


def build_graph():
    """Build and compile the LangGraph pipeline.

    Pipeline: scrape_or_validate → analyze_job → match_skills →
              generate_content → advise_strategy → save_results → END

    Each node has a conditional edge: if error is set, skip to save_results.
    """
    graph = StateGraph(ApplicationState)

    # Add nodes
    graph.add_node("scrape_or_validate", scrape_or_validate)
    graph.add_node("analyze_job", analyze_job)
    graph.add_node("match_skills", match_skills)
    graph.add_node("generate_content", generate_content)
    graph.add_node("advise_strategy", advise_strategy)
    graph.add_node("save_results", save_results)

    # Set entry point
    graph.set_entry_point("scrape_or_validate")

    # Conditional edges: on error, skip to save_results
    graph.add_conditional_edges(
        "scrape_or_validate",
        _has_error,
        {"save_results": "save_results", "continue": "analyze_job"},
    )
    graph.add_conditional_edges(
        "analyze_job",
        _has_error,
        {"save_results": "save_results", "continue": "match_skills"},
    )
    graph.add_conditional_edges(
        "match_skills",
        _has_error,
        {"save_results": "save_results", "continue": "generate_content"},
    )
    graph.add_conditional_edges(
        "generate_content",
        _has_error,
        {"save_results": "save_results", "continue": "advise_strategy"},
    )
    graph.add_conditional_edges(
        "advise_strategy",
        _has_error,
        {"save_results": "save_results", "continue": "save_results"},
    )

    # save_results → END
    graph.add_edge("save_results", END)

    app = graph.compile()
    logger.info("LangGraph pipeline compiled successfully")
    return app

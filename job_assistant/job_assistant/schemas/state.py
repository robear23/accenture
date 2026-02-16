"""LangGraph application state definition."""

from typing import TypedDict

from job_assistant.schemas.models import (
    AdvisorOutput,
    JobAnalysis,
    MatchAnalysis,
    WriterOutput,
)


class ApplicationState(TypedDict, total=False):
    """State passed through the LangGraph pipeline.

    All fields are optional (total=False) so the state can be built incrementally.
    """

    # Input
    job_url: str
    job_text: str

    # Pipeline outputs
    job_analysis: JobAnalysis
    match_analysis: MatchAnalysis
    writer_output: WriterOutput
    advisor_output: AdvisorOutput

    # Error handling
    error: str

    # Metadata
    output_path: str
    db_id: int

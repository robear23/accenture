"""Content Writer Agent - generates cover letter and application email."""

from typing import Any

from job_assistant.agents.base import BaseAgent
from job_assistant.rag.retriever import retrieve
from job_assistant.schemas.models import JobAnalysis, MatchAnalysis, WriterOutput
from job_assistant.utils.prompts import WRITER_PROMPT


class ContentWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(output_schema=WriterOutput)

    def get_prompt(self, **kwargs: Any) -> str:
        analysis: JobAnalysis = kwargs["job_analysis"]
        match: MatchAnalysis = kwargs["match_analysis"]

        # Retrieve profile context for writing
        context_chunks = retrieve("professional profile experience achievements", top_k=8)
        context = "\n\n---\n\n".join(c["text"] for c in context_chunks)

        strong = ", ".join(m.skill for m in match.strong_matches)
        usps = ", ".join(match.unique_selling_points)

        return WRITER_PROMPT.format(
            context=context,
            title=analysis.title,
            company=analysis.company,
            location=analysis.location,
            industry=analysis.industry,
            match_score=match.overall_score,
            strong_matches=strong,
            usps=usps,
            match_summary=match.match_summary,
        )

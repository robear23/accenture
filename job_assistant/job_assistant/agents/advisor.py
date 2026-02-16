"""Strategy Advisor Agent - provides strategic application advice."""

from typing import Any

from job_assistant.agents.base import BaseAgent
from job_assistant.rag.retriever import retrieve
from job_assistant.schemas.models import (
    AdvisorOutput,
    JobAnalysis,
    MatchAnalysis,
)
from job_assistant.utils.prompts import ADVISOR_PROMPT


class StrategyAdvisorAgent(BaseAgent):
    def __init__(self):
        super().__init__(output_schema=AdvisorOutput)

    def get_prompt(self, **kwargs: Any) -> str:
        analysis: JobAnalysis = kwargs["job_analysis"]
        match: MatchAnalysis = kwargs["match_analysis"]

        # Brief context for strategic advice
        context_chunks = retrieve("professional profile achievements skills", top_k=5)
        context = "\n\n---\n\n".join(c["text"] for c in context_chunks)

        strong = ", ".join(m.skill for m in match.strong_matches)
        partial = ", ".join(m.skill for m in match.partial_matches)
        gaps = ", ".join(m.skill for m in match.gaps)
        usps = ", ".join(match.unique_selling_points)

        return ADVISOR_PROMPT.format(
            title=analysis.title,
            company=analysis.company,
            location=analysis.location,
            industry=analysis.industry,
            seniority=analysis.seniority,
            match_score=match.overall_score,
            strong_matches=strong,
            partial_matches=partial,
            gaps=gaps,
            usps=usps,
            context=context,
        )

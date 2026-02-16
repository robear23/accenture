"""Skill Matcher Agent - matches candidate skills to job requirements using RAG."""

from typing import Any

from job_assistant.agents.base import BaseAgent
from job_assistant.rag.retriever import multi_query_retrieve
from job_assistant.schemas.models import JobAnalysis, MatchAnalysis
from job_assistant.utils.logger import get_logger
from job_assistant.utils.prompts import MATCHER_PROMPT

logger = get_logger(__name__)


class SkillMatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(output_schema=MatchAnalysis)

    def _build_rag_queries(self, analysis: JobAnalysis) -> list[str]:
        """Build one RAG query per requirement for comprehensive retrieval."""
        queries = []
        for skill in analysis.required_skills:
            queries.append(f"experience with {skill}")
        for skill in analysis.preferred_skills:
            queries.append(f"experience with {skill}")
        for resp in analysis.responsibilities[:5]:
            queries.append(resp)
        return queries

    def _retrieve_context(self, analysis: JobAnalysis) -> str:
        """Retrieve relevant knowledge base chunks via multi-query RAG."""
        queries = self._build_rag_queries(analysis)
        logger.info(f"Running {len(queries)} RAG queries for skill matching")
        results = multi_query_retrieve(queries)
        context_parts = [r["text"] for r in results]
        return "\n\n---\n\n".join(context_parts)

    def get_prompt(self, **kwargs: Any) -> str:
        analysis: JobAnalysis = kwargs["job_analysis"]
        context = self._retrieve_context(analysis)
        return MATCHER_PROMPT.format(
            context=context,
            title=analysis.title,
            company=analysis.company,
            required_skills=", ".join(analysis.required_skills),
            preferred_skills=", ".join(analysis.preferred_skills),
            responsibilities="\n".join(f"- {r}" for r in analysis.responsibilities),
            seniority=analysis.seniority,
        )

"""Job Analyzer Agent - extracts structured info from job postings."""

from typing import Any

from job_assistant.agents.base import BaseAgent
from job_assistant.schemas.models import JobAnalysis
from job_assistant.utils.prompts import ANALYZER_PROMPT


class JobAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(output_schema=JobAnalysis)

    def get_prompt(self, **kwargs: Any) -> str:
        return ANALYZER_PROMPT.format(job_text=kwargs["job_text"])

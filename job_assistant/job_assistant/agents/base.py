"""Base agent with ChatGoogleGenerativeAI and structured output."""

from abc import ABC, abstractmethod
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from job_assistant.config import settings
from job_assistant.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base agent using Google Gemini with structured output."""

    def __init__(self, output_schema: type[BaseModel]):
        self.output_schema = output_schema
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            max_output_tokens=4096,
        )
        self.structured_llm = self.llm.with_structured_output(output_schema)

    @abstractmethod
    def get_prompt(self, **kwargs: Any) -> str:
        """Build the prompt for this agent. Subclasses must implement."""
        ...

    def run(self, **kwargs: Any) -> BaseModel:
        """Execute the agent and return structured output."""
        prompt = self.get_prompt(**kwargs)
        logger.info(f"Running {self.__class__.__name__}...")
        result = self.structured_llm.invoke(prompt)
        logger.info(f"{self.__class__.__name__} completed.")
        return result

"""LangGraph node functions wrapping each agent."""

from job_assistant.agents.analyzer import JobAnalyzerAgent
from job_assistant.agents.matcher import SkillMatcherAgent
from job_assistant.agents.writer import ContentWriterAgent
from job_assistant.agents.advisor import StrategyAdvisorAgent
from job_assistant.schemas.state import ApplicationState
from job_assistant.storage.database import save_application
from job_assistant.storage.exporter import export_analysis
from job_assistant.utils.logger import get_logger
from job_assistant.utils.scraper import scrape_job_posting

logger = get_logger(__name__)


def scrape_or_validate(state: ApplicationState) -> ApplicationState:
    """Scrape job URL or validate provided text."""
    try:
        if state.get("job_text"):
            logger.info("Using provided job text")
            return state

        url = state.get("job_url")
        if not url:
            return {**state, "error": "No job URL or text provided."}

        logger.info(f"Scraping job posting from: {url}")
        text = scrape_job_posting(url)
        return {**state, "job_text": text}
    except Exception as e:
        logger.error(f"Scrape/validate failed: {e}")
        return {**state, "error": str(e)}


def analyze_job(state: ApplicationState) -> ApplicationState:
    """Run the Job Analyzer agent."""
    try:
        agent = JobAnalyzerAgent()
        result = agent.run(job_text=state["job_text"])
        return {**state, "job_analysis": result}
    except Exception as e:
        logger.error(f"Job analysis failed: {e}")
        return {**state, "error": str(e)}


def match_skills(state: ApplicationState) -> ApplicationState:
    """Run the Skill Matcher agent with RAG."""
    try:
        agent = SkillMatcherAgent()
        result = agent.run(job_analysis=state["job_analysis"])
        return {**state, "match_analysis": result}
    except Exception as e:
        logger.error(f"Skill matching failed: {e}")
        return {**state, "error": str(e)}


def generate_content(state: ApplicationState) -> ApplicationState:
    """Run the Content Writer agent."""
    try:
        agent = ContentWriterAgent()
        result = agent.run(
            job_analysis=state["job_analysis"],
            match_analysis=state["match_analysis"],
        )
        return {**state, "writer_output": result}
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return {**state, "error": str(e)}


def advise_strategy(state: ApplicationState) -> ApplicationState:
    """Run the Strategy Advisor agent."""
    try:
        agent = StrategyAdvisorAgent()
        result = agent.run(
            job_analysis=state["job_analysis"],
            match_analysis=state["match_analysis"],
        )
        return {**state, "advisor_output": result}
    except Exception as e:
        logger.error(f"Strategy advising failed: {e}")
        return {**state, "error": str(e)}


def save_results(state: ApplicationState) -> ApplicationState:
    """Save results to database and export JSON."""
    try:
        job_analysis = state.get("job_analysis")
        match_analysis = state.get("match_analysis")
        writer_output = state.get("writer_output")
        advisor_output = state.get("advisor_output")

        # Export JSON
        filepath = export_analysis(
            job_analysis=job_analysis,
            match_analysis=match_analysis,
            writer_output=writer_output,
            advisor_output=advisor_output,
            job_url=state.get("job_url"),
        )

        # Save to database
        db_id = save_application(
            job_url=state.get("job_url"),
            job_analysis=job_analysis,
            match_analysis=match_analysis,
            writer_output=writer_output,
            advisor_output=advisor_output,
        )

        return {**state, "output_path": str(filepath), "db_id": db_id}
    except Exception as e:
        logger.error(f"Saving results failed: {e}")
        return {**state, "error": str(e)}

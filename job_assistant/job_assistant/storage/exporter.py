"""JSON export for individual analysis results."""

import json
from datetime import datetime
from pathlib import Path

from job_assistant.config import OUTPUT_DIR
from job_assistant.schemas.models import (
    AdvisorOutput,
    JobAnalysis,
    MatchAnalysis,
    WriterOutput,
)
from job_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def export_analysis(
    job_analysis: JobAnalysis | None,
    match_analysis: MatchAnalysis | None,
    writer_output: WriterOutput | None,
    advisor_output: AdvisorOutput | None,
    job_url: str | None = None,
) -> Path:
    """Export a complete analysis to a timestamped JSON file.

    Returns the path to the exported file.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    company = "unknown"
    title = "unknown"
    if job_analysis:
        company = job_analysis.company.lower().replace(" ", "_")[:20]
        title = job_analysis.title.lower().replace(" ", "_")[:20]

    filename = f"{timestamp}_{company}_{title}.json"
    filepath = OUTPUT_DIR / filename

    data = {
        "exported_at": datetime.now().isoformat(),
        "job_url": job_url,
        "job_analysis": job_analysis.model_dump() if job_analysis else None,
        "match_analysis": match_analysis.model_dump() if match_analysis else None,
        "writer_output": writer_output.model_dump() if writer_output else None,
        "advisor_output": advisor_output.model_dump() if advisor_output else None,
    }

    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Exported analysis to {filepath}")
    return filepath

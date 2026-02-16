"""SQLite database for application tracking."""

import json
import sqlite3
from datetime import datetime

from job_assistant.config import DB_PATH
from job_assistant.schemas.models import (
    AdvisorOutput,
    JobAnalysis,
    MatchAnalysis,
    WriterOutput,
)
from job_assistant.utils.logger import get_logger

logger = get_logger(__name__)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    job_url TEXT,
    job_title TEXT,
    company TEXT,
    location TEXT,
    industry TEXT,
    seniority TEXT,
    match_score INTEGER,
    recommendation TEXT,
    confidence TEXT,
    cover_letter TEXT,
    application_email TEXT,
    job_analysis_json TEXT,
    match_analysis_json TEXT,
    writer_output_json TEXT,
    advisor_output_json TEXT,
    status TEXT DEFAULT 'generated',
    notes TEXT
)
"""


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute(CREATE_TABLE)
    conn.commit()
    return conn


def save_application(
    job_url: str | None,
    job_analysis: JobAnalysis | None,
    match_analysis: MatchAnalysis | None,
    writer_output: WriterOutput | None,
    advisor_output: AdvisorOutput | None,
) -> int:
    """Save a complete application analysis to the database.

    Returns the inserted row ID.
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO applications (
                created_at, job_url, job_title, company, location, industry,
                seniority, match_score, recommendation, confidence,
                cover_letter, application_email,
                job_analysis_json, match_analysis_json,
                writer_output_json, advisor_output_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now().isoformat(),
                job_url,
                job_analysis.title if job_analysis else None,
                job_analysis.company if job_analysis else None,
                job_analysis.location if job_analysis else None,
                job_analysis.industry if job_analysis else None,
                job_analysis.seniority if job_analysis else None,
                match_analysis.overall_score if match_analysis else None,
                advisor_output.overall_recommendation if advisor_output else None,
                advisor_output.confidence_level if advisor_output else None,
                writer_output.cover_letter if writer_output else None,
                writer_output.application_email if writer_output else None,
                job_analysis.model_dump_json() if job_analysis else None,
                match_analysis.model_dump_json() if match_analysis else None,
                writer_output.model_dump_json() if writer_output else None,
                advisor_output.model_dump_json() if advisor_output else None,
            ),
        )
        conn.commit()
        row_id = cursor.lastrowid
        logger.info(f"Saved application #{row_id} to database")
        return row_id
    finally:
        conn.close()


def update_status(row_id: int, status: str, notes: str | None = None) -> None:
    """Update the status of an application."""
    conn = _get_connection()
    try:
        conn.execute(
            "UPDATE applications SET status = ?, notes = ? WHERE id = ?",
            (status, notes, row_id),
        )
        conn.commit()
    finally:
        conn.close()


def list_applications() -> list[dict]:
    """List all applications with summary info."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            """SELECT id, created_at, job_title, company, match_score,
                      recommendation, status
               FROM applications ORDER BY created_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

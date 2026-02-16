"""Markdown loader and section-based chunker for knowledge base files."""

from pathlib import Path

from job_assistant.config import KNOWLEDGE_BASE_DIR
from job_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def _categorize_file(filename: str) -> str:
    """Derive a category from the knowledge base filename."""
    if filename.startswith("experience_"):
        return "experience"
    if filename.startswith("skills_"):
        return "skills"
    if filename.startswith("cv_"):
        return "profile"
    return filename.replace(".md", "")


def chunk_markdown(filepath: Path) -> list[dict]:
    """Split a markdown file into chunks by ## headers.

    Returns a list of dicts with keys: text, metadata (source, category, section).
    """
    text = filepath.read_text(encoding="utf-8")
    filename = filepath.stem
    category = _categorize_file(filepath.name)

    chunks = []
    current_section = "intro"
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            # Save previous section if it has content
            content = "\n".join(current_lines).strip()
            if content:
                chunks.append({
                    "text": content,
                    "metadata": {
                        "source": filename,
                        "category": category,
                        "section": current_section,
                    },
                })
            current_section = line.lstrip("# ").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    # Don't forget the last section
    content = "\n".join(current_lines).strip()
    if content:
        chunks.append({
            "text": content,
            "metadata": {
                "source": filename,
                "category": category,
                "section": current_section,
            },
        })

    return chunks


def load_knowledge_base() -> list[dict]:
    """Load and chunk all markdown files in the knowledge base directory.

    Returns a list of dicts with keys: text, metadata.
    """
    all_chunks = []
    md_files = sorted(KNOWLEDGE_BASE_DIR.glob("*.md"))

    if not md_files:
        logger.warning(f"No markdown files found in {KNOWLEDGE_BASE_DIR}")
        return all_chunks

    for filepath in md_files:
        chunks = chunk_markdown(filepath)
        all_chunks.extend(chunks)
        logger.info(f"Loaded {len(chunks)} chunks from {filepath.name}")

    logger.info(f"Total knowledge base chunks: {len(all_chunks)}")
    return all_chunks

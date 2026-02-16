# Multi-Agent Job Application Assistant

A production-ready multi-agent system that analyzes job postings and generates tailored application materials using LangGraph, LangChain, RAG, and Claude.

## Architecture

```
START → scrape_or_validate → analyze_job → match_skills → generate_content → advise_strategy → save_results → END
```

**4 Specialized Agents:**
- **Job Analyzer** - Extracts structured data from job postings
- **Skill Matcher** - Matches candidate skills using RAG retrieval against a personal knowledge base
- **Content Writer** - Generates tailored cover letters and application emails
- **Strategy Advisor** - Provides strategic application advice and interview prep

**Key Technologies:**
- **LangGraph** - Pipeline orchestration with error bail-out
- **LangChain + Claude** - LLM agents with structured output
- **ChromaDB + SentenceTransformers** - Local RAG with persistent vector store
- **Rich + Click** - Beautiful CLI output

## Setup

```bash
# Create virtual environment
py -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API key
copy .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

```bash
# Index knowledge base (first run or after changes)
py run.py --reindex

# Analyze a job posting URL
py run.py --url "https://example.com/job-posting"

# Analyze from text
py run.py --text "Full job description text here..."

# Analyze from file
py run.py --text-file job_description.txt

# Debug mode
py run.py --verbose --text-file job_description.txt
```

## Output

Each analysis produces:
- **Console output** - Rich formatted display of all results
- **JSON file** - Timestamped export in `output/`
- **Database record** - SQLite entry in `data/applications.db`

## Project Structure

```
job_assistant/
├── run.py                  # CLI entry point
├── job_assistant/
│   ├── config.py           # Settings and paths
│   ├── agents/             # 4 LLM agents (analyzer, matcher, writer, advisor)
│   ├── schemas/            # Pydantic models + LangGraph state
│   ├── rag/                # ChromaDB + embeddings + retriever
│   ├── orchestration/      # LangGraph pipeline
│   ├── storage/            # SQLite + JSON export
│   └── utils/              # Scraper, logger, prompts, display
├── knowledge_base/         # 10 markdown files (candidate profile)
├── output/                 # Generated analysis JSON files
└── data/                   # ChromaDB, SQLite, logs
```

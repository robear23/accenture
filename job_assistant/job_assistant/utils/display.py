"""Rich console output formatting for results display."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from job_assistant.schemas.models import (
    AdvisorOutput,
    JobAnalysis,
    MatchAnalysis,
    WriterOutput,
)

console = Console()


def display_job_analysis(analysis: JobAnalysis) -> None:
    """Display structured job analysis."""
    table = Table(title="Job Analysis", show_header=False, padding=(0, 2))
    table.add_column("Field", style="bold cyan", width=20)
    table.add_column("Value")

    table.add_row("Title", analysis.title)
    table.add_row("Company", analysis.company)
    table.add_row("Location", analysis.location)
    table.add_row("Seniority", analysis.seniority)
    table.add_row("Industry", analysis.industry)
    table.add_row("Salary", analysis.salary_info)
    table.add_row("Required Skills", ", ".join(analysis.required_skills))
    if analysis.preferred_skills:
        table.add_row("Preferred Skills", ", ".join(analysis.preferred_skills))

    console.print()
    console.print(table)
    console.print(Panel(analysis.summary, title="Summary", border_style="blue"))


def display_match_analysis(match: MatchAnalysis) -> None:
    """Display skill matching results."""
    # Score display
    score = match.overall_score
    if score >= 70:
        color = "green"
    elif score >= 40:
        color = "yellow"
    else:
        color = "red"

    console.print()
    console.print(
        Panel(
            f"[bold {color}]{score}/100[/bold {color}]",
            title="Match Score",
            border_style=color,
        )
    )

    # Matches table
    if match.strong_matches:
        table = Table(title="Strong Matches", border_style="green")
        table.add_column("Skill", style="bold")
        table.add_column("Evidence")
        for m in match.strong_matches:
            table.add_row(m.skill, m.evidence)
        console.print(table)

    if match.partial_matches:
        table = Table(title="Partial Matches", border_style="yellow")
        table.add_column("Skill", style="bold")
        table.add_column("Evidence")
        for m in match.partial_matches:
            table.add_row(m.skill, m.evidence)
        console.print(table)

    if match.gaps:
        table = Table(title="Gaps", border_style="red")
        table.add_column("Skill", style="bold")
        table.add_column("Notes")
        for m in match.gaps:
            table.add_row(m.skill, m.evidence)
        console.print(table)

    if match.unique_selling_points:
        console.print(
            Panel(
                "\n".join(f"- {usp}" for usp in match.unique_selling_points),
                title="Unique Selling Points",
                border_style="magenta",
            )
        )

    console.print(Panel(match.match_summary, title="Match Summary", border_style="blue"))


def display_writer_output(output: WriterOutput) -> None:
    """Display generated application materials."""
    console.print()
    console.print(
        Panel(output.cover_letter, title="Cover Letter", border_style="green")
    )
    console.print(
        Panel(output.application_email, title="Application Email", border_style="cyan")
    )
    if output.key_themes:
        console.print(
            Panel(
                "\n".join(f"- {t}" for t in output.key_themes),
                title="Key Themes",
                border_style="blue",
            )
        )


def display_advisor_output(output: AdvisorOutput) -> None:
    """Display strategic advice."""
    rec = output.overall_recommendation
    if "Strong" in rec:
        color = "green"
    elif "Caveat" in rec or "Low" in output.confidence_level:
        color = "yellow"
    elif "Skip" in rec:
        color = "red"
    else:
        color = "cyan"

    console.print()
    console.print(
        Panel(
            f"[bold {color}]{rec}[/bold {color}] (Confidence: {output.confidence_level})",
            title="Recommendation",
            border_style=color,
        )
    )
    console.print(Panel(output.strategy, title="Strategy", border_style="blue"))

    if output.cv_tailoring:
        console.print(
            Panel(
                "\n".join(f"- {s}" for s in output.cv_tailoring),
                title="CV Tailoring Suggestions",
                border_style="cyan",
            )
        )

    if output.interview_prep:
        console.print(
            Panel(
                "\n".join(f"- {t}" for t in output.interview_prep),
                title="Interview Prep Topics",
                border_style="magenta",
            )
        )

    if output.potential_questions:
        console.print(
            Panel(
                "\n".join(f"- {q}" for q in output.potential_questions),
                title="Likely Interview Questions",
                border_style="blue",
            )
        )

    if output.risk_factors:
        console.print(
            Panel(
                "\n".join(f"- {r}" for r in output.risk_factors),
                title="Risk Factors",
                border_style="yellow",
            )
        )


def display_error(error: str) -> None:
    """Display an error message."""
    console.print(Panel(f"[bold red]{error}[/bold red]", title="Error", border_style="red"))


def display_saved(output_path: str, db_id: int) -> None:
    """Display save confirmation."""
    console.print()
    console.print(f"[green]Results saved:[/green]")
    console.print(f"  JSON: {output_path}")
    console.print(f"  Database ID: {db_id}")

"""Pydantic output models for all agents."""

from pydantic import BaseModel, Field


# --- Job Analyzer Agent Output ---

class JobAnalysis(BaseModel):
    """Structured analysis of a job posting."""

    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    location: str = Field(description="Job location (city/remote/hybrid)")
    seniority: str = Field(description="Seniority level (entry/mid/senior/lead)")
    salary_info: str = Field(default="Not specified", description="Salary if mentioned")
    required_skills: list[str] = Field(description="Required skills and qualifications")
    preferred_skills: list[str] = Field(
        default_factory=list, description="Preferred/nice-to-have skills"
    )
    responsibilities: list[str] = Field(description="Key responsibilities")
    cultural_indicators: list[str] = Field(
        default_factory=list,
        description="Cultural values, team dynamics, work environment indicators",
    )
    industry: str = Field(description="Industry/sector")
    summary: str = Field(description="2-3 sentence summary of the role")


# --- Skill Matcher Agent Output ---

class SkillMatch(BaseModel):
    """A single skill match with evidence."""

    skill: str = Field(description="The skill being matched")
    evidence: str = Field(description="Evidence from Robbie's background")
    strength: str = Field(description="How strong the match is: strong/partial/gap")


class MatchAnalysis(BaseModel):
    """Comprehensive skill matching analysis."""

    overall_score: int = Field(
        ge=0, le=100, description="Overall match score 0-100"
    )
    strong_matches: list[SkillMatch] = Field(
        description="Skills where Robbie is a strong match"
    )
    partial_matches: list[SkillMatch] = Field(
        description="Skills where Robbie has partial/transferable experience"
    )
    gaps: list[SkillMatch] = Field(
        description="Skills where Robbie has limited/no experience"
    )
    transferable_skills: list[str] = Field(
        description="Key transferable skills from other domains"
    )
    unique_selling_points: list[str] = Field(
        description="What makes Robbie stand out for this role"
    )
    match_summary: str = Field(
        description="2-3 sentence summary of the overall match"
    )


# --- Content Writer Agent Output ---

class WriterOutput(BaseModel):
    """Generated application materials."""

    cover_letter: str = Field(
        description="Full cover letter tailored to the role (3-4 paragraphs)"
    )
    application_email: str = Field(
        description="Brief email to accompany the application (2-3 paragraphs)"
    )
    key_themes: list[str] = Field(
        description="Key themes and angles used in the application materials"
    )


# --- Strategy Advisor Agent Output ---

class AdvisorOutput(BaseModel):
    """Strategic advice for the application."""

    overall_recommendation: str = Field(
        description="Overall recommendation: Strong Apply / Apply / Apply with Caveats / Consider Skipping"
    )
    strategy: str = Field(
        description="Recommended application strategy (2-3 sentences)"
    )
    cv_tailoring: list[str] = Field(
        description="Specific suggestions for tailoring the CV to this role"
    )
    interview_prep: list[str] = Field(
        description="Key topics to prepare for if invited to interview"
    )
    potential_questions: list[str] = Field(
        description="Likely interview questions and suggested angles"
    )
    networking_suggestions: list[str] = Field(
        description="Networking or research actions to strengthen the application"
    )
    risk_factors: list[str] = Field(
        description="Potential concerns or risks with this application"
    )
    confidence_level: str = Field(
        description="Overall confidence: High / Medium / Low"
    )

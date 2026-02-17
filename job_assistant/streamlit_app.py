import sys
from pathlib import Path
import streamlit as st

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from job_assistant.config import settings
from job_assistant.orchestration.graph import build_graph
from job_assistant.schemas.models import (
    JobAnalysis,
    MatchAnalysis,
    WriterOutput,
    AdvisorOutput,
)
import os

# Page configuration
st.set_page_config(
    page_title="Job Application Assistant",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 Job Application Assistant")
st.markdown("Analyzes job postings and generates tailored application materials using AI agents.")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Try to load from Streamlit secrets
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
        settings.google_api_key = st.secrets["GOOGLE_API_KEY"]
    
    if not settings.google_api_key:
        st.error("GOOGLE_API_KEY not set. Please create a .env file or add to Streamlit Secrets.")
        st.stop()
    
    st.success("API Key detected.")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown(
        """
        This tool uses a multi-agent system to:
        1. Analyze job postings
        2. Match your skills (RAG)
        3. Generate cover letters
        4. Provide strategic advice
        """
    )

# Input Section
input_method = st.radio("Input Method", ["URL", "Text"], horizontal=True)

job_url = ""
job_text = ""

if input_method == "URL":
    job_url = st.text_input("Job Posting URL", placeholder="https://linkedin.com/jobs/...")
else:
    job_text = st.text_area("Job Description", height=300, placeholder="Paste job description here...")

if st.button("Analyze Job", type="primary"):
    if not job_url and not job_text:
        st.warning("Please provide a URL or Job Description.")
    else:
        # Run the graph
        status_container = st.container()
        
        with status_container:
            progress_text = "Starting analysis..."
            bar = st.progress(0, text=progress_text)
            
            graph = build_graph()
            initial_state = {}
            if job_url:
                initial_state["job_url"] = job_url
            if job_text:
                initial_state["job_text"] = job_text
            
            steps = [
                "scrape_or_validate",
                "analyze_job",
                "match_skills",
                "generate_content",
                "advise_strategy",
                "save_results",
            ]
            
            final_state = {}
            
            try:
                step_count = 0
                for event in graph.stream(initial_state):
                    node_name = list(event.keys())[0]
                    final_state = event[node_name]
                    
                    # Update progress
                    step_count += 1
                    progress = min(step_count / len(steps), 1.0)
                    bar.progress(progress, text=f"Processing: {node_name}...")
                    
                    if final_state.get("error"):
                        st.error(f"Error in {node_name}: {final_state['error']}")
                        break
                
                bar.progress(1.0, text="Analysis Complete!")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

        # Display Results using Tabs
        if final_state and not final_state.get("error"):
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Job Analysis", 
                "🎯 Skill Match", 
                "✍️ Application Materials", 
                "💡 Strategy Advice"
            ])
            
            # 1. Job Analysis
            with tab1:
                if final_state.get("job_analysis"):
                    ja: JobAnalysis = final_state["job_analysis"]
                    st.header(ja.title)
                    st.subheader(f"{ja.company} - {ja.location}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Seniority:** {ja.seniority}")
                        st.markdown(f"**Industry:** {ja.industry}")
                    with col2:
                        st.markdown(f"**Salary:** {ja.salary_info}")
                    
                    st.divider()
                    st.markdown("### Summary")
                    st.info(ja.summary)
                    
                    st.markdown("### Skills")
                    st.markdown("**Required:** " + ", ".join(ja.required_skills))
                    if ja.preferred_skills:
                        st.markdown("**Preferred:** " + ", ".join(ja.preferred_skills))
                    
                    st.markdown("### Responsibilities")
                    for resp in ja.responsibilities:
                        st.markdown(f"- {resp}")

            # 2. Skill Match
            with tab2:
                if final_state.get("match_analysis"):
                    ma: MatchAnalysis = final_state["match_analysis"]
                    
                    # Score
                    score_color = "green" if ma.overall_score >= 70 else "orange" if ma.overall_score >= 40 else "red"
                    st.metric("Match Score", f"{ma.overall_score}/100")
                    st.progress(ma.overall_score / 100)
                    
                    st.markdown("### Match Summary")
                    st.info(ma.match_summary)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### ✅ Strong Matches")
                        for m in ma.strong_matches:
                            with st.expander(m.skill):
                                st.write(m.evidence)
                                
                    with col2:
                        st.markdown("### ⚠️ Gaps & Partial")
                        for m in ma.partial_matches:
                            with st.expander(f"Partial: {m.skill}"):
                                st.write(m.evidence)
                        for m in ma.gaps:
                            with st.expander(f"Gap: {m.skill}"):
                                st.write(m.evidence)
                    
                    if ma.unique_selling_points:
                        st.markdown("### ✨ Unique Selling Points")
                        for usp in ma.unique_selling_points:
                            st.markdown(f"- {usp}")

            # 3. Application Materials
            with tab3:
                if final_state.get("writer_output"):
                    wo: WriterOutput = final_state["writer_output"]
                    
                    st.subheader("Cover Letter")
                    st.text_area("Copy content", wo.cover_letter, height=400)
                    
                    st.subheader("Email Application")
                    st.text_area("Copy content", wo.application_email, height=200)
                    
                    st.markdown("### Key Themes")
                    for theme in wo.key_themes:
                        st.markdown(f"- {theme}")

            # 4. Strategy Advice
            with tab4:
                if final_state.get("advisor_output"):
                    ao: AdvisorOutput = final_state["advisor_output"]
                    
                    rec_color = "green" if "Strong" in ao.overall_recommendation else "orange"
                    st.markdown(f"### Recommendation: :{rec_color}[{ao.overall_recommendation}]")
                    st.caption(f"Confidence: {ao.confidence_level}")
                    
                    st.info(ao.strategy)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 📝 CV Tailoring")
                        for item in ao.cv_tailoring:
                            st.markdown(f"- {item}")
                            
                        st.markdown("### 🤝 Networking")
                        for item in ao.networking_suggestions:
                            st.markdown(f"- {item}")
                            
                    with col2:
                        st.markdown("### 🎤 Interview Prep")
                        for item in ao.interview_prep:
                            st.markdown(f"- {item}")
                            
                        st.markdown("### ❓ Potential Questions")
                        for item in ao.potential_questions:
                            st.markdown(f"- {item}")

                    if ao.risk_factors:
                        st.error("### ⚠️ Risk Factors")
                        for risk in ao.risk_factors:
                            st.markdown(f"- {risk}")

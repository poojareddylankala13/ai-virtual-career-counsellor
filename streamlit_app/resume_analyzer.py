import streamlit as st
import re
from io import BytesIO
from utils.db_helper import DBHelper
from utils.recommender import CareerRecommender
from utils.nltk_preprocessor import NLTKPreprocessor

# Standard packages
try:
    import pypdf
except ImportError:
    pypdf = None

db = DBHelper()
recommender = CareerRecommender()
preprocessor = NLTKPreprocessor()


def extract_text_from_pdf(file_bytes) -> str:
    """Extracts raw text content from uploaded PDF file using pypdf."""
    if not pypdf:
        return "pypdf library not installed. Cannot parse PDF."
    try:
        reader = pypdf.PdfReader(BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"


def parse_and_score_resume(resume_text: str, target_skills: list) -> tuple:
    """
    Parses resume text and returns:
    1. Overall Resume Score (length, structure, links, sections)
    2. ATS Match Score (overlap with target career skills)
    3. Missing Skills list
    4. Improvement Suggestions list
    """
    score = 0
    suggestions = []

    # 1. Check Contact Details
    email_regex = r"[\w\.-]+@[\w\.-]+\.\w+"
    phone_regex = r"\+?\d[\d -]{8,12}\d"
    has_email = bool(re.search(email_regex, resume_text))
    has_phone = bool(re.search(phone_regex, resume_text))

    if has_email:
        score += 15
    else:
        suggestions.append("Missing Contact Info: Include a professional email address.")

    if has_phone:
        score += 15
    else:
        suggestions.append("Missing Contact Info: Add a reachable contact number.")

    # 2. Check Professional Links (LinkedIn, GitHub, Portfolio)
    has_links = "linkedin.com" in resume_text.lower() or "github.com" in resume_text.lower()
    if has_links:
        score += 15
    else:
        suggestions.append("Online Presence: Add links to your LinkedIn, GitHub, or portfolio website.")

    # 3. Check Crucial Sections
    sections = {
        "education": ["education", "academic", "university", "school", "college"],
        "experience": ["experience", "employment", "work history", "internship", "professional background"],
        "projects": ["projects", "personal projects", "portfolio"],
        "skills": ["skills", "technical skills", "expertise", "competencies"]
    }
    
    found_sections = []
    text_lower = resume_text.lower()
    for sec_name, keywords in sections.items():
        found = False
        for kw in keywords:
            if kw in text_lower:
                found = True
                break
        if found:
            score += 10
            found_sections.append(sec_name)
        else:
            suggestions.append(f"Structure: Add a dedicated section for '{sec_name.capitalize()}'.")

    # 4. Check word count / length
    words = resume_text.split()
    if len(words) > 300:
        score += 15
    elif len(words) > 100:
        score += 8
        suggestions.append("Length: Expand your descriptions. A professional resume should have at least 300 words.")
    else:
        suggestions.append("Length: Your resume is extremely short. Ensure you describe your experiences, projects, and skills in detail.")

    # Cap Resume Score at 100
    overall_score = min(100, score)

    # 5. Calculate ATS Match Score based on Target Career Skills
    # Use NLTK lemmatization to check resume words
    clean_resume_tokens = set(preprocessor.preprocess(resume_text))
    
    matching_skills = []
    missing_skills = []

    for skill in target_skills:
        clean_skill_tokens = preprocessor.preprocess(skill)
        # Check if all tokens of the skill overlap in resume
        is_found = False
        for cst in clean_skill_tokens:
            if cst in clean_resume_tokens or any(cst in r_tok for r_tok in clean_resume_tokens):
                is_found = True
                break
        
        if is_found:
            matching_skills.append(skill)
        else:
            missing_skills.append(skill)

    if target_skills:
        ats_score = int((len(matching_skills) / len(target_skills)) * 100)
    else:
        ats_score = 100

    if missing_skills:
        suggestions.append(f"ATS Optimization: Incorporate missing keywords into your skills or projects section: {', '.join(missing_skills[:5])}")

    return overall_score, ats_score, missing_skills, suggestions


def render_resume_analyzer():
    user_email = st.session_state["user_email"]

    st.markdown("""
    <div class="header-container">
        <div class="header-title">📄 ATS Resume Analyzer & Scorecard</div>
        <div class="header-subtitle">Upload your resume in PDF/TXT format, evaluate your score against a target career, and get suggestions.</div>
    </div>
    """, unsafe_allow_html=True)

    # Check if pypdf is installed
    if not pypdf:
        st.warning("The PDF parsing package `pypdf` was not found. PDF uploads will fail. You can install it or upload standard .txt resumes instead.")

    # Target career selection
    careers = recommender.careers
    career_names = [c["name"] for c in careers]
    
    col_sel, _ = st.columns([2, 2])
    with col_sel:
        target_career_name = st.selectbox("Select Target Career to analyze against:", career_names)
    
    target_career = next((c for c in careers if c["name"] == target_career_name), None)
    target_skills = target_career.get("required_skills", []) if target_career else []

    # File Uploader
    uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file is not None:
        filename = uploaded_file.name
        file_bytes = uploaded_file.read()
        
        # Parse text
        if filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_bytes)
        else:
            resume_text = file_bytes.decode("utf-8", errors="ignore")

        if not resume_text or "Error parsing" in resume_text or "not installed" in resume_text:
            st.error("Failed to parse resume text. Please check the file format.")
            return

        with st.spinner("Analyzing resume content against target skills..."):
            overall_score, ats_score, missing_skills, suggestions = parse_and_score_resume(resume_text, target_skills)
            
            # Save analysis results to database
            db.save_resume_analysis(user_email, overall_score, ats_score, missing_skills, suggestions, filename)
            
        st.success("Resume analyzed successfully!")

        # Display Scores side-by-side
        st.markdown("### 📊 Evaluation Metrics")
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.markdown(f"""
            <div class="career-card" style="text-align: center; border-left: 5px solid #EC4899;">
                <h4 style="margin: 0; color: #EC4899;">Overall Resume Score</h4>
                <p style="font-size: 2.2rem; font-weight: 700; margin: 0.5rem 0 0 0;">{overall_score}/100</p>
                <p style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.3rem;">Checks formatting, links, email, phone, and standard sections.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_s2:
            st.markdown(f"""
            <div class="career-card" style="text-align: center; border-left: 5px solid #8B5CF6;">
                <h4 style="margin: 0; color: #8B5CF6;">ATS Skill Match Rating</h4>
                <p style="font-size: 2.2rem; font-weight: 700; margin: 0.5rem 0 0 0;">{ats_score}%</p>
                <p style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.3rem;">Checks how well your resume matches skills required for {target_career_name}.</p>
            </div>
            """, unsafe_allow_html=True)

        # Tabs for detailed breakdown
        tab_suggestions, tab_missing, tab_report = st.tabs(["💡 Suggestions", "❌ Missing Skills", "📋 Export Report"])
        
        with tab_suggestions:
            st.markdown("#### Actionable Improvement Suggestions")
            if suggestions:
                for sug in suggestions:
                    st.write(f"- {sug}")
            else:
                st.balloons()
                st.success("Excellent! Your resume satisfies all basic criteria and matches keywords perfectly.")

        with tab_missing:
            st.markdown(f"#### Skills missing in your resume for {target_career_name}")
            if missing_skills:
                st.write("These key skills are required for your target role but were not found in your resume text:")
                # Display in nice tags
                cols = st.columns(4)
                for i, ms in enumerate(missing_skills):
                    with cols[i % 4]:
                        st.markdown(f'<div class="badge" style="width:100%; text-align:center;">{ms}</div>', unsafe_allow_html=True)
            else:
                st.success("All required skills for this career path are present in your resume!")

        with tab_report:
            # Generate Text Report
            report_text = f"==========================================\n"
            report_text += f"RESUME ATS ANALYSIS REPORT - AI VIRTUAL CAREER COUNSELLOR\n"
            report_text += f"==========================================\n"
            report_text += f"Target Career: {target_career_name}\n"
            report_text += f"File Analyzed: {filename}\n\n"
            report_text += f"Overall Resume Score: {overall_score}/100\n"
            report_text += f"ATS Skill Match: {ats_score}%\n\n"
            report_text += f"--- MISSING SKILLS ---\n"
            for ms in missing_skills:
                report_text += f"- {ms}\n"
            report_text += f"\n--- IMPROVEMENT SUGGESTIONS ---\n"
            for sug in suggestions:
                report_text += f"- {sug}\n"
            report_text += f"\nGenerated via AI Virtual Career Counsellor."

            st.text_area("Analysis Report Summary", value=report_text, height=250)
            
            st.download_button(
                label="Download Analysis Report (.txt)",
                data=report_text,
                file_name=f"ATS_Report_{target_career_name.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        # Load previous analysis if exists
        prev_data = db.get_resume_analysis(user_email)
        if prev_data:
            st.markdown("### 📜 Previous Analysis Summary")
            st.markdown(f"**Last File Evaluated:** `{prev_data.get('filename')}` (on {prev_data.get('updated_at')[:10]})")
            
            col_ps1, col_ps2 = st.columns(2)
            with col_ps1:
                st.metric(label="Resume Score", value=f"{prev_data.get('score')}/100")
            with col_ps2:
                st.metric(label="ATS Match Rating", value=f"{prev_data.get('ats_score')}%")
            
            st.markdown("**Suggestions:**")
            for sug in prev_data.get("suggestions", []):
                st.write(f"- {sug}")
        else:
            st.info("Upload your resume in PDF/TXT format above to begin the evaluation.")

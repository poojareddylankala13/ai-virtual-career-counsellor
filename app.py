import streamlit as st
import uuid
import os
from config import APP_TITLE, APP_THEME_COLOR, ACCENT_COLOR
from utils.db_helper import DBHelper

# Set page config as the very first Streamlit command
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database Helper
db = DBHelper()

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

session_id = st.session_state["session_id"]

if "user_profile" not in st.session_state:
    # Try to load existing profile from DB
    profile = db.get_profile(session_id)
    if not profile:
        profile = {
            "name": "",
            "age": 18,
            "highest_qualification": "High School",
            "current_degree": "",
            "academic_year": "1st Year",
            "skills": "",
            "interests": "",
            "preferred_domain": "Technology",
            "career_goal": ""
        }
    st.session_state["user_profile"] = profile

if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = []

# Inject custom global CSS for rich premium aesthetics
st.markdown(f"""
<style>
    /* Main body background and font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif;
    }}
    
    /* Elegant Title and Header styling */
    .header-container {{
        background: linear-gradient(135deg, {APP_THEME_COLOR} 0%, #1E293B 100%);
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        color: white;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }}
    
    .header-container::before {{
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 60%);
        pointer-events: none;
    }}
    
    .header-title {{
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #60A5FA, #3B82F6, #93C5FD);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .header-subtitle {{
        font-size: 1.2rem;
        color: #94A3B8;
        font-weight: 400;
    }}
    
    /* Modern Glassmorphic Cards */
    .career-card {{
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .career-card:hover {{
        transform: translateY(-4px);
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1), 0 4px 6px -2px rgba(59, 130, 246, 0.05);
    }}
    
    .badge {{
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(59, 130, 246, 0.2);
        display: inline-block;
        margin-bottom: 0.5rem;
    }}
    
    .score-badge {{
        float: right;
        font-size: 1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        border: none;
    }}
    
    /* Custom Sidebar Logo/Branding */
    .sidebar-brand {{
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
    }}
</style>
""", unsafe_allow_html=True)

# Import sub-page modules
from streamlit_app.home import render_home
from streamlit_app.counsellor import render_counsellor
from streamlit_app.explorer import render_explorer
from streamlit_app.about import render_about

# Sidebar navigation branding
st.sidebar.markdown("""
<div class="sidebar-brand">
    <h2 style="color: #60A5FA; margin-bottom: 0; font-weight:700;">ApexPath AI</h2>
    <p style="color: #94A3B8; font-size: 0.85rem;">Virtual Career Counsellor</p>
</div>
""", unsafe_allow_html=True)

# Navigation radio list
page = st.sidebar.radio(
    "Navigate to:",
    ["Home", "Career Counsellor", "Career Explorer", "About Project"],
    index=0
)

# Active Session details in sidebar footer
st.sidebar.markdown("---")
st.sidebar.caption(f"Session Active: `...{session_id[-8:]}`")

# Route to respective render page
if page == "Home":
    render_home()
elif page == "Career Counsellor":
    render_counsellor()
elif page == "Career Explorer":
    render_explorer()
elif page == "About Project":
    render_about()

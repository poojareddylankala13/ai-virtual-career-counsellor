import streamlit as st
import uuid
from config import APP_TITLE, APP_THEME_COLOR
from utils.db_helper import DBHelper
from streamlit_app.auth import render_auth_pages, handle_logout

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

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

# 1. Global CSS Styling Rules
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif;
    }}
    
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
    
    .sidebar-brand {{
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
    }}
</style>
""", unsafe_allow_html=True)

# 2. Light Theme Overrides (Inject if selected)
if st.session_state["theme"] == "light":
    st.markdown("""
    <style>
        .stApp {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }
        .career-card {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            color: #0F172A !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        }
        .career-card:hover {
            border-color: #3B82F6 !important;
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.05) !important;
        }
        h1, h2, h3, h4, h5, h6, p, li, span, label, div {
            color: #0F172A !important;
        }
        .stMarkdown p, .stMarkdown li, .stMarkdown span {
            color: #1E293B !important;
        }
        .badge {
            background: rgba(59, 130, 246, 0.08) !important;
            color: #2563EB !important;
            border: 1px solid rgba(59, 130, 246, 0.15) !important;
        }
        .sidebar-brand h2 {
            color: #2563EB !important;
        }
        .header-title {
            background: linear-gradient(to right, #2563EB, #1D4ED8, #3B82F6) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
        }
        .header-subtitle {
            color: #F1F5F9 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# 3. Route Access Protections (Block page rendering if unauthenticated)
if "user_email" not in st.session_state or not st.session_state["user_email"]:
    render_auth_pages()
else:
    # Set theme from database profile configuration
    user_profile = db.get_user_profile(st.session_state["user_email"])
    st.session_state["theme"] = user_profile.get("theme", "dark")

    # Import view render helper modules
    from streamlit_app.dashboard import render_dashboard
    from streamlit_app.counsellor import render_counsellor
    from streamlit_app.career_match import render_career_match
    from streamlit_app.roadmaps import render_roadmaps
    from streamlit_app.resume_analyzer import render_resume_analyzer
    from streamlit_app.home import render_home as render_analytics
    from streamlit_app.chat_history import render_chat_history
    from streamlit_app.profile import render_profile
    from streamlit_app.settings import render_settings

    # Sidebar Navigation brand logo
    st.sidebar.markdown("""
    <div class="sidebar-brand">
        <h2 style="color: #60A5FA; margin-bottom: 0; font-weight:700;">ApexPath AI</h2>
        <p style="color: #94A3B8; font-size: 0.85rem;">Virtual Career Counsellor</p>
    </div>
    """, unsafe_allow_html=True)

    # Collapsible sidebar with icons + labels
    page = st.sidebar.radio(
        "Navigation Menu:",
        [
            "🏠 Dashboard",
            "🤖 Career Counsellor",
            "🏆 Career Match",
            "🗺️ Study Roadmaps",
            "📄 Resume Analyzer",
            "📊 Analytics",
            "📜 Chat History",
            "👤 Profile",
            "⚙️ Settings",
            "🚪 Logout"
        ],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Logged in as: `{st.session_state['user_email']}`")

    # Routing redirection handlers
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "🤖 Career Counsellor":
        render_counsellor()
    elif page == "🏆 Career Match":
        render_career_match()
    elif page == "🗺️ Study Roadmaps":
        render_roadmaps()
    elif page == "📄 Resume Analyzer":
        render_resume_analyzer()
    elif page == "📊 Analytics":
        render_analytics()
    elif page == "📜 Chat History":
        render_chat_history()
    elif page == "👤 Profile":
        render_profile()
    elif page == "⚙️ Settings":
        render_settings()
    elif page == "🚪 Logout":
        handle_logout()

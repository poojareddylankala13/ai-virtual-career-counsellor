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
    
    .stApp {{
        background-color: #0B0B0F !important;
        color: #FFFFFF !important;
    }}
    
    .header-container {{
        background: linear-gradient(135deg, #15151E 0%, #0B0B0F 100%);
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid #2A2A35;
        box-shadow: 0 4px 30px rgba(124, 58, 237, 0.08);
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
        background: radial-gradient(circle, rgba(124, 58, 237, 0.12) 0%, transparent 60%);
        pointer-events: none;
    }}
    
    .header-title {{
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #C084FC, #7C3AED, #A855F7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .header-subtitle {{
        font-size: 1.2rem;
        color: #B3B3C5;
        font-weight: 400;
    }}
    
    .career-card {{
        background: #15151E;
        border: 1px solid #2A2A35;
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }}
    
    .career-card:hover {{
        transform: translateY(-4px);
        border-color: #7C3AED;
        box-shadow: 0 10px 25px rgba(124, 58, 237, 0.12);
    }}
    
    .badge {{
        background: rgba(124, 58, 237, 0.1);
        color: #C084FC;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(124, 58, 237, 0.25);
        display: inline-block;
        margin-bottom: 0.5rem;
    }}
    
    .score-badge {{
        float: right;
        font-size: 1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        border: none;
        box-shadow: 0 4px 10px rgba(124, 58, 237, 0.2);
    }}
    
    .sidebar-brand {{
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid #2A2A35;
        margin-bottom: 1.5rem;
    }}

    /* Target all Streamlit standard buttons for premium purple gradients */
    div.stButton > button {{
        background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15) !important;
        transition: all 0.2s ease !important;
        height: auto !important;
    }}
    
    div.stButton > button:hover {{
        background: linear-gradient(135deg, #9333EA 0%, #A855F7 100%) !important;
        box-shadow: 0 6px 18px rgba(124, 58, 237, 0.3) !important;
        transform: translateY(-2px) !important;
        border: none !important;
    }}
    
    div.stButton > button:active {{
        transform: translateY(1px) !important;
    }}

    /* Custom scrollbar styles */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: #0B0B0F;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #2A2A35;
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #7C3AED;
    }}
    
    /* Progress Bars styling */
    div.stProgress > div > div > div > div {{
        background-color: #7C3AED !important;
    }}
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
        <h2 style="color: #C084FC; margin-bottom: 0; font-weight:700; font-size: 1.4rem;">AI Virtual</h2>
        <p style="color: #B3B3C5; font-size: 0.85rem;">Career Counsellor</p>
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
    st.sidebar.markdown("<div style='text-align: center; color: #B3B3C5; font-size: 0.75rem; margin-top: 1rem;'>© 2026 AI Virtual Career Counsellor</div>", unsafe_allow_html=True)

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

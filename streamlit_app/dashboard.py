import streamlit as st
import pandas as pd
import base64
import plotly.express as px
import plotly.graph_objects as go
from utils.db_helper import DBHelper
from utils.recommender import CareerRecommender
from streamlit_app.home import load_career_stats

db = DBHelper()
recommender = CareerRecommender()


def get_avatar_html(photo_bytes) -> str:
    """Returns HTML tag for circular profile avatar."""
    if photo_bytes:
        try:
            encoded = base64.b64encode(photo_bytes).decode()
            src = f"data:image/png;base64,{encoded}"
        except Exception:
            src = "https://api.dicebear.com/7.x/bottts/svg?seed=counsellor"
    else:
        src = "https://api.dicebear.com/7.x/bottts/svg?seed=counsellor"
    return f'<img src="{src}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid #7C3AED; box-shadow: 0 4px 10px rgba(124,58,237,0.25);">'


def render_dashboard():
    user_email = st.session_state["user_email"]
    
    # Reload profile from Database to ensure freshness
    profile = db.get_user_profile(user_email)
    st.session_state["user_profile"] = profile

    name = profile.get("name", "User")
    photo = profile.get("profile_photo")

    st.markdown("""
    <div class="header-container">
        <div class="header-title">📊 AI Virtual Career Counsellor Dashboard</div>
        <div class="header-subtitle">Your personalized portal for career development, study plans, and resume matching.</div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome Header Panel
    col_av, col_wel = st.columns([1, 8])
    with col_av:
        st.markdown(get_avatar_html(photo), unsafe_allow_html=True)
    with col_wel:
        st.markdown(f"""
        <div style="margin-top: 0.5rem;">
            <h2 style="color: #C084FC; margin-bottom: 0.2rem; font-weight:700;">Welcome back, {name}! 🚀</h2>
            <p style="color: #B3B3C5; font-size: 1rem; margin-top:0;">Explore your career milestones, continue roadmaps, or consult your AI guide.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. Fetch Metrics Data
    recs = recommender.recommend(profile)
    top_match_pct = "0%"
    top_career = "None"
    if recs:
        top_match_pct = f"{recs[0]['match_percentage']}%"
        top_career = recs[0]["name"]
        
    saved_roadmaps = db.get_saved_roadmaps(user_email)
    saved_count = len(saved_roadmaps)
    
    # Calculate completed lessons
    completed_lessons = 0
    for career in saved_roadmaps:
        progress = db.get_roadmap_progress(user_email, career)
        completed_lessons += sum(1 for val in progress.values() if val)

    resume_data = db.get_resume_analysis(user_email)
    resume_score = "N/A"
    ats_score = "N/A"
    if resume_data:
        resume_score = f"{resume_data.get('score', 0)}/100"
        ats_score = f"{resume_data.get('ats_score', 0)}%"

    # Summary Cards Grid Layout
    m1, m2, m3, m4, m5, m6 = st.columns(6)

    with m1:
        st.markdown(f"""
        <div class="career-card" style="text-align: center; padding: 1rem; height: 130px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Top Match %</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #10B981; margin-top: 0.5rem;">{top_match_pct}</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="career-card" style="text-align: center; padding: 1rem; height: 130px; overflow: hidden; text-overflow: ellipsis;">
            <div style="font-size: 0.75rem; color: #B3B3C5; text-transform: uppercase;">Recommended</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #C084FC; margin-top: 0.8rem; line-height: 1.2;">{top_career}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="career-card" style="text-align: center; padding: 1rem; height: 130px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Active Roadmaps</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #F59E0B; margin-top: 0.5rem;">{saved_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="career-card" style="text-align: center; padding: 1rem; height: 130px;">
            <div style="font-size: 0.75rem; color: #B3B3C5; text-transform: uppercase;">Tasks Done</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #C084FC; margin-top: 0.5rem;">{completed_lessons}</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown(f"""
        <div class="career-card" style="text-align: center; padding: 1rem; height: 130px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Resume Score</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #EC4899; margin-top: 0.5rem;">{resume_score}</div>
        </div>
        """, unsafe_allow_html=True)

    with m6:
        st.markdown(f"""
        <div class="career-card" style="text-align: center; padding: 1rem; height: 130px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Resume ATS</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #8B5CF6; margin-top: 0.5rem;">{ats_score}</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Main sections
    col_content1, col_content2 = st.columns([7, 5])

    with col_content1:
        # Continue Learning progress bars
        st.markdown("### 📚 Continue Learning & Milestones")
        if saved_roadmaps:
            for career_name in saved_roadmaps:
                # Find matching career detail
                career_data = next((c for c in recommender.careers if c["name"] == career_name), None)
                if career_data:
                    total_steps = len(career_data.get("learning_roadmap", []))
                    progress = db.get_roadmap_progress(user_email, career_name)
                    done = sum(1 for val in progress.values() if val)
                    
                    percent = int((done / max(1, total_steps)) * 100)
                    
                    st.markdown(f"""
                    <div style="margin-bottom: 1.2rem;">
                        <span style="font-weight: 600; color:#E2E8F0;">{career_name}</span> 
                        <span style="float: right; color: #C084FC; font-size: 0.85rem;">{percent}% Complete ({done}/{total_steps} steps)</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(done / max(1, total_steps))
        else:
            st.info("You haven't saved any career roadmaps yet. Go to 'Career Match' or 'Explorer' and pin pathways to track them here!")

        # Recent AI Chats
        st.markdown("<br>### 💬 Recent AI Conversations", unsafe_allow_html=True)
        sessions = db.get_chat_sessions(user_email)
        if sessions:
            for s in sessions[:3]:  # Top 3 sessions
                st.markdown(f"""
                <div class="career-card" style="padding: 1rem; margin-bottom: 0.8rem;">
                    <span style="color: #B3B3C5; font-size: 0.8rem; float:right;">Created: {s['created_at'][:10]}</span>
                    <h4 style="margin: 0; color: #C084FC;">💬 {s['title']}</h4>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No recent chat conversations. Visit the Career Counsellor to start a session.")

    with col_content2:
        # Latest Career recommendations list
        st.markdown("### 🏆 Top Matches for You")
        if recs:
            for r in recs[:3]:
                st.markdown(f"""
                <div class="career-card" style="padding: 1rem; margin-bottom: 0.8rem;">
                    <span class="score-badge" style="font-size: 0.8rem;">{r['match_percentage']}%</span>
                    <h4 style="margin: 0; color: #C084FC;">{r['name']}</h4>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #B3B3C5;">Domain: {r['domain']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No career match data calculated. Please verify your skills and interests in your Profile.")

        # Recommended Courses for Top Career
        st.markdown("### 📚 Recommended Courses")
        if recs and len(recs) > 0:
            top_rec_courses = recs[0].get("recommended_courses", [])
            if top_rec_courses:
                for course in top_rec_courses[:3]:
                    st.markdown(f"• **{course}**")
            else:
                st.write("No specific courses available for your top career.")
        else:
            st.write("Fill your profile details to see recommended courses.")

    # 3. Analytics Section (Move existing charts lower)
    st.markdown("---")
    st.markdown("## 📊 Career Market Analytics")
    df = load_career_stats()

    if not df.empty:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown("### Career Domains Distribution")
            domain_counts = df["Domain"].value_counts().reset_index()
            domain_counts.columns = ["Domain", "Careers Count"]
            fig1 = px.bar(
                domain_counts,
                x="Domain",
                y="Careers Count",
                color="Domain",
                color_discrete_sequence=["#7C3AED", "#A855F7", "#C084FC", "#9333EA", "#5B21B6", "#D8B4FE"],
                template="plotly_dark"
            )
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=20),
                height=250
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_c2:
            st.markdown("### Salary Benchmarks (INR)")
            df_salary = df.sort_values(by="Mid Salary", ascending=False).head(5)
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=df_salary["Name"], y=df_salary["Entry Salary"], name="Entry", marker_color="#7C3AED"))
            fig2.add_trace(go.Bar(x=df_salary["Name"], y=df_salary["Mid Salary"], name="Mid", marker_color="#A855F7"))
            fig2.add_trace(go.Bar(x=df_salary["Name"], y=df_salary["Senior Salary"], name="Senior", marker_color="#C084FC"))
            fig2.update_layout(
                barmode='group',
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=20),
                height=250,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig2, use_container_width=True)

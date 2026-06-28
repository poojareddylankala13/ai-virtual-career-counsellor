import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from config import CAREER_DATASET_PATH


def load_career_stats():
    """Loads dataset and aggregates data for visualizations."""
    if not os.path.exists(CAREER_DATASET_PATH):
        return pd.DataFrame()
    try:
        with open(CAREER_DATASET_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        rows = []
        for c in data:
            salaries = c.get("salary_range", {})
            # Helper to extract integer from salary range string e.g. "₹6,00,000 - ₹10,00,000" -> average 800000
            def parse_avg_salary(sal_str):
                if not sal_str or sal_str == "N/A":
                    return 0
                # Extract digits
                nums = [int(s) for s in sal_str.replace(",", "").split() if s.isdigit()]
                # If we have INR symbols and numbers
                nums_clean = [int(s) for s in sal_str.replace("₹", "").replace(",", "").replace("+", "").split() if s.replace("-", "").strip().isdigit()]
                # Let's do a regex extraction of numbers
                import re
                found = re.findall(r'\d+', sal_str.replace(",", ""))
                if found:
                    found_ints = [int(x) for x in found]
                    return sum(found_ints) / len(found_ints)
                return 0

            avg_entry = parse_avg_salary(salaries.get("entry", ""))
            avg_mid = parse_avg_salary(salaries.get("mid", ""))
            avg_senior = parse_avg_salary(salaries.get("senior", ""))

            rows.append({
                "Name": c["name"],
                "Domain": c["domain"],
                "Entry Salary": avg_entry,
                "Mid Salary": avg_mid,
                "Senior Salary": avg_senior,
                "Skills Count": len(c.get("required_skills", []))
            })
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Error loading stats: {e}")
        return pd.DataFrame()


def render_home():
    # Elegant Hero Banner
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🎓 AI Virtual Career Counsellor</div>
        <div class="header-subtitle">Navigate your academic and professional future with AI-guided recommendations, custom study roadmaps, and natural language career support.</div>
    </div>
    """, unsafe_allow_html=True)

    # Core Features (Grid Layout)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="career-card" style="height: 250px;">
            <h4 style="color:#C084FC; margin-top:0;">🤖 Conversational AI</h4>
            <p style="color:#B3B3C5; font-size:0.9rem;">Chat with our Rasa-powered virtual counsellor to inquire about specific job requirements, study roadmaps, portfolio projects, and salary figures in plain language.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="career-card" style="height: 250px;">
            <h4 style="color:#C084FC; margin-top:0;">🧠 Hybrid Match Engine</h4>
            <p style="color:#B3B3C5; font-size:0.9rem;">Fill out a structured profile with your skills, qualification level, and interests to receive instantaneous percentage-based career matching recommendations.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="career-card" style="height: 250px;">
            <h4 style="color:#C084FC; margin-top:0;">🗺️ Curated Study Paths</h4>
            <p style="color:#B3B3C5; font-size:0.9rem;">Every recommendation comes with a step-by-step roadmap, recommended online courses (MOOCs), recognized certifications, and practical portfolio project ideas.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## 📊 Career Market Analytics")
    df = load_career_stats()

    if not df.empty:
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("### Job Availability by Domain")
            # Count domain values
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
                height=300
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_chart2:
            st.markdown("### Average Annual Salary Trends (INR)")
            # Take top 6 high-paying or standard careers for visual neatness
            df_salary = df.sort_values(by="Mid Salary", ascending=False).head(6)

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_salary["Name"],
                y=df_salary["Entry Salary"],
                name="Entry Level",
                marker_color="#7C3AED"
            ))
            fig2.add_trace(go.Bar(
                x=df_salary["Name"],
                y=df_salary["Mid Salary"],
                name="Mid Level",
                marker_color="#A855F7"
            ))
            fig2.add_trace(go.Bar(
                x=df_salary["Name"],
                y=df_salary["Senior Salary"],
                name="Senior Level",
                marker_color="#C084FC"
            ))

            fig2.update_layout(
                barmode='group',
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Career statistics are unavailable. Please ensure `data/careers.json` exists.")

    st.markdown("---")
    st.markdown("""
    ### How to Get Started:
    1. Click on the **Career Counsellor** tab in the sidebar.
    2. Fill out your details in the **User Profile Form** to save your preferences.
    3. View your matching career cards instantly, or interact with the **Counsellor Chatbot** to ask specific career-related questions in real-time.
    """)

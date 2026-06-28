import streamlit as st
import json
import os
from config import CAREER_DATASET_PATH
from utils.recommender import CareerRecommender

recommender = CareerRecommender()


def render_explorer():
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🔍 Career Explorer Dashboard</div>
        <div class="header-subtitle">Browse, filter, and search our catalog of 25+ professional career paths across multiple sectors.</div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Search and filter tools
    col_search, col_filter = st.columns([2, 1])

    with col_search:
        search_query = st.text_input("Search careers by name or skill keyword:", placeholder="e.g. ML, Analyst, Python, Design...")

    with col_filter:
        domains = ["All"] + recommender.get_all_domains()
        selected_domain = st.selectbox("Filter by Domain/Sector:", domains)

    # 2. Filter Careers based on controls
    careers = recommender.careers
    filtered_careers = []

    for c in careers:
        match_domain = (selected_domain == "All") or (c["domain"].lower() == selected_domain.lower())
        
        match_query = True
        if search_query:
            query = search_query.lower()
            name_match = query in c["name"].lower()
            desc_match = query in c.get("description", "").lower()
            skills_match = any(query in s.lower() for s in c.get("required_skills", []))
            match_query = name_match or desc_match or skills_match

        if match_domain and match_query:
            filtered_careers.append(c)

    # 3. Display Results
    st.markdown(f"Showing **{len(filtered_careers)}** matching career profiles:")

    if filtered_careers:
        for c in filtered_careers:
            st.markdown(f"""
            <div class="career-card" style="margin-bottom: 0.5rem;">
                <span class="badge" style="float: right;">{c['domain']}</span>
                <h3 style="margin: 0; color: #C084FC;">{c['name']}</h3>
                <p style="margin-top: 0.5rem; margin-bottom: 0; font-size: 0.9rem; color: #B3B3C5;">{c['description'][:150]}...</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"Explore the {c['name']} pathway"):
                st.write(c["description"])
                
                col_det1, col_det2 = st.columns(2)
                
                with col_det1:
                    st.markdown("#### 🛠️ Core Skills Required")
                    st.write(", ".join(c.get("required_skills", [])))
                    
                    st.markdown("#### 🗺️ Step-by-Step Roadmap")
                    for i, step in enumerate(c.get("learning_roadmap", []), start=1):
                        st.write(f"{i}. {step}")
                        
                    st.markdown("#### 🏅 Certifications")
                    for cert in c.get("certifications", []):
                        st.write(f"✓ {cert}")

                with col_det2:
                    st.markdown("#### 💰 Salary Range (Annual)")
                    salaries = c.get("salary_range", {})
                    st.write(f"• **Entry Level**: {salaries.get('entry', 'N/A')}")
                    st.write(f"• **Mid Level**: {salaries.get('mid', 'N/A')}")
                    st.write(f"• **Senior Level**: {salaries.get('senior', 'N/A')}")
                    
                    st.markdown("#### 📚 Recommended MOOCs")
                    for course in c.get("courses", []):
                        st.write(f"• {course}")
                        
                    st.markdown("#### ⚡ Suggested Portfolio Projects")
                    for proj in c.get("projects", []):
                        st.write(f"• {proj}")
                
                st.markdown("---")
                st.markdown(f"📈 **Growth:** {c.get('growth', '')}")
                st.markdown(f"🚀 **Future Outlook:** {c.get('future_scope', '')}")
                
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.warning("No career pathways match your query. Try clearing the search or filtering by another sector.")

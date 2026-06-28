import streamlit as st
from utils.db_helper import DBHelper
from utils.recommender import CareerRecommender

db = DBHelper()
recommender = CareerRecommender()


def render_career_match():
    user_email = st.session_state["user_email"]
    
    # Reload profile from Database to keep fresh
    profile = db.get_user_profile(user_email)
    st.session_state["user_profile"] = profile

    st.markdown("""
    <div class="header-container">
        <div class="header-title">🏆 Hybrid Career Match Engine</div>
        <div class="header-subtitle">Define your credentials, interests, and skills to discover matching professional career paths.</div>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_recs = st.columns([5, 6])

    with col_form:
        st.markdown("### 📋 Academic & Skills Profile")
        with st.form("match_profile_form"):
            name = st.text_input("Full Name", value=profile.get("name", ""))
            
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", min_value=12, max_value=60, value=int(profile.get("age", 18) or 18))
                highest_qual = st.selectbox(
                    "Highest Qualification",
                    ["High School", "Diploma", "Bachelor's", "Master's", "PhD"],
                    index=["High School", "Diploma", "Bachelor's", "Master's", "PhD"].index(profile.get("highest_qualification", "High School"))
                )
            with c2:
                degree = st.text_input("Current/Planned Degree (e.g., B.Tech, B.Com)", value=profile.get("current_degree", ""))
                ac_year = st.selectbox(
                    "Academic Year",
                    ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"],
                    index=["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"].index(profile.get("academic_year", "1st Year"))
                )

            skills = st.text_area("Skills (comma-separated, e.g. Python, SQL, Excel, Writing)", value=profile.get("skills", ""))
            interests = st.text_area("Interests / Hobbies (comma-separated, e.g. Coding, Finance)", value=profile.get("interests", ""))
            
            c3, c4 = st.columns(2)
            with c3:
                domain = st.selectbox(
                    "Preferred Career Domain",
                    ["Technology", "Commerce", "Arts", "Healthcare", "Business", "Government"],
                    index=["Technology", "Commerce", "Arts", "Healthcare", "Business", "Government"].index(profile.get("preferred_domain", "Technology"))
                )
            with c4:
                goal = st.text_input("Career Goal / Ambition", value=profile.get("career_goal", ""))

            save_btn = st.form_submit_button("Calculate Career Matches")

            if save_btn:
                updated_profile = {
                    "name": name,
                    "age": age,
                    "highest_qualification": highest_qual,
                    "current_degree": degree,
                    "academic_year": ac_year,
                    "skills": skills,
                    "interests": interests,
                    "preferred_domain": domain,
                    "career_goal": goal
                }
                
                # Update SQLite profile
                db.update_user_profile(user_email, updated_profile)
                st.session_state["user_profile"] = db.get_user_profile(user_email)
                
                # Recalculate
                recs = recommender.recommend(updated_profile)
                st.session_state["recommendations"] = recs
                st.success("Profile saved and matches updated!")
                st.rerun()

    with col_recs:
        st.markdown("### 🏆 Compatible Pathways")
        
        # Load recommendations if empty
        recs = st.session_state.get("recommendations", [])
        if not recs:
            recs = recommender.recommend(profile)
            st.session_state["recommendations"] = recs

        if recs:
            # Query saved list to render correct button state
            saved_roadmaps = db.get_saved_roadmaps(user_email)

            for rec in recs[:4]:  # Show top 4 matches
                is_saved = rec["name"] in saved_roadmaps
                
                st.markdown(f"""
                <div class="career-card" style="border-left: 5px solid #7C3AED;">
                    <span class="score-badge">{rec['match_percentage']}% Match</span>
                    <span class="badge">{rec['domain']}</span>
                    <h3 style="margin: 0.5rem 0; color:#C084FC;">{rec['name']}</h3>
                    <p style="font-size:0.9rem; color:#E2E8F0; margin-bottom:1rem;">{rec['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_exp, col_save = st.columns([2, 1])
                with col_exp:
                    exp = st.expander(f"Explore details for {rec['name']}")
                    with exp:
                        st.write(rec["description"])
                        
                        st.markdown("**💰 Salary Range:**")
                        st.write(f"- Entry Level: {rec['salary_range'].get('entry', 'N/A')}")
                        st.write(f"- Mid Level: {rec['salary_range'].get('mid', 'N/A')}")
                        st.write(f"- Senior Level: {rec['salary_range'].get('senior', 'N/A')}")
                        
                        st.markdown("**🛠️ Skills Breakdown:**")
                        st.write(f"- **Matching Skills:** {', '.join(rec['user_existing_skills']) if rec['user_existing_skills'] else 'None'}")
                        st.write(f"- **Skills to Learn:** {', '.join(rec['skills_to_improve']) if rec['skills_to_improve'] else 'None'}")
                        
                        st.markdown("**🏅 Certifications:**")
                        for cert in rec["recommended_certifications"]:
                            st.write(f"✓ {cert}")
                        
                        st.markdown("**⚡ Suggested Projects:**")
                        for p in rec["suggested_projects"]:
                            st.write(f"• {p}")
                            
                        st.markdown("📈 **outlook:**")
                        st.write(rec["future_scope"])

                with col_save:
                    if is_saved:
                        st.button("Saved ✓", key=f"save_{rec['name']}", disabled=True, use_container_width=True)
                    else:
                        if st.button("Save Roadmap", key=f"save_{rec['name']}", use_container_width=True):
                            db.save_roadmap(user_email, rec["name"])
                            st.success(f"Pinned {rec['name']} study plan!")
                            st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("Provide academic & skills details in the form to generate career matches.")

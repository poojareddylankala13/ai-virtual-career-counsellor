import streamlit as st
import requests
import json
import os
from config import RASA_WEBHOOK_URL, RASA_SERVER_URL, CAREER_DATASET_PATH
from utils.db_helper import DBHelper
from utils.recommender import CareerRecommender
from utils.nltk_preprocessor import NLTKPreprocessor

# Initialize database, recommender, and NLTK preprocessor
db = DBHelper()
recommender = CareerRecommender()
preprocessor = NLTKPreprocessor()


def sync_rasa_slots(session_id: str, profile: dict):
    """Sends slot update events to Rasa to synchronize Streamlit profile form edits."""
    url = f"{RASA_SERVER_URL}/conversations/{session_id}/tracker/events"
    slot_mapping = {
        "name": "user_name",
        "age": "user_age",
        "highest_qualification": "qualification",
        "current_degree": "degree",
        "academic_year": "academic_year",
        "skills": "skills",
        "interests": "interests",
        "preferred_domain": "preferred_domain",
        "career_goal": "career_goal"
    }
    events = []
    for prof_key, slot_name in slot_mapping.items():
        val = profile.get(prof_key, "")
        events.append({
            "event": "slot",
            "name": slot_name,
            "value": str(val)
        })
    try:
        response = requests.post(url, json=events, timeout=1.0)
        return response.status_code == 200
    except Exception:
        return False


def get_rasa_response(session_id: str, message: str) -> list:
    """Sends user message to Rasa REST webhook and returns bot utterances."""
    payload = {"sender": session_id, "message": message}
    try:
        response = requests.post(RASA_WEBHOOK_URL, json=payload, timeout=3.0)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []


def handle_offline_fallback(user_msg: str, session_id: str) -> str:
    """
    Fallback NLP assistant using NLTK to parse inquiries
    and generate replies from careers.json when Rasa is offline.
    """
    msg_clean = user_msg.lower()
    
    # Load careers for search
    careers = recommender.careers
    
    # 1. Detect if inquiring about a specific career from the database
    matched_career = None
    for c in careers:
        if c["name"].lower() in msg_clean:
            matched_career = c
            break
            
    # Check if there is an active career in session
    if not matched_career and "active_chat_career" in st.session_state:
        matched_career = st.session_state["active_chat_career"]

    if matched_career:
        st.session_state["active_chat_career"] = matched_career
        c_name = matched_career["name"]
        
        # Check sub-questions using NLTK preprocessed tokens
        tokens = preprocessor.preprocess(msg_clean)
        
        if any(w in tokens for w in ["salary", "pay", "earn", "wage"]):
            salaries = matched_career.get("salary_range", {})
            return (
                f"💼 **Annual Salary Range for {c_name}**:\n\n"
                f"• **Entry Level**: {salaries.get('entry', 'N/A')}\n"
                f"• **Mid Level**: {salaries.get('mid', 'N/A')}\n"
                f"• **Senior Level**: {salaries.get('senior', 'N/A')}"
            )
            
        if any(w in tokens for w in ["skill", "qualify", "requirement", "require"]):
            skills = ", ".join(matched_career.get("required_skills", []))
            return f"🛠️ **Core Skills needed for {c_name}**:\n\n👉 {skills}"
            
        if any(w in tokens for w in ["course", "study", "class", "moocs"]):
            courses = matched_career.get("courses", [])
            lines = "\n".join([f"• {c}" for c in courses])
            return f"📚 **Recommended Courses for {c_name}**:\n\n{lines}"
            
        if any(w in tokens for w in ["certification", "certify", "credentials"]):
            certs = matched_career.get("certifications", [])
            lines = "\n".join([f"• {c}" for c in certs])
            return f"🏅 **Key Certifications for {c_name}**:\n\n{lines}"
            
        if any(w in tokens for w in ["project", "portfolio"]):
            projs = matched_career.get("projects", [])
            lines = "\n".join([f"• {proj}" for proj in projs])
            return f"⚡ **Suggested Portfolio Projects for {c_name}**:\n\n{lines}"
            
        if any(w in tokens for w in ["roadmap", "path", "step", "learn"]):
            steps = matched_career.get("learning_roadmap", [])
            lines = "\n".join([f"{i}. {s}" for i, s in enumerate(steps, start=1)])
            return f"🗺️ **Learning Roadmap for {c_name}**:\n\n{lines}"
            
        if any(w in tokens for w in ["scope", "future", "grow", "outlook"]):
            return (
                f"🚀 **Scope & Growth for {c_name}**:\n\n"
                f"• **Growth Track**: {matched_career.get('growth', '')}\n\n"
                f"• **Future Outlook**: {matched_career.get('future_scope', '')}"
            )

        # General description if career name matched but no sub-questions
        return (
            f"**{c_name}** ({matched_career['domain']}):\n\n"
            f"{matched_career['description']}\n\n"
            f"You can ask me about its **roadmap**, **skills**, **salary**, **courses**, **projects**, or **scope**!"
        )

    # 2. General recommendation intent check
    tokens = preprocessor.preprocess(msg_clean)
    if any(w in tokens for w in ["recommend", "suggest", "find", "match", "option"]):
        profile = st.session_state["user_profile"]
        has_profile = any([profile[k] for k in ["skills", "interests", "current_degree"] if profile[k]])
        
        if not has_profile:
            return "Please update your skills, degree, and interests in the profile form on the left, then I can recommend matching careers!"
            
        recs = recommender.recommend(profile)
        if recs:
            top_rec = recs[0]
            st.session_state["active_chat_career"] = top_rec
            st.session_state["recommendations"] = recs
            other_rec_names = ", ".join([r["name"] for r in recs[1:4]])
            return (
                f"Based on your profile, I recommend a career as an **{top_rec['name']}**!\n\n"
                f"💡 **Why**: {top_rec['reason']}\n\n"
                f"Other matched options: {other_rec_names}."
            )
        return "I couldn't find a direct career match. Try adding more skills or adjusting your interests in the form!"

    # 3. Simple conversational keywords
    if any(w in tokens for w in ["hi", "hello", "hey", "greet"]):
        return "Hello! I am your AI Career Counsellor (running in offline fallback mode). 🚀 Tell me your skills or ask about a specific career!"
    if any(w in tokens for w in ["bye", "goodbye", "exit"]):
        return "Goodbye! Wish you the best in your career!"
        
    return (
        "I'm here to counsel you! Ask me about specific careers (e.g., 'What is the salary of a Data Scientist?'), "
        "or say 'recommend a career' to run matches on your profile details."
    )


def render_counsellor():
    session_id = st.session_state["session_id"]
    profile = st.session_state["user_profile"]

    st.markdown("""
    <div class="header-container">
        <div class="header-title">💼 Interactive Career Counselling Hub</div>
        <div class="header-subtitle">Build your academic profile, evaluate matching career statistics, and chat with the AI counsellor.</div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([5, 7])

    # Left Column: Profile Form & Career Matching results
    with col_left:
        st.markdown("### 📋 User Profile Builder")
        with st.form("profile_form"):
            name = st.text_input("Full Name", value=profile.get("name", ""))
            
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", min_value=12, max_value=60, value=int(profile.get("age", 18)))
                highest_qual = st.selectbox(
                    "Highest Qualification",
                    ["High School", "Diploma", "Bachelor's", "Master's", "PhD"],
                    index=["High School", "Diploma", "Bachelor's", "Master's", "PhD"].index(profile.get("highest_qualification", "High School"))
                )
            with c2:
                degree = st.text_input("Current/Planned Degree (e.g., B.Tech, B.Com, BFA)", value=profile.get("current_degree", ""))
                ac_year = st.selectbox(
                    "Academic Year",
                    ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"],
                    index=["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"].index(profile.get("academic_year", "1st Year"))
                )

            skills = st.text_area("Skills (comma-separated, e.g. Python, SQL, Writing, Excel)", value=profile.get("skills", ""))
            interests = st.text_area("Interests / Hobbies (comma-separated, e.g. Coding, Painting, Investing)", value=profile.get("interests", ""))
            
            c3, c4 = st.columns(2)
            with c3:
                domain = st.selectbox(
                    "Preferred Career Domain",
                    ["Technology", "Commerce", "Arts", "Healthcare", "Business", "Government"],
                    index=["Technology", "Commerce", "Arts", "Healthcare", "Business", "Government"].index(profile.get("preferred_domain", "Technology"))
                )
            with c4:
                goal = st.text_input("Specific Career Goal (e.g. Lead tech teams)", value=profile.get("career_goal", ""))

            save_btn = st.form_submit_button("Save & Match Career Paths")

            if save_btn:
                # Update Session State
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
                st.session_state["user_profile"] = updated_profile
                
                # Save to Database
                db.save_profile(session_id, updated_profile)
                
                # Synchronize slots with Rasa if online
                sync_success = sync_rasa_slots(session_id, updated_profile)
                
                # Compute Recommendations
                recs = recommender.recommend(updated_profile)
                st.session_state["recommendations"] = recs
                
                st.success("Profile saved successfully! Career recommendations updated.")
                if sync_success:
                    st.info("Profile slots synchronized with the Rasa chatbot tracker state.")

        # Matches Result Section
        st.markdown("### 🏆 Top Recommended Career Matches")
        recs = st.session_state.get("recommendations", [])
        if not recs:
            # Attempt load on page launch if not calculated
            if any([profile[k] for k in ["skills", "interests", "current_degree"] if profile[k]]):
                recs = recommender.recommend(profile)
                st.session_state["recommendations"] = recs

        if recs:
            for rec in recs[:3]:  # Top 3 matches
                st.markdown(f"""
                <div class="career-card">
                    <span class="score-badge">{rec['match_percentage']}% Match</span>
                    <span class="badge">{rec['domain']}</span>
                    <h3 style="margin-top:0.5rem; margin-bottom:0.5rem; color:#60A5FA;">{rec['name']}</h3>
                    <p style="font-size:0.9rem; color:#E2E8F0; margin-bottom:0.8rem;">{rec['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"View details for {rec['name']}"):
                    st.write(rec["description"])
                    st.markdown("**Salary Details:**")
                    st.write(f"- Entry Level: {rec['salary_range']['entry']}")
                    st.write(f"- Mid Level: {rec['salary_range']['mid']}")
                    st.write(f"- Senior Level: {rec['salary_range']['senior']}")
                    
                    st.markdown("**Recommended Courses:**")
                    for c in rec["recommended_courses"]:
                        st.write(f"- {c}")
                        
                    st.markdown("**Suggested Project:**")
                    for p in rec["suggested_projects"]:
                        st.write(f"- {p}")
        else:
            st.info("Fill out your profile details above to discover tailored career recommendations.")

    # Right Column: Chatbot Interface
    with col_right:
        st.markdown("### 🤖 Chat with AI Counsellor")
        
        # Check Rasa Server status
        rasa_online = False
        try:
            res = requests.get(RASA_SERVER_URL, timeout=1.0)
            if res.status_code == 200:
                rasa_online = True
        except Exception:
            pass

        if rasa_online:
            st.caption("🟢 **Rasa Bot Online** (REST Hook Enabled)")
        else:
            st.caption("🟡 **Rasa Bot Offline** (Operating in NLTK fallback mode)")

        # Clear Chat Button
        if st.button("Reset Conversation Logs", key="clear_chat"):
            db.clear_chat_history(session_id)
            st.rerun()

        # Chat container window
        chat_container = st.container(height=450)
        
        # Load conversation history from SQL
        history = db.get_chat_history(session_id)
        
        with chat_container:
            if not history:
                st.chat_message("assistant").write("Hello! I am your AI Virtual Career Counsellor. 🚀 Tell me your academic interests or ask questions like 'What is the salary of an AI Engineer?'")
            else:
                for chat in history:
                    st.chat_message(chat["sender"]).write(chat["message"])

        # User query input
        user_input = st.chat_input("Ask something (e.g. show roadmap for full stack developer)...")

        if user_input:
            # 1. Render user message
            chat_container.chat_message("user").write(user_input)
            db.add_chat_message(session_id, "user", user_input)
            
            # 2. Get AI Response
            if rasa_online:
                # Synchronize slots first before message
                sync_rasa_slots(session_id, st.session_state["user_profile"])
                
                # Fetch Rasa responses
                bot_responses = get_rasa_response(session_id, user_input)
                if bot_responses:
                    for r in bot_responses:
                        text = r.get("text", "")
                        if text:
                            chat_container.chat_message("assistant").write(text)
                            db.add_chat_message(session_id, "assistant", text)
                else:
                    fallback_reply = "I'm having trouble retrieving details. Let me process this locally: " + handle_offline_fallback(user_input, session_id)
                    chat_container.chat_message("assistant").write(fallback_reply)
                    db.add_chat_message(session_id, "assistant", fallback_reply)
            else:
                # Local fallback using NLTK preprocessor
                fallback_reply = handle_offline_fallback(user_input, session_id)
                chat_container.chat_message("assistant").write(fallback_reply)
                db.add_chat_message(session_id, "assistant", fallback_reply)
                
            st.rerun()

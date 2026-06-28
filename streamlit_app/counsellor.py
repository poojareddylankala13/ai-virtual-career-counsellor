import streamlit as st
import requests
import uuid
import json
from config import RASA_WEBHOOK_URL, RASA_SERVER_URL, CAREER_DATASET_PATH
from utils.db_helper import DBHelper
from utils.recommender import CareerRecommender
from utils.nltk_preprocessor import NLTKPreprocessor

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


def handle_offline_fallback(user_msg: str, session_id: str) -> str:
    """
    Fallback NLP assistant using NLTK to parse inquiries
    and generate replies from careers.json when Rasa is offline.
    """
    msg_clean = user_msg.lower()
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
            return f"🛠️ **Suggested Portfolio Projects for {c_name}**:\n\n{lines}"
            
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
    user_email = st.session_state["user_email"]
    profile = st.session_state["user_profile"]

    st.markdown("""
    <div class="header-container">
        <div class="header-title">🤖 AI Career Counsellor Chat</div>
        <div class="header-subtitle">Discuss qualifications, seek career advice, ask for roadmaps, projects, or salaries in real-time.</div>
    </div>
    """, unsafe_allow_html=True)

    # Establish Active Chat Session
    sessions = db.get_chat_sessions(user_email)
    
    if "active_session_id" not in st.session_state or not st.session_state["active_session_id"]:
        if sessions:
            st.session_state["active_session_id"] = sessions[0]["session_id"]
        else:
            # Create first session
            new_id = str(uuid.uuid4())
            db.create_chat_session(user_email, new_id, "New Chat Session")
            st.session_state["active_session_id"] = new_id
            sessions = db.get_chat_sessions(user_email)

    active_session_id = st.session_state["active_session_id"]

    # Layout: Left column for session history, Right column for chat
    col_hist, col_chat = st.columns([3, 7])

    with col_hist:
        st.markdown("### 💬 Chat History")
        
        # New Chat Button
        if st.button("➕ Start New Chat", key="new_chat_btn", use_container_width=True):
            new_id = str(uuid.uuid4())
            db.create_chat_session(user_email, new_id, "New Chat Session")
            st.session_state["active_session_id"] = new_id
            st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # List existing sessions as buttons
        for s in sessions:
            is_active = s["session_id"] == active_session_id
            bg_color = "background-color: rgba(59, 130, 246, 0.08);" if is_active else ""
            
            col_b, col_del = st.columns([8, 2])
            with col_b:
                # Custom styled button for session list
                if st.button(
                    f"💬 {s['title'][:22]}...", 
                    key=f"sess_{s['session_id']}", 
                    use_container_width=True
                ):
                    st.session_state["active_session_id"] = s["session_id"]
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_sess_{s['session_id']}", use_container_width=True):
                    db.delete_chat_session(s["session_id"])
                    if st.session_state["active_session_id"] == s["session_id"]:
                        st.session_state.pop("active_session_id", None)
                    st.rerun()

    with col_chat:
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

        # Chat container window
        chat_container = st.container(height=400)
        history = db.get_chat_history(active_session_id)

        # Auto-scroll script injection
        st.markdown("""
        <script>
            var chat = window.parent.document.querySelector('[data-testid="stChatMessageContainer"]');
            if (chat) {
                chat.scrollTop = chat.scrollHeight;
            }
        </script>
        """, unsafe_allow_html=True)

        with chat_container:
            if not history:
                st.chat_message("assistant").write("Hello! I am your AI Career Counsellor. 🚀 Tell me your academic interests or click on one of the suggested questions below!")
            else:
                for chat in history:
                    with st.chat_message(chat["sender"]):
                        st.write(chat["message"])
                        st.markdown(f'<span style="font-size:0.7rem; color:#94A3B8; float:right;">{chat.get("timestamp", "")}</span>', unsafe_allow_html=True)

        # Suggested Questions
        st.markdown("💡 **Suggested Questions:**")
        sq_cols = st.columns(3)
        suggestions = [
            "Give me the roadmap for AI Engineer",
            "What is the salary of a Data Scientist?",
            "What projects should a UI/UX Designer build?"
        ]
        
        click_query = ""
        for idx, sug in enumerate(suggestions):
            with sq_cols[idx % 3]:
                if st.button(sug, key=f"sug_{idx}", use_container_width=True):
                    click_query = sug

        # Chat input
        user_input = st.chat_input("Ask about roles, roadmaps, credentials...")

        # Process user query (either clicked suggestions or typed input)
        active_query = click_query or user_input

        if active_query:
            # 1. Update session title if first message
            if not history:
                short_title = active_query[:25] + "..." if len(active_query) > 25 else active_query
                db.rename_chat_session(active_session_id, short_title)

            # 2. Render and save user message
            db.add_chat_message(active_session_id, "user", active_query)
            
            # Show typing animation/spinner
            with st.spinner("AI Counsellor is thinking..."):
                if rasa_online:
                    # Sync slots
                    sync_rasa_slots(active_session_id, profile)
                    
                    # Fetch response from Rasa
                    bot_responses = []
                    try:
                        payload = {"sender": active_session_id, "message": active_query}
                        response = requests.post(RASA_WEBHOOK_URL, json=payload, timeout=3.0)
                        if response.status_code == 200:
                            bot_responses = response.json()
                    except Exception:
                        pass
                    
                    if bot_responses:
                        for r in bot_responses:
                            text = r.get("text", "")
                            if text:
                                db.add_chat_message(active_session_id, "assistant", text)
                    else:
                        fallback_reply = "I'm processing this locally: " + handle_offline_fallback(active_query, active_session_id)
                        db.add_chat_message(active_session_id, "assistant", fallback_reply)
                else:
                    # Local NLTK fallback
                    fallback_reply = handle_offline_fallback(active_query, active_session_id)
                    db.add_chat_message(active_session_id, "assistant", fallback_reply)

            st.rerun()

import streamlit as st
from utils.db_helper import DBHelper

db = DBHelper()


def render_chat_history():
    user_email = st.session_state["user_email"]
    
    st.markdown("""
    <div class="header-container">
        <div class="header-title">📜 Conversation Archives</div>
        <div class="header-subtitle">Review and read through your past consulting sessions with the AI Career Counsellor.</div>
    </div>
    """, unsafe_allow_html=True)

    sessions = db.get_chat_sessions(user_email)

    if not sessions:
        st.info("You do not have any archived conversation history. Start a new chat in the 'Career Counsellor' page!")
        return

    # Select past session to view
    session_titles = {s["session_id"]: f"{s['title']} ({s['created_at'][:10]})" for s in sessions}
    
    col_sel, _ = st.columns([2, 2])
    with col_sel:
        selected_session_id = st.selectbox(
            "Select past conversation session:", 
            options=list(session_titles.keys()),
            format_func=lambda x: session_titles[x]
        )

    # Fetch messages
    messages = db.get_chat_history(selected_session_id)
    
    st.markdown("### 💬 Transcript Review")
    
    if messages:
        for msg in messages:
            with st.chat_message(msg["sender"]):
                st.write(msg["message"])
                st.markdown(f'<span style="font-size:0.7rem; color:#94A3B8; float:right;">{msg.get("timestamp", "")}</span>', unsafe_allow_html=True)
    else:
        st.caption("No messages in this chat session.")

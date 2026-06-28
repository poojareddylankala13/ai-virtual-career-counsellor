import streamlit as st
from utils.db_helper import DBHelper
from streamlit_app.auth import handle_logout

db = DBHelper()


def render_settings():
    user_email = st.session_state["user_email"]
    profile = db.get_user_profile(user_email)

    st.markdown("""
    <div class="header-container">
        <div class="header-title">⚙️ Account Settings</div>
        <div class="header-subtitle">Manage notifications, visual themes, change passwords, and configure account deletions.</div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Preferences & Notifications
    st.markdown("### 🎨 Preferences")
    
    current_notif = profile.get("notifications", 1)
    notif_opt = st.toggle("Enable system alerts and notifications", value=bool(current_notif))
    new_notif = 1 if notif_opt else 0

    if st.button("Apply Preferences Settings", key="apply_pref_btn"):
        db.update_user_settings(user_email, "dark", new_notif)
        st.session_state["theme"] = "dark"
        st.success("App preferences updated!")
        st.rerun()

    st.markdown("---")

    # 2. Change Password
    st.markdown("### 🔑 Security & Password Management")
    with st.form("change_password_form"):
        old_pass = st.text_input("Current Password", type="password")
        new_pass = st.text_input("New Password", type="password")
        confirm_new = st.text_input("Confirm New Password", type="password")

        change_btn = st.form_submit_button("Change Account Password")

        if change_btn:
            if not old_pass or not new_pass or not confirm_new:
                st.error("Please fill in all security fields.")
            elif new_pass != confirm_new:
                st.error("New passwords do not match.")
            elif len(new_pass) < 6:
                st.error("New password must be at least 6 characters long.")
            else:
                success = db.change_user_password(user_email, old_pass, new_pass)
                if success:
                    st.success("Your password was updated successfully!")
                else:
                    st.error("Failed to update password. Please check your current password.")

    st.markdown("---")

    # 3. Danger Zone
    st.markdown("### ⚠️ Danger Zone")
    with st.expander("Delete Account Options"):
        st.write("Deleting your account is permanent. All saved career roadmaps, chat sessions, and profile settings will be permanently erased.")
        
        confirm_email = st.text_input("Type your email address to confirm deletion:")
        
        if st.button("Permanently Delete Account", key="delete_acc_btn", type="primary"):
            if confirm_email.lower().strip() == user_email.lower().strip():
                success = db.delete_user_account(user_email)
                if success:
                    st.success("Account successfully deleted.")
                    # Force logout
                    st.session_state.pop("user_email", None)
                    st.session_state.pop("user_name", None)
                    st.session_state["auth_page"] = "login"
                    st.rerun()
                else:
                    st.error("Failed to delete account. Please try again.")
            else:
                st.error("Confirmation email does not match your active logged-in email.")

    st.markdown("---")
    
    # 4. Standard Logout Button
    if st.button("Log Out of Session", key="settings_logout_btn"):
        handle_logout()

    st.markdown("<br><br><div style='text-align: center; color: #B3B3C5; font-size: 0.85rem;'>© 2026 AI Virtual Career Counsellor</div>", unsafe_allow_html=True)

import streamlit as st
import re
from utils.db_helper import DBHelper

db = DBHelper()


def is_valid_email(email: str) -> bool:
    """Validates email format using regex."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))


def render_auth_pages():
    """Renders Login, Signup, or Forgot Password screens based on state."""
    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"

    # Centered container for form styling
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #60A5FA; font-weight:700; margin-bottom:0.2rem;">ApexPath AI</h1>
        <p style="color: #94A3B8; font-size:1rem;">Your Intelligent Path to Professional Success</p>
    </div>
    """, unsafe_allow_html=True)

    # Render Active Screen
    if st.session_state["auth_page"] == "login":
        render_login()
    elif st.session_state["auth_page"] == "signup":
        render_signup()
    elif st.session_state["auth_page"] == "forgot_password":
        render_forgot_password()


def render_login():
    """Renders the Login form."""
    st.markdown("""
    <div class="career-card" style="max-width: 450px; margin: 0 auto; padding: 2rem;">
        <h3 style="margin-top:0; color: #60A5FA; text-align: center;">Welcome Back</h3>
        <p style="color:#94A3B8; text-align: center; font-size: 0.9rem; margin-bottom: 1.5rem;">Log in to access your counsellor chat and roadmaps</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        # Form centered using columns
        _, col, _ = st.columns([1, 2, 1])
        with col:
            with st.form("login_form"):
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                
                login_btn = st.form_submit_button("Log In", use_container_width=True)

                if login_btn:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        user = db.authenticate_user(email, password)
                        if user:
                            st.session_state["user_email"] = user["email"]
                            st.session_state["user_name"] = user["name"]
                            st.session_state["user_profile"] = user
                            st.success("Successfully logged in!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password. Please try again.")

            # Form links
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Create Account", key="go_signup", use_container_width=True):
                    st.session_state["auth_page"] = "signup"
                    st.rerun()
            with c2:
                if st.button("Forgot Password?", key="go_forgot", use_container_width=True):
                    st.session_state["auth_page"] = "forgot_password"
                    st.rerun()


def render_signup():
    """Renders the Sign Up form."""
    st.markdown("""
    <div class="career-card" style="max-width: 450px; margin: 0 auto; padding: 2rem;">
        <h3 style="margin-top:0; color: #60A5FA; text-align: center;">Register Account</h3>
        <p style="color:#94A3B8; text-align: center; font-size: 0.9rem; margin-bottom: 1.5rem;">Join ApexPath AI to start planning your career pathway</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            signup_btn = st.form_submit_button("Create Account", use_container_width=True)

            if signup_btn:
                if not name or not email or not password or not confirm_password:
                    st.error("Please fill in all input fields.")
                elif not is_valid_email(email):
                    st.error("Please enter a valid email format.")
                elif password != confirm_password:
                    st.error("Passwords do not match. Please verify.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    success = db.create_user(email, password, name)
                    if success:
                        st.success("Account created successfully! Please log in.")
                        st.session_state["auth_page"] = "login"
                        st.rerun()
                    else:
                        st.error("An account with this email address already exists.")

        if st.button("Back to Login", key="signup_back_login", use_container_width=True):
            st.session_state["auth_page"] = "login"
            st.rerun()


def render_forgot_password():
    """Renders the Forgot Password form."""
    st.markdown("""
    <div class="career-card" style="max-width: 450px; margin: 0 auto; padding: 2rem;">
        <h3 style="margin-top:0; color: #60A5FA; text-align: center;">Reset Password</h3>
        <p style="color:#94A3B8; text-align: center; font-size: 0.9rem; margin-bottom: 1.5rem;">Enter email to reset password settings</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        with st.form("forgot_form"):
            email = st.text_input("Registered Email Address")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")

            reset_btn = st.form_submit_button("Reset Password", use_container_width=True)

            if reset_btn:
                if not email or not new_password or not confirm_new_password:
                    st.error("Please fill in all input fields.")
                elif new_password != confirm_new_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    # Direct mock override inside SQLite database
                    with db._get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT email FROM users WHERE email = ?", (email.lower().strip(),))
                        row = cursor.fetchone()
                        if row:
                            from utils.db_helper import hash_password
                            p_hash = hash_password(new_password)
                            cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (p_hash, email.lower().strip()))
                            conn.commit()
                            st.success("Password reset completed successfully! Please log in.")
                            st.session_state["auth_page"] = "login"
                            st.rerun()
                        else:
                            st.error("No account associated with this email address was found.")

        if st.button("Back to Login", key="forgot_back_login", use_container_width=True):
            st.session_state["auth_page"] = "login"
            st.rerun()


def handle_logout():
    """Logs out the active user session."""
    st.session_state.pop("user_email", None)
    st.session_state.pop("user_name", None)
    st.session_state.pop("user_profile", None)
    st.session_state.pop("recommendations", None)
    st.session_state.pop("active_chat_career", None)
    st.session_state.pop("active_session_id", None)
    st.session_state["auth_page"] = "login"
    st.success("Successfully logged out!")
    st.rerun()

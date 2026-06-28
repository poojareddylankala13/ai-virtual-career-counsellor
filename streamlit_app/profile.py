import streamlit as st
from utils.db_helper import DBHelper

db = DBHelper()


def render_profile():
    user_email = st.session_state["user_email"]
    
    # Reload profile details
    profile = db.get_user_profile(user_email)
    st.session_state["user_profile"] = profile

    st.markdown("""
    <div class="header-container">
        <div class="header-title">👤 User Profile Settings</div>
        <div class="header-subtitle">Upload your profile photo and edit your academic credentials, technical skills, and career focus.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("profile_editor_form"):
        st.markdown("### Profile Photo Upload")
        uploaded_photo = st.file_uploader("Upload Profile Image (PNG or JPG, max 500KB)", type=["png", "jpg", "jpeg"])

        st.markdown("### Academic & Professional Details")
        name = st.text_input("Name", value=profile.get("name", ""))
        
        # Email is shown but non-editable (serves as unique ID key)
        st.text_input("Email (Linked to your account)", value=user_email, disabled=True)
        
        col_c, col_d = st.columns(2)
        with col_c:
            college = st.text_input("College / University", value=profile.get("college", ""))
            degree = st.text_input("Degree (e.g., B.Tech in CS)", value=profile.get("current_degree", ""))
        with col_d:
            year = st.selectbox(
                "Academic Year",
                ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"],
                index=["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"].index(profile.get("academic_year", "1st Year"))
            )
            goal = st.text_input("Core Career Goal", value=profile.get("career_goal", ""))

        skills = st.text_area("Technical & Professional Skills (comma-separated)", value=profile.get("skills", ""))
        interests = st.text_area("Areas of Interest / Hobbies (comma-separated)", value=profile.get("interests", ""))

        save_btn = st.form_submit_button("Update Profile Information")

        if save_btn:
            profile_data = {
                "name": name,
                "college": college,
                "degree": degree,
                "year": year,
                "skills": skills,
                "interests": interests,
                "career_goal": goal
            }
            
            # Extract photo bytes if uploaded
            if uploaded_photo is not None:
                photo_bytes = uploaded_photo.read()
                profile_data["profile_photo"] = photo_bytes

            success = db.update_user_profile(user_email, profile_data)
            if success:
                st.success("Your profile details have been successfully updated in the system!")
                st.session_state["user_profile"] = db.get_user_profile(user_email)
                st.rerun()
            else:
                st.error("Failed to save changes. Please try again.")

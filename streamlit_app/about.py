import streamlit as st


def render_about():
    st.markdown("""
    <div class="header-container">
        <div class="header-title">ℹ️ About the Project</div>
        <div class="header-subtitle">Technical documentation, architectural design system, and developer profiles.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🏗️ Architectural Flow")
    st.markdown("""
    The system follows a modular architecture separating the conversational agent (Rasa 3.x), the natural language text preprocessor (NLTK), the matching and recommendations processor (Engine), and the visual user interface (Streamlit).
    """)

    st.markdown("""
    ```mermaid
    graph TD
        A[Streamlit User Interface] -->|1. Updates Profile Form| B[(SQLite database)]
        A -->|2. Syncs profile details| C[Rasa Chatbot Server]
        A -->|3. Submits user questions| C
        C -->|4. Invokes actions| D[Rasa Action Server]
        D -->|5. Queries matching parameters| E[Career Recommender Engine]
        E -->|6. Scans| F[data/careers.json]
        E -->|7. Runs NLP tokens| G[NLTK Preprocessor]
        A -.->|8. Fallback to Local Engine if Rasa offline| E
    ```
    *(Note: The diagram above demonstrates the synchronous data channels of the system).*
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🛠️ Technology Stack")
        st.markdown("""
        * **Programming Language**: Python (3.8 - 3.10)
        * **Chatbot Framework**: Rasa Open Source 3.x (Dialog management and intent classification)
        * **Natural Language Toolkit (NLTK)**: Tokenization, stop-word removal, and lemmatization for query refinement
        * **Web UI Framework**: Streamlit (Responsive web pages with custom styles)
        * **Data Visualizations**: Plotly (Salary graphs and domain count charts)
        * **Database**: SQLite3 (Chat history log tracker & user profile storage)
        """)

    with col2:
        st.markdown("### 📂 Modular Folder Structure")
        st.markdown("""
        ```text
        ai-virtual-career-counsellor/
        ├── app.py                  # Streamlit entry point
        ├── config.py               # Main configurations
        ├── requirements.txt        # Package lists
        ├── data/
        │   └── careers.json        # 26 Careers catalog
        ├── utils/
        │   ├── nltk_preprocessor.py# NLTK preprocessor
        │   ├── recommender.py      # Matching calculations
        │   └── db_helper.py        # SQLite connection helper
        ├── streamlit_app/
        │   ├── home.py             # Home page layout
        │   ├── counsellor.py       # Counsellor chat and form
        │   ├── explorer.py         # Career search grid
        │   └── about.py            # System architecture details
        ├── rasa/                   # Rasa model directory
        │   ├── config.yml          # DIETClassifier settings
        │   ├── domain.yml          # Intents and slot configurations
        │   ├── actions.py          # Custom action implementations
        │   └── data/
        │       ├── nlu.yml         # Training examples
        │       └── stories.yml     # Conversational stories
        ```
        """)

    st.markdown("---")
    st.markdown("### 👨‍💻 Developer & Internship Details")
    st.markdown("""
    * **Project Name**: AI Virtual Career Counsellor
    * **Submission Phase**: Final Internship Project Deliverable
    * **Academic Year**: 2026
    * **License**: MIT Open Source License
    
    This application is designed as a production-grade showcase system matching the guidelines for technical interviews and resume submissions.
    """)

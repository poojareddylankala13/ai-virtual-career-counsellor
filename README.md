# ApexPath AI | Virtual Career Counsellor

ApexPath AI is a production-ready, NLP-powered Career Counselling web application designed to guide students and professionals in finding their ideal career trajectories. By combining a **Rasa 3.x conversational chatbot**, **NLTK-based text preprocessing**, and a **custom Career Recommendation Engine**, it creates a modern, personalized guidance experience.

---

## 🎯 Objectives
* **Context-Aware Recommendations**: Match user profiles (skills, academic background, qualification levels, and interests) against 25+ detailed career paths.
* **Natural Language Guidance**: Chat with an AI assistant to fetch roadmaps, project suggestions, salary statistics, and certification pathways.
* **Offline Resiliency**: Features an NLTK-driven keyword parsing fallback engine that functions even if the Rasa backend is offline.
* **Interactive Dashboards**: Modern visual metrics and salary graphs comparing entry, mid, and senior levels for a realistic career outlook.

---

## 🛠️ Technology Stack
* **Frontend UI**: Streamlit
* **Conversational Agent**: Rasa Open Source 3.x
* **Language Processing**: NLTK (Tokenization, stop-word removal, Lemmatization)
* **Visualizations**: Plotly Express & Graph Objects
* **Database**: SQLite3 (Chat transcript and profile storage)
* **Unit Testing**: Pytest

---

## 📂 Folder Structure
```text
ai-virtual-career-counsellor/
├── app.py                      # Main entry point running the Streamlit app
├── config.py                   # Centralized configuration mappings
├── requirements.txt            # Python package dependencies
├── LICENSE                     # MIT License
├── README.md                   # Technical documentation
├── DEPLOYMENT.md               # Quickstart and hosting guidelines
├── INTERNSHIP_REPORT.md        # Internship report draft for submission
├── data/
│   └── careers.json            # Database of 26 comprehensive career paths
├── utils/
│   ├── __init__.py
│   ├── nltk_preprocessor.py    # Text parsing & lemmatization pipeline
│   ├── recommender.py          # Domain, skill, and academic matching logic
│   └── db_helper.py            # SQLite data access objects
├── streamlit_app/
│   ├── home.py                 # Home page analytics and graphs
│   ├── counsellor.py           # Dual-pane profile matching and chat interface
│   ├── explorer.py             # Domain-specific career directory
│   └── about.py                # Architectural schemas and flows
├── rasa/
│   ├── config.yml              # Rasa classifier pipelines & policies
│   ├── domain.yml              # Slots, intents, and conversational templates
│   ├── credentials.yml         # REST API channels configuration
│   ├── endpoints.yml           # Custom action server endpoints
│   ├── actions.py              # Rasa custom action python business logic
│   └── data/
│       ├── nlu.yml             # Training phrases for intent matching
│       ├── stories.yml         # Conversational stories
│       └── rules.yml           # Fallback & fixed rules
└── tests/
    ├── __init__.py
    ├── test_preprocessor.py    # NLTK preprocessor unit tests
    └── test_recommender.py     # Recommender engine unit tests
```

---

## 🚀 Installation and Setup

### Prerequisites
* Python 3.8, 3.9, or 3.10 (Recommended for Rasa 3.x compatibility)
* Virtual Environment manager (venv/conda)

### 1. Install Dependencies
Clone this repository, navigate to the folder, and run:
```bash
pip install -r requirements.txt
```
*(This automatically downloads packages and triggers NLTK data downloads for `punkt`, `stopwords`, `wordnet`, and `omw-1.4` on first run).*

### 2. Set Up the Rasa Chatbot
Open a new terminal window inside the `rasa/` directory:
```bash
cd rasa
# Train the Rasa model
rasa train
```
This compile/train step creates a compressed model file inside `rasa/models/`.

### 3. Run the Custom Actions Server
From the `rasa/` directory, start the custom action server:
```bash
rasa run actions
```
This runs the Python business logic webhook at `http://localhost:5055/webhook`.

### 4. Run the Rasa Core Server
Open another terminal, navigate to the `rasa/` directory, and run the Rasa server with the REST webhook enabled:
```bash
rasa run -m models --enable-api --cors "*"
```
This launches the REST server on `http://localhost:5005`.

### 5. Launch the Streamlit Frontend
Open a separate terminal at the **root project directory** and run:
```bash
streamlit run app.py
```
Your default browser will launch the web application at `http://localhost:8501`.

---

## 🧪 Running Unit Tests
Validate the NLTK parser and Recommendation engine using:
```bash
pytest tests/
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

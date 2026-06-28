# INTERNSHIP PROJECT REPORT

**Project Title**: AI Virtual Career Counsellor  
**Author / Intern**: Product Engineering Intern  
**Academic Submission Phase**: Final Assessment  
**Submission Date**: June 2026  

---

## 1. ABSTRACT
In the modern educational landscape, selecting a suitable career trajectory has become increasingly complex due to the rapid evolution of technology and diversifying market demands. Traditional career guidance often suffers from resource limitations, subjective bias, or lack of accessibility. 

This project presents the design and implementation of the **AI Virtual Career Counsellor**, a production-grade web application that leverages Natural Language Processing (NLP) to provide personalized, data-driven career counseling. By integrating the **Rasa Open Source 3.x** dialogue management framework with the **Natural Language Toolkit (NLTK)** and **Streamlit**, the application delivers interactive career recommendations based on user profiles (skills, qualifications, academic status, and interests). The system features an NLTK-powered keyword fallback mechanism to maintain operational resilience under offline server states, alongside visual analytics plotting salary trends and job domain allocations.

---

## 2. INTRODUCTION
Choosing a career is one of the most critical decisions in a student's life. The objective of this project is to develop an automated tool that assists candidates in identifying optimal professional paths matching their inherent skills and qualifications. 

The AI Virtual Career Counsellor operates as a hybrid guidance portal:
1. **Dynamic Profiler Form**: Gathers structured user characteristics (such as degrees, certifications, self-reported skills, and preferred domains).
2. **Interactive Chat Companion**: Allows free-text conversations to query salary expectations, certifications, roadmaps, and portfolio projects in natural language.
3. **Curated Job Catalog**: Functions as a searchable database containing 26 detailed career profiles across six distinct sectors.

---

## 3. OBJECTIVES
The principal objectives of this engineering implementation include:
* Developing a modular, clean Python architecture dividing data access, NLP preprocessing, and UI display layers.
* Building a Rasa chatbot to recognize user queries (salaries, projects, courses) and route logic to appropriate custom webhook actions.
* Creating an NLTK pipeline covering tokenization, lowercasing, stop-word removal, and lemmatization to extract keywords from raw text inputs.
* Scoring user compatibility scores mathematically based on academic pathway validation, interest mapping, and skill overlap.
* Visualizing career statistics with Plotly graphs to convey salary distributions.
* Ensuring full offline fallback capability so the system can run locally or in cloud sandbox environments without active external servers.

---

## 4. SYSTEM MODULES & TOOLS USED

### 4.1 Technology Stack
* **Python**: Core programming language.
* **Streamlit**: Web frontend rendering layout cards, sidebars, and chat frames.
* **Rasa Open Source 3.x**: Contextual NLU engine classifying intents and maintaining dialogue tracks.
* **Natural Language Toolkit (NLTK)**: Cleaning and tokenizing text inputs for keyword scoring.
* **Plotly & Matplotlib**: Generating dynamic UI graphs.
* **SQLite3**: Lightweight relational database saving profile cards and session message logs.

### 4.2 Architectural Design Flow
The system processes data through three key layers:
1. **User Presentation Layer (Streamlit)**: Collects text inputs and form profiles, communicating with the database and Rasa API.
2. **Dialogue & Business Layer (Rasa & Custom Actions)**: Classifies the user's intent, tracks variables (slots), and triggers Python backend recommendations.
3. **Data & Preprocessing Layer (NLTK & JSON)**: Lemmatizes and filters inputs against the structured `careers.json` catalog to calculate matches.

---

## 5. STEPS INVOLVED IN BUILDING THE PROJECT

### Phase 1: Requirement Gathering & Dataset Design
Compiled 26 thorough career pathways spanning Technology, Commerce, Arts, Healthcare, Business, and Government sectors. Curated distinct roadmap milestones, credentials, courses, and salary metrics for each path.

### Phase 2: NLTK Preprocessing Pipeline
Created the `NLTKPreprocessor` class inside `utils/nltk_preprocessor.py`. Implemented regular expression cleanups, token segmentation, stop-word filters, and lemmatized comparison models using WordNet.

### Phase 3: Recommendation Engine Development
Wrote the scoring algorithms in `utils/recommender.py`. Established mathematical scoring criteria allocating:
* Up to **40 points** for matching the preferred domain or interest words.
* Up to **40 points** for proportional matching of required career skills to user skills.
* Up to **20 points** for qualification/degree path validation.

### Phase 4: Rasa Chatbot Training
Structured the Rasa conversational models under `rasa/`. Authored training data in `data/nlu.yml` covering 20+ intents. Wrote stories and rules in YAML. Implemented the custom action class `actions.py` to fetch career fields and load them into Rasa's dialogue tracker.

### Phase 5: Streamlit Interface Assembly
Created a multi-page portal using Streamlit, featuring an analytics home screen, an interactive counselor chatbot, a career card grid with detail expanders, and developer documentation. Injected custom CSS styles to give the app a modern dark slate appearance.

### Phase 6: SQLite Integration
Implemented `db_helper.py` to create the local tables on startup. Handled CRUD transactions so profile data and chat records are stored locally and loaded automatically when returning users launch the app.

---

## 6. CONCLUSION & FUTURE ENHANCEMENTS
The AI Virtual Career Counsellor successfully accomplishes its goals, delivering a responsive, multi-page application that resolves professional queries using Rasa and NLTK. The modular code structure is compliant with clean programming standards, features unit tests, and handles offline states gracefully.

### Future Scope:
1. **API Integrations**: Connecting to job portals (like LinkedIn or Indeed APIs) to show real-time job openings for recommended careers.
2. **Deep Learning Matching**: Transitioning from rule-based keyword overlaps to semantic word embeddings (e.g. Sentence-BERT) for skill matching.
3. **Document Parser**: Adding a PDF resume uploader that automatically extracts skills using NLTK, bypassing manual form input.

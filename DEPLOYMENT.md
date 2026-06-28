# ApexPath AI | Deployment & Hosting Guide

This guide details steps to deploy and run the AI Virtual Career Counsellor. It covers local operations, multi-server startup processes, and cloud hosting guidelines.

---

## 💻 Local Deployment

To run all components locally, you need three separate terminal processes.

### Step 1: Install Python Environment & Packages
Create a clean virtual environment and install the required modules:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Train & Run the Rasa Bot
Rasa acts as the natural language understanding (NLU) controller.
1. **Train Model**:
   ```bash
   cd rasa
   rasa train
   ```
2. **Start Custom Action Webhook (Port 5055)**:
   ```bash
   rasa run actions
   ```
3. **Start Core Rasa Bot API Server (Port 5005)**:
   *(Open a new terminal window inside the `rasa/` directory)*
   ```bash
   rasa run -m models --enable-api --cors "*"
   ```

### Step 3: Run the Streamlit User Interface
*(Open a new terminal window at the root project directory)*
```bash
# Ensure virtual environment is active
streamlit run app.py
```
Access the dashboard at `http://localhost:8501`.

---

## ☁️ Cloud Deployment (Streamlit Cloud)

Streamlit Cloud hosts interactive python apps directly from a GitHub repository.

### Hosting the Frontend
1. Push your project files to a public GitHub repository.
2. Sign in to [Streamlit Share](https://share.streamlit.io/).
3. Click **New App**, select your repository, branch (`main`), and set the entry file path to `app.py`.
4. Click **Deploy**. Streamlit Cloud will compile dependencies from `requirements.txt` and launch.

### Handling the Rasa Backend in the Cloud
Since Streamlit Cloud only runs the Streamlit app process, the local Rasa engine (`localhost:5005`) will not be directly reachable by public users:

#### Option A: NLTK Fallback Mode (Simplest & Recommended)
* The application is built with a resilient NLTK keyword-matching engine.
* If the frontend cannot ping a Rasa instance, it **automatically switches to the offline NLTK assistant**.
* Users can still fill out profiles, get career recommendations, search careers, and chat.
* **No further configuration is required.**

#### Option B: Deploying Rasa to a Cloud VM (Production Setup)
To enable the full Conversational Rasa experience for public web users:
1. Spin up an AWS EC2 instance, GCP VM, or Heroku Dyno.
2. Install Python, Rasa, and clone the `rasa/` folder to the server.
3. Train the model and run the Rasa server, binding to `0.0.0.0:5005` (with HTTPS security).
4. Update `RASA_SERVER_URL` in `config.py` on your Streamlit Cloud repository to point to your VM's public IP address/domain:
   ```python
   # In config.py:
   RASA_SERVER_URL = "https://your-rasa-domain-or-ip.com"
   ```
5. Deploy the Rasa custom actions server on the same VM or a serverless function (like AWS Lambda) and configure `rasa/endpoints.yml` to target it.

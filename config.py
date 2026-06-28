import os

# Base directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UTILS_DIR = os.path.join(BASE_DIR, "utils")
DB_PATH = os.path.join(BASE_DIR, "counsellor_data.db")

# Career Dataset Configuration
CAREER_DATASET_PATH = os.path.join(DATA_DIR, "careers.json")

# Rasa Configuration
RASA_SERVER_URL = "http://localhost:5005"
RASA_WEBHOOK_URL = f"{RASA_SERVER_URL}/webhooks/rest/webhook"

# Streamlit App Styling & Aesthetics
APP_TITLE = "AI Virtual Career Counsellor"
APP_THEME_COLOR = "#0F172A"  # Deep slate grey
ACCENT_COLOR = "#7C3AED"      # Premium primary purple

# Ensure necessary folders exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UTILS_DIR, exist_ok=True)

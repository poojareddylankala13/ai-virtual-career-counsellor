import sqlite3
import os
import hashlib
import secrets
from datetime import datetime
from config import DB_PATH


def hash_password(password: str) -> str:
    """Generates a secure salt and sha256 hash of a password."""
    salt = secrets.token_hex(8)
    h = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}:{h}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its hashed representation."""
    if not hashed_password or ":" not in hashed_password:
        return False
    salt, h = hashed_password.split(":")
    test_h = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return test_h == h


class DBHelper:
    """
    Manages SQLite database transactions for user authentication, profile data,
    multi-session chat records, roadmap tracking, and resume analyses.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Users & Profile Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT,
                    name TEXT,
                    college TEXT,
                    degree TEXT,
                    year TEXT,
                    skills TEXT,
                    interests TEXT,
                    career_goal TEXT,
                    profile_photo BLOB,
                    theme TEXT DEFAULT 'dark',
                    notifications INTEGER DEFAULT 1,
                    created_at TEXT
                )
            """)

            # Chat Sessions Table (supports multiple chat threads per user)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_email TEXT,
                    title TEXT,
                    created_at TEXT,
                    FOREIGN KEY (user_email) REFERENCES users (email) ON DELETE CASCADE
                )
            """)

            # Chat History table (linked to session_id)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    sender TEXT,
                    message TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id) ON DELETE CASCADE
                )
            """)

            # Saved Roadmaps Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_roadmaps (
                    user_email TEXT,
                    career_name TEXT,
                    saved_at TEXT,
                    PRIMARY KEY (user_email, career_name),
                    FOREIGN KEY (user_email) REFERENCES users (email) ON DELETE CASCADE
                )
            """)

            # Roadmap Progress Table (checkbox states for roadmap steps)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roadmap_progress (
                    user_email TEXT,
                    career_name TEXT,
                    step_index INTEGER,
                    completed INTEGER DEFAULT 0,
                    PRIMARY KEY (user_email, career_name, step_index),
                    FOREIGN KEY (user_email) REFERENCES users (email) ON DELETE CASCADE
                )
            """)

            # Resume Analyses Table (evaluation scores and missing skills)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_analyses (
                    user_email TEXT PRIMARY KEY,
                    score INTEGER,
                    ats_score INTEGER,
                    missing_skills TEXT,
                    suggestions TEXT,
                    filename TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (user_email) REFERENCES users (email) ON DELETE CASCADE
                )
            """)

            conn.commit()

    # ==========================================
    # USER AUTHENTICATION & MANAGEMENT
    # ==========================================

    def create_user(self, email: str, password: str, name: str) -> bool:
        """Creates a new user record with hashed password."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                p_hash = hash_password(password)
                cursor.execute("""
                    INSERT INTO users (
                        email, password_hash, name, college, degree, year, 
                        skills, interests, career_goal, created_at
                    ) VALUES (?, ?, ?, '', '', '1st Year', '', '', '', ?)
                """, (email.lower().strip(), p_hash, name.strip(), datetime.now().isoformat()))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # User already exists
            return False

    def authenticate_user(self, email: str, password: str) -> dict:
        """Verifies email and password, returning user profile on success."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
            row = cursor.fetchone()
            if row and verify_password(password, row["password_hash"]):
                user_dict = dict(row)
                # Omit password hash for safety
                user_dict.pop("password_hash", None)
                return user_dict
        return {}

    def get_user_profile(self, email: str) -> dict:
        """Fetches the user details profile."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
            row = cursor.fetchone()
            if row:
                user_dict = dict(row)
                user_dict.pop("password_hash", None)
                return user_dict
        return {}

    def update_user_profile(self, email: str, profile_data: dict) -> bool:
        """Updates academic details, skills, interests, and profile photo."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if profile_photo is in profile_data, else do not overwrite
                if "profile_photo" in profile_data:
                    cursor.execute("""
                        UPDATE users SET
                            name = ?, college = ?, degree = ?, year = ?, 
                            skills = ?, interests = ?, career_goal = ?, profile_photo = ?
                        WHERE email = ?
                    """, (
                        profile_data.get("name", ""),
                        profile_data.get("college", ""),
                        profile_data.get("degree", ""),
                        profile_data.get("year", ""),
                        profile_data.get("skills", ""),
                        profile_data.get("interests", ""),
                        profile_data.get("career_goal", ""),
                        profile_data.get("profile_photo"),
                        email.lower().strip()
                    ))
                else:
                    cursor.execute("""
                        UPDATE users SET
                            name = ?, college = ?, degree = ?, year = ?, 
                            skills = ?, interests = ?, career_goal = ?
                        WHERE email = ?
                    """, (
                        profile_data.get("name", ""),
                        profile_data.get("college", ""),
                        profile_data.get("degree", ""),
                        profile_data.get("year", ""),
                        profile_data.get("skills", ""),
                        profile_data.get("interests", ""),
                        profile_data.get("career_goal", ""),
                        email.lower().strip()
                    ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False

    def update_user_settings(self, email: str, theme: str, notifications: int) -> bool:
        """Saves user visual theme (light/dark) and notification preferences."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET theme = ?, notifications = ? WHERE email = ?
                """, (theme, notifications, email.lower().strip()))
                conn.commit()
                return True
        except Exception:
            return False

    def change_user_password(self, email: str, old_pass: str, new_pass: str) -> bool:
        """Changes user password if old password matches."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email.lower().strip(),))
            row = cursor.fetchone()
            if row and verify_password(old_pass, row[0]):
                p_hash = hash_password(new_pass)
                cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (p_hash, email.lower().strip()))
                conn.commit()
                return True
        return False

    def delete_user_account(self, email: str) -> bool:
        """Deletes user and cascades delete to other tables."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE email = ?", (email.lower().strip(),))
                conn.commit()
                return True
        except Exception:
            return False

    # ==========================================
    # CHAT SESSION & HISTORY LOGS
    # ==========================================

    def create_chat_session(self, user_email: str, session_id: str, title: str):
        """Creates a new unique chat session thread."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO chat_sessions (session_id, user_email, title, created_at)
                VALUES (?, ?, ?, ?)
            """, (session_id, user_email.lower().strip(), title, datetime.now().isoformat()))
            conn.commit()

    def get_chat_sessions(self, user_email: str) -> list:
        """Gets all sessions of a user sorted by creation date descending."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM chat_sessions 
                WHERE user_email = ? 
                ORDER BY created_at DESC
            """, (user_email.lower().strip(),))
            return [dict(row) for row in cursor.fetchall()]

    def delete_chat_session(self, session_id: str):
        """Deletes a chat session and all messages contained."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
            conn.commit()

    def add_chat_message(self, session_id: str, sender: str, message: str):
        """Appends a message linked to a specific session_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (session_id, sender, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, sender, message, datetime.now().strftime("%I:%M %p")))
            conn.commit()

    def get_chat_history(self, session_id: str) -> list:
        """Retrieves sorted chat history for a given session."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sender, message, timestamp 
                FROM chat_history 
                WHERE session_id = ? 
                ORDER BY id ASC
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def rename_chat_session(self, session_id: str, new_title: str):
        """Renames a conversation session thread."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE chat_sessions SET title = ? WHERE session_id = ?", (new_title, session_id))
            conn.commit()

    # ==========================================
    # SAVED ROADMAPS & COMPLETED STEPS
    # ==========================================

    def save_roadmap(self, user_email: str, career_name: str) -> bool:
        """Pins a roadmap for tracking."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO saved_roadmaps (user_email, career_name, saved_at)
                    VALUES (?, ?, ?)
                """, (user_email.lower().strip(), career_name, datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception:
            return False

    def get_saved_roadmaps(self, user_email: str) -> list:
        """Retrieves all saved roadmaps for a user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT career_name FROM saved_roadmaps 
                WHERE user_email = ? 
                ORDER BY saved_at DESC
            """, (user_email.lower().strip(),))
            return [row[0] for row in cursor.fetchall()]

    def unsave_roadmap(self, user_email: str, career_name: str) -> bool:
        """Unpins a roadmap and deletes associated progress logs."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM saved_roadmaps WHERE user_email = ? AND career_name = ?", (user_email.lower().strip(), career_name))
                cursor.execute("DELETE FROM roadmap_progress WHERE user_email = ? AND career_name = ?", (user_email.lower().strip(), career_name))
                conn.commit()
                return True
        except Exception:
            return False

    def update_roadmap_progress(self, user_email: str, career_name: str, step_index: int, completed: int):
        """Logs completion checkbox state for a roadmap milestone step."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO roadmap_progress (user_email, career_name, step_index, completed)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_email, career_name, step_index) 
                DO UPDATE SET completed = excluded.completed
            """, (user_email.lower().strip(), career_name, step_index, completed))
            conn.commit()

    def get_roadmap_progress(self, user_email: str, career_name: str) -> dict:
        """Returns completed step indexes mapped as boolean flags."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT step_index, completed FROM roadmap_progress 
                WHERE user_email = ? AND career_name = ?
            """, (user_email.lower().strip(), career_name))
            return {row[0]: bool(row[1]) for row in cursor.fetchall()}

    # ==========================================
    # RESUME ANALYZER SCORES
    # ==========================================

    def save_resume_analysis(self, user_email: str, score: int, ats_score: int, missing_skills: list, suggestions: list, filename: str):
        """Persists the score statistics of a resume evaluation."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resume_analyses (
                    user_email, score, ats_score, missing_skills, suggestions, filename, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_email) DO UPDATE SET
                    score = excluded.score,
                    ats_score = excluded.ats_score,
                    missing_skills = excluded.missing_skills,
                    suggestions = excluded.suggestions,
                    filename = excluded.filename,
                    updated_at = excluded.updated_at
            """, (
                user_email.lower().strip(),
                score,
                ats_score,
                ",".join(missing_skills),
                "||".join(suggestions),
                filename,
                datetime.now().isoformat()
            ))
            conn.commit()

    def get_resume_analysis(self, user_email: str) -> dict:
        """Fetches the resume evaluation details."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resume_analyses WHERE user_email = ?", (user_email.lower().strip(),))
            row = cursor.fetchone()
            if row:
                res_dict = dict(row)
                # Split skills and suggestions back to lists
                res_dict["missing_skills"] = [s.strip() for s in res_dict["missing_skills"].split(",") if s.strip()]
                res_dict["suggestions"] = [s.strip() for s in res_dict["suggestions"].split("||") if s.strip()]
                return res_dict
            return {}

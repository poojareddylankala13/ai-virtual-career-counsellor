import sqlite3
import os
from datetime import datetime
from config import DB_PATH


class DBHelper:
    """
    Manages SQLite database transactions for user profile persistence
    and chatbot conversation transcripts.
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
            
            # Profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    session_id TEXT PRIMARY KEY,
                    name TEXT,
                    age INTEGER,
                    highest_qualification TEXT,
                    current_degree TEXT,
                    academic_year TEXT,
                    skills TEXT,
                    interests TEXT,
                    preferred_domain TEXT,
                    career_goal TEXT,
                    updated_at TEXT
                )
            """)

            # Chat history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    sender TEXT,
                    message TEXT,
                    timestamp TEXT
                )
            """)
            conn.commit()

    def save_profile(self, session_id: str, profile: dict):
        """Inserts or updates a user profile."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO profiles (
                    session_id, name, age, highest_qualification, current_degree,
                    academic_year, skills, interests, preferred_domain, career_goal, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    name=excluded.name,
                    age=excluded.age,
                    highest_qualification=excluded.highest_qualification,
                    current_degree=excluded.current_degree,
                    academic_year=excluded.academic_year,
                    skills=excluded.skills,
                    interests=excluded.interests,
                    preferred_domain=excluded.preferred_domain,
                    career_goal=excluded.career_goal,
                    updated_at=excluded.updated_at
            """, (
                session_id,
                profile.get("name", ""),
                profile.get("age", 0),
                profile.get("highest_qualification", ""),
                profile.get("current_degree", ""),
                profile.get("academic_year", ""),
                profile.get("skills", ""),
                profile.get("interests", ""),
                profile.get("preferred_domain", ""),
                profile.get("career_goal", ""),
                datetime.now().isoformat()
            ))
            conn.commit()

    def get_profile(self, session_id: str) -> dict:
        """Fetches a user profile by session ID."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                profile = dict(row)
                # Convert updated_at string to datetime or keep as string
                return profile
            return {}

    def add_chat_message(self, session_id: str, sender: str, message: str):
        """Appends a single message to the conversation history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (session_id, sender, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, sender, message, datetime.now().isoformat()))
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

    def clear_chat_history(self, session_id: str):
        """Clears all chat logs associated with a session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
            conn.commit()

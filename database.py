import sqlite3
from datetime import datetime

DB_NAME = "legal_ai.db"


# -----------------------------
# 1️⃣ Initialize Database
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        question TEXT NOT NULL,
        question_type TEXT,
        retrieved_context TEXT,
        answer TEXT NOT NULL,
        feedback TEXT DEFAULT NULL
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# 2️⃣ Save Interaction
# -----------------------------
def save_interaction(question, question_type, context, answer):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO interactions 
    (timestamp, question, question_type, retrieved_context, answer)
    VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        question,
        question_type,
        context,
        answer
    ))

    conn.commit()
    conn.close()


# -----------------------------
# 3️⃣ Save Feedback
# -----------------------------
def save_feedback(interaction_id, feedback):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE interactions
    SET feedback = ?
    WHERE id = ?
    """, (feedback, interaction_id))

    conn.commit()
    conn.close()


# -----------------------------
# 4️⃣ Fetch All Interactions
# -----------------------------
def get_all_interactions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interactions ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows


# -----------------------------
# 5️⃣ Fetch Recent Interactions
# -----------------------------
def get_recent_interactions(limit=3):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interactions ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()

    conn.close()
    return rows


# -----------------------------
# 6️⃣ Clear All Interactions
# -----------------------------
def clear_all_interactions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM interactions")

    conn.commit()
    conn.close()
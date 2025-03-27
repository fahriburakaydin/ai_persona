import sqlite3
import json
from datetime import datetime

DB_FILE = "posts.db"

def init_db():
    """Initialize the SQLite database with a 'posts' table."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            caption TEXT,
            image_idea TEXT,
            dynamic_scene TEXT,
            technical_prompt TEXT,
            image_source TEXT,
            post_category TEXT,
            insta_post_id TEXT,
            insta_code TEXT,
            is_posted INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def log_post_draft(post_data: dict) -> int:
    """
    Logs a post draft into the SQLite database.
    The draft is logged with is_posted = 0.
    Expected keys in post_data:
      - timestamp: ISO formatted string.
      - caption: Caption text.
      - image_idea: The creative image idea.
      - dynamic_scene: The refined dynamic scene description.
      - technical_prompt: The final technical prompt used.
      - image_source: (Empty at draft time)
      - post_category: "self" or "general".
      - insta_post_id: (Empty at draft time)
      - insta_code: (Empty at draft time)
    Returns the row id of the inserted draft.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO posts (timestamp, caption, image_idea, dynamic_scene, technical_prompt, image_source, post_category, insta_post_id, insta_code, is_posted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        post_data.get("timestamp"),
        post_data.get("caption"),
        post_data.get("image_idea"),
        post_data.get("dynamic_scene"),
        post_data.get("technical_prompt"),
        post_data.get("image_source"),  # Empty at draft time.
        post_data.get("post_category"),
        post_data.get("insta_post_id", ""),
        post_data.get("insta_code", ""),
        0  # is_posted is 0 for a draft.
    ))
    row_id = c.lastrowid
    conn.commit()
    conn.close()
    return row_id

def update_post_status(row_id: int, updated_data: dict) -> None:
    """
    Updates the post entry with the given row_id using updated_data.
    This function updates fields like insta_post_id, insta_code, image_source, caption,
    and sets is_posted to 1.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        UPDATE posts
        SET insta_post_id = ?,
            insta_code = ?,
            image_source = ?,
            caption = ?,
            is_posted = ?
        WHERE id = ?
    ''', (
        updated_data.get("insta_post_id", ""),
        updated_data.get("insta_code", ""),
        updated_data.get("image_source", ""),
        updated_data.get("caption", ""),
        1,  # Mark as posted.
        row_id
    ))
    conn.commit()
    conn.close()

def get_all_posts() -> list:
    """Retrieves all logged post records from the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM posts")
    rows = c.fetchall()
    conn.close()
    return rows

# Initialize the database when this module is imported.
init_db()

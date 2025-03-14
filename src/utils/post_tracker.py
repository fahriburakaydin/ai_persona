# src/utils/post_tracker.py

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
            insta_code TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_post(post_data: dict) -> None:
    """
    Logs a post record to the SQLite database.
    
    Expected keys in post_data:
      - timestamp: ISO formatted string.
      - caption: Caption text.
      - image_idea: The creative image idea.
      - dynamic_scene: The refined dynamic scene description.
      - technical_prompt: The final technical prompt used.
      - image_source: URL or local file path of the generated image.
      - post_category: "self" or "general".
      - result: A dictionary containing Instagram result details.
    
    This function extracts only key fields from the Instagram result (for example, 'pk' and 'code').
    """
    # Extract key fields from the Instagram result.
    insta_result = post_data.get("result", {})
    insta_post_id = insta_result.get("pk", "") if isinstance(insta_result, dict) else ""
    insta_code = insta_result.get("code", "") if isinstance(insta_result, dict) else ""
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO posts (timestamp, caption, image_idea, dynamic_scene, technical_prompt, image_source, post_category, insta_post_id, insta_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        post_data.get("timestamp"),
        post_data.get("caption"),
        post_data.get("image_idea"),
        post_data.get("dynamic_scene"),
        post_data.get("technical_prompt"),
        post_data.get("image_source"),
        post_data.get("post_category"),
        insta_post_id,
        insta_code
    ))
    conn.commit()
    conn.close()

def get_all_posts() -> list:
    """Retrieves all logged post records."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM posts")
    rows = c.fetchall()
    conn.close()
    return rows

# Initialize the database when this module is imported.
init_db()

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ==========================================
# PostgreSQL Connection
# ==========================================

def get_connection():
    return psycopg2.connect(DATABASE_URL)


# ==========================================
# Initialize Database
# ==========================================

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # ---------------- USERS TABLE ----------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            bio TEXT DEFAULT '',
            profile_image TEXT DEFAULT '',
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------- POSTS TABLE ----------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts(
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            risk_level VARCHAR(20),
            risk_score INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# ==========================================
# Save Post
# ==========================================

def save_post_to_db(user_id, content, risk_level, risk_score):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO posts(user_id, content, risk_level, risk_score)
        VALUES (%s,%s,%s,%s)
    """, (user_id, content, risk_level, risk_score))

    conn.commit()
    cur.close()
    conn.close()


# ==========================================
# Get All Posts
# ==========================================

def get_all_posts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            posts.id,
            users.username,
            posts.content,
            posts.risk_level,
            posts.risk_score,
            posts.timestamp

        FROM posts

        JOIN users
        ON posts.user_id = users.id

        ORDER BY posts.id DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    posts = []

    for row in rows:
        posts.append({
            "id": row[0],
            "username": row[1],
            "content": row[2],
            "risk_level": row[3],
            "risk_score": row[4],
            "timestamp": row[5]
        })

    return posts


# ==========================================
# Get Single Post
# ==========================================

def get_post(post_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            posts.id,
            users.username,
            posts.content,
            posts.risk_level,
            posts.risk_score,
            posts.timestamp

        FROM posts

        JOIN users
        ON posts.user_id = users.id

        WHERE posts.id=%s
    """, (post_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return {
            "id": row[0],
            "username": row[1],
            "content": row[2],
            "risk_level": row[3],
            "risk_score": row[4],
            "timestamp": row[5]
        }

    return None


# ==========================================
# Update Post
# ==========================================

def update_post(post_id, content):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE posts
        SET content=%s
        WHERE id=%s
    """, (content, post_id))

    conn.commit()
    cur.close()
    conn.close()


# ==========================================
# Delete Post
# ==========================================

def delete_post_from_db(post_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM posts
        WHERE id=%s
    """, (post_id,))

    conn.commit()
    cur.close()
    conn.close()


# ==========================================
# Statistics
# ==========================================

def get_statistics():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM posts")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM posts WHERE risk_level='LOW'")
    low = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM posts WHERE risk_level='MEDIUM'")
    medium = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM posts WHERE risk_level='HIGH'")
    high = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "total_posts": total,
        "low_risk": low,
        "medium_risk": medium,
        "high_risk": high
    }


# ==========================================
# USER FUNCTIONS
# ==========================================

def create_user(username, bio=""):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users(username, bio)
        VALUES(%s, %s)
        RETURNING id
    """, (username, bio))

    user_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return user_id

def get_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, bio, profile_image
        FROM users
        WHERE username=%s
    """, (username,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return {
            "id": row[0],
            "username": row[1],
            "bio": row[2],
            "profile_image": row[3]
        }

    return None

def update_user(username, bio):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET bio=%s
        WHERE username=%s
    """, (bio, username))

    conn.commit()
    cur.close()
    conn.close()
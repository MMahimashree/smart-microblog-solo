import os
import psycopg2
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    # Connect to Neon PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connected to Neon Successfully!")

    # Create cursor
    cur = conn.cursor()

    # Check PostgreSQL Version
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(version)

    # Create Posts Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts(
        id SERIAL PRIMARY KEY,
        username VARCHAR(100),
        content TEXT NOT NULL,
        risk_level VARCHAR(20),
        risk_score INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    print("✅ Posts table created successfully!")

    # Close everything
    cur.close()
    conn.close()

except Exception as e:
    print("❌ Error:", e)
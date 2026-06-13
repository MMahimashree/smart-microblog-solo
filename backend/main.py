# ============================================
# main.py
# PURPOSE: FastAPI backend server
# This is the entry point of our backend
# It creates the API endpoints that the
# React frontend will communicate with
#
# ENDPOINTS:
# GET  /           → health check (is server running?)
# POST /scan-post  → scan text for PII and return risk level
# POST /save-post  → save approved post to database
# GET  /get-feed   → get all published posts
# ============================================

from fastapi import FastAPI
# FastAPI → the web framework we use to build our API
# It automatically creates documentation at /docs

from fastapi.middleware.cors import CORSMiddleware
# CORSMiddleware → allows our React frontend (running on port 3000)
# to communicate with our backend (running on port 8000)
# Without this, browser will block the requests for security reasons

from pydantic import BaseModel
# BaseModel → used to define the structure of data
# we expect to receive from the frontend

from pii_detector import detect_pii
# Import our PII detection function from pii_detector.py

from risk_scorer import calculate_risk
# Import our risk scoring function from risk_scorer.py

import sqlite3
# sqlite3 → built-in Python library to work with SQLite database
# No installation needed!

import datetime
# datetime → used to record timestamp when post is saved


# ── CREATE FASTAPI APP ───────────────────────────────────────
# This creates the main FastAPI application instance
# All our endpoints will be attached to this app
app = FastAPI(
    title="Smart Microblog Privacy Guard",  # shown in /docs
    description="API that scans posts for PII before publishing",
    version="1.0.0"
)

# ── CORS SETTINGS ────────────────────────────────────────────
# Allow React frontend to talk to this backend
# origins = list of allowed frontend addresses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React runs on port 3000
    allow_credentials=True,
    allow_methods=["*"],   # allow all HTTP methods (GET, POST etc.)
    allow_headers=["*"],   # allow all headers
)


# ── DATABASE SETUP ───────────────────────────────────────────
# Function to initialize the SQLite database
# Creates the posts table if it doesn't exist yet
def init_db():
    # connect() opens a connection to blog.db file
    # If blog.db doesn't exist, SQLite creates it automatically
    conn = sqlite3.connect('blog.db')

    # cursor lets us execute SQL commands
    cursor = conn.cursor()

    # CREATE TABLE IF NOT EXISTS → creates table only if not already there
    # So running this multiple times won't cause errors
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    # commit() saves the changes to the database file
    conn.commit()

    # close() closes the connection — always close after use
    conn.close()

# Call init_db when server starts
# This ensures the table exists before any request comes in
init_db()


# ── DATA MODELS ──────────────────────────────────────────────
# These classes define what data we expect from the frontend
# Pydantic automatically validates the incoming data

class ScanRequest(BaseModel):
    # When frontend calls /scan-post, it must send:
    text: str  # the post text to scan

class SaveRequest(BaseModel):
    # When frontend calls /save-post, it must send:
    content: str      # the post text
    risk_level: str   # LOW / MEDIUM / HIGH
    risk_score: int   # the numeric score


# ── ENDPOINT 1: HEALTH CHECK ─────────────────────────────────
# GET / → just confirms the server is running
# Used to test if backend is alive
@app.get("/")
def home():
    return {"message": "Smart Microblog Privacy Guard API is running!"}


# ── ENDPOINT 2: SCAN POST ────────────────────────────────────
# POST /scan-post → main endpoint
# Receives post text, scans for PII, returns risk assessment
# Frontend calls this BEFORE publishing a post
@app.post("/scan-post")
def scan_post(request: ScanRequest):
    # request.text = the text sent by frontend

    # STEP 1: Detect PII using our pii_detector.py
    # detect_pii() returns dict with emails, phones, persons, locations
    detected_entities = detect_pii(request.text)

    # STEP 2: Calculate risk using our risk_scorer.py
    # calculate_risk() returns risk_score, risk_level, recommendation
    risk_result = calculate_risk(detected_entities)

    # STEP 3: Return everything as JSON response to frontend
    return {
        "detected_entities": detected_entities,   # what was found
        "risk_score": risk_result['risk_score'],   # 0-100
        "risk_level": risk_result['risk_level'],   # LOW/MEDIUM/HIGH
        "recommendation": risk_result['recommendation']  # message
    }


# ── ENDPOINT 3: SAVE POST ────────────────────────────────────
# POST /save-post → saves approved post to database
# Frontend calls this AFTER user confirms they want to publish
@app.post("/save-post")
def save_post(request: SaveRequest):
    # Get current timestamp for recording when post was made
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Open database connection
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # INSERT INTO → adds a new row to the posts table
    # ? marks are placeholders — prevents SQL injection attacks
    cursor.execute('''
        INSERT INTO posts (content, risk_level, risk_score, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (request.content, request.risk_level, request.risk_score, timestamp))

    # Save changes
    conn.commit()
    conn.close()

    # Return success message to frontend
    return {"message": "Post saved successfully!"}


# ── ENDPOINT 4: GET FEED ─────────────────────────────────────
# GET /get-feed → retrieves all published posts
# Frontend calls this to display the timeline/feed
@app.get("/get-feed")
def get_feed():
    # Open database connection
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # SELECT * → get all columns
    # ORDER BY id DESC → newest posts first (highest id = newest)
    cursor.execute('SELECT * FROM posts ORDER BY id DESC')

    # fetchall() returns all matching rows as a list of tuples
    rows = cursor.fetchall()
    conn.close()

    # Convert each row tuple into a dictionary
    # so it's easier to use in the frontend
    posts = []
    for row in rows:
        posts.append({
            "id": row[0],           # unique post id
            "content": row[1],      # the post text
            "risk_level": row[2],   # LOW/MEDIUM/HIGH
            "risk_score": row[3],   # numeric score
            "timestamp": row[4]     # when it was posted
        })

    # Return the list of posts as JSON
    return {"posts": posts}
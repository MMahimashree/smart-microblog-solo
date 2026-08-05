# ============================================
# main.py
# Smart Microblog Privacy Guard
# PostgreSQL Version
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pii_detector import detect_pii
from risk_scorer import calculate_risk
from database import (
    init_db,
    save_post_to_db,
    get_all_posts,
    delete_post_from_db,
    get_post,
    update_post,
    get_statistics,
    create_user,
    get_user,
    update_user
)

# ============================================
# FASTAPI
# ============================================

app = FastAPI(
    title="Smart Microblog Privacy Guard",
    description="AI Powered Privacy Detection System",
    version="4.0"
)

# ============================================
# CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Initialize Database
# ============================================

init_db()

# ============================================
# Request Models
# ============================================

class ScanRequest(BaseModel):
    text: str


class SaveRequest(BaseModel):
    username: str
    content: str
    risk_level: str
    risk_score: int


class UpdateRequest(BaseModel):
    content: str

# ============================================
# Profile Request
# ============================================

class ProfileRequest(BaseModel):
    username: str
    bio: str

# ============================================
# HOME
# ============================================

@app.get("/")
def home():
    return {
        "message": "Smart Microblog Privacy Guard API Running"
    }


# ============================================
# SCAN POST
# ============================================
@app.post("/scan-post")
def scan_post(request: ScanRequest):

    print("\n========================")
    print("INPUT:", request.text)

    detected = detect_pii(request.text)
    print("DETECTED:", detected)

    risk = calculate_risk(detected)
    print("RISK:", risk)

    return {
        "detected_entities": detected,
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "recommendation": risk["recommendation"]
    }


# ============================================
# SAVE POST
# ============================================
@app.post("/save-post")
def save_post(request: SaveRequest):

    user = get_user(request.username)

    if user is None:
        user_id = create_user(request.username)
    else:
        user_id = user["id"]

    save_post_to_db(
        user_id,
        request.content,
        request.risk_level,
        request.risk_score
    )

    return {
        "message": "Post saved successfully"
    }

# ============================================
# SAVE / UPDATE PROFILE
# ============================================
@app.post("/profile")
def save_profile(request: ProfileRequest):

    user = get_user(request.username)

    if user:
        update_user(
            request.username,
            request.bio
        )

        return {
            "message": "Profile updated successfully"
        }

    create_user(
        request.username,
        request.bio
    )

    return {
        "message": "Profile created successfully"
    }
# ============================================
# GET PROFILE
# ============================================

@app.get("/profile/{username}")
def read_profile(username: str):

    user = get_user(username)

    if user is None:
        return {
            "message": "User not found"
        }

    return {
    "id": user["id"],
    "username": user["username"],
    "bio": user["bio"],
    "profile_image": user["profile_image"]
}

# ============================================
# FEED
# ============================================

@app.get("/get-feed")
def get_feed():

    return {
        "posts": get_all_posts()
    }


# ============================================
# GET SINGLE POST
# ============================================

@app.get("/post/{post_id}")
def read_post(post_id: int):

    return get_post(post_id)


# ============================================
# UPDATE POST
# ============================================

@app.put("/update-post/{post_id}")
def edit_post(post_id: int, request: UpdateRequest):

    update_post(
        post_id,
        request.content
    )

    return {
        "message": "Post updated successfully"
    }


# ============================================
# DELETE POST
# ============================================

@app.delete("/delete-post/{post_id}")
def delete_post(post_id: int):

    delete_post_from_db(post_id)

    return {
        "message": "Post deleted successfully"
    }


# ============================================
# STATISTICS
# ============================================

@app.get("/stats")
def statistics():

    return get_statistics()
# ============================================
# main.py
# Smart Microblog Privacy Guard
#
# FastAPI + Hybrid PII Detection
# + Ollama Verification
# + Context Analysis
# + Risk Scoring
# + PostgreSQL / Neon
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pii_detector import detect_pii
from ollama_verifier import verify_entities
from context_analyzer import analyze_context
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
# FASTAPI APPLICATION
# ============================================

app = FastAPI(
    title="Smart Microblog Privacy Guard",
    description=(
        "AI-powered privacy protection system "
        "using Hybrid PII Detection, "
        "Ollama Verification, Context Analysis "
        "and Privacy Risk Scoring."
    ),
    version="6.0"
)


# ============================================
# CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# INITIALIZE DATABASE
# ============================================

init_db()


# ============================================
# REQUEST MODELS
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

    print("\n")
    print("=" * 60)
    print("SMART MICROBLOG PRIVACY GUARD")
    print("=" * 60)

    print("\nINPUT TEXT:")
    print(request.text)

    # ========================================
    # STEP 1: HYBRID PII DETECTION
    # ========================================

    print("\n[STEP 1] HYBRID PII DETECTION")

    detected = detect_pii(request.text)

    detected_entities = detected.get("entities", [])

    print("Detected entities:")
    print(detected_entities)

    # ========================================
    # STEP 2: OLLAMA VERIFICATION
    # ========================================

    print("\n[STEP 2] OLLAMA VERIFICATION")

    verified_entities = verify_entities(
        detected_entities
    )

    print("Verified entities:")
    print(verified_entities)

    # ========================================
    # STEP 3: REBUILD VERIFIED PII CATEGORIES
    # ========================================

    verified_detected = {

        "phones": [],
        "emails": [],
        "aadhaars": [],
        "pans": [],
        "dobs": [],
        "persons": [],
        "locations": [],

        "entities": verified_entities
    }

    # ========================================
    # CLASSIFY VERIFIED ENTITIES
    # ========================================

    for entity in verified_entities:

        label = str(
            entity.get("label", "")
        ).upper()

        entity_text = entity.get(
            "text",
            ""
        )

        if label == "PHONE":

            verified_detected["phones"].append(
                entity_text
            )

        elif label == "EMAIL":

            verified_detected["emails"].append(
                entity_text
            )

        elif label == "AADHAAR":

            verified_detected["aadhaars"].append(
                entity_text
            )

        elif label == "PAN":

            verified_detected["pans"].append(
                entity_text
            )

        elif label == "DOB":

            verified_detected["dobs"].append(
                entity_text
            )

        elif label == "PERSON":

            verified_detected["persons"].append(
                entity_text
            )

        elif label == "LOCATION":

            verified_detected["locations"].append(
                entity_text
            )

    # ========================================
    # STEP 4: CONTEXT ANALYSIS
    # ========================================

    print("\n[STEP 3] CONTEXT ANALYSIS")

    context = analyze_context(
        request.text
    )

    print("Context analysis:")
    print(context)

    # ========================================
    # STEP 5: RISK SCORING
    # ========================================

    print("\n[STEP 4] RISK SCORING")

    # IMPORTANT:
    # Pass BOTH verified PII and context
    # to the risk scorer.

    risk = calculate_risk(
        verified_detected,
        context
    )

    print("Risk analysis:")
    print(risk)

    # ========================================
    # FINAL PRIVACY ANALYSIS
    # ========================================

    print("\n")
    print("=" * 60)
    print("FINAL PRIVACY ANALYSIS")
    print("=" * 60)

    print(
        "PII Score:",
        risk.get("pii_score", 0)
    )

    print(
        "Context Score:",
        risk.get("context_score", 0)
    )

    print(
        "Risk Score:",
        risk.get("risk_score", 0)
    )

    print(
        "Risk Level:",
        risk.get("risk_level", "LOW")
    )

    print(
        "Action:",
        risk.get("action", "ALLOW")
    )

    print(
        "Recommendation:",
        risk.get("recommendation", "")
    )

    print("=" * 60)
    print("\n")

    # ========================================
    # FINAL RESPONSE
    # ========================================

    return {

        # Detected and verified PII
        "detected_entities": verified_detected,

        # Context information
        "context_analysis": context,

        # Risk information
        "risk_score": risk.get(
            "risk_score",
            0
        ),

        "risk_level": risk.get(
            "risk_level",
            "LOW"
        ),

        "recommendation": risk.get(
            "recommendation",
            ""
        ),

        "action": risk.get(
            "action",
            "ALLOW"
        ),

        "pii_score": risk.get(
            "pii_score",
            0
        ),

        "context_score": risk.get(
            "context_score",
            0
        )
    }


# ============================================
# SAVE POST
# ============================================

@app.post("/save-post")
def save_post(request: SaveRequest):

    user = get_user(
        request.username
    )

    # ----------------------------------------
    # Create user if not found
    # ----------------------------------------

    if user is None:

        user_id = create_user(
            request.username
        )

    else:

        user_id = user["id"]

    # ----------------------------------------
    # Save post
    # ----------------------------------------

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
def save_profile(
    request: ProfileRequest
):

    user = get_user(
        request.username
    )

    # ----------------------------------------
    # Update existing profile
    # ----------------------------------------

    if user:

        update_user(
            request.username,
            request.bio
        )

        return {
            "message": "Profile updated successfully"
        }

    # ----------------------------------------
    # Create new profile
    # ----------------------------------------

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
def read_profile(
    username: str
):

    user = get_user(
        username
    )

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
# GET FEED
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
def read_post(
    post_id: int
):

    return get_post(
        post_id
    )


# ============================================
# UPDATE POST
# ============================================

@app.put("/update-post/{post_id}")
def edit_post(
    post_id: int,
    request: UpdateRequest
):

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
def delete_post(
    post_id: int
):

    delete_post_from_db(
        post_id
    )

    return {
        "message": "Post deleted successfully"
    }


# ============================================
# STATISTICS
# ============================================

@app.get("/stats")
def statistics():

    return get_statistics()
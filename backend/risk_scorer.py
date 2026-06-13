# ============================================
# risk_scorer.py
# PURPOSE: Calculate risk score from detected PII
# and classify it as LOW, MEDIUM or HIGH
# 
# SCORING LOGIC:
# Each PII type has a weight/points value
# We add up all points and classify:
# 0-29  → LOW
# 30-69 → MEDIUM
# 70+   → HIGH
# ============================================


# ── RISK WEIGHTS ─────────────────────────────────────────────
# Each PII type has a score value based on how dangerous it is
# Phone and Email are most dangerous (strangers can directly contact you)
# Location is medium danger (reveals where you are)
# Person name alone is least dangerous
RISK_WEIGHTS = {
    'phone': 50,     # most dangerous — direct contact possible
    'email': 50,     # most dangerous — direct contact possible
    'location': 20,  # medium danger — reveals where you live/are
    'person': 10     # least dangerous — name alone is not enough
}

# ── RISK THRESHOLDS ──────────────────────────────────────────
# These values decide which category the final score falls into
LOW_MAX = 29      # 0 to 29 = LOW risk
MEDIUM_MAX = 69   # 30 to 69 = MEDIUM risk
                  # 70+ = HIGH risk


# ── MAIN FUNCTION ────────────────────────────────────────────
# Takes the detected PII dictionary from pii_detector.py
# Returns risk score, risk level and a recommendation message
def calculate_risk(detected_entities):

    # Start with zero score
    # We will add points for each PII found
    score = 0

    # ── STEP 1: ADD POINTS FOR EACH PII FOUND ────────────────

    # For each phone number found, add 50 points
    # len() counts how many phone numbers were detected
    score += len(detected_entities['phones']) * RISK_WEIGHTS['phone']

    # For each email found, add 50 points
    score += len(detected_entities['emails']) * RISK_WEIGHTS['email']

    # For each location found, add 20 points
    score += len(detected_entities['locations']) * RISK_WEIGHTS['location']

    # For each person name found, add 10 points
    score += len(detected_entities['persons']) * RISK_WEIGHTS['person']

    # ── STEP 2: CAP THE SCORE AT 100 ─────────────────────────
    # Score should never exceed 100 (like a percentage)
    # If someone shares phone + email + location, score would be 120
    # We cap it at 100 to keep it clean
    if score > 100:
        score = 100

    # ── STEP 3: CLASSIFY RISK LEVEL ──────────────────────────
    # Based on the final score, assign a risk level
    if score <= LOW_MAX:
        # 0-29 = LOW — safe to post, no critical PII found
        risk_level = 'LOW'
        recommendation = 'Your post looks safe to publish.'

    elif score <= MEDIUM_MAX:
        # 30-69 = MEDIUM — some PII found, user should be careful
        risk_level = 'MEDIUM'
        recommendation = 'Some personal information detected. Consider reviewing before posting.'

    else:
        # 70+ = HIGH — critical PII found, must warn user
        risk_level = 'HIGH'
        recommendation = 'Sensitive personal information detected! Remove it before publishing.'

    # ── STEP 4: RETURN RESULT ─────────────────────────────────
    # Return a dictionary with score, level and recommendation
    # This will be sent back to the frontend as JSON
    return {
        'risk_score': score,        # the numeric score (0-100)
        'risk_level': risk_level,   # LOW / MEDIUM / HIGH
        'recommendation': recommendation  # message to show user
    }


# ── QUICK TEST ───────────────────────────────────────────────
# Only runs when you directly run this file
if __name__ == '__main__':
    # Simulate what pii_detector would return
    test_entities = {
        'phones': ['9876543210'],
        'emails': ['mahima@gmail.com'],
        'persons': ['Mahima'],
        'locations': ['Bangalore']
    }
    print("Testing Risk Scorer...")
    print("Input:", test_entities)
    print("Output:", calculate_risk(test_entities))
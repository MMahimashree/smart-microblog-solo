# ============================================
# risk_scorer.py
# PURPOSE:
# Calculates a privacy risk score based on the
# detected Personal Identifiable Information (PII)
# and classifies it as LOW, MEDIUM or HIGH.
# ============================================

# ---------------- RISK WEIGHTS ---------------- #

RISK_WEIGHTS = {
    "phone": 50,
    "email": 50,
    "aadhaar": 100,
    "pan": 80,
    "dob": 30,
    "location": 20,
    "person": 10
}

# ---------------- THRESHOLDS ---------------- #

LOW_MAX = 29
MEDIUM_MAX = 69
# HIGH = 70+

# ---------------- MAIN FUNCTION ---------------- #

def calculate_risk(detected_entities):

    score = 0

    # Phone Numbers
    score += len(detected_entities["phones"]) * RISK_WEIGHTS["phone"]

    # Emails
    score += len(detected_entities["emails"]) * RISK_WEIGHTS["email"]

    # Aadhaar Numbers
    score += len(detected_entities["aadhaars"]) * RISK_WEIGHTS["aadhaar"]

    # PAN Numbers
    score += len(detected_entities["pans"]) * RISK_WEIGHTS["pan"]

    # Date of Birth
    score += len(detected_entities["dobs"]) * RISK_WEIGHTS["dob"]

    # Locations
    score += len(detected_entities["locations"]) * RISK_WEIGHTS["location"]

    # Person Names
    score += len(detected_entities["persons"]) * RISK_WEIGHTS["person"]

    # Maximum score is 100
    score = min(score, 100)

    # -------- Risk Classification -------- #

    if score <= LOW_MAX:

        risk_level = "LOW"

        recommendation = (
            "No major privacy risks detected. "
            "Your post appears safe to publish."
        )

    elif score <= MEDIUM_MAX:

        risk_level = "MEDIUM"

        recommendation = (
            "Some personal information was detected. "
            "Please review your post before publishing."
        )

    else:

        risk_level = "HIGH"

        recommendation = (
            "Highly sensitive personal information detected. "
            "Remove or mask the information before publishing."
        )

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "recommendation": recommendation
    }


# ---------------- TEST ---------------- #

if __name__ == "__main__":

    sample = {
        "phones": ["9876543210"],
        "emails": ["mahima@gmail.com"],
        "aadhaars": ["1234 5678 9012"],
        "pans": ["ABCDE1234F"],
        "dobs": ["23/12/2005"],
        "persons": ["Mahimashree"],
        "locations": ["Mangalore"]
    }

    print(calculate_risk(sample))
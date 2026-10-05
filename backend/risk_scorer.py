# ============================================
# risk_scorer.py
# Smart Microblog Privacy Guard
#
# Rule-Based Context-Aware Privacy Risk Scoring
# Score: 0 - 100
# ============================================


# ============================================
# PII SENSITIVITY WEIGHTS
# ============================================
RISK_WEIGHTS = {
    "AADHAAR": 100,
    "PAN": 90,
    "PHONE": 60,
    "DOB": 50,
    "EMAIL": 50,
    "LOCATION": 25,
    "PERSON": 10
}


# ============================================
# CONTEXT CONFIGURATION
# ============================================

# Context should modify the risk,
# not completely dominate the PII score.

MAX_CONTEXT_BONUS = 20


# ============================================
# CRITICAL ENTITIES
# ============================================

CRITICAL_ENTITIES = {
    "AADHAAR"
}


# ============================================
# CALCULATE PII SCORE
# ============================================

def calculate_pii_score(detected_entities):

    entities = detected_entities.get(
        "entities",
        []
    )

    if not entities:
        return 0, [], []


    processed_entities = set()

    scores = []
    detected_labels = []


    for entity in entities:

        label = str(
            entity.get("label", "")
        ).upper()

        value = str(
            entity.get("text", "")
        )

        identity = (
            label,
            value,
            entity.get("start"),
            entity.get("end")
        )

        # Avoid duplicate entities
        if identity in processed_entities:
            continue

        processed_entities.add(identity)

        weight = RISK_WEIGHTS.get(
            label,
            10
        )

        scores.append(weight)

        if label not in detected_labels:
            detected_labels.append(label)


    if not scores:
        return 0, [], []


    # ----------------------------------------
    # Critical PII immediately creates
    # very high risk
    # ----------------------------------------

    if any(
        label in CRITICAL_ENTITIES
        for label in detected_labels
    ):

        return 100, detected_labels, scores


    # ----------------------------------------
    # Highest sensitivity is the base risk
    # ----------------------------------------

    highest_score = max(scores)


    # ----------------------------------------
    # Additional entities add limited risk
    #
    # This prevents many low-risk entities
    # from unnecessarily reaching 100.
    # ----------------------------------------

    remaining_scores = sorted(
        scores,
        reverse=True
    )[1:]


    additional_score = 0

    for score in remaining_scores:

        additional_score += score * 0.15


    pii_score = (
        highest_score +
        additional_score
    )


    pii_score = min(
        round(pii_score),
        100
    )


    return (
        pii_score,
        detected_labels,
        scores
    )


# ============================================
# CONTEXT CONTRIBUTION
# ============================================

def calculate_context_adjustment(
    context_analysis,
    pii_score
):

    if not context_analysis:
        return 0


    context_score = context_analysis.get(
        "context_score",
        0
    )


    try:
        context_score = float(
            context_score
        )
    except:
        context_score = 0


    context_score = max(
        0,
        min(context_score, 100)
    )


    # ----------------------------------------
    # Context contributes at most +20
    # ----------------------------------------

    context_bonus = (
        context_score / 100
    ) * MAX_CONTEXT_BONUS


    # ----------------------------------------
    # Low-risk PII should not suddenly become
    # extremely high only because of context.
    # ----------------------------------------

    if pii_score < 30:

        context_bonus *= 0.5


    return round(
        context_bonus
    )


# ============================================
# MAIN RISK FUNCTION
# ============================================

def calculate_risk(
    detected_entities,
    context_analysis=None
):

    # ========================================
    # STEP 1
    # Calculate PII sensitivity
    # ========================================

    (
        pii_score,
        detected_labels,
        individual_scores
    ) = calculate_pii_score(
        detected_entities
    )


    # ========================================
    # STEP 2
    # Calculate context contribution
    # ========================================

    context_bonus = calculate_context_adjustment(
        context_analysis,
        pii_score
    )


    # ========================================
    # STEP 3
    # Final score
    # ========================================

    final_score = (
        pii_score +
        context_bonus
    )


    # ========================================
    # SAFETY LIMIT
    # ========================================

    final_score = max(
        0,
        min(
            round(final_score),
            100
        )
    )


    # ========================================
    # STEP 4
    # CLASSIFICATION
    # ========================================

    if final_score < 30:

        risk_level = "LOW"

        action = "ALLOW"

        recommendation = (
            "No significant privacy risk detected. "
            "The post appears safe to publish."
        )


    elif final_score < 60:

        risk_level = "MEDIUM"

        action = "WARNING"

        recommendation = (
            "Personal information or contextual "
            "privacy risk was detected. "
            "Review the post before publishing."
        )


    else:

        risk_level = "HIGH"

        action = "BLOCK"

        recommendation = (
            "Highly sensitive personal information "
            "or significant contextual privacy risk "
            "was detected. Remove or mask the "
            "sensitive information before publishing."
        )


    # ========================================
    # STEP 5
    # RETURN RESULT
    # ========================================

    return {

        "risk_score": final_score,

        "risk_level": risk_level,

        "action": action,

        "pii_score": pii_score,

        "context_score": (
            context_analysis.get(
                "context_score",
                0
            )
            if context_analysis
            else 0
        ),

        "context_bonus": context_bonus,

        "detected_types": detected_labels,

        "recommendation": recommendation
    }


# ============================================
# QUICK TEST
# ============================================

if __name__ == "__main__":

    test_cases = [

        {
            "name": "Location only",
            "entities": [
                {
                    "text": "Mangalore",
                    "label": "LOCATION"
                }
            ]
        },

        {
            "name": "Person only",
            "entities": [
                {
                    "text": "Kavya",
                    "label": "PERSON"
                }
            ]
        },

        {
            "name": "Phone",
            "entities": [
                {
                    "text": "9876543210",
                    "label": "PHONE"
                }
            ]
        },

        {
            "name": "Email",
            "entities": [
                {
                    "text": "test@gmail.com",
                    "label": "EMAIL"
                }
            ]
        },

        {
            "name": "Aadhaar",
            "entities": [
                {
                    "text": "1234 5678 9012",
                    "label": "AADHAAR"
                }
            ]
        },

        {
            "name": "Multiple PII",
            "entities": [
                {
                    "text": "Kavya",
                    "label": "PERSON"
                },
                {
                    "text": "Mangalore",
                    "label": "LOCATION"
                },
                {
                    "text": "9876543210",
                    "label": "PHONE"
                },
                {
                    "text": "test@gmail.com",
                    "label": "EMAIL"
                }
            ]
        }
    ]


    for test in test_cases:

        detected = {
            "entities": test["entities"]
        }

        result = calculate_risk(
            detected,
            {
                "context_score": 0
            }
        )

        print("\n================================")
        print(test["name"])
        print("================================")

        print(
            "PII Score:",
            result["pii_score"]
        )

        print(
            "Context Bonus:",
            result["context_bonus"]
        )

        print(
            "Final Score:",
            result["risk_score"]
        )

        print(
            "Risk Level:",
            result["risk_level"]
        )

        print(
            "Action:",
            result["action"]
        )
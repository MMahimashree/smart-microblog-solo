# ============================================
# context_analyzer.py
# Smart Microblog Privacy Guard
#
# PURPOSE:
# Analyze the linguistic and sharing context
# of a social-media post to identify additional
# privacy-related risk.
# ============================================

import re


# ============================================
# MAIN CONTEXT ANALYZER
# ============================================

def analyze_context(text):

    # ----------------------------------------
    # Normalize text
    # ----------------------------------------

    text_lower = text.lower().strip()

    context_score = 0
    reasons = []

    # ========================================
    # 1. SELF-DISCLOSURE DETECTION
    # ========================================

    # Direct personal-information disclosure
    direct_disclosure_patterns = [

        r"\bmy name is\b",
        r"\bi live in\b",
        r"\bi stay in\b",
        r"\bi work at\b",
        r"\bi study at\b",

        r"\bmy address is\b",
        r"\bmy phone is\b",
        r"\bmy number is\b",
        r"\bmy email is\b",

        r"\bmy home is\b",
        r"\bmy workplace is\b",
        r"\bmy college is\b",
        r"\bmy school is\b"
    ]

    direct_disclosure = any(
        re.search(pattern, text_lower)
        for pattern in direct_disclosure_patterns
    )

    # ----------------------------------------
    # Identity disclosure using:
    # "I am Mahimashree"
    # "I'm Mahimashree"
    #
    # Avoid treating:
    # "I am learning Java"
    # "I am studying Python"
    # as personal identity disclosure.
    # ----------------------------------------

    identity_disclosure = bool(
        re.search(
            r"\b(i am|i'm)\s+"
            r"(?:called\s+|named\s+)?"
            r"[a-zA-Z][a-zA-Z'-]{2,}"
            r"(?:\s+[a-zA-Z][a-zA-Z'-]{2,})?"
            r"\b",
            text_lower
        )
    )

    # ----------------------------------------
    # Avoid common activity/occupation phrases
    # that begin with "I am".
    # ----------------------------------------

    non_identity_patterns = [

        r"\bi am learning\b",
        r"\bi am studying\b",
        r"\bi am working\b",
        r"\bi am developing\b",
        r"\bi am building\b",
        r"\bi am using\b",
        r"\bi am reading\b",
        r"\bi am watching\b",
        r"\bi am playing\b",
        r"\bi am doing\b",
        r"\bi am going\b",
        r"\bi am trying\b",
        r"\bi am practicing\b",
        r"\bi am sharing\b",

        

        r"\bi'm learning\b",
        r"\bi'm studying\b",
        r"\bi'm working\b",
        r"\bi'm developing\b",
        r"\bi'm building\b",
        r"\bi'm using\b",
        r"\bi'm reading\b",
        r"\bi'm watching\b",
        r"\bi'm playing\b",
        r"\bi'm doing\b",
        r"\bi'm going\b",
        r"\bi'm trying\b",
        r"\bi'm practicing\b",
        r"\bi'm sharing\b"
    ]

    generic_activity = any(
        re.search(pattern, text_lower)
        for pattern in non_identity_patterns
    )

    # ----------------------------------------
    # Final self-disclosure decision
    # ----------------------------------------

    self_disclosure = (
        direct_disclosure
        or (identity_disclosure and not generic_activity)
    )

    if self_disclosure:

        context_score += 20

        reasons.append(
            "Personal self-disclosure detected"
        )

    # ========================================
    # 2. SENSITIVE CONTEXT
    # ========================================

    sensitive_keywords = [

        "home address",
        "address",
        "password",
        "bank",
        "bank account",
        "account number",
        "medical",
        "hospital",
        "health",
        "salary",
        "income",
        "private",
        "secret",
        "confidential",
        "credit card",
        "debit card",
        "financial",
        "insurance"
    ]

    sensitive_context = any(
        re.search(
            r"\b" + re.escape(word) + r"\b",
            text_lower
        )
        for word in sensitive_keywords
    )

    if sensitive_context:

        context_score += 30

        reasons.append(
            "Sensitive context detected"
        )

    # ========================================
    # 3. PUBLIC SHARING CONTEXT
    # ========================================

    public_keywords = [

        "everyone",
        "public",
        "followers",
        "instagram",
        "twitter",
        "linkedin",
        "publicly",
        "share with everyone",
        "post publicly"
    ]

    public_context = any(
        re.search(
            r"\b" + re.escape(word) + r"\b",
            text_lower
        )
        for word in public_keywords
    )

    if public_context:

        context_score += 10

        reasons.append(
            "Public sharing context detected"
        )

    # ========================================
    # 4. EXPLICIT SHARING OF SENSITIVE DATA
    # ========================================

    sensitive_sharing_patterns = [

        r"\bsharing my\b",
        r"\bposting my\b",
        r"\bpost my\b",
        r"\bshare my\b",
        r"\bsharing .*password\b",
        r"\bsharing .*address\b",
        r"\bsharing .*phone\b",
        r"\bsharing .*email\b"
    ]

    sensitive_sharing = any(
        re.search(pattern, text_lower)
        for pattern in sensitive_sharing_patterns
    )

    if sensitive_sharing:

        context_score += 20

        reasons.append(
            "Explicit sensitive information sharing detected"
        )

    # ========================================
    # LIMIT SCORE
    # ========================================

    context_score = min(
        context_score,
        100
    )

    # ========================================
    # FINAL RESULT
    # ========================================

    return {

        "context_score": context_score,

        "self_disclosure": self_disclosure,

        "sensitive_context": sensitive_context,

        "public_context": public_context,

        "context_reasons": reasons
    }


# ============================================
# QUICK TEST
# ============================================

if __name__ == "__main__":

    test_cases = [

        "I am learning Java Full Stack development.",

        "I am reading manga today.",

        "My name is Mahimashree and I live in Mangalore.",

        "I am Mahimashree.",

        "I'm studying at Canara Engineering College.",

        "My phone number is 9876543210.",

        "My home address is private.",

        "I am sharing my phone number publicly."
    ]

    print("\n============================================")
    print("CONTEXT ANALYZER TEST")
    print("============================================")

    for text in test_cases:

        result = analyze_context(text)

        print("\nText:")
        print(text)

        print("Result:")
        print(result)

    print("\n============================================")
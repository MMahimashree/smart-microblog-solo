import json
import re
import requests


# ============================================
# CONFIGURATION
# ============================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

CONFIDENCE_THRESHOLD = 0.90
REQUEST_TIMEOUT = 60


# ============================================
# VERIFY ONE ENTITY
# ============================================

def verify_entity(context, entity):

    entity_text = entity.get("text", "")
    entity_label = entity.get("label", "OTHER")
    entity_confidence = float(entity.get("confidence", 0.0))

    # ----------------------------------------
    # HIGH CONFIDENCE
    # ----------------------------------------

    if entity_confidence >= CONFIDENCE_THRESHOLD:

        return {
            **entity,
            "verification": "ACCEPTED",
            "verified_by": "ML_MODELS",
            "verification_reason":
                "High-confidence prediction accepted directly"
        }

    # ----------------------------------------
    # LOW CONFIDENCE -> OLLAMA
    # ----------------------------------------

    prompt = f"""
You are a privacy and PII verification system.

Determine whether the following text contains personally
identifiable information.

Entity text: "{entity_text}"
Predicted label: "{entity_label}"
Model confidence: {entity_confidence:.4f}

Possible labels:
PERSON, LOCATION, EMAIL, PHONE, AADHAAR, PAN, DOB, NOT_PII

Return ONLY valid JSON in exactly this format:

{{
  "is_pii": true,
  "label": "PHONE",
  "confidence": 0.99,
  "reason": "This is a phone number."
}}

Rules:
- If the entity is clearly PII, set is_pii to true.
- If it is not PII, set is_pii to false and label to NOT_PII.
- Confidence must be between 0 and 1.
- Do not include markdown.
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        raw_response = data.get("response", "").strip()

        if not raw_response:
            raise ValueError("Ollama returned an empty response")

        # ------------------------------------
        # Parse JSON
        # ------------------------------------

        try:
            result = json.loads(raw_response)

        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                raw_response,
                re.DOTALL
            )

            if not match:
                raise ValueError(
                    "Invalid JSON returned by Ollama"
                )

            result = json.loads(match.group())

        # ------------------------------------
        # Extract result
        # ------------------------------------

        raw_is_pii = result.get("is_pii", False)

        # Handle both boolean and string responses
        if isinstance(raw_is_pii, str):
            is_pii = raw_is_pii.strip().lower() == "true"
        else:
            is_pii = bool(raw_is_pii)

        verified_label = str(
            result.get("label", entity_label)
        ).upper()

        llm_confidence = float(
            result.get("confidence", 0.0)
        )

        reason = str(
            result.get(
                "reason",
                "Verified by local LLM"
            )
        )

        # Keep confidence within valid range
        llm_confidence = max(
            0.0,
            min(llm_confidence, 1.0)
        )

        # ------------------------------------
        # NOT PII
        # ------------------------------------

        if not is_pii:

            return {
                **entity,
                "verification": "REJECTED",
                "verified_by": "Ollama",
                "verification_reason": reason,
                "llm_label": "NOT_PII",
                "llm_confidence": llm_confidence
            }

        # ------------------------------------
        # VERIFIED PII
        # ------------------------------------

        return {
            **entity,
            "label": verified_label,
            "verification": "VERIFIED",
            "verified_by": "Ollama",
            "verification_reason": reason,
            "llm_label": verified_label,
            "llm_confidence": llm_confidence
        }

    except requests.exceptions.ConnectionError:

        # ------------------------------------
        # OLLAMA UNAVAILABLE
        # IMPORTANT:
        # KEEP ORIGINAL ML DETECTION
        # ------------------------------------

        return {
            **entity,
            "verification": "FALLBACK",
            "verified_by": "ML_MODELS",
            "verification_reason":
                "Ollama unavailable; original ML prediction retained"
        }

    except Exception as error:

        # ------------------------------------
        # SAFE FALLBACK
        # NEVER LOSE A DETECTED PII ENTITY
        # ------------------------------------

        return {
            **entity,
            "verification": "FALLBACK",
            "verified_by": "ML_MODELS",
            "verification_reason":
                f"LLM verification failed; original prediction retained: {error}"
        }


# ============================================
# VERIFY ALL ENTITIES
# ============================================

def verify_entities(entities):

    verified_entities = []

    for entity in entities:

        verified = verify_entity(
            None,
            entity
        )

        # ------------------------------------
        # SAFETY RULE
        # Never silently lose an entity
        # ------------------------------------

        if not verified:
            verified = {
                **entity,
                "verification": "FALLBACK",
                "verified_by": "ML_MODELS",
                "verification_reason":
                    "Verification returned no result; original prediction retained"
            }

        # ------------------------------------
        # Remove only when Ollama explicitly
        # says NOT_PII
        # ------------------------------------

        if verified.get("verification") == "REJECTED":
            continue

        verified_entities.append(verified)

    return verified_entities


# ============================================
# TEST
# ============================================

if __name__ == "__main__":

    test_entity = {
        "text": "9876543210",
        "label": "PHONE",
        "start": 39,
        "end": 49,
        "confidence": 0.8459,
        "source": "Hybrid",
        "models": [
            "BERT",
            "Regex",
            "RoBERTa"
        ]
    }

    result = verify_entity(
        None,
        test_entity
    )

    print("\n================================")
    print("OLLAMA VERIFICATION TEST")
    print("================================")

    print(
        json.dumps(
            result,
            indent=2
        )
    )
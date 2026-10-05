# ============================================================
# pii_detector.py
# SMART MICROBLOG PRIVACY GUARD
# ============================================================

# FINAL BACKEND PII DETECTOR
#
# Detection layers:
#   1. Regex - structured PII
#   2. BERT - transformer NER
#   3. RoBERTa - transformer NER
#   4. spaCy - contextual NER
#   5. Location Detector
#   6. Hybrid span-level fusion
#
# Final NER architecture:
#
#       BERT --------\
#                     \
#       RoBERTa -------> Hybrid Fusion ---> Final PII
#                     /
#       spaCy --------/
#                     \
#       Location -----/
#
# Regex is retained as a deterministic safety layer
# for strongly structured identifiers.
# ============================================================


import re
import json
import sys
from pathlib import Path


# ============================================================
# LOCATION DETECTOR
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
ML_DIR = BASE_DIR / "ml"

if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))


from location_detector import detect_known_locations


# ============================================================
# ML LIBRARIES
# ============================================================

import torch
import spacy

from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification
)


# ============================================================
# MODEL PATHS
# ============================================================

BERT_MODEL_DIR = (
    BASE_DIR
    / "ml"
    / "models"
    / "bert_pii"
)

ROBERTA_MODEL_DIR = (
    BASE_DIR
    / "ml"
    / "models"
    / "roberta_pii"
)

SPACY_MODEL_DIR = (
    BASE_DIR
    / "ml"
    / "models"
    / "spacy_pii_combined"
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


print("\n" + "=" * 70)
print("SMART MICROBLOG PRIVACY GUARD")
print("INITIALIZING FINAL PII DETECTOR")
print("=" * 70)

print("Device:", DEVICE)


# ============================================================
# REGEX PATTERNS
# ============================================================

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
)


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


AADHAAR_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\d{4}[\s-]?){2}\d{4}"
    r"(?!\d)"
)


PAN_PATTERN = re.compile(
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    re.IGNORECASE
)


DOB_PATTERN = re.compile(
    r"\b(?:"
    r"(?:0?[1-9]|[12][0-9]|3[01])"
    r"[\/.-]"
    r"(?:0?[1-9]|1[0-2])"
    r"[\/.-]"
    r"(?:19|20)\d{2}"
    r"|"
    r"(?:19|20)\d{2}"
    r"[\/.-]"
    r"(?:0?[1-9]|1[0-2])"
    r"[\/.-]"
    r"(?:0?[1-9]|[12][0-9]|3[01])"
    r")\b"
)


# ============================================================
# PROJECT PII TYPES
# ============================================================

ALLOWED_LABELS = {
    "PERSON",
    "LOCATION",
    "PHONE",
    "EMAIL",
    "AADHAAR",
    "PAN",
    "DOB"
}


# ============================================================
# COMMON INDIAN LOCATIONS
# ============================================================

INDIAN_LOCATIONS = {
    "bangalore",
    "bengaluru",
    "mangalore",
    "mysore",
    "mysuru",
    "udupi",
    "hubli",
    "dharwad",
    "belgaum",
    "shimoga",
    "tumkur",
    "hassan",

    "chennai",
    "madurai",
    "coimbatore",
    "salem",
    "erode",
    "tirunelveli",
    "vellore",
    "trichy",

    "kochi",
    "kozhikode",
    "thrissur",
    "kollam",
    "kannur",
    "palakkad",

    "hyderabad",
    "warangal",
    "karimnagar",

    "mumbai",
    "pune",
    "nagpur",
    "nashik",

    "delhi",
    "new delhi",
    "noida",
    "gurgaon",
    "faridabad",

    "ahmedabad",
    "surat",
    "rajkot",
    "vadodara",

    "jaipur",
    "jodhpur",
    "udaipur",

    "lucknow",
    "kanpur",
    "agra",
    "varanasi",

    "goa",
    "panaji",

    "kolkata",
    "patna",
    "bhubaneswar",
    "ranchi",
    "indore",
    "bhopal"
}


# ============================================================
# TECHNICAL TERMS
# ============================================================

NON_PERSON_TERMS = {
    "java",
    "python",
    "javascript",
    "typescript",
    "react",
    "angular",
    "node",
    "nodejs",
    "spring",
    "springboot",
    "full",
    "stack",
    "development",
    "developer",
    "developers",
    "software",
    "engineering",
    "computer",
    "science",
    "technology",
    "database",
    "databases",
    "sql",
    "html",
    "css",
    "api",
    "backend",
    "frontend",
    "programming",
    "coding",
    "machine",
    "learning",
    "artificial",
    "intelligence",
    "cloud",
    "devops",
    "github",
    "git",
    "android",
    "mobile",
    "application",
    "applications"
}


# ============================================================
# LOAD TRANSFORMER LABEL MAPPING
# ============================================================

def load_label_mapping(model_dir):

    mapping_file = model_dir / "label_mapping.json"

    if not mapping_file.exists():
        raise FileNotFoundError(
            f"Label mapping not found:\n{mapping_file}"
        )

    with open(
        mapping_file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    id_to_label = {}

    if "id2label" in data:

        for key, value in data["id2label"].items():

            id_to_label[int(key)] = str(value)

    elif "label_names" in data:

        for index, label in enumerate(
            data["label_names"]
        ):

            id_to_label[index] = str(label)

    else:

        for key, value in data.items():

            try:

                id_to_label[int(key)] = str(value)

            except (
                ValueError,
                TypeError
            ):

                pass

    if not id_to_label:

        raise ValueError(
            f"Unable to read label mapping:\n{mapping_file}"
        )

    return id_to_label


# ============================================================
# TRANSFORMER MODEL
# ============================================================

class TransformerPIIModel:

    def __init__(
        self,
        model_dir,
        model_name
    ):

        self.model_dir = Path(model_dir)
        self.model_name = model_name

        print(
            f"\nLoading {model_name}..."
        )

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                self.model_dir,
                use_fast=True
            )
        )

        self.model = (
            AutoModelForTokenClassification.from_pretrained(
                self.model_dir
            )
        )

        self.model.to(DEVICE)
        self.model.eval()

        self.id_to_label = (
            load_label_mapping(
                self.model_dir
            )
        )

        print(
            f"{model_name} loaded successfully."
        )

    # ========================================================
    # PREDICT
    # ========================================================

    def predict(self, text):

        if not isinstance(text, str):
            return []

        if not text.strip():
            return []

        encoded = self.tokenizer(
            text,
            return_offsets_mapping=True,
            return_overflowing_tokens=True,
            truncation=True,
            max_length=128,
            stride=32,
            padding=False
        )

        all_entities = []

        input_ids = encoded["input_ids"]
        attention_masks = encoded["attention_mask"]
        offsets = encoded["offset_mapping"]

        for chunk_index in range(
            len(input_ids)
        ):

            input_tensor = torch.tensor(
                [input_ids[chunk_index]],
                dtype=torch.long,
                device=DEVICE
            )

            attention_tensor = torch.tensor(
                [attention_masks[chunk_index]],
                dtype=torch.long,
                device=DEVICE
            )

            with torch.no_grad():

                outputs = self.model(
                    input_ids=input_tensor,
                    attention_mask=attention_tensor
                )

            probabilities = torch.softmax(
                outputs.logits,
                dim=-1
            )[0]

            predicted_ids = torch.argmax(
                probabilities,
                dim=-1
            ).cpu().numpy()

            confidence_values = torch.max(
                probabilities,
                dim=-1
            ).values.cpu().numpy()

            token_predictions = []

            for token_index, label_id in enumerate(
                predicted_ids
            ):

                start, end = offsets[
                    chunk_index
                ][token_index]

                # Ignore special tokens
                if start == end:
                    continue

                label = self.id_to_label.get(
                    int(label_id),
                    "O"
                )

                confidence = float(
                    confidence_values[
                        token_index
                    ]
                )

                token_predictions.append(
                    (
                        int(start),
                        int(end),
                        label,
                        confidence
                    )
                )

            entities = (
                self._bio_to_entities(
                    token_predictions,
                    text
                )
            )

            all_entities.extend(
                entities
            )

        return self._deduplicate(
            all_entities
        )

    # ========================================================
    # BIO -> ENTITY SPANS
    # ========================================================

    @staticmethod
    def _bio_to_entities(
        predictions,
        text
    ):

        entities = []

        current_start = None
        current_end = None
        current_label = None
        current_scores = []

        def close_entity():

            nonlocal current_start
            nonlocal current_end
            nonlocal current_label
            nonlocal current_scores

            if (
                current_start is not None
                and current_end is not None
                and current_label is not None
            ):

                confidence = (
                    sum(current_scores)
                    / len(current_scores)
                    if current_scores
                    else 0.0
                )

                entities.append(
                    {
                        "start": current_start,
                        "end": current_end,
                        "label": current_label,
                        "text": text[
                            current_start:current_end
                        ],
                        "confidence": confidence,
                        "source": "Transformer"
                    }
                )

            current_start = None
            current_end = None
            current_label = None
            current_scores = []

        for (
            start,
            end,
            bio_label,
            confidence
        ) in predictions:

            if bio_label == "O":

                close_entity()
                continue

            if "-" in bio_label:

                prefix, entity_type = (
                    bio_label.split(
                        "-",
                        1
                    )
                )

            else:

                prefix = "B"
                entity_type = bio_label

            if (
                prefix == "B"
                or current_label != entity_type
            ):

                close_entity()

                current_start = start
                current_end = end
                current_label = entity_type
                current_scores = [
                    confidence
                ]

            else:

                current_end = max(
                    current_end,
                    end
                )

                current_scores.append(
                    confidence
                )

        close_entity()

        return entities

    # ========================================================
    # DEDUPLICATE
    # ========================================================

    @staticmethod
    def _deduplicate(entities):

        unique = {}

        for entity in entities:

            key = (
                entity["start"],
                entity["end"],
                entity["label"]
            )

            if key not in unique:

                unique[key] = entity

            else:

                if (
                    entity["confidence"]
                    >
                    unique[key]["confidence"]
                ):

                    unique[key] = entity

        return list(
            unique.values()
        )


# ============================================================
# LOAD MODELS
# ============================================================

print("\nLoading BERT model...")

bert_model = TransformerPIIModel(
    BERT_MODEL_DIR,
    "BERT"
)


print("\nLoading RoBERTa model...")

roberta_model = TransformerPIIModel(
    ROBERTA_MODEL_DIR,
    "RoBERTa"
)


print("\nLoading spaCy model...")

spacy_model = spacy.load(
    str(SPACY_MODEL_DIR)
)

print(
    "spaCy model loaded successfully."
)

print("\nAll PII models loaded.")


# ============================================================
# FAST LOCATION DETECTION
# ============================================================

def location_detect(text):

    """
    Detect known locations using the dedicated
    location detector.

    Uses the fast known-location dictionary only.
    Does NOT load the large GeoNames database.
    """

    entities = []

    locations = detect_known_locations(
        text
    )

    for location in locations:

        entities.append(
            {
                "start": location["start"],
                "end": location["end"],
                "label": "LOCATION",
                "text": location["text"],
                "confidence": location["confidence"],
                "source": "LocationDetector"
            }
        )

    return entities


# ============================================================
# REGEX DETECTION
# ============================================================

def regex_detect(text):

    """
    Detect structured PII using deterministic
    regular expressions.
    """

    entities = []

    patterns = [
        (PHONE_PATTERN, "PHONE"),
        (EMAIL_PATTERN, "EMAIL"),
        (AADHAAR_PATTERN, "AADHAAR"),
        (PAN_PATTERN, "PAN"),
        (DOB_PATTERN, "DOB"),
    ]

    for pattern, label in patterns:

        for match in pattern.finditer(text):

            entities.append(
                {
                    "start": match.start(),
                    "end": match.end(),
                    "label": label,
                    "text": match.group(),
                    "confidence": 1.0,
                    "source": "Regex"
                }
            )

    return entities


# ============================================================
# SPACY DETECTION
# ============================================================

def spacy_detect(text):

    """
    Keep only PERSON and LOCATION from spaCy NER.
    """

    doc = spacy_model(text)

    entities = []

    for ent in doc.ents:

        value = ent.text.strip()

        if not value:
            continue

        label = ent.label_

        # ----------------------------------------------------
        # PERSON
        # ----------------------------------------------------

        if label == "PERSON":

            words = value.lower().split()

            if any(
                word in NON_PERSON_TERMS
                for word in words
            ):
                continue

            entities.append(
                {
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "label": "PERSON",
                    "text": value,
                    "confidence": 0.90,
                    "source": "spaCy"
                }
            )

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        elif label in {
            "GPE",
            "LOC",
            "LOCATION"
        }:

            entities.append(
                {
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "label": "LOCATION",
                    "text": value,
                    "confidence": 0.90,
                    "source": "spaCy"
                }
            )

    return entities


# ============================================================
# OVERLAP CALCULATION
# ============================================================

def overlap_ratio(a, b):

    start = max(
        a["start"],
        b["start"]
    )

    end = min(
        a["end"],
        b["end"]
    )

    overlap = max(
        0,
        end - start
    )

    if overlap == 0:
        return 0.0

    shorter = min(
        a["end"] - a["start"],
        b["end"] - b["start"]
    )

    if shorter <= 0:
        return 0.0

    return overlap / shorter


# ============================================================
# HYBRID FUSION
# ============================================================

def hybrid_merge(
    text,
    bert_entities,
    roberta_entities,
    spacy_entities,
    regex_entities,
    location_entities
):

    all_entities = []

    # ========================================================
    # REGEX
    # ========================================================

    for entity in regex_entities:

        entity = dict(entity)
        entity["votes"] = 1

        if entity["label"] in ALLOWED_LABELS:

            all_entities.append(
                entity
            )

    # ========================================================
    # BERT
    # ========================================================

    for entity in bert_entities:

        entity = dict(entity)
        entity["votes"] = 1

        if entity["label"] in ALLOWED_LABELS:

            all_entities.append(
                entity
            )

    # ========================================================
    # ROBERTA
    # ========================================================

    for entity in roberta_entities:

        entity = dict(entity)
        entity["votes"] = 1

        if entity["label"] in ALLOWED_LABELS:

            all_entities.append(
                entity
            )

    # ========================================================
    # SPACY
    # ========================================================

    for entity in spacy_entities:

        entity = dict(entity)
        entity["votes"] = 1

        if entity["label"] in ALLOWED_LABELS:

            all_entities.append(
                entity
            )

    # ========================================================
    # LOCATION DETECTOR
    # ========================================================

    for entity in location_entities:

        entity = dict(entity)
        entity["votes"] = 1

        if entity["label"] in ALLOWED_LABELS:

            all_entities.append(
                entity
            )

    if not all_entities:
        return []

    # ========================================================
    # CLUSTER OVERLAPPING ENTITIES
    # ========================================================

    clusters = []

    for entity in all_entities:

        placed = False

        for cluster in clusters:

            representative = cluster[0]

            if (
                overlap_ratio(
                    entity,
                    representative
                ) >= 0.50
            ):

                cluster.append(
                    entity
                )

                placed = True
                break

        if not placed:

            clusters.append(
                [entity]
            )

    # ========================================================
    # SELECT BEST ENTITY FROM EACH CLUSTER
    # ========================================================

    final_entities = []

    for cluster in clusters:

        label_votes = {}

        for entity in cluster:

            label = entity["label"]

            label_votes.setdefault(
                label,
                []
            )

            label_votes[label].append(
                entity
            )

        # ----------------------------------------------------
        # Find strongest label
        # ----------------------------------------------------

        best_label = None
        best_score = -1.0

        for label, members in label_votes.items():

            score = 0.0

            for member in members:

                source = member["source"]

                confidence = (
                    member["confidence"]
                    if member["confidence"] is not None
                    else 0.90
                )

                # ------------------------------------------------
                # Source weighting
                # ------------------------------------------------

                if source == "Regex":

                    weight = 1.20

                elif source == "BERT":

                    weight = 1.00

                elif source == "RoBERTa":

                    weight = 1.00

                elif source == "LocationDetector":

                    weight = 0.90

                else:

                    weight = 0.85

                score += (
                    weight * confidence
                )

            # ------------------------------------------------
            # Agreement bonus
            # ------------------------------------------------

            if len(members) >= 2:

                score += 0.25

            if len(members) >= 3:

                score += 0.25

            if score > best_score:

                best_score = score
                best_label = label

        members = label_votes[
            best_label
        ]

        # ====================================================
        # FINAL SPAN
        # ====================================================

        final_start = min(
            entity["start"]
            for entity in members
        )

        final_end = max(
            entity["end"]
            for entity in members
        )

        # ====================================================
        # CONFIDENCE
        # ====================================================

        confidences = []

        for member in members:

            confidence = (
                member["confidence"]
                if member["confidence"] is not None
                else 0.90
            )

            confidences.append(
                confidence
            )

        final_confidence = (
            sum(confidences)
            / len(confidences)
        )

        # ====================================================
        # MODELS
        # ====================================================

        models = sorted(
            set(
                entity["source"]
                for entity in members
            )
        )

        # ====================================================
        # FINAL ENTITY
        # ====================================================

        final_entities.append(
            {
                "start": final_start,
                "end": final_end,
                "label": best_label,

                "text": text[
                    final_start:final_end
                ],

                "confidence": round(
                    final_confidence,
                    4
                ),

                "source": "Hybrid",

                "models": models
            }
        )

    # ========================================================
    # FINAL CONFLICT RESOLUTION
    # ========================================================

    final_entities.sort(
        key=lambda x: (
            x["start"],
            x["end"]
        )
    )

    cleaned = []

    for entity in final_entities:

        conflict = False

        for previous in cleaned:

            if (
                overlap_ratio(
                    entity,
                    previous
                ) >= 0.50
            ):

                conflict = True

                # --------------------------------------------
                # Keep stronger prediction
                # --------------------------------------------

                if (
                    entity["confidence"]
                    >
                    previous["confidence"]
                ):

                    cleaned.remove(
                        previous
                    )

                    cleaned.append(
                        entity
                    )

                break

        if not conflict:

            cleaned.append(
                entity
            )

    cleaned.sort(
        key=lambda x: (
            x["start"],
            x["end"]
        )
    )

    return cleaned


# ============================================================
# CONVERT HYBRID ENTITIES TO API FORMAT
# ============================================================

def format_result(
    text,
    entities
):

    result = {

        "phones": [],
        "emails": [],
        "aadhaars": [],
        "pans": [],
        "dobs": [],
        "persons": [],
        "locations": [],

        "entities": []
    }

    for entity in entities:

        value = entity["text"]
        label = entity["label"]

        result["entities"].append(
            {
                "text": value,
                "label": label,
                "start": entity["start"],
                "end": entity["end"],
                "confidence": entity["confidence"],
                "source": entity["source"],
                "models": entity.get(
                    "models",
                    []
                )
            }
        )

        if label == "PHONE":

            result["phones"].append(
                value
            )

        elif label == "EMAIL":

            result["emails"].append(
                value
            )

        elif label == "AADHAAR":

            result["aadhaars"].append(
                value
            )

        elif label == "PAN":

            result["pans"].append(
                value
            )

        elif label in {
            "DOB",
            "DATE"
        }:

            result["dobs"].append(
                value
            )

        elif label == "PERSON":

            result["persons"].append(
                value
            )

        elif label in {
            "LOCATION",
            "ADDRESS"
        }:

            result["locations"].append(
                value
            )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    for key in result:

        if key != "entities":

            result[key] = list(
                dict.fromkeys(
                    result[key]
                )
            )

    return result


# ============================================================
# EMPTY RESULT
# ============================================================

def empty_result():

    return {
        "phones": [],
        "emails": [],
        "aadhaars": [],
        "pans": [],
        "dobs": [],
        "persons": [],
        "locations": [],
        "entities": []
    }


# ============================================================
# MAIN DETECTION FUNCTION
# ============================================================

def detect_pii(text):

    if not isinstance(
        text,
        str
    ):

        return empty_result()

    if not text.strip():

        return empty_result()

    print(
        "\n=============================="
    )

    print(
        "FINAL HYBRID PII DETECTION"
    )

    print(
        "=============================="
    )

    # ========================================================
    # 1. REGEX
    # ========================================================

    regex_entities = regex_detect(
        text
    )

    # ========================================================
    # 2. BERT
    # ========================================================

    bert_entities = (
        bert_model.predict(
            text
        )
    )

    for entity in bert_entities:

        entity["source"] = "BERT"

    # ========================================================
    # 3. RoBERTa
    # ========================================================

    roberta_entities = (
        roberta_model.predict(
            text
        )
    )

    for entity in roberta_entities:

        entity["source"] = "RoBERTa"

    # ========================================================
    # 4. spaCy
    # ========================================================

    spacy_entities = (
        spacy_detect(
            text
        )
    )

    # ========================================================
    # 5. LOCATION DETECTOR
    # ========================================================

    location_entities = (
        location_detect(
            text
        )
    )

    # ========================================================
    # 6. HYBRID FUSION
    # ========================================================

    # IMPORTANT:
    # location_entities MUST be passed here because
    # hybrid_merge() expects it.

    final_entities = hybrid_merge(

        text,

        bert_entities,

        roberta_entities,

        spacy_entities,

        regex_entities,

        location_entities
    )

    # ========================================================
    # 7. FINAL FORMAT
    # ========================================================

    result = format_result(
        text,
        final_entities
    )

    print(
        "Detected entities:",
        len(
            result["entities"]
        )
    )

    for entity in result["entities"]:

        print(
            f"{entity['text']} "
            f"-> {entity['label']} "
            f"({entity['confidence']:.2f}) "
            f"[{', '.join(entity['models'])}]"
        )

    print(
        "==============================\n"
    )

    return result


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":

    test_cases = [

        (
            "My name is Mahimashree and "
            "I live in Mangalore."
        ),

        (
            "Contact me at "
            "mahima@gmail.com or "
            "9876543210."
        ),

        (
            "My Aadhaar is "
            "1234 5678 9012 and "
            "PAN is ABCDE1234F."
        ),

        (
            "I am learning Java Full Stack "
            "development."
        ),

        (
            "My IP address is "
            "192.168.1.10."
        )
    ]

    for text in test_cases:

        print("\n")

        print(
            "=" * 70
        )

        print("TEXT:")

        print(text)

        print(
            "=" * 70
        )

        output = detect_pii(
            text
        )

        print(
            "\nFINAL OUTPUT:"
        )

        print(
            json.dumps(
                output,
                indent=2,
                ensure_ascii=False
            )
        )
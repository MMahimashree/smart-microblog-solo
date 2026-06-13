# ============================================
# pii_detector.py
# PURPOSE: Detect Personal Identifiable Information (PII)
# from user's post text using two methods:
# 1. Regex → finds structured patterns (phone, email)
# 2. spaCy → finds unstructured data (names, locations)
# ============================================

import re  # Built-in Python library for pattern matching using regular expressions
import spacy  # NLP library — used to detect names, locations from text

# Load spaCy's small English model
# This model is pre-trained on English text and can identify
# real world entities like person names, cities, organisations
nlp = spacy.load('en_core_web_sm')

# Phone pattern explanation:
# \b = word boundary (makes sure we don't match part of a longer number)
# [6-9] = first digit must be 6,7,8 or 9 (all Indian numbers start this way)
# \d{9} = followed by exactly 9 more digits
# Total = 10 digit Indian mobile number
PHONE_PATTERN = re.compile(r'\b[6-9]\d{9}\b')

# Email pattern explanation:
# [A-Za-z0-9._%+-]+ = one or more letters, numbers, dots, underscores
# @ = the @ symbol
# [A-Za-z0-9.-]+ = domain name like gmail, yahoo
# \. = a dot
# [A-Za-z]{2,} = extension like com, in, org (minimum 2 letters)
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

# Manual list of common Indian cities
# Because en_core_web_sm is a small model, it sometimes
# misclassifies Indian city names as PERSON
# So we maintain a manual list as backup
INDIAN_CITIES = [
    'bangalore', 'bengaluru', 'mumbai', 'delhi', 'chennai',
    'hyderabad', 'pune', 'kolkata', 'ahmedabad', 'jaipur',
    'mysore', 'mangalore', 'hubli', 'dharwad', 'udupi',
    'kochi', 'coimbatore', 'surat', 'lucknow', 'nagpur'
]


# ── MAIN FUNCTION ────────────────────────────────────────────
# This function takes the user's post text as input
# and returns a dictionary of all PII found
def detect_pii(text):

    # Initialize empty lists for each type of PII
    # We will fill these as we find matches
    result = {
        'emails': [],     # will store detected email addresses
        'phones': [],     # will store detected phone numbers
        'persons': [],    # will store detected person names (via spaCy)
        'locations': []   # will store detected locations (via spaCy)
    }

    # ── STEP 1: REGEX DETECTION ──────────────────────────────
    # findall() searches the entire text and returns ALL matches as a list

    # Find all phone numbers in the text
    phones = PHONE_PATTERN.findall(text)
    result['phones'] = phones  # store found phones in result

    # Find all email addresses in the text
    emails = EMAIL_PATTERN.findall(text)
    result['emails'] = emails  # store found emails in result

    # ── STEP 2: spaCy NER DETECTION ──────────────────────────
    # NER = Named Entity Recognition
    # spaCy reads the text and identifies real world entities
    # doc = processed version of the text with all entities tagged
    doc = nlp(text)

    # Loop through all entities spaCy found
    for ent in doc.ents:
        # ent.text = the actual word found (e.g. "Mahima", "Bangalore")
        # ent.label_ = the category spaCy assigned (PERSON, GPE, LOC etc.)

        # Check if spaCy tagged it as PERSON
        # but it is actually an Indian city name
        if ent.label_ == 'PERSON' and ent.text.lower() in INDIAN_CITIES:
            # Move it to locations instead of persons
            result['locations'].append(ent.text)

        elif ent.label_ == 'PERSON':
            # PERSON = a real person's name
            result['persons'].append(ent.text)

        elif ent.label_ in ['GPE', 'LOC']:
            # GPE = Geopolitical Entity (countries, cities, states)
            # LOC = Location (mountains, rivers, areas)
            result['locations'].append(ent.text)

    # ── IMPORTANT ────────────────────────────────────────────
    # return the final result dictionary back to whoever called this function
    # Without this line the function returns None (which was your bug!)
    return result


# ── QUICK TEST ───────────────────────────────────────────────
# This block only runs when you directly run this file
# It will NOT run when imported from main.py
if __name__ == '__main__':
    test_text = "Hi I am Mahima, call me at 9876543210 or email mahima@gmail.com, I live in Bangalore"
    print("Testing PII Detector...")
    print("Input:", test_text)
    print("Output:", detect_pii(test_text))
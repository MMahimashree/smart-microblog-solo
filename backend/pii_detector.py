import re
import spacy

nlp = spacy.load("en_core_web_sm")

# ---------------- REGEX PATTERNS ---------------- #

PHONE_PATTERN = re.compile(
    r'\b(?:\+91[- ]?)?[6-9]\d{9}\b'
)

EMAIL_PATTERN = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
)

AADHAAR_PATTERN = re.compile(
    r'\b\d{4}\s?\d{4}\s?\d{4}\b'
)

PAN_PATTERN = re.compile(
    r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
    re.IGNORECASE
)

DOB_PATTERN = re.compile(
    r'\b(?:0?[1-9]|[12][0-9]|3[01])[\/.-](?:0?[1-9]|1[0-2])[\/.-](?:19|20)\d{2}\b'
)

# ---------------- INDIAN LOCATIONS ---------------- #

INDIAN_LOCATIONS = [

    # Karnataka
    "bangalore","bengaluru","mangalore","mysore","udupi","hubli",
    "dharwad","belgaum","shimoga","bellary","tumkur","hassan",

    # Tamil Nadu
    "chennai","madurai","coimbatore","salem","erode",
    "tirunelveli","vellore","trichy","thoothukudi",

    # Kerala
    "kochi","kozhikode","thrissur","kollam","kannur","palakkad",

    # Andhra Pradesh
    "visakhapatnam","vijayawada","tirupati","guntur",

    # Telangana
    "hyderabad","warangal","karimnagar","nizamabad",

    # Maharashtra
    "mumbai","pune","nagpur","nashik",

    # Delhi NCR
    "delhi","new delhi","noida","gurgaon","faridabad",

    # Gujarat
    "ahmedabad","surat","rajkot","vadodara",

    # Rajasthan
    "jaipur","jodhpur","udaipur",

    # Uttar Pradesh
    "lucknow","kanpur","agra","varanasi",

    # Goa
    "goa","panaji",

    # Others
    "kolkata","patna","bhubaneswar","ranchi","indore","bhopal"
]
KNOWN_NAMES = [
    "mahima",
    "mahimashree",
    "kavana",
    "kamakshi",
    "manyashree",
    "manya",
    "nivedha",
    "saritha",
    "sneha",
    "priyanka",
    "nandita",
    "ananya",
    "aravind",  
    "madhumitha",
    "siddharth",
    "kavya",
    "rahul",
    "rohit",
    "priya",
    "anjali",
    "akash",
    "arjun",
    "kiran",
    "deepak",
    "pooja",
    "sneha",
    "vikram",
    "ajay",
    "vijay",
    "suresh",
    "ramesh",
    "apoorva",
    "koushik"
]

def detect_pii(text):

    result = {
        "phones": [],
        "emails": [],
        "aadhaars": [],
        "pans": [],
        "dobs": [],
        "persons": [],
        "locations": []
    }

    # ---------- REGEX ----------

    result["phones"] = list(set(PHONE_PATTERN.findall(text)))
    result["emails"] = list(set(EMAIL_PATTERN.findall(text)))
    result["aadhaars"] = list(set(AADHAAR_PATTERN.findall(text)))
    result["pans"] = list(set(PAN_PATTERN.findall(text)))

    result["dobs"] = [
        m.group(0)
        for m in DOB_PATTERN.finditer(text)
    ]

    # ---------- SPACY ----------

    doc = nlp(text)

    print("\n========== SPACY ==========")

    for ent in doc.ents:
        print(ent.text, "---->", ent.label_)

    print("===========================\n")

    for ent in doc.ents:

        value = ent.text.strip()

        if ent.label_ == "PERSON":

            if value.lower() in INDIAN_LOCATIONS:
                result["locations"].append(value.title())
            else:
                result["persons"].append(value)

        elif ent.label_ in ["GPE", "LOC"]:

            result["locations"].append(value.title())

    # ---------- Manual Indian Location Detection ----------

    lower = text.lower()

    for city in INDIAN_LOCATIONS:
        if city in lower:
            result["locations"].append(city.title())

    # Manual person detection

    for name in KNOWN_NAMES:
        if name in lower:
             result["persons"].append(name.title())

    # ---------- Remove Duplicates ----------

    result["persons"] = list(set(result["persons"]))
    result["locations"] = list(set(result["locations"]))

    return result


if __name__ == "__main__":

    sample = """
    My name is Mahimashree.
    DOB: 23/12/2005
    Phone: 9876543210
    Email: mahima@gmail.com
    Aadhaar: 1234 5678 9012
    PAN: ABCDE1234F
    I live in Mangalore.
    """

    print(detect_pii(sample))
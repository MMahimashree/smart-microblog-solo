from datasets import load_dataset
from pathlib import Path
import json
import random
from collections import Counter

# ============================================================
# CONFIGURATION
# ============================================================

AI4PRIVACY_TRAIN = Path("ml/data/processed/train.json")

MASKARA_DATASET = "somukandula/maskara-indian-pii-200k"

OUTPUT_DIR = Path("ml/data/combined")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MASKARA_TRAIN_SIZE = 50000

SEED = 42
random.seed(SEED)


# ============================================================
# AI4PRIVACY LABEL MAPPING
# ============================================================
AI4PRIVACY_MAP = {

    # Person
    "PERSON": "PERSON",
    "FIRSTNAME": "PERSON",
    "LASTNAME": "PERSON",
    "MIDDLENAME": "PERSON",

    # Contact
    "PHONE": "PHONE",
    "PHONENUMBER": "PHONE",
    "PHONEIMEI": "DEVICE_ID",
    "EMAIL": "EMAIL",

    # Address / location
    "ADDRESS": "ADDRESS",
    "STREET": "ADDRESS",
    "BUILDINGNUMBER": "ADDRESS",
    "SECONDARYADDRESS": "ADDRESS",

    "LOCATION": "LOCATION",
    "CITY": "LOCATION",
    "STATE": "LOCATION",
    "COUNTY": "LOCATION",

    # Dates
    "DOB": "DOB",
    "DATE": "DATE",

    # Demographic
    "AGE": "AGE",
    "GENDER": "GENDER",
    "SEX": "SEX",

    # Network / device
    "IP_ADDRESS": "IP_ADDRESS",
    "IP": "IP_ADDRESS",
    "IPV4": "IP_ADDRESS",
    "IPV6": "IP_ADDRESS",

    "MAC_ADDRESS": "MAC_ADDRESS",
    "MAC": "MAC_ADDRESS",

    "DEVICE_ID": "DEVICE_ID",
    "USER_AGENT": "USER_AGENT",

    # Financial
    "CREDIT_CARD": "CREDIT_CARD",
    "CREDITCARDNUMBER": "CREDIT_CARD",
    "CREDITCARDCVV": "CREDIT_CARD",

    "BANK_ACCOUNT": "BANK_ACCOUNT",
    "ACCOUNT": "ACCOUNT",
    "ACCOUNTNUMBER": "BANK_ACCOUNT",
    "ACCOUNTNAME": "ACCOUNT",

    "IBAN": "IBAN",
    "BIC": "BIC",

    # Authentication
    "USERNAME": "USERNAME",
    "PASSWORD": "PASSWORD",
    "PIN": "PIN",

    # Identity
    "SSN": "SSN",

    # Web
    "URL": "URL",

    # Vehicle
    "VEHICLE_ID": "VEHICLE_REG",
    "VEHICLEVIN": "VEHICLE_REG",
    "VEHICLEVRM": "VEHICLE_REG",

    # Crypto
    "CRYPTO_ADDRESS": "CRYPTO_ADDRESS",
    "BITCOINADDRESS": "CRYPTO_ADDRESS",
    "ETHEREUMADDRESS": "CRYPTO_ADDRESS",
    "LITECOINADDRESS": "CRYPTO_ADDRESS",

    # Employment
    "JOBAREA": "JOB_AREA",
    "JOBTITLE": "JOB_TITLE",
    "JOBTYPE": "JOB_TYPE",

    # Organization
    "COMPANYNAME": "COMPANY",

    # Other
    "AMOUNT": "AMOUNT",
    "CURRENCY": "CURRENCY",
    "CURRENCYCODE": "CURRENCY",
    "CURRENCYNAME": "CURRENCY",
    "CURRENCYSYMBOL": "CURRENCY",
}

# ============================================================
# MASKARA LABEL MAPPING
# ============================================================

MASKARA_MAP = {

    "PERSON_NAME": "PERSON",

    "PHONE": "PHONE",

    "EMAIL": "EMAIL",

    "ADDRESS": "ADDRESS",

    "DATE_OF_BIRTH": "DOB",

    "IP_ADDRESS": "IP_ADDRESS",

    "CREDIT_CARD": "CREDIT_CARD",

    "USERNAME": "USERNAME",

    "PASSWORD": "PASSWORD",

    "SSN": "SSN",

    "PASSPORT": "PASSPORT",

    "DRIVER_LICENSE": "DRIVER_LICENSE",

    "VEHICLE_REG": "VEHICLE_REG",

    # Indian PII
    "AADHAAR": "AADHAAR",

    "PAN_CARD": "PAN",

    "UPI_ID": "UPI_ID",

    "API_KEY": "API_KEY",
}


# ============================================================
# LOAD EXISTING AI4PRIVACY TRAINING DATA
# ============================================================

print("=" * 70)
print("PREPARING CORRECTED COMBINED DATASET")
print("=" * 70)

print("\nLoading existing AI4Privacy training data...")

with open(
    AI4PRIVACY_TRAIN,
    "r",
    encoding="utf-8"
) as f:

    ai4privacy = json.load(f)

print("AI4Privacy training examples:", len(ai4privacy))


# ============================================================
# CONVERT AI4PRIVACY
# ============================================================

converted_ai4privacy = []

skipped_ai4privacy = 0

for item in ai4privacy:

    text = item["text"]

    entities = []

    for entity in item["entities"]:

        old_label = entity["label"]

        if old_label not in AI4PRIVACY_MAP:

            skipped_ai4privacy += 1
            continue

        new_label = AI4PRIVACY_MAP[old_label]

        entities.append({
            "start": entity["start"],
            "end": entity["end"],
            "label": new_label
        })

    converted_ai4privacy.append({
        "text": text,
        "entities": entities,
        "source": "AI4Privacy"
    })


print(
    "AI4Privacy entities skipped:",
    skipped_ai4privacy
)


# ============================================================
# LOAD MASKARA
# ============================================================

print("\nLoading Maskara...")

maskara = load_dataset(
    MASKARA_DATASET,
    split="train"
)

print(
    "Maskara total examples:",
    len(maskara)
)


# ============================================================
# SELECT MASKARA SUBSET
# ============================================================

indices = list(range(len(maskara)))

random.shuffle(indices)

indices = indices[:MASKARA_TRAIN_SIZE]

print(
    "Maskara selected examples:",
    len(indices)
)


# ============================================================
# CONVERT MASKARA
# ============================================================

converted_maskara = []

skipped_maskara = 0

for index in indices:

    item = maskara[index]

    text = item["text"]

    entities = []

    for entity in item["entities"]:

        old_label = entity["label"]

        if old_label not in MASKARA_MAP:

            skipped_maskara += 1
            continue

        new_label = MASKARA_MAP[old_label]

        entities.append({
            "start": entity["start"],
            "end": entity["end"],
            "label": new_label
        })

    converted_maskara.append({
        "text": text,
        "entities": entities,
        "source": "Maskara"
    })


print(
    "Maskara entities skipped:",
    skipped_maskara
)


# ============================================================
# COMBINE
# ============================================================

combined = (
    converted_ai4privacy +
    converted_maskara
)

random.shuffle(combined)


# ============================================================
# REMOVE DUPLICATE TEXTS
# ============================================================

unique = {}

for item in combined:

    unique[item["text"]] = item

combined = list(unique.values())

print("\nUnique combined examples:", len(combined))


# ============================================================
# ENTITY DISTRIBUTION
# ============================================================

label_counts = Counter()

for item in combined:

    for entity in item["entities"]:

        label_counts[entity["label"]] += 1


print("\n" + "=" * 70)
print("COMBINED ENTITY DISTRIBUTION")
print("=" * 70)

for label, count in label_counts.most_common():

    print(
        f"{label:<25} {count:>8}"
    )


# ============================================================
# SPLIT
# ============================================================

total = len(combined)

train_end = int(total * 0.80)

validation_end = int(total * 0.90)

train_data = combined[:train_end]

validation_data = combined[
    train_end:validation_end
]

test_data = combined[
    validation_end:
]


# ============================================================
# SAVE
# ============================================================

def save_json(data, filename):

    path = OUTPUT_DIR / filename

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"Saved {len(data)} examples -> {path}"
    )


save_json(
    train_data,
    "train.json"
)

save_json(
    validation_data,
    "validation.json"
)

save_json(
    test_data,
    "test.json"
)


# ============================================================
# SAVE MAPPING
# ============================================================

mapping = {

    "AI4PRIVACY": AI4PRIVACY_MAP,

    "MASKARA": MASKARA_MAP
}

with open(
    OUTPUT_DIR / "label_mapping.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        mapping,
        f,
        indent=4
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CORRECTED COMBINED DATASET COMPLETE")
print("=" * 70)

print(
    "AI4Privacy:",
    len(converted_ai4privacy)
)

print(
    "Maskara:",
    len(converted_maskara)
)

print(
    "Combined:",
    len(combined)
)

print(
    "Training:",
    len(train_data)
)

print(
    "Validation:",
    len(validation_data)
)

print(
    "Testing:",
    len(test_data)
)

print("\nOutput directory:")
print(OUTPUT_DIR)
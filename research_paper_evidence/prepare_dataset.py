from datasets import load_dataset
import json
import random
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

random.seed(SEED)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD DATASET
# ============================================================

print("Loading AI4Privacy dataset...")

dataset = load_dataset(
    "ai4privacy/pii-masking-200k",
    data_files=["english_pii_43k.jsonl"]
)

data = dataset["train"]

print("Total examples:", len(data))

# ============================================================
# LABEL MAPPING
# ============================================================

LABEL_MAP = {

    # PERSON
    "FIRSTNAME": "PERSON",
    "LASTNAME": "PERSON",
    "MIDDLENAME": "PERSON",

    # LOCATION
    "CITY": "LOCATION",
    "STATE": "LOCATION",
    "COUNTY": "LOCATION",

    # ADDRESS
    "STREET": "ADDRESS",
    "BUILDINGNUMBER": "ADDRESS",
    "SECONDARYADDRESS": "ADDRESS",
    "ZIPCODE": "ADDRESS",

    # CONTACT
    "EMAIL": "EMAIL",
    "PHONENUMBER": "PHONE",

    # DATE / PERSONAL
    "DOB": "DOB",
    "DATE": "DATE",
    "AGE": "AGE",

    # ACCOUNT / AUTHENTICATION
    "USERNAME": "USERNAME",
    "PASSWORD": "PASSWORD",
    "ACCOUNTNUMBER": "ACCOUNT",
    "ACCOUNTNAME": "ACCOUNT",
    "PIN": "PIN",

    # FINANCIAL
    "CREDITCARDNUMBER": "CREDIT_CARD",
    "CREDITCARDCVV": "CREDIT_CARD",
    "CREDITCARDISSUER": "CREDIT_CARD",
    "IBAN": "BANK_ACCOUNT",

    # NETWORK / DEVICE
    "IP": "IP_ADDRESS",
    "IPV4": "IP_ADDRESS",
    "IPV6": "IP_ADDRESS",
    "MAC": "MAC_ADDRESS",
    "PHONEIMEI": "DEVICE_ID",

    # OTHER IDENTIFIERS
    "SSN": "SSN",
    "VEHICLEVIN": "VEHICLE_ID",
    "VEHICLEVRM": "VEHICLE_ID",

    # CRYPTO
    "BITCOINADDRESS": "CRYPTO_ADDRESS",
    "ETHEREUMADDRESS": "CRYPTO_ADDRESS",
    "LITECOINADDRESS": "CRYPTO_ADDRESS",

    # ONLINE
    "URL": "URL",
    "USERAGENT": "USER_AGENT"
}

# ============================================================
# CONVERT DATA
# ============================================================

processed = []

for row in data:

    text = row["source_text"]

    entities = []

    for item in row["privacy_mask"]:

        original_label = item["label"]

        if original_label not in LABEL_MAP:
            continue

        new_label = LABEL_MAP[original_label]

        entities.append({
            "start": item["start"],
            "end": item["end"],
            "label": new_label
        })

    processed.append({
        "text": text,
        "entities": entities
    })

# ============================================================
# SHUFFLE
# ============================================================

random.shuffle(processed)

total = len(processed)

train_end = int(total * TRAIN_RATIO)
val_end = train_end + int(total * VAL_RATIO)

train_data = processed[:train_end]
val_data = processed[train_end:val_end]
test_data = processed[val_end:]

# ============================================================
# SAVE
# ============================================================

def save_json(filename, data):

    path = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved {len(data)} examples → {path}")


save_json("train.json", train_data)
save_json("validation.json", val_data)
save_json("test.json", test_data)

# ============================================================
# SUMMARY
# ============================================================

print("\n==========================================")
print("DATASET PREPARATION COMPLETE")
print("==========================================")

print("Total:", total)
print("Training:", len(train_data))
print("Validation:", len(val_data))
print("Testing:", len(test_data))

print("\nOutput files:")
print("train.json")
print("validation.json")
print("test.json")
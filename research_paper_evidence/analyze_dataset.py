from datasets import load_dataset
from collections import Counter
import pandas as pd
import ast

print("=" * 70)
print("AI4Privacy PII DATASET ANALYSIS")
print("=" * 70)

# Load dataset
dataset = load_dataset(
    "ai4privacy/pii-masking-200k",
    data_files=["english_pii_43k.jsonl"]
)

data = dataset["train"]

print("\nTotal examples:", len(data))

# ============================================================
# 1. DATASET SPLIT INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("DATASET SPLITS")
print("=" * 70)

split_counts = Counter(data["set"])

for split, count in split_counts.items():
    print(f"{split}: {count}")

# ============================================================
# 2. PII LABEL DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("PII LABEL DISTRIBUTION")
print("=" * 70)

label_counter = Counter()

for row in data:
    for item in row["privacy_mask"]:
        label_counter[item["label"]] += 1

for label, count in label_counter.most_common():
    print(f"{label:30} {count}")

# ============================================================
# 3. NUMBER OF UNIQUE LABELS
# ============================================================

print("\n" + "=" * 70)
print("LABEL SUMMARY")
print("=" * 70)

print("Number of unique PII labels:", len(label_counter))

print("\nLabels:")

for label in sorted(label_counter):
    print("-", label)

# ============================================================
# 4. EXAMPLES PER LABEL
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE ANNOTATIONS")
print("=" * 70)

shown = set()

for row in data:

    for item in row["privacy_mask"]:

        label = item["label"]

        if label not in shown:

            print("\nLABEL:", label)
            print("VALUE:", item["value"])
            print("TEXT :", row["source_text"])

            shown.add(label)

        if len(shown) == len(label_counter):
            break

    if len(shown) == len(label_counter):
        break

# ============================================================
# 5. SAVE LABEL COUNTS
# ============================================================

df = pd.DataFrame(
    label_counter.items(),
    columns=["label", "count"]
)

df = df.sort_values(
    "count",
    ascending=False
)

df.to_csv(
    "label_distribution.csv",
    index=False
)

print("\n" + "=" * 70)
print("Analysis completed.")
print("Saved: ml/data/label_distribution.csv")
print("=" * 70)
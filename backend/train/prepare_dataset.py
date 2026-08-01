"""
FinSight AI — Dataset Preparation
Downloads Financial PhraseBank, cleans, and creates train/val/test splits.
"""

import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.config import (
    DATA_DIR,
    RAW_DATA_PATH,
    TRAIN_DATA_PATH,
    VAL_DATA_PATH,
    TEST_DATA_PATH,
    TRAIN_RATIO,
    VAL_RATIO,
    LABEL_TO_ID,
)
from app.ml.preprocessing import clean_text


def download_dataset():
    """Download Financial PhraseBank from HuggingFace."""
    print("[*] Downloading Financial PhraseBank dataset...")

    try:
        from datasets import load_dataset

        # Load the 'sentences_allagree' subset (highest agreement)
        dataset = load_dataset(
            "financial_phrasebank",
            "sentences_allagree",
            trust_remote_code=True,
        )

        # Convert to DataFrame
        df = pd.DataFrame(dataset["train"])
        df.columns = ["text", "label"]

        print(f"[+] Downloaded {len(df)} samples")
        return df

    except Exception as e:
        print(f"[!] HuggingFace download failed: {e}")
        print("[*] Attempting alternative download...")

        # Fallback: try sentences_75agree if allagree is too small
        try:
            dataset = load_dataset(
                "financial_phrasebank",
                "sentences_75agree",
                trust_remote_code=True,
            )
            df = pd.DataFrame(dataset["train"])
            df.columns = ["text", "label"]
            print(f"[+] Downloaded {len(df)} samples (75% agreement)")
            return df
        except Exception as e2:
            print(f"[!] Alternative download also failed: {e2}")
            raise RuntimeError("Could not download Financial PhraseBank dataset.")


def process_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and process the dataset."""
    print("[*] Processing dataset...")

    # Map label integers: HF dataset uses 0=negative, 1=neutral, 2=positive
    # This already matches our LABEL_TO_ID mapping
    print(f"    Label distribution (raw):")
    print(f"    {df['label'].value_counts().to_dict()}")

    # Remove duplicates
    initial_len = len(df)
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)
    print(f"    Removed {initial_len - len(df)} duplicates")

    # Clean text
    df["clean_text"] = df["text"].apply(clean_text)

    # Remove empty after cleaning
    df = df[df["clean_text"].str.len() > 10].reset_index(drop=True)

    print(f"[+] Processed dataset: {len(df)} samples")
    print(f"    Label distribution (final):")
    for label_name, label_id in LABEL_TO_ID.items():
        count = (df["label"] == label_id).sum()
        print(f"    {label_name}: {count} ({count/len(df)*100:.1f}%)")

    return df


def split_dataset(df: pd.DataFrame):
    """Stratified train/val/test split."""
    print("[*] Splitting dataset...")

    # First split: train+val vs test
    train_val_df, test_df = train_test_split(
        df,
        test_size=1 - TRAIN_RATIO,
        random_state=42,
        stratify=df["label"],
    )

    # Second split: train vs val (from the remaining)
    val_relative_size = VAL_RATIO / (VAL_RATIO + (1 - TRAIN_RATIO - VAL_RATIO + VAL_RATIO))
    # Simpler: we want val to be half of the remaining 20%
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=0.5,  # split remaining 20% into 10% val + 10% test equivalent
        random_state=42,
        stratify=train_val_df["label"],
    )

    # Actually let's redo this properly
    # Total = 100%, Train = 80%, Val = 10%, Test = 10%
    train_df, temp_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["label"]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, random_state=42, stratify=temp_df["label"]
    )

    print(f"[+] Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

    return train_df, val_df, test_df


def main():
    """Full dataset preparation pipeline."""
    print("=" * 60)
    print("  FinSight AI — Dataset Preparation")
    print("=" * 60)

    os.makedirs(DATA_DIR, exist_ok=True)

    # Download
    df = download_dataset()

    # Process
    df = process_dataset(df)

    # Save raw processed
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"[+] Saved processed dataset to {RAW_DATA_PATH}")

    # Split
    train_df, val_df, test_df = split_dataset(df)

    # Save splits
    train_df.to_csv(TRAIN_DATA_PATH, index=False)
    val_df.to_csv(VAL_DATA_PATH, index=False)
    test_df.to_csv(TEST_DATA_PATH, index=False)

    print(f"[+] Saved train to {TRAIN_DATA_PATH}")
    print(f"[+] Saved val to {VAL_DATA_PATH}")
    print(f"[+] Saved test to {TEST_DATA_PATH}")

    print("\n[✓] Dataset preparation complete!")


if __name__ == "__main__":
    main()

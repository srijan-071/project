"""
FinSight AI — Model Evaluation
Runs trained model on test set, computes detailed metrics and confusion matrix.
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.config import (
    DEVICE,
    MAX_SEQ_LEN,
    BATCH_SIZE,
    NUM_CLASSES,
    LABEL_MAP,
    MODEL_WEIGHTS_PATH,
    TOKENIZER_PATH,
    TEST_DATA_PATH,
    EVALUATION_METRICS_PATH,
)
from app.ml.transformer import FinSightTransformer
from app.ml.tokenizer import FinSightTokenizer


class EvalDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoded = self.tokenizer.encode(str(self.texts[idx]), max_len=self.max_len)
        return {
            "input_ids": torch.tensor(encoded["input_ids"], dtype=torch.long),
            "attention_mask": torch.tensor(encoded["attention_mask"], dtype=torch.long),
            "label": torch.tensor(int(self.labels[idx]), dtype=torch.long),
        }


def main():
    print("=" * 60)
    print("  FinSight AI — Model Evaluation")
    print("=" * 60)

    # ─── Load Tokenizer ──────────────────────────────────
    tokenizer = FinSightTokenizer()
    tokenizer.load(TOKENIZER_PATH)
    print(f"[+] Loaded tokenizer (vocab: {tokenizer.actual_vocab_size})")

    # ─── Load Model ──────────────────────────────────────
    checkpoint = torch.load(MODEL_WEIGHTS_PATH, map_location=DEVICE, weights_only=False)

    model = FinSightTransformer(
        vocab_size=checkpoint["vocab_size"],
        embed_dim=checkpoint["embed_dim"],
        num_heads=checkpoint["num_heads"],
        num_layers=checkpoint["num_layers"],
        ff_dim=checkpoint["ff_dim"],
        max_len=checkpoint["max_len"],
        num_classes=checkpoint["num_classes"],
        dropout=checkpoint.get("dropout", 0.2),
    ).to(DEVICE)

    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    print(f"[+] Loaded model (params: {model.count_parameters():,})")

    # ─── Load Test Data ──────────────────────────────────
    test_df = pd.read_csv(TEST_DATA_PATH)
    test_texts = test_df["clean_text"].fillna(test_df["text"]).tolist()
    test_labels = test_df["label"].tolist()
    print(f"[+] Test set: {len(test_df)} samples")

    test_dataset = EvalDataset(test_texts, test_labels, tokenizer, MAX_SEQ_LEN)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # ─── Run Evaluation ──────────────────────────────────
    print("[*] Evaluating...")
    all_preds = []
    all_labels = []
    all_probs = []
    inference_times = []

    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["label"].to(DEVICE)

            t0 = time.time()
            logits, _ = model(input_ids, attention_mask)
            inference_times.append(time.time() - t0)

            probs = torch.softmax(logits, dim=1)
            preds = torch.argmax(logits, dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)

    # ─── Compute Metrics ─────────────────────────────────
    label_names = [LABEL_MAP[i] for i in range(NUM_CLASSES)]

    accuracy = accuracy_score(all_labels, all_preds)
    precision_macro = precision_score(all_labels, all_preds, average="macro")
    recall_macro = recall_score(all_labels, all_preds, average="macro")
    f1_macro = f1_score(all_labels, all_preds, average="macro")
    f1_weighted = f1_score(all_labels, all_preds, average="weighted")

    precision_per_class = precision_score(all_labels, all_preds, average=None)
    recall_per_class = recall_score(all_labels, all_preds, average=None)
    f1_per_class = f1_score(all_labels, all_preds, average=None)

    cm = confusion_matrix(all_labels, all_preds)

    # Inference stats
    total_inference_time = sum(inference_times)
    avg_inference_per_sample = total_inference_time / len(test_labels) * 1000  # ms

    # Model size
    model_size_bytes = os.path.getsize(MODEL_WEIGHTS_PATH)
    model_size_mb = model_size_bytes / (1024 * 1024)

    # ─── Print Results ───────────────────────────────────
    print(f"\n{'─' * 40}")
    print(f"  Accuracy:         {accuracy:.4f}")
    print(f"  Precision (macro): {precision_macro:.4f}")
    print(f"  Recall (macro):    {recall_macro:.4f}")
    print(f"  F1 Score (macro):  {f1_macro:.4f}")
    print(f"  F1 Score (weighted): {f1_weighted:.4f}")
    print(f"{'─' * 40}")

    print(f"\n  Per-Class Performance:")
    for i, name in enumerate(label_names):
        print(
            f"    {name:>10}: P={precision_per_class[i]:.4f} "
            f"R={recall_per_class[i]:.4f} F1={f1_per_class[i]:.4f}"
        )

    print(f"\n  Confusion Matrix:")
    print(f"    {cm}")

    print(f"\n  Inference: {avg_inference_per_sample:.2f} ms/sample")
    print(f"  Model Size: {model_size_mb:.2f} MB")

    # ─── Save Results ────────────────────────────────────
    evaluation = {
        "overall": {
            "accuracy": round(accuracy, 4),
            "precision_macro": round(precision_macro, 4),
            "recall_macro": round(recall_macro, 4),
            "f1_macro": round(f1_macro, 4),
            "f1_weighted": round(f1_weighted, 4),
        },
        "per_class": {
            name: {
                "precision": round(float(precision_per_class[i]), 4),
                "recall": round(float(recall_per_class[i]), 4),
                "f1": round(float(f1_per_class[i]), 4),
                "support": int((all_labels == i).sum()),
            }
            for i, name in enumerate(label_names)
        },
        "confusion_matrix": cm.tolist(),
        "confusion_matrix_labels": label_names,
        "inference": {
            "avg_ms_per_sample": round(avg_inference_per_sample, 2),
            "total_time_seconds": round(total_inference_time, 2),
            "test_samples": len(test_labels),
        },
        "model": {
            "parameters": model.count_parameters(),
            "size_mb": round(model_size_mb, 2),
            "architecture": model.get_architecture_info(),
        },
    }

    with open(EVALUATION_METRICS_PATH, "w") as f:
        json.dump(evaluation, f, indent=2)

    print(f"\n[+] Evaluation saved to {EVALUATION_METRICS_PATH}")
    print("[✓] Evaluation complete!")


if __name__ == "__main__":
    main()

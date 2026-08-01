"""
FinSight AI — Baseline Model Training
Trains LSTM and TF-IDF + Logistic Regression baselines for Model Comparison Lab.
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.config import (
    DEVICE,
    MAX_SEQ_LEN,
    EMBED_DIM,
    NUM_CLASSES,
    BATCH_SIZE,
    TRAIN_DATA_PATH,
    VAL_DATA_PATH,
    TEST_DATA_PATH,
    TOKENIZER_PATH,
    BASELINE_METRICS_PATH,
)
from app.ml.tokenizer import FinSightTokenizer


# ─── LSTM Baseline ────────────────────────────────────────

class LSTMClassifier(nn.Module):
    """Simple 2-layer LSTM baseline."""

    def __init__(self, vocab_size, embed_dim=64, hidden_dim=64, num_classes=3, dropout=0.3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim, num_layers=2,
            batch_first=True, dropout=dropout, bidirectional=True
        )
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_dim * 2, num_classes),
        )

    def forward(self, input_ids, attention_mask=None):
        x = self.embedding(input_ids)
        output, (hidden, _) = self.lstm(x)
        # Concatenate last hidden states from both directions
        hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        logits = self.classifier(hidden)
        return logits

    def count_parameters(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class SimpleDataset(Dataset):
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


def train_lstm_baseline(train_texts, train_labels, val_texts, val_labels, test_texts, test_labels, tokenizer):
    """Train LSTM baseline and return metrics."""
    print("\n[*] Training LSTM Baseline...")

    vocab_size = tokenizer.actual_vocab_size
    model = LSTMClassifier(vocab_size, embed_dim=64, hidden_dim=64, num_classes=NUM_CLASSES).to(DEVICE)

    train_dataset = SimpleDataset(train_texts, train_labels, tokenizer, MAX_SEQ_LEN)
    test_dataset = SimpleDataset(test_texts, test_labels, tokenizer, MAX_SEQ_LEN)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Train for 15 epochs
    start_time = time.time()
    for epoch in range(15):
        model.train()
        for batch in train_loader:
            input_ids = batch["input_ids"].to(DEVICE)
            labels = batch["label"].to(DEVICE)
            optimizer.zero_grad()
            logits = model(input_ids)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

    train_time = time.time() - start_time

    # Evaluate on test set
    model.eval()
    all_preds = []
    all_labels_list = []
    inference_times = []

    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(DEVICE)
            labels = batch["label"].to(DEVICE)

            t0 = time.time()
            logits = model(input_ids)
            inference_times.append(time.time() - t0)

            preds = torch.argmax(logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels_list.extend(labels.cpu().numpy())

    accuracy = accuracy_score(all_labels_list, all_preds)
    f1 = f1_score(all_labels_list, all_preds, average="weighted")
    precision = precision_score(all_labels_list, all_preds, average="weighted")
    recall = recall_score(all_labels_list, all_preds, average="weighted")

    # Model size
    param_count = model.count_parameters()
    model_size_mb = param_count * 4 / (1024 * 1024)  # float32

    avg_inference_ms = np.mean(inference_times) * 1000 / BATCH_SIZE

    print(f"    LSTM Accuracy: {accuracy:.4f}, F1: {f1:.4f}")

    return {
        "model_name": "LSTM Baseline",
        "architecture": "2-Layer Bidirectional LSTM",
        "accuracy": round(accuracy, 4),
        "f1_score": round(f1, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "parameters": param_count,
        "model_size_mb": round(model_size_mb, 2),
        "avg_inference_ms": round(avg_inference_ms, 2),
        "training_time_seconds": round(train_time, 2),
    }


def train_tfidf_baseline(train_texts, train_labels, test_texts, test_labels):
    """Train TF-IDF + Logistic Regression baseline."""
    print("\n[*] Training TF-IDF + Logistic Regression Baseline...")

    start_time = time.time()

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=2)
    X_train = vectorizer.fit_transform(train_texts)
    X_test = vectorizer.transform(test_texts)

    # Logistic Regression
    clf = LogisticRegression(max_iter=1000, C=1.0, class_weight="balanced", random_state=42)
    clf.fit(X_train, train_labels)

    train_time = time.time() - start_time

    # Evaluate
    t0 = time.time()
    preds = clf.predict(X_test)
    inference_time = time.time() - t0

    accuracy = accuracy_score(test_labels, preds)
    f1 = f1_score(test_labels, preds, average="weighted")
    precision = precision_score(test_labels, preds, average="weighted")
    recall = recall_score(test_labels, preds, average="weighted")

    avg_inference_ms = inference_time * 1000 / len(test_labels)

    print(f"    TF-IDF+LR Accuracy: {accuracy:.4f}, F1: {f1:.4f}")

    return {
        "model_name": "TF-IDF + Logistic Regression",
        "architecture": "TF-IDF (10K features, bigrams) + Logistic Regression",
        "accuracy": round(accuracy, 4),
        "f1_score": round(f1, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "parameters": X_train.shape[1] * NUM_CLASSES,
        "model_size_mb": round(X_train.shape[1] * NUM_CLASSES * 8 / (1024 * 1024), 2),
        "avg_inference_ms": round(avg_inference_ms, 4),
        "training_time_seconds": round(train_time, 2),
    }


def main():
    print("=" * 60)
    print("  FinSight AI — Baseline Training")
    print("=" * 60)

    # Load data
    train_df = pd.read_csv(TRAIN_DATA_PATH)
    val_df = pd.read_csv(VAL_DATA_PATH)
    test_df = pd.read_csv(TEST_DATA_PATH)

    train_texts = train_df["clean_text"].fillna(train_df["text"]).tolist()
    val_texts = val_df["clean_text"].fillna(val_df["text"]).tolist()
    test_texts = test_df["clean_text"].fillna(test_df["text"]).tolist()
    train_labels = train_df["label"].tolist()
    val_labels = val_df["label"].tolist()
    test_labels = test_df["label"].tolist()

    # Load tokenizer
    tokenizer = FinSightTokenizer()
    tokenizer.load(TOKENIZER_PATH)

    results = {}

    # Train LSTM
    results["lstm"] = train_lstm_baseline(
        train_texts, train_labels, val_texts, val_labels, test_texts, test_labels, tokenizer
    )

    # Train TF-IDF + LR
    results["tfidf_lr"] = train_tfidf_baseline(train_texts, train_labels, test_texts, test_labels)

    # FinBERT reference (published benchmarks, not trained here)
    results["finbert_reference"] = {
        "model_name": "FinBERT (Reference)",
        "architecture": "Pre-trained BERT fine-tuned on financial text",
        "accuracy": 0.87,
        "f1_score": 0.87,
        "precision": 0.87,
        "recall": 0.87,
        "parameters": 110_000_000,
        "model_size_mb": 418.0,
        "avg_inference_ms": 45.0,
        "training_time_seconds": None,
        "note": "Published benchmark values. Not trained in this project.",
    }

    # Save
    with open(BASELINE_METRICS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[+] Baseline metrics saved to {BASELINE_METRICS_PATH}")
    print("[✓] Baseline training complete!")


if __name__ == "__main__":
    main()

"""
FinSight AI — Model Training Script
Trains the custom Transformer on Financial PhraseBank with full metric tracking.
"""

import os
import sys
import json
import time
import math
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, f1_score

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.config import (
    DEVICE,
    VOCAB_SIZE,
    MAX_SEQ_LEN,
    EMBED_DIM,
    NUM_HEADS,
    NUM_LAYERS,
    FF_DIM,
    DROPOUT,
    NUM_CLASSES,
    BATCH_SIZE,
    LEARNING_RATE,
    WEIGHT_DECAY,
    NUM_EPOCHS,
    WARMUP_EPOCHS,
    PATIENCE,
    TRAIN_DATA_PATH,
    VAL_DATA_PATH,
    MODEL_WEIGHTS_PATH,
    TOKENIZER_PATH,
    TRAINING_METRICS_PATH,
    MODELS_DIR,
)
from app.ml.transformer import FinSightTransformer
from app.ml.tokenizer import FinSightTokenizer
from app.ml.preprocessing import clean_text


class FinancialDataset(Dataset):
    """PyTorch Dataset for financial sentiment data."""

    def __init__(self, texts, labels, tokenizer, max_len=256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])

        encoded = self.tokenizer.encode(text, max_len=self.max_len)

        return {
            "input_ids": torch.tensor(encoded["input_ids"], dtype=torch.long),
            "attention_mask": torch.tensor(encoded["attention_mask"], dtype=torch.long),
            "label": torch.tensor(label, dtype=torch.long),
        }


def get_cosine_schedule_with_warmup(optimizer, warmup_steps, total_steps):
    """Cosine annealing LR schedule with linear warmup."""

    def lr_lambda(current_step):
        if current_step < warmup_steps:
            return float(current_step) / float(max(1, warmup_steps))
        progress = float(current_step - warmup_steps) / float(
            max(1, total_steps - warmup_steps)
        )
        return max(0.0, 0.5 * (1.0 + math.cos(math.pi * progress)))

    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)


def train_one_epoch(model, dataloader, optimizer, scheduler, criterion, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    all_preds = []
    all_labels = []

    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["label"].to(device)

        optimizer.zero_grad()
        logits, _ = model(input_ids, attention_mask)
        loss = criterion(logits, labels)

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()

        total_loss += loss.item()
        preds = torch.argmax(logits, dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average="weighted")

    return avg_loss, accuracy, f1


def evaluate(model, dataloader, criterion, device):
    """Evaluate model on validation set."""
    model.eval()
    total_loss = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)

            logits, _ = model(input_ids, attention_mask)
            loss = criterion(logits, labels)

            total_loss += loss.item()
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average="weighted")

    return avg_loss, accuracy, f1


def main():
    """Full training pipeline."""
    print("=" * 60)
    print("  FinSight AI — Transformer Training")
    print("=" * 60)
    print(f"  Device: {DEVICE}")
    print()

    # ─── Load Data ────────────────────────────────────────
    print("[*] Loading datasets...")
    train_df = pd.read_csv(TRAIN_DATA_PATH)
    val_df = pd.read_csv(VAL_DATA_PATH)
    print(f"    Train: {len(train_df)}, Val: {len(val_df)}")

    # Use clean_text column if available, else raw text
    train_texts = (
        train_df["clean_text"].fillna(train_df["text"]).tolist()
    )
    val_texts = (
        val_df["clean_text"].fillna(val_df["text"]).tolist()
    )
    train_labels = train_df["label"].tolist()
    val_labels = val_df["label"].tolist()

    # ─── Build Tokenizer ─────────────────────────────────
    print("[*] Building tokenizer...")
    tokenizer = FinSightTokenizer(vocab_size=VOCAB_SIZE, max_len=MAX_SEQ_LEN)
    tokenizer.build_vocab(train_texts)
    tokenizer.save(TOKENIZER_PATH)
    actual_vocab = tokenizer.actual_vocab_size
    print(f"    Vocabulary size: {actual_vocab}")
    print(f"    Saved tokenizer to {TOKENIZER_PATH}")

    # ─── Create Datasets ─────────────────────────────────
    train_dataset = FinancialDataset(train_texts, train_labels, tokenizer, MAX_SEQ_LEN)
    val_dataset = FinancialDataset(val_texts, val_labels, tokenizer, MAX_SEQ_LEN)

    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0
    )
    val_loader = DataLoader(
        val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0
    )

    # ─── Build Model ─────────────────────────────────────
    print("[*] Building model...")
    model = FinSightTransformer(
        vocab_size=actual_vocab,
        embed_dim=EMBED_DIM,
        num_heads=NUM_HEADS,
        num_layers=NUM_LAYERS,
        ff_dim=FF_DIM,
        max_len=MAX_SEQ_LEN,
        num_classes=NUM_CLASSES,
        dropout=DROPOUT,
    ).to(DEVICE)

    total_params = model.count_parameters()
    print(f"    Total parameters: {total_params:,}")

    # ─── Setup Training ──────────────────────────────────
    # Compute class weights for imbalanced data
    class_counts = np.bincount(train_labels, minlength=NUM_CLASSES).astype(float)
    class_weights = 1.0 / (class_counts + 1e-6)
    class_weights = class_weights / class_weights.sum() * NUM_CLASSES
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32).to(DEVICE)

    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY
    )

    total_steps = len(train_loader) * NUM_EPOCHS
    warmup_steps = len(train_loader) * WARMUP_EPOCHS
    scheduler = get_cosine_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    # ─── Training Loop ───────────────────────────────────
    print("[*] Starting training...")
    print(f"    Epochs: {NUM_EPOCHS}, Batch size: {BATCH_SIZE}")
    print(f"    LR: {LEARNING_RATE}, Warmup epochs: {WARMUP_EPOCHS}")
    print()

    best_val_f1 = 0.0
    patience_counter = 0
    training_history = {
        "train_loss": [],
        "val_loss": [],
        "train_acc": [],
        "val_acc": [],
        "train_f1": [],
        "val_f1": [],
        "learning_rates": [],
        "epoch_times": [],
    }

    training_start = time.time()

    for epoch in range(NUM_EPOCHS):
        epoch_start = time.time()

        # Train
        train_loss, train_acc, train_f1 = train_one_epoch(
            model, train_loader, optimizer, scheduler, criterion, DEVICE
        )

        # Validate
        val_loss, val_acc, val_f1 = evaluate(model, val_loader, criterion, DEVICE)

        epoch_time = time.time() - epoch_start
        current_lr = scheduler.get_last_lr()[0]

        # Record metrics
        training_history["train_loss"].append(round(train_loss, 4))
        training_history["val_loss"].append(round(val_loss, 4))
        training_history["train_acc"].append(round(train_acc, 4))
        training_history["val_acc"].append(round(val_acc, 4))
        training_history["train_f1"].append(round(train_f1, 4))
        training_history["val_f1"].append(round(val_f1, 4))
        training_history["learning_rates"].append(round(current_lr, 6))
        training_history["epoch_times"].append(round(epoch_time, 2))

        # Print progress
        print(
            f"  Epoch {epoch+1:02d}/{NUM_EPOCHS} | "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} F1: {val_f1:.4f} | "
            f"LR: {current_lr:.6f} | {epoch_time:.1f}s"
        )

        # Save best model
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            patience_counter = 0
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "vocab_size": actual_vocab,
                    "embed_dim": EMBED_DIM,
                    "num_heads": NUM_HEADS,
                    "num_layers": NUM_LAYERS,
                    "ff_dim": FF_DIM,
                    "max_len": MAX_SEQ_LEN,
                    "num_classes": NUM_CLASSES,
                    "dropout": DROPOUT,
                    "epoch": epoch + 1,
                    "val_f1": val_f1,
                    "val_acc": val_acc,
                },
                MODEL_WEIGHTS_PATH,
            )
            print(f"  -> Best model saved (Val F1: {val_f1:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"\n[!] Early stopping at epoch {epoch+1} (no improvement for {PATIENCE} epochs)")
                break

    total_time = time.time() - training_start

    # ─── Save Training Metrics ───────────────────────────
    training_metrics = {
        "model_name": "FinSight Transformer v1",
        "total_parameters": total_params,
        "best_val_f1": round(best_val_f1, 4),
        "best_val_acc": round(max(training_history["val_acc"]), 4),
        "total_epochs_trained": len(training_history["train_loss"]),
        "total_training_time_seconds": round(total_time, 2),
        "hyperparameters": {
            "vocab_size": actual_vocab,
            "embed_dim": EMBED_DIM,
            "num_heads": NUM_HEADS,
            "num_layers": NUM_LAYERS,
            "ff_dim": FF_DIM,
            "max_seq_len": MAX_SEQ_LEN,
            "dropout": DROPOUT,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "warmup_epochs": WARMUP_EPOCHS,
        },
        "history": training_history,
        "device": str(DEVICE),
        "train_samples": len(train_df),
        "val_samples": len(val_df),
    }

    with open(TRAINING_METRICS_PATH, "w") as f:
        json.dump(training_metrics, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"  Training Complete!")
    print(f"  Best Val F1: {best_val_f1:.4f}")
    print(f"  Total Time: {total_time:.1f}s")
    print(f"  Model saved to: {MODEL_WEIGHTS_PATH}")
    print(f"  Metrics saved to: {TRAINING_METRICS_PATH}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

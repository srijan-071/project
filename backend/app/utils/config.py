"""
FinSight AI — Central Configuration
All model hyperparameters, paths, and settings.
"""

import os

# ─── Paths ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "app", "models")
DB_PATH = os.path.join(DATA_DIR, "finsight.db")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# ─── Model Hyperparameters ────────────────────────────────
VOCAB_SIZE = 15000
MAX_SEQ_LEN = 256
EMBED_DIM = 128
NUM_HEADS = 4
NUM_LAYERS = 3
FF_DIM = 256
DROPOUT = 0.2
NUM_CLASSES = 3

# Class labels
LABEL_MAP = {0: "negative", 1: "neutral", 2: "positive"}
LABEL_TO_ID = {"negative": 0, "neutral": 1, "positive": 2}

# ─── Training Hyperparameters ─────────────────────────────
BATCH_SIZE = 64
LEARNING_RATE = 3e-4
WEIGHT_DECAY = 1e-4
NUM_EPOCHS = 30
WARMUP_EPOCHS = 3
PATIENCE = 7  # early stopping patience

# Data splits
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

# ─── Device ───────────────────────────────────────────────
try:
    import torch
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
except Exception:
    DEVICE = "cpu"

# ─── File Paths ───────────────────────────────────────────
MODEL_WEIGHTS_PATH = os.path.join(MODELS_DIR, "transformer_weights.pt")
TOKENIZER_PATH = os.path.join(MODELS_DIR, "tokenizer.json")
TRAINING_METRICS_PATH = os.path.join(MODELS_DIR, "training_metrics.json")
EVALUATION_METRICS_PATH = os.path.join(MODELS_DIR, "evaluation_metrics.json")
BASELINE_METRICS_PATH = os.path.join(MODELS_DIR, "baseline_metrics.json")

# Dataset paths
RAW_DATA_PATH = os.path.join(DATA_DIR, "financial_phrasebank.csv")
TRAIN_DATA_PATH = os.path.join(DATA_DIR, "train.csv")
VAL_DATA_PATH = os.path.join(DATA_DIR, "val.csv")
TEST_DATA_PATH = os.path.join(DATA_DIR, "test.csv")

# ─── Model Metadata ──────────────────────────────────────
MODEL_NAME = "FinSight-TX"
MODEL_VERSION = "1.0"
MODEL_DESCRIPTION = "Custom Lightweight Transformer Encoder for Financial Sentiment Classification"

# ─── API Settings ─────────────────────────────────────────
MAX_INPUT_LENGTH = 5000  # characters
MAX_FILE_SIZE_MB = 1
ALLOWED_FILE_TYPES = [".txt", ".csv"]

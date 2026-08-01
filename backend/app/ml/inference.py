"""
FinSight AI — Model Inference Engine
Loads the trained model and provides prediction functions.
"""

import time
import torch
import torch.nn.functional as F
import numpy as np
from typing import Optional

from app.utils.config import (
    DEVICE,
    MODEL_WEIGHTS_PATH,
    TOKENIZER_PATH,
    LABEL_MAP,
    MAX_SEQ_LEN,
)
from app.ml.transformer import FinSightTransformer
from app.ml.tokenizer import FinSightTokenizer
from app.ml.preprocessing import clean_text, split_sentences


class InferenceEngine:
    """Manages model loading and prediction."""

    def __init__(self):
        self.model: Optional[FinSightTransformer] = None
        self.tokenizer: Optional[FinSightTokenizer] = None
        self.is_loaded = False

    def load(self):
        """Load model and tokenizer from saved files."""
        try:
            # Load tokenizer
            self.tokenizer = FinSightTokenizer()
            self.tokenizer.load(TOKENIZER_PATH)

            # Load model checkpoint
            checkpoint = torch.load(MODEL_WEIGHTS_PATH, map_location=DEVICE, weights_only=False)

            self.model = FinSightTransformer(
                vocab_size=checkpoint["vocab_size"],
                embed_dim=checkpoint["embed_dim"],
                num_heads=checkpoint["num_heads"],
                num_layers=checkpoint["num_layers"],
                ff_dim=checkpoint["ff_dim"],
                max_len=checkpoint["max_len"],
                num_classes=checkpoint["num_classes"],
                dropout=checkpoint.get("dropout", 0.2),
            ).to(DEVICE)

            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.model.eval()
            self.is_loaded = True

            print(f"[+] Model loaded: {self.model.count_parameters():,} parameters")
            return True

        except FileNotFoundError:
            print("[!] Model weights not found. Please train the model first.")
            self.is_loaded = False
            return False
        except Exception as e:
            print(f"[!] Failed to load model: {e}")
            self.is_loaded = False
            return False

    def predict(self, text: str) -> dict:
        """
        Run full prediction on a single text.
        Returns sentiment, confidence, probabilities, attention weights, tokens, and timing.
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        # Preprocess
        cleaned = clean_text(text)

        # Tokenize
        encoded = self.tokenizer.encode(cleaned, max_len=MAX_SEQ_LEN)

        input_ids = torch.tensor([encoded["input_ids"]], dtype=torch.long).to(DEVICE)
        attention_mask = torch.tensor([encoded["attention_mask"]], dtype=torch.long).to(DEVICE)

        # Inference
        start_time = time.time()
        with torch.no_grad():
            logits, attention_weights = self.model(input_ids, attention_mask)
        latency_ms = (time.time() - start_time) * 1000

        # Probabilities
        probs = F.softmax(logits, dim=1).cpu().numpy()[0]

        # Predicted class
        pred_class = int(np.argmax(probs))
        confidence = float(probs[pred_class])
        sentiment = LABEL_MAP[pred_class]

        # Sentiment score: -1 (negative) to +1 (positive)
        sentiment_score = float(probs[2] - probs[0])  # positive - negative

        # Token list (non-padding only)
        num_tokens = encoded["num_tokens"]
        tokens = encoded["tokens"][:num_tokens]

        # Process attention weights for all layers
        processed_attention = []
        for layer_idx, attn in enumerate(attention_weights):
            # attn: (1, heads, seq, seq) → (heads, seq, seq)
            attn_np = attn.cpu().numpy()[0]
            # Only keep non-padding region
            attn_trimmed = attn_np[:, :num_tokens, :num_tokens]
            processed_attention.append({
                "layer": layer_idx,
                "weights": attn_trimmed.tolist(),
                "shape": list(attn_trimmed.shape),
            })

        # Token importance from attention (average across heads and layers, CLS row)
        token_importance = self._compute_token_importance(attention_weights, num_tokens)

        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 4),
            "sentiment_score": round(sentiment_score, 4),
            "probabilities": {
                "positive": round(float(probs[2]), 4),
                "neutral": round(float(probs[1]), 4),
                "negative": round(float(probs[0]), 4),
            },
            "tokens": tokens,
            "num_tokens": num_tokens,
            "token_importance": token_importance,
            "attention_weights": processed_attention,
            "latency_ms": round(latency_ms, 2),
            "cleaned_text": cleaned,
        }

    def predict_batch(self, texts: list) -> list:
        """Predict on a batch of texts."""
        results = []
        for text in texts:
            try:
                result = self.predict(text)
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "sentiment": "error",
                    "confidence": 0.0,
                })
        return results

    def predict_sentences(self, text: str) -> list:
        """Predict sentiment for each sentence in the text."""
        sentences = split_sentences(text)
        results = []
        for i, sentence in enumerate(sentences):
            try:
                pred = self.predict(sentence)
                results.append({
                    "index": i,
                    "sentence": sentence,
                    "sentiment": pred["sentiment"],
                    "confidence": pred["confidence"],
                    "sentiment_score": pred["sentiment_score"],
                    "probabilities": pred["probabilities"],
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "sentence": sentence,
                    "sentiment": "error",
                    "confidence": 0.0,
                    "error": str(e),
                })
        return results

    def _compute_token_importance(self, attention_weights, num_tokens: int) -> list:
        """
        Compute per-token importance scores from attention weights.
        Uses average attention from CLS token across all heads and layers.
        """
        importance = np.zeros(num_tokens)

        for attn in attention_weights:
            # attn: (1, heads, seq, seq)
            attn_np = attn.cpu().numpy()[0]  # (heads, seq, seq)
            # Average across heads
            avg_attn = attn_np.mean(axis=0)  # (seq, seq)
            # CLS token attention to all other tokens
            cls_attn = avg_attn[0, :num_tokens]
            importance += cls_attn

        # Normalize across layers
        importance /= len(attention_weights)

        # Normalize to 0-1
        if importance.max() > 0:
            importance = importance / importance.max()

        return [round(float(v), 4) for v in importance]

    def get_model_info(self) -> dict:
        """Return model metadata."""
        if not self.is_loaded:
            return {"status": "not_loaded"}

        info = self.model.get_architecture_info()
        info["status"] = "online"
        info["device"] = str(DEVICE)
        info["tokenizer_vocab_size"] = self.tokenizer.actual_vocab_size
        return info


# Global inference engine instance
engine = InferenceEngine()

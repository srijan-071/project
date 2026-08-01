"""
FinSight AI — Model API Routes
Model info, training metrics, evaluation, architecture, and comparison data.
"""

import json
import os
from fastapi import APIRouter, HTTPException

from app.ml.inference import engine
from app.utils.config import (
    TRAINING_METRICS_PATH,
    EVALUATION_METRICS_PATH,
    BASELINE_METRICS_PATH,
    MODEL_NAME,
    MODEL_VERSION,
)

router = APIRouter(prefix="/api/model", tags=["model"])


@router.get("/info")
async def model_info():
    """Get model architecture metadata and status."""
    info = engine.get_model_info()
    info["model_name"] = MODEL_NAME
    info["model_version"] = MODEL_VERSION
    return info


@router.get("/metrics")
async def model_metrics():
    """Get training and evaluation metrics."""
    result = {}

    # Training metrics
    if os.path.exists(TRAINING_METRICS_PATH):
        with open(TRAINING_METRICS_PATH, "r") as f:
            result["training"] = json.load(f)
    else:
        result["training"] = None

    # Evaluation metrics
    if os.path.exists(EVALUATION_METRICS_PATH):
        with open(EVALUATION_METRICS_PATH, "r") as f:
            result["evaluation"] = json.load(f)
    else:
        result["evaluation"] = None

    return result


@router.get("/architecture")
async def model_architecture():
    """Get detailed architecture info for the Architecture Visualizer."""
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    return engine.get_model_info()


@router.get("/comparison")
async def model_comparison():
    """Get model comparison data (Transformer vs baselines)."""
    result = {"models": []}

    # Transformer metrics from evaluation
    if os.path.exists(EVALUATION_METRICS_PATH):
        with open(EVALUATION_METRICS_PATH, "r") as f:
            eval_data = json.load(f)
            result["models"].append({
                "model_name": "FinSight Transformer",
                "architecture": "Custom Transformer Encoder",
                "accuracy": eval_data["overall"]["accuracy"],
                "f1_score": eval_data["overall"]["f1_weighted"],
                "precision": eval_data["overall"]["precision_macro"],
                "recall": eval_data["overall"]["recall_macro"],
                "parameters": eval_data["model"]["parameters"],
                "model_size_mb": eval_data["model"]["size_mb"],
                "avg_inference_ms": eval_data["inference"]["avg_ms_per_sample"],
                "is_primary": True,
            })

    # Baseline metrics
    if os.path.exists(BASELINE_METRICS_PATH):
        with open(BASELINE_METRICS_PATH, "r") as f:
            baselines = json.load(f)
            for key, data in baselines.items():
                data["is_primary"] = False
                result["models"].append(data)

    return result

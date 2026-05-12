#!/usr/bin/env python3
"""
MLX vision server — FastAPI wrapper around mlx-vlm.

Runs on the M1 MacBook. The bot on the NAS POSTs base64-encoded images
to /analyze; this server feeds them through Phi-3.5-Vision (default)
and returns a schema-aligned JSON analysis.

Setup (M1, one-time)
--------------------
    python -m venv ~/.venv/aq-vision
    source ~/.venv/aq-vision/bin/activate
    pip install mlx-vlm fastapi uvicorn pillow

    # First run downloads the model (~2.5GB for Phi-3.5 4-bit)
    python mlx_vision_server.py

Run
---
    python mlx_vision_server.py
    # listens on :8000

Env
---
    AQ_MLX_MODEL    HuggingFace id (default: mlx-community/Phi-3.5-vision-instruct-4bit)
    AQ_MLX_PORT     default 8000
    AQ_MLX_HOST     default 0.0.0.0 (so NAS can reach it on the LAN)
    AQ_MLX_MAX_TOKENS  default 350
    AQ_MLX_TEMPERATURE default 0.1 (low — we want deterministic JSON)
"""

import base64
import io
import json
import logging
import os
import re
import time
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image

# Lazy MLX imports — keeps `python mlx_vision_server.py --help` fast and
# lets the smoke test stub these out.
try:
    from mlx_vlm import generate, load
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import load_config
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False

# --- Config ----------------------------------------------------------------

MODEL_ID = os.environ.get("AQ_MLX_MODEL", "mlx-community/Phi-3.5-vision-instruct-4bit")
PORT = int(os.environ.get("AQ_MLX_PORT", "8000"))
HOST = os.environ.get("AQ_MLX_HOST", "0.0.0.0")
MAX_TOKENS = int(os.environ.get("AQ_MLX_MAX_TOKENS", "350"))
TEMPERATURE = float(os.environ.get("AQ_MLX_TEMPERATURE", "0.1"))

# Constrain output to schema-valid values
CATEGORIES = [
    "burning", "trash", "vehicle", "construction",
    "industrial", "dust", "other", "none",
]
SEVERITIES = ["low", "medium", "high", "critical"]

logging.basicConfig(
    level=os.environ.get("AQ_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("mlx-vision")

# --- Model lifecycle -------------------------------------------------------

_state: Dict[str, Any] = {"model": None, "processor": None, "config": None}


def load_model() -> None:
    """Load the model into _state. Called once at startup."""
    if not MLX_AVAILABLE:
        raise RuntimeError(
            "mlx-vlm not installed. pip install mlx-vlm fastapi uvicorn pillow"
        )
    log.info("loading %s — this may take a minute on first run", MODEL_ID)
    t0 = time.time()
    model, processor = load(MODEL_ID)
    config = load_config(MODEL_ID)
    _state.update(model=model, processor=processor, config=config)
    log.info("model ready in %.1fs", time.time() - t0)


# --- Inference -------------------------------------------------------------

def _decode_image(image_b64: str) -> Image.Image:
    raw = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(raw))
    # Convert to RGB and resize big phone photos — Phi-3.5 handles
    # 1344x1344 well; bigger is just wasted compute.
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail((1344, 1344))
    return img


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Tolerate prose around the JSON object."""
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _coerce(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize whatever Phi-3.5 returned into our canonical shape."""
    category = str(raw.get("category", "other")).lower().strip()
    if category not in CATEGORIES:
        category = "other"
    severity = str(raw.get("severity", "low")).lower().strip()
    if severity not in SEVERITIES:
        severity = "low"
    try:
        confidence = float(raw.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    indicators = raw.get("indicators") or []
    if not isinstance(indicators, list):
        indicators = [str(indicators)]
    indicators = [str(x)[:120] for x in indicators][:8]

    detected = bool(raw.get("detected", category not in ("none", "other")))
    return {
        "detected": detected,
        "category": category,
        "confidence": round(confidence, 3),
        "indicators": indicators,
        "description": str(raw.get("description", ""))[:400],
        "severity": severity,
        "model_version": f"mlx:{MODEL_ID.split('/')[-1]}",
    }


def analyze(image_b64: str, prompt: str) -> Dict[str, Any]:
    if _state["model"] is None:
        raise RuntimeError("model not loaded")
    img = _decode_image(image_b64)
    formatted = apply_chat_template(
        _state["processor"], _state["config"], prompt, num_images=1
    )
    raw_text = generate(
        _state["model"],
        _state["processor"],
        formatted,
        image=[img],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        verbose=False,
    )
    # mlx-vlm return type varies by version:
    #   older  → str
    #   middle → (str, stats) tuple
    #   newer  → GenerationResult with .text attribute
    if isinstance(raw_text, tuple):
        raw_text = raw_text[0]
    if hasattr(raw_text, "text"):
        raw_text = raw_text.text
    elif hasattr(raw_text, "output_text"):
        raw_text = raw_text.output_text
    raw_text = str(raw_text)
    parsed = _extract_json(raw_text)
    if parsed is None:
        # Fall back to a needs-review result so the bot pipeline never breaks
        return {
            "detected": False,
            "category": "other",
            "confidence": 0.0,
            "indicators": [],
            "description": f"Model returned non-JSON: {raw_text[:300]}",
            "severity": "low",
            "model_version": f"mlx:{MODEL_ID.split('/')[-1]}:parse_error",
        }
    return _coerce(parsed)


# --- HTTP layer ------------------------------------------------------------

app = FastAPI(title="AQ Reporter — MLX vision server", version="0.1")


class AnalyzeRequest(BaseModel):
    image_b64: str
    prompt: str


@app.on_event("startup")
def _startup() -> None:
    load_model()


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "ok": _state["model"] is not None,
        "model": MODEL_ID,
        "mlx_available": MLX_AVAILABLE,
    }


# NOTE: must be `async def` so it runs on the main event-loop thread.
# MLX GPU streams are thread-local — the model is loaded on the startup
# thread, so inference must execute on that same thread. A plain `def`
# endpoint gets dispatched to FastAPI's worker thread pool, which
# triggers "There is no Stream(gpu, 1) in current thread."
@app.post("/analyze")
async def analyze_endpoint(req: AnalyzeRequest) -> Dict[str, Any]:
    if _state["model"] is None:
        raise HTTPException(status_code=503, detail="model still loading")
    try:
        # analyze() is sync and will block the event loop during inference.
        # That's fine — this server is single-tenant by design.
        return analyze(req.image_b64, req.prompt)
    except Exception as e:  # noqa: BLE001
        log.exception("inference failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")

"""
Vision analyzer — backend-agnostic pollution image classifier.

The bot only knows one function: analyze_pollution_image(image_path).
What's behind it is determined by the AQ_VISION_BACKEND env var, so we
can swap MLX, Ollama, Claude Haiku, or a mock without touching the bot.

Backends
--------
- mlx     (default) POST to a local FastAPI wrapper around mlx-vlm
                    running on the M1. Endpoint env: AQ_VISION_ENDPOINT
                    (default: http://localhost:8000/analyze)
- ollama  POST to Ollama running on the M1 (Moondream / Llava / Qwen2-VL).
          Endpoint env: AQ_OLLAMA_ENDPOINT (default: http://localhost:11434)
          Model env:    AQ_OLLAMA_MODEL    (default: moondream)
- haiku   Call Anthropic Claude Haiku vision (fallback when local is down).
          Requires ANTHROPIC_API_KEY.
- mock    Filename heuristics. Used for offline tests / CI.

All backends MUST return a dict matching the schema's ai_analysis shape:

    {
        "detected":     bool,
        "category":     str,    # see CATEGORIES below
        "confidence":   float,  # 0..1
        "indicators":   [str],
        "description":  str,
        "severity":     str,    # low | medium | high | critical
        "model_version": str,
    }

Failures never raise to the caller — they return a "needs_review" dict
so the bot can keep moving and a human can triage later.
"""

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests

# --- Configuration ---------------------------------------------------------

BACKEND = os.environ.get("AQ_VISION_BACKEND", "mlx").lower()

MLX_ENDPOINT = os.environ.get(
    "AQ_VISION_ENDPOINT",
    "http://localhost:8000/analyze",
)
OLLAMA_ENDPOINT = os.environ.get(
    "AQ_OLLAMA_ENDPOINT",
    "http://localhost:11434",
)
OLLAMA_MODEL = os.environ.get("AQ_OLLAMA_MODEL", "moondream")

ANTHROPIC_MODEL = os.environ.get(
    "AQ_ANTHROPIC_MODEL",
    "claude-haiku-4-5-20251001",
)

REQUEST_TIMEOUT = float(os.environ.get("AQ_VISION_TIMEOUT", "30"))

# Schema-aligned categories for the Bukit pilot. Keep this list short —
# overstuffing the prompt with rare categories hurts classification.
CATEGORIES = [
    "burning",       # open burning of trash / agricultural waste
    "trash",         # accumulated waste, illegal dumping
    "vehicle",       # traffic exhaust, motorbike smoke
    "construction",  # dust, demolition, excavation
    "industrial",    # factory smoke, generator emissions
    "dust",          # non-construction airborne particulates
    "other",         # pollution present but not in list
    "none",          # no pollution visible
]

SEVERITIES = ["low", "medium", "high", "critical"]


# --- Public API ------------------------------------------------------------

def analyze_pollution_image(image_path: str) -> Dict[str, Any]:
    """
    Classify a pollution image. Backend chosen by AQ_VISION_BACKEND.

    Never raises. On any failure, returns a 'needs_review' result so the
    bot can store the report and a human / fallback worker can revisit.
    """
    path = Path(image_path)
    if not path.exists():
        return _needs_review(f"image not found: {image_path}", model="none")

    try:
        if BACKEND == "mlx":
            return _analyze_via_http(path, MLX_ENDPOINT, backend_label="mlx")
        if BACKEND == "ollama":
            return _analyze_via_ollama(path)
        if BACKEND == "haiku":
            return _analyze_via_haiku(path)
        if BACKEND == "mock":
            return _analyze_via_mock(path)
        return _needs_review(f"unknown AQ_VISION_BACKEND: {BACKEND}", model="none")
    except requests.Timeout:
        return _needs_review(
            f"{BACKEND} timed out after {REQUEST_TIMEOUT}s", model=BACKEND
        )
    except requests.ConnectionError as e:
        return _needs_review(
            f"{BACKEND} unreachable: {e}", model=BACKEND
        )
    except Exception as e:  # noqa: BLE001 — last-resort: never crash the bot
        return _needs_review(
            f"{BACKEND} error: {type(e).__name__}: {e}", model=BACKEND
        )


# --- Prompt ----------------------------------------------------------------

_PROMPT = f"""You are analyzing a photo from a community air-quality
reporting system in Bali, Indonesia. The photo was sent by a resident
reporting suspected air pollution.

Classify the image. Respond with ONLY a JSON object, no prose:

{{
  "detected": true|false,
  "category": one of {CATEGORIES},
  "confidence": 0.0 to 1.0,
  "indicators": [short phrases describing what you see, e.g. "thick smoke", "burning plastic", "haze"],
  "description": one short sentence describing the scene,
  "severity": one of {SEVERITIES}
}}

Rules:
- If no pollution is visible, set detected=false, category="none", severity="low".
- "burning" covers open burning of trash, waste, agricultural material.
- "vehicle" covers exhaust, idling traffic, motorbike smoke.
- "construction" covers active building, demolition, excavation dust.
- "dust" is non-construction airborne particulates (e.g. road dust).
- Be conservative with "critical" — reserve it for thick smoke clouds,
  large fires, or scenes with visible health impact on people.
- Output JSON only. No markdown, no commentary."""


# --- Backend: HTTP (used by mlx wrapper) ----------------------------------

def _analyze_via_http(path: Path, endpoint: str, backend_label: str) -> Dict[str, Any]:
    """
    Generic JSON POST to a local vision server.

    Contract: server accepts {"image_b64": str, "prompt": str} and
    returns the analysis dict. The MLX wrapper script implements this.
    """
    img_b64 = _encode_image(path)
    resp = requests.post(
        endpoint,
        json={"image_b64": img_b64, "prompt": _PROMPT},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    body = resp.json()
    return _coerce_result(body, model=body.get("model_version", backend_label))


# --- Backend: Ollama -------------------------------------------------------

def _analyze_via_ollama(path: Path) -> Dict[str, Any]:
    """Call Ollama's /api/generate with an embedded base64 image."""
    img_b64 = _encode_image(path)
    resp = requests.post(
        f"{OLLAMA_ENDPOINT}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": _PROMPT,
            "images": [img_b64],
            "stream": False,
            "format": "json",
        },
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    body = resp.json()
    text = body.get("response", "")
    parsed = _extract_json(text)
    if parsed is None:
        return _needs_review(
            f"ollama returned non-JSON: {text[:200]}", model=f"ollama:{OLLAMA_MODEL}"
        )
    return _coerce_result(parsed, model=f"ollama:{OLLAMA_MODEL}")


# --- Backend: Anthropic Claude Haiku --------------------------------------

def _analyze_via_haiku(path: Path) -> Dict[str, Any]:
    """Anthropic vision fallback. Lazy import so the dep is optional."""
    try:
        import anthropic  # type: ignore
    except ImportError:
        return _needs_review(
            "anthropic SDK not installed; pip install anthropic",
            model="haiku",
        )

    img_b64 = _encode_image(path)
    media_type = _guess_media_type(path)
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=400,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_b64,
                        },
                    },
                    {"type": "text", "text": _PROMPT},
                ],
            }
        ],
    )
    text = msg.content[0].text if msg.content else ""
    parsed = _extract_json(text)
    if parsed is None:
        return _needs_review(
            f"haiku returned non-JSON: {text[:200]}", model=ANTHROPIC_MODEL
        )
    return _coerce_result(parsed, model=ANTHROPIC_MODEL)


# --- Backend: Mock (filename heuristics, for offline tests) ---------------

def _analyze_via_mock(path: Path) -> Dict[str, Any]:
    """Filename-keyword heuristics. Useful for CI and offline dev."""
    fn = path.name.lower()
    rules = [
        (("burn", "fire", "smoke"), "burning", 0.85, "high",
         ["visible smoke", "open flame"], "Open burning visible"),
        (("trash", "dump", "waste"), "trash", 0.78, "medium",
         ["waste pile"], "Accumulated waste"),
        (("factory", "industrial", "smokestack"), "industrial", 0.9, "high",
         ["industrial smokestack"], "Industrial emission source"),
        (("traffic", "exhaust", "vehicle"), "vehicle", 0.72, "medium",
         ["vehicle exhaust"], "Vehicle emission"),
        (("construction", "demolition", "dust"), "construction", 0.7, "medium",
         ["construction dust"], "Construction-related particulates"),
    ]
    for keywords, cat, conf, sev, inds, desc in rules:
        if any(k in fn for k in keywords):
            return {
                "detected": True,
                "category": cat,
                "confidence": conf,
                "indicators": inds,
                "description": desc,
                "severity": sev,
                "model_version": "mock-filename-v1",
            }
    return {
        "detected": False,
        "category": "none",
        "confidence": 0.3,
        "indicators": [],
        "description": "No clear pollution indicators (mock backend)",
        "severity": "low",
        "model_version": "mock-filename-v1",
    }


# --- Helpers ---------------------------------------------------------------

def _encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _guess_media_type(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "gif": "image/gif",
    }.get(ext, "image/jpeg")


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Pull a JSON object out of a model response, tolerating prose."""
    if not text:
        return None
    text = text.strip()
    # Strip ```json fences if present
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Last resort: find first { ... } balanced block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
    return None


def _coerce_result(raw: Dict[str, Any], model: str) -> Dict[str, Any]:
    """Coerce a backend response into our canonical shape."""
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
        "model_version": str(model),
    }


def _needs_review(reason: str, model: str) -> Dict[str, Any]:
    """Construct a non-failing 'manual review needed' result."""
    return {
        "detected": False,
        "category": "other",
        "confidence": 0.0,
        "indicators": [],
        "description": f"Automated analysis failed — needs manual review. ({reason})",
        "severity": "low",
        "model_version": f"{model}:error",
    }


# --- CLI smoke test --------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"Backend: {BACKEND}")
        print("Usage: python vision_analyzer.py <image_path>")
        print("Env:   AQ_VISION_BACKEND={mlx|ollama|haiku|mock}")
        print(f"       AQ_VISION_ENDPOINT={MLX_ENDPOINT}")
        print(f"       AQ_OLLAMA_ENDPOINT={OLLAMA_ENDPOINT}")
        print(f"       AQ_OLLAMA_MODEL={OLLAMA_MODEL}")
        sys.exit(0)

    target = sys.argv[1]
    print(f"Backend: {BACKEND}")
    print(f"Image:   {target}")
    result = analyze_pollution_image(target)
    print(json.dumps(result, indent=2))

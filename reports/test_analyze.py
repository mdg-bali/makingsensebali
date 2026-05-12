#!/usr/bin/env python3
"""
Hit the local MLX vision server with an image and pretty-print the result.

Usage:
    python test_analyze.py /path/to/some_photo.jpg
    python test_analyze.py ~/Desktop/burning_test.jpg

Useful for step A4 of TEST_PLAN.md and for spot-checking model quality
on new images later.
"""
import base64
import json
import sys
import time
from pathlib import Path

import requests

PROMPT = """You are analyzing a photo from a community air-quality
reporting system in Bali, Indonesia. Respond with ONLY a JSON object:

{
  "detected": true|false,
  "category": one of [burning, trash, vehicle, construction, industrial, dust, other, none],
  "confidence": 0.0 to 1.0,
  "indicators": [short phrases describing what you see],
  "description": one short sentence describing the scene,
  "severity": one of [low, medium, high, critical]
}

Rules:
- If no pollution is visible, set detected=false, category="none", severity="low".
- "burning" = open burning of trash/waste/agricultural material.
- "vehicle" = exhaust, idling traffic, motorbike smoke.
- "construction" = active building, demolition, excavation dust.
- Be conservative with "critical" — reserve for thick smoke, large fires.
- Output JSON only. No markdown, no commentary."""

ENDPOINT = "http://localhost:8000/analyze"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python test_analyze.py /path/to/photo.jpg")
        return 1

    img_path = Path(sys.argv[1]).expanduser()
    if not img_path.exists():
        print(f"File not found: {img_path}")
        return 1

    print(f"Image:    {img_path}")
    print(f"Endpoint: {ENDPOINT}")

    img_b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
    print(f"Size:     {len(img_b64):,} bytes (base64)")

    t0 = time.time()
    print("Calling /analyze (first call after model load can take 30+ sec)...")
    try:
        r = requests.post(
            ENDPOINT,
            json={"image_b64": img_b64, "prompt": PROMPT},
            timeout=300,
        )
    except requests.ConnectionError:
        print("\nCould not connect. Is the MLX server running?")
        print("  python mlx_vision_server.py")
        return 1
    except requests.Timeout:
        print("\nServer took longer than 5 minutes. Something's wrong.")
        return 1

    elapsed = time.time() - t0
    print(f"Latency:  {elapsed:.1f}s")
    print(f"Status:   {r.status_code}")
    print()

    try:
        body = r.json()
        print(json.dumps(body, indent=2))
    except json.JSONDecodeError:
        print("Response is not JSON:")
        print(r.text[:2000])
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

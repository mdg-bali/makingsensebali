#!/usr/bin/env python3
"""
generate_summary.py — produce a templated daily/weekly summary of
approved Bukit reports.

Reads sanitized profile JSONs from a source directory and writes a
summary.json next to the public index.json. Output shape:

    {
      "line": "Today: 3 burning trash, 1 water pollution.",
      "today": {"total": 4, "by_category": {"burning": 3, "water": 1}},
      "week":  {"total": 11, "by_category": {...}},
      "generated_at": "2026-05-14T03:42:00+00:00"
    }

The `line` field is what the public dashboard renders. Today's
intentionally templated — we'll swap to an LLM-generated sentence
once daily volume justifies the cost and the new dependency.

Usage:
    python3 generate_summary.py <source_dir> <output_path>

Defaults: source = ./data/profiles/, output = ./data/reports/summary.json
"""

import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Human-facing labels per category. Keep in lockstep with
# messages.CATEGORY_BAHASA / dashboard's color dict.
CATEGORY_LABELS = {
    "burning": "burning trash",
    "trash": "trash piles",
    "water": "water pollution",
    "vehicle": "vehicle smoke",
    "construction": "construction dust",
    "industrial": "industrial pollution",
    "dust": "dust",
    "other": "other issues",
    "none": "clear",
}


def _parse_ts(raw: str) -> datetime:
    """Lenient ISO-8601 parser that accepts the 'Z' suffix and naive ts."""
    if not raw:
        raise ValueError("empty timestamp")
    s = raw.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _human_list(counter: Counter) -> str:
    """'3 burning, 2 trash, 1 water' — oxford comma, 'and' for the last."""
    parts = [
        f"{n} {CATEGORY_LABELS.get(cat, cat)}"
        for cat, n in counter.most_common()
    ]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return " and ".join(parts)
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def _today_line(today_total: int, today_cats: Counter) -> str:
    """The one sentence the public dashboard renders."""
    if today_total == 0:
        return (
            "No reports today yet — the page updates as residents submit."
        )
    if today_total == 1:
        cat = next(iter(today_cats))
        return f"Today: 1 report — {CATEGORY_LABELS.get(cat, cat)}."
    return f"Today: {today_total} reports — {_human_list(today_cats)}."


def build_summary(source: Path, now: datetime) -> dict:
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    today_cats: Counter = Counter()
    week_cats: Counter = Counter()

    if source.is_dir():
        for p in source.glob("AQ_*.json"):
            try:
                r = json.loads(p.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            # Murmurations profiles use date_added; canonical reports
            # use timestamp. Take whichever's present.
            ts_raw = (
                r.get("date_added")
                or r.get("reviewed_at")
                or r.get("timestamp")
                or ""
            )
            try:
                ts = _parse_ts(ts_raw)
            except ValueError:
                continue
            cat = (
                r.get("pollution_category")
                or r.get("category")
                or "other"
            )
            if ts >= today_start:
                today_cats[cat] += 1
            if ts >= week_start:
                week_cats[cat] += 1

    return {
        "line": _today_line(sum(today_cats.values()), today_cats),
        "today": {
            "total": sum(today_cats.values()),
            "by_category": dict(today_cats),
        },
        "week": {
            "total": sum(week_cats.values()),
            "by_category": dict(week_cats),
        },
        "generated_at": now.isoformat(),
    }


def main(argv: list) -> int:
    source = Path(argv[1] if len(argv) > 1 else "./data/profiles")
    output = Path(argv[2] if len(argv) > 2 else "./data/reports/summary.json")
    summary = build_summary(source, datetime.now(timezone.utc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2))
    print(
        f"wrote {output} — today={summary['today']['total']} "
        f"week={summary['week']['total']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

#!/usr/bin/env python3
"""
Dashboard for the AQ Reporter — single-file Flask UI for non-terminal users.

Designed as part of the PLANETAI Community Node replication kit. The
dashboard reads the same config.json the bot reads, so anything you
configure here (locality, bioregion, allowlist) is the same data the
bot uses.

Pages
-----
  /                  Home — system status, queue depth, recent activity
  /allowlist         Add/remove/list pilot tester phone numbers
  /reports           Table of recent reports
  /map               Geographic view of complete reports
  /consent           Consented senders (anonymous hashes), revoke

Auth
----
Basic auth via env:
  DASHBOARD_USER     (default: admin)
  DASHBOARD_PASSWORD (REQUIRED — refuses to start if unset)

Bot config-reload
-----------------
After changes that affect runtime (allowlist edits), we POST to the
bot's /admin/reload-config endpoint with the EVOLUTION_API_KEY as the
admin key. No container restart needed.
"""

import json
import os
import sys
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from flask import (
    Flask,
    Response,
    abort,
    jsonify,
    redirect,
    render_template_string,
    request,
    url_for,
)

# --- Paths (shared with the bot) ------------------------------------------

ROOT = Path(os.environ.get("AQ_ROOT", "/app"))
DATA_DIR = ROOT / "reports"
PROFILE_DIR = ROOT / "profiles"
VISION_QUEUE = ROOT / "vision_queue"
CONFIG_FILE = ROOT / "config.json"
CONSENT_FILE = ROOT / "consent.json"

# --- Auth ------------------------------------------------------------------

ADMIN_USER = os.environ.get("DASHBOARD_USER", "admin")
ADMIN_PASS = os.environ.get("DASHBOARD_PASSWORD", "")

if not ADMIN_PASS:
    print(
        "ERROR: set DASHBOARD_PASSWORD env var before starting. "
        "Generate one with: openssl rand -hex 16",
        file=sys.stderr,
    )
    sys.exit(1)

# --- Bot reload endpoint ---------------------------------------------------

BOT_URL = os.environ.get("BOT_URL", "http://aq-bot:5055")


def reload_bot_config() -> bool:
    """Tell the bot to re-read config.json. Returns True on success."""
    api_key = os.environ.get("AQ_EVOLUTION_KEY", "")
    if not api_key:
        # Try to pull from config.json as fallback
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
            api_key = cfg.get("evolution_api", {}).get("api_key", "")
        except Exception:  # noqa: BLE001
            pass
    if not api_key:
        return False
    try:
        r = requests.post(
            f"{BOT_URL}/admin/reload-config",
            headers={"X-Admin-Key": api_key},
            timeout=5,
        )
        return r.ok
    except requests.RequestException:
        return False


# --- Config helpers --------------------------------------------------------

def load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def save_config(cfg: Dict[str, Any]) -> None:
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))


# --- Report / profile helpers ---------------------------------------------

def load_reports(limit: int = 100) -> List[Dict[str, Any]]:
    files = sorted(DATA_DIR.glob("AQ_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for p in files[:limit]:
        try:
            out.append(json.loads(p.read_text()))
        except json.JSONDecodeError:
            continue
    return out


def load_profiles(limit: int = 200) -> List[Dict[str, Any]]:
    files = sorted(PROFILE_DIR.glob("AQ_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for p in files[:limit]:
        try:
            out.append(json.loads(p.read_text()))
        except json.JSONDecodeError:
            continue
    return out


def queue_depth() -> Dict[str, int]:
    """Counts for pending/processing/done/failed."""
    def count(p: Path) -> int:
        if not p.exists():
            return 0
        return len(list(p.glob("AQ_*.json")))

    return {
        "pending": count(VISION_QUEUE),
        "processing": count(VISION_QUEUE / "processing"),
        "done": count(VISION_QUEUE / "done"),
        "failed": count(VISION_QUEUE / "failed"),
    }


def load_consent() -> Dict[str, str]:
    if not CONSENT_FILE.exists():
        return {}
    try:
        return json.loads(CONSENT_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def save_consent(state: Dict[str, str]) -> None:
    CONSENT_FILE.write_text(json.dumps(state, indent=2))


# --- Bot health check ------------------------------------------------------

def check_bot_health() -> Dict[str, Any]:
    try:
        r = requests.get(f"{BOT_URL}/health", timeout=3)
        if r.ok:
            return {"status": "ok", **r.json()}
        return {"status": "degraded", "code": r.status_code}
    except requests.RequestException as e:
        return {"status": "down", "error": str(e)}


# --- Evolution API client (WhatsApp pairing) ------------------------------

EVOLUTION_BASE = os.environ.get("EVOLUTION_BASE", "http://aq-evolution:8080")
EVOLUTION_INSTANCE = os.environ.get("EVOLUTION_INSTANCE", "bali-aq")


def _evo_headers() -> Dict[str, str]:
    api_key = os.environ.get("AQ_EVOLUTION_KEY", "")
    if not api_key:
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
            api_key = cfg.get("evolution_api", {}).get("api_key", "")
        except (json.JSONDecodeError, OSError):
            pass
    return {"apikey": api_key, "Content-Type": "application/json"}


def evolution_state() -> Dict[str, Any]:
    try:
        r = requests.get(
            f"{EVOLUTION_BASE}/instance/connectionState/{EVOLUTION_INSTANCE}",
            headers=_evo_headers(),
            timeout=5,
        )
        if r.ok:
            return r.json()
        # 404 means instance doesn't exist — return a normalized "none" state
        if r.status_code == 404:
            return {"_no_instance": True}
        return {"_error": f"HTTP {r.status_code}: {r.text[:200]}"}
    except requests.RequestException as e:
        return {"_error": str(e)}


def evolution_state_normalized() -> str:
    """Return one of: 'open', 'connecting', 'close', 'none', 'error'."""
    info = evolution_state()
    if info.get("_no_instance"):
        return "none"
    if info.get("_error"):
        return "error"
    state = info.get("instance", {}).get("state", "")
    return state or "unknown"


def evolution_logout() -> Dict[str, Any]:
    try:
        r = requests.delete(
            f"{EVOLUTION_BASE}/instance/logout/{EVOLUTION_INSTANCE}",
            headers=_evo_headers(),
            timeout=10,
        )
        return r.json() if r.content else {"ok": r.ok}
    except requests.RequestException as e:
        return {"error": str(e)}


def evolution_delete() -> Dict[str, Any]:
    try:
        r = requests.delete(
            f"{EVOLUTION_BASE}/instance/delete/{EVOLUTION_INSTANCE}",
            headers=_evo_headers(),
            timeout=10,
        )
        return r.json() if r.content else {"ok": r.ok}
    except requests.RequestException as e:
        return {"error": str(e)}


def evolution_create() -> Dict[str, Any]:
    try:
        r = requests.post(
            f"{EVOLUTION_BASE}/instance/create",
            json={
                "instanceName": EVOLUTION_INSTANCE,
                "qrcode": True,
                "integration": "WHATSAPP-BAILEYS",
            },
            headers=_evo_headers(),
            timeout=15,
        )
        if r.ok:
            return r.json()
        return {"error": f"HTTP {r.status_code}: {r.text[:200]}"}
    except requests.RequestException as e:
        return {"error": str(e)}


def evolution_qr_bytes() -> bytes:
    """Fetch fresh QR PNG bytes. Returns empty bytes on failure."""
    try:
        r = requests.get(
            f"{EVOLUTION_BASE}/instance/connect/{EVOLUTION_INSTANCE}",
            headers=_evo_headers(),
            timeout=10,
        )
        if not r.ok:
            return b""
        data = r.json()
        b64 = data.get("base64") or data.get("qrcode", {}).get("base64", "") or ""
        if "," in b64:
            b64 = b64.split(",", 1)[1]
        import base64 as _b64
        return _b64.b64decode(b64) if b64 else b""
    except (requests.RequestException, ValueError):
        return b""


# --- Flask app + auth ------------------------------------------------------

app = Flask(__name__)


def check_auth(user: str, pw: str) -> bool:
    return user == ADMIN_USER and pw == ADMIN_PASS


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        a = request.authorization
        if not a or not check_auth(a.username, a.password):
            return Response(
                "Authentication required",
                401,
                {"WWW-Authenticate": 'Basic realm="AQ Reporter Dashboard"'},
            )
        return fn(*args, **kwargs)

    return wrapper


# --- Shared base template --------------------------------------------------

BASE_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }} — {{ node_label }}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.classless.min.css">
  <style>
    :root {
      --accent: #E55A3C;
      --accent-soft: #F8E0D7;
      --ink: #1a1a1a;
      --muted: #6b6b6b;
      --rule: #e6e6e6;
    }
    body { max-width: 1100px; margin: 0 auto; padding: 1.5rem 1.5rem 4rem; }
    header.top { display: flex; align-items: baseline; justify-content: space-between;
                 padding-bottom: 1rem; border-bottom: 1px solid var(--rule); margin-bottom: 1.5rem; }
    header.top h1 { font-size: 1.25rem; margin: 0; letter-spacing: -0.01em; }
    header.top h1 .node { color: var(--accent); font-weight: 700; }
    nav.tabs { display: flex; gap: 1.5rem; font-size: 0.95rem; }
    nav.tabs a { color: var(--muted); text-decoration: none; padding-bottom: 0.25rem; }
    nav.tabs a.active { color: var(--ink); border-bottom: 2px solid var(--accent); font-weight: 600; }
    nav.tabs a:hover { color: var(--ink); }
    .pill { display: inline-block; padding: 0.15rem 0.55rem; border-radius: 2px;
            font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
    .pill.ok { background: #e0f3e0; color: #1d6f1d; }
    .pill.warn { background: #fff4d6; color: #8a5d00; }
    .pill.down { background: #ffd9d9; color: #8a1d1d; }
    .pill.neutral { background: var(--accent-soft); color: var(--accent); }
    .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                  gap: 0.75rem; margin: 1rem 0; }
    .stat { background: white; border: 1px solid var(--rule); padding: 0.75rem 1rem; }
    .stat .label { color: var(--muted); font-size: 0.78rem; text-transform: uppercase;
                   letter-spacing: 0.05em; margin: 0; }
    .stat .value { font-size: 1.6rem; font-weight: 700; margin: 0.2rem 0 0; }
    table { font-size: 0.92rem; }
    table th { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em;
               color: var(--muted); font-weight: 600; }
    table td.mono, table th.mono { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 0.85rem; }
    form.inline { display: flex; gap: 0.5rem; align-items: end; }
    form.inline input[type="text"] { flex: 1; }
    .empty { color: var(--muted); padding: 2rem 0; text-align: center; font-style: italic; }
    .flash { background: var(--accent-soft); color: var(--accent); padding: 0.6rem 1rem;
             border-left: 3px solid var(--accent); margin-bottom: 1rem; }
    a.btn-danger {
      background: transparent; border: 1px solid #c44; color: #c44;
      padding: 0.2rem 0.6rem; font-size: 0.8rem; text-decoration: none;
    }
    a.btn-danger:hover { background: #c44; color: white; }
    .footer-note { color: var(--muted); font-size: 0.85rem; margin-top: 3rem;
                   padding-top: 1rem; border-top: 1px solid var(--rule); }
    #map { height: 520px; border: 1px solid var(--rule); }
  </style>
  {% block head %}{% endblock %}
</head>
<body>
  <header class="top">
    <h1><span class="node">{{ node_label }}</span> · {{ title }}</h1>
    <nav class="tabs">
      <a href="{{ url_for('home') }}" class="{{ 'active' if active=='home' else '' }}">Status</a>
      <a href="{{ url_for('pending_view') }}" class="{{ 'active' if active=='pending' else '' }}">
        Pending{% if pending_count %} <span class="pill warn" style="margin-left:0.3rem;">{{ pending_count }}</span>{% endif %}
      </a>
      <a href="{{ url_for('allowlist_view') }}" class="{{ 'active' if active=='allowlist' else '' }}">Allowlist</a>
      <a href="{{ url_for('whatsapp_status') }}" class="{{ 'active' if active=='whatsapp' else '' }}">WhatsApp</a>
      <a href="{{ url_for('reports_view') }}" class="{{ 'active' if active=='reports' else '' }}">Reports</a>
      <a href="{{ url_for('map_view') }}" class="{{ 'active' if active=='map' else '' }}">Map</a>
      <a href="{{ url_for('consent_view') }}" class="{{ 'active' if active=='consent' else '' }}">Consent</a>
    </nav>
  </header>

  {% if flash %}<div class="flash">{{ flash }}</div>{% endif %}

  {% block body %}{% endblock %}

  <footer class="footer-note">
    AQ Reporter · {{ node_id }} · {{ bioregion }}
  </footer>
</body>
</html>
"""


def render(page_template: str, **ctx) -> str:
    cfg = load_config()
    full = BASE_HTML.replace("{% block body %}{% endblock %}", page_template)
    head_extra = ctx.pop("head_extra", "")
    if head_extra:
        full = full.replace("{% block head %}{% endblock %}", head_extra)

    # Defaults first, then let ctx override — avoids duplicate-kwarg errors
    template_args: Dict[str, Any] = {
        "title": "Dashboard",
        "node_id": cfg.get("node_id", "unconfigured"),
        "node_label": _node_label(cfg),
        "bioregion": cfg.get("bioregion", "—"),
        "active": "",
        "flash": request.args.get("msg", ""),
        "pending_count": _count_pending(),
    }
    template_args.update(ctx)
    return render_template_string(full, **template_args)


def _count_pending() -> int:
    """Count reports with review_status='pending'. Used by nav badge."""
    n = 0
    for p in DATA_DIR.glob("AQ_*.json"):
        try:
            r = json.loads(p.read_text())
            if r.get("review_status", "pending") == "pending":
                n += 1
        except (json.JSONDecodeError, OSError):
            continue
    return n


def _node_label(cfg: Dict[str, Any]) -> str:
    """Produce a readable name from the node_id, e.g. 'bali.fab.city' → 'Bali'."""
    node = cfg.get("node_id", "")
    parts = node.split(".")
    if parts and parts[0]:
        return parts[0].title()
    return "Node"


# --- Routes ----------------------------------------------------------------

HOME_TEMPLATE = """
  <section class="grid-stats">
    <div class="stat">
      <p class="label">Bot</p>
      <p class="value">
        {% if bot_health.status == 'ok' %}
          <span class="pill ok">running</span>
        {% elif bot_health.status == 'degraded' %}
          <span class="pill warn">degraded</span>
        {% else %}
          <span class="pill down">down</span>
        {% endif %}
      </p>
    </div>
    <div class="stat">
      <p class="label">WhatsApp</p>
      <p class="value">
        <a href="{{ url_for('whatsapp_status') }}" style="text-decoration:none; color:inherit;">
        {% if whatsapp_state == 'open' %}
          <span class="pill ok">connected</span>
        {% elif whatsapp_state == 'connecting' %}
          <span class="pill warn">pairing</span>
        {% elif whatsapp_state == 'none' %}
          <span class="pill neutral">unpaired</span>
        {% else %}
          <span class="pill down">{{ whatsapp_state }}</span>
        {% endif %}
        </a>
      </p>
    </div>
    <div class="stat">
      <p class="label">Mode</p>
      <p class="value">
        {% if mode == 'strict' %}
          <span class="pill neutral">allowlist</span>
        {% else %}
          <span class="pill warn">open</span>
        {% endif %}
      </p>
    </div>
    <div class="stat">
      <p class="label">Allowed senders</p>
      <p class="value">{{ allowed_count }}</p>
    </div>
  </section>

  <section class="grid-stats">
    <div class="stat">
      <p class="label">Pending review</p>
      <p class="value">
        <a href="{{ url_for('pending_view') }}" style="text-decoration:none; color:inherit;">
          {{ pending_count }}{% if pending_count %} <small style="font-size:0.7rem; color:#8a5d00;">→ review</small>{% endif %}
        </a>
      </p>
    </div>
    <div class="stat">
      <p class="label">Approved</p>
      <p class="value">{{ approved_count }}</p>
    </div>
    <div class="stat">
      <p class="label">Reports today</p>
      <p class="value">{{ reports_today }}</p>
    </div>
    <div class="stat">
      <p class="label">Vision queue</p>
      <p class="value">{{ q.pending }} pending · {{ q.failed }} failed</p>
    </div>
  </section>

  <h2 style="margin-top:2rem;">Recent reports</h2>
  {% if recent %}
  <table>
    <thead>
      <tr>
        <th>When</th>
        <th>Locality</th>
        <th>Category</th>
        <th>Severity</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>
      {% for r in recent %}
      <tr>
        <td class="mono">{{ r.ts }}</td>
        <td>{{ r.locality }}</td>
        <td>{{ r.category or '—' }}</td>
        <td>{{ r.severity or '—' }}</td>
        <td>{{ r.description|truncate(70) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p class="empty">No reports yet. Once an allowlisted sender messages the bot, they'll appear here.</p>
  {% endif %}
"""


@app.get("/")
@auth_required
def home():
    cfg = load_config()
    reports = load_reports(limit=10)
    all_reports = load_reports(limit=10000)
    today = datetime.now().strftime("%Y-%m-%d")
    reports_today = sum(
        1 for r in all_reports if (r.get("timestamp") or "").startswith(today)
    )

    recent = [
        {
            "ts": _short_ts(r.get("timestamp", "")),
            "locality": (r.get("location") or {}).get("locality")
                         or _from_description(r.get("description", "")),
            "category": (r.get("ai_analysis") or {}).get("category") or r.get("category"),
            "severity": (r.get("ai_analysis") or {}).get("severity"),
            "description": r.get("description") or "",
        }
        for r in reports
    ]

    approved_count = sum(
        1 for r in all_reports if r.get("review_status") == "approved"
    )
    pending_count = sum(
        1 for r in all_reports if r.get("review_status", "pending") == "pending"
    )

    return render(
        HOME_TEMPLATE,
        title="Status",
        active="home",
        bot_health=check_bot_health(),
        whatsapp_state=evolution_state_normalized(),
        mode=cfg.get("allowlist_mode", "strict"),
        allowed_count=len(cfg.get("allowed_senders", [])),
        consent_count=sum(1 for v in load_consent().values() if v == "granted"),
        reports_today=reports_today,
        reports_total=len(all_reports),
        approved_count=approved_count,
        pending_count=pending_count,
        q=queue_depth(),
        recent=recent,
    )


ALLOWLIST_TEMPLATE = """
  <h2>Allowlist</h2>
  <p style="color: var(--muted);">
    Mode is <strong>{{ mode }}</strong>.
    {% if mode == 'strict' %}
      Only numbers in this list can interact with the bot. Anyone else is silently ignored — no reply, no report saved.
    {% else %}
      <strong>Open mode</strong> — everyone who messages the bot is processed. Only safe with a dedicated bot phone number.
    {% endif %}
  </p>

  <form method="post" action="{{ url_for('allowlist_add') }}" class="inline" style="margin: 1.5rem 0;">
    <label style="flex:1;">
      <span style="font-size: 0.85rem; color: var(--muted);">New number (E.164 format, e.g. +6281234567890)</span>
      <input type="text" name="number" required pattern="^\\+[0-9]{8,15}$" placeholder="+62...">
    </label>
    <button type="submit">Add</button>
  </form>

  {% if allowed %}
  <table>
    <thead>
      <tr>
        <th>Number</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {% for n in allowed %}
      <tr>
        <td class="mono">{{ n }}</td>
        <td style="text-align:right;">
          <a class="btn-danger" href="{{ url_for('allowlist_remove', number=n) }}"
             onclick="return confirm('Remove {{ n }} from allowlist?');">remove</a>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
    <p class="empty">No numbers in allowlist yet. Add at least one to receive messages.</p>
  {% endif %}

  <details style="margin-top: 3rem;">
    <summary style="cursor: pointer;">Switch allowlist mode</summary>
    <form method="post" action="{{ url_for('allowlist_set_mode') }}" style="margin-top: 1rem;">
      <label><input type="radio" name="mode" value="strict" {% if mode=='strict' %}checked{% endif %}> <strong>Strict</strong> — only allowlisted senders processed (recommended for personal numbers)</label><br>
      <label><input type="radio" name="mode" value="open" {% if mode=='open' %}checked{% endif %}> <strong>Open</strong> — everyone processed (only with a dedicated bot number)</label><br><br>
      <button type="submit">Save mode</button>
    </form>
  </details>
"""


@app.get("/allowlist")
@auth_required
def allowlist_view():
    cfg = load_config()
    return render(
        ALLOWLIST_TEMPLATE,
        title="Allowlist",
        active="allowlist",
        allowed=cfg.get("allowed_senders", []),
        mode=cfg.get("allowlist_mode", "strict"),
    )


@app.post("/allowlist/add")
@auth_required
def allowlist_add():
    number = (request.form.get("number") or "").strip()
    if not number.startswith("+") or not number[1:].isdigit() or not (8 <= len(number[1:]) <= 15):
        return redirect(url_for("allowlist_view") + "?msg=Invalid+number+format")

    cfg = load_config()
    allowed = cfg.setdefault("allowed_senders", [])
    if number in allowed:
        return redirect(url_for("allowlist_view") + f"?msg=Already+in+allowlist:+{number}")
    allowed.append(number)
    save_config(cfg)
    reloaded = reload_bot_config()
    suffix = "" if reloaded else "+(bot+reload+failed,+restart+manually)"
    return redirect(url_for("allowlist_view") + f"?msg=Added+{number}{suffix}")


@app.get("/allowlist/remove/<number>")
@auth_required
def allowlist_remove(number: str):
    cfg = load_config()
    allowed = cfg.get("allowed_senders", [])
    cfg["allowed_senders"] = [n for n in allowed if n.strip() != number.strip()]
    save_config(cfg)
    reload_bot_config()
    return redirect(url_for("allowlist_view") + f"?msg=Removed+{number}")


@app.post("/allowlist/mode")
@auth_required
def allowlist_set_mode():
    mode = request.form.get("mode", "strict")
    if mode not in ("open", "strict"):
        mode = "strict"
    cfg = load_config()
    cfg["allowlist_mode"] = mode
    save_config(cfg)
    reload_bot_config()
    return redirect(url_for("allowlist_view") + f"?msg=Mode+set+to+{mode}")


# --- Pending review ------------------------------------------------------

PENDING_TEMPLATE = """
  <h2>Pending review</h2>
  <p style="color: var(--muted);">
    Reports stay here until you approve or reject them. Approved reports
    are published to the public dashboard. Rejected reports stay locally
    for the record but are never federated.
  </p>

  {% if pending %}
  {% for r in pending %}
  <article class="pending-card">
    <header style="display:flex; justify-content:space-between; align-items:baseline;">
      <div>
        <strong class="mono">{{ r.id[:24] }}</strong>
        <span style="color:var(--muted); margin-left:0.5rem;">{{ r.ts }}</span>
      </div>
      <div>
        <span class="pill neutral">{{ r.type }}</span>
        {% if r.category %}<span class="pill warn">{{ r.category }}</span>{% endif %}
        {% if r.severity %}<span class="pill {{ 'down' if r.severity in ('high','critical') else 'neutral' }}">{{ r.severity }}</span>{% endif %}
      </div>
    </header>
    <div class="pending-grid">
      <div class="pending-text">
        <p style="margin: 0.5rem 0;">{{ r.description or '_(no description)_' }}</p>
        <p style="color: var(--muted); font-size: 0.9rem;">
          📍 {{ r.locality }}
          {% if r.coords %}<span class="mono" style="margin-left:0.5rem;">{{ r.coords }}</span>{% endif %}
        </p>
        {% if r.ai_description %}
        <p class="ai-block">
          🤖 <em>{{ r.ai_description }}</em>
        </p>
        {% elif r.has_photo and not r.ai_description and not r.ai_indicators %}
        <p style="color: var(--muted); font-size: 0.85rem; font-style: italic;">
          🤖 Photo analysis pending — M1 worker will fill this in shortly.
        </p>
        {% endif %}
        {% if r.ai_indicators %}
        <p style="color: var(--muted); font-size: 0.9rem;">🔍 {{ r.ai_indicators }}</p>
        {% endif %}
      </div>
      <div class="pending-visuals">
        {% if r.has_photo %}
        <img class="pending-thumb"
             src="{{ url_for('report_image', report_id=r.id) }}"
             alt="report photo"
             onclick="openImgModal(this.src)">
        {% else %}
        <div class="pending-thumb-empty">no photo</div>
        {% endif %}
        {% if r.lat is not none and r.lon is not none %}
        <div id="map-{{ loop.index0 }}" class="pending-map" data-lat="{{ r.lat }}" data-lon="{{ r.lon }}" data-cat="{{ r.category or 'other' }}"></div>
        {% else %}
        <div class="pending-thumb-empty">no location</div>
        {% endif %}
      </div>
    </div>
    <div style="display:flex; gap:0.75rem; margin-top:0.75rem; align-items:center; flex-wrap:wrap;">
      <form method="post" action="{{ url_for('approve', report_id=r.id) }}"
            style="margin:0; display:flex; gap:0.6rem; align-items:center;">
        {% if r.has_photo %}
        <label class="publish-photo-toggle"
               title="If checked, the photo travels to the public repo too. Once published, it lives in git history.">
          <input type="checkbox" name="include_photo" value="1"
                 onchange="onPublishPhotoToggle(this)">
          <span>📷 Publish photo too</span>
        </label>
        {% endif %}
        <button type="submit" style="background:#1d6f1d; border:0;">Approve &amp; publish</button>
      </form>
      <form method="post" action="{{ url_for('reject', report_id=r.id) }}" style="margin:0;">
        <button type="submit" class="contrast outline">Reject</button>
      </form>
      <a href="{{ url_for('report_detail', report_id=r.id) }}"
         style="align-self:center; color:var(--muted);">View raw JSON →</a>
    </div>
  </article>
  {% endfor %}

  <div id="img-modal" class="img-modal" onclick="this.style.display='none'">
    <img id="img-modal-content" alt="">
  </div>

  <script>
    // One Leaflet mini-map per pending card. Marker only — no popup,
    // because the same info is already in the card body.
    const CAT_COLORS = {
      burning: '#c4392b', trash: '#e08a2e', water: '#3a7ab8',
      vehicle: '#5b8def', construction: '#a37e3e', industrial: '#7a3a8c',
      dust: '#9b9b9b', other: '#666', none: '#28a745'
    };
    document.querySelectorAll('.pending-map').forEach(el => {
      const lat = parseFloat(el.dataset.lat);
      const lon = parseFloat(el.dataset.lon);
      const cat = el.dataset.cat || 'other';
      if (isNaN(lat) || isNaN(lon)) return;
      const m = L.map(el, {
        scrollWheelZoom: false, dragging: false, zoomControl: false,
        attributionControl: false, doubleClickZoom: false,
      }).setView([lat, lon], 15);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19}).addTo(m);
      const color = CAT_COLORS[cat] || '#666';
      L.circleMarker([lat, lon], {
        radius: 9, color: color, fillColor: color, fillOpacity: 0.85, weight: 2
      }).addTo(m);
    });

    function openImgModal(src) {
      document.getElementById('img-modal-content').src = src;
      document.getElementById('img-modal').style.display = 'flex';
    }
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') document.getElementById('img-modal').style.display = 'none';
    });

    // Photo-publish confirmation. First time per page-load that the
    // operator checks any "Publish photo too" box, surface a confirm
    // dialog spelling out that git history is permanent. After they
    // confirm once, free to check more boxes without re-prompting.
    let photoPublishConfirmedThisSession = false;
    function onPublishPhotoToggle(cb) {
      if (!cb.checked) return;
      if (photoPublishConfirmedThisSession) return;
      const msg =
        'This photo will be published to the public GitHub repo at ' +
        'mdg-bali/smartcitizenbali and archived in git history.\\n\\n' +
        'Once published, the photo cannot be fully removed without ' +
        'rewriting git history — anyone who has cloned the repo can ' +
        'still recover it.\\n\\n' +
        'EXIF metadata (including GPS) will be stripped before publish.\\n\\n' +
        'Confirm publish for this and other photos this session?';
      if (window.confirm(msg)) {
        photoPublishConfirmedThisSession = true;
      } else {
        cb.checked = false;
      }
    }
  </script>
  {% else %}
  <p class="empty">No reports awaiting review. All caught up.</p>
  {% endif %}
"""


@app.get("/pending")
@auth_required
def pending_view():
    rows = []
    for r in load_reports(limit=200):
        if r.get("review_status", "pending") != "pending":
            continue
        loc = r.get("location") or {}
        lat = loc.get("lat") if isinstance(loc, dict) else None
        lon = loc.get("lon") if isinstance(loc, dict) else None
        coords = f"{lat:.4f}, {lon:.4f}" if (lat is not None and lon is not None) else ""
        ai = r.get("ai_analysis") or {}
        rows.append({
            "id": r.get("id", "?"),
            "ts": _short_ts(r.get("timestamp", "")),
            "type": r.get("type", "?"),
            "description": r.get("description", ""),
            "category": ai.get("category") or r.get("category"),
            "severity": ai.get("severity"),
            # AI's natural-language description of the photo (when the
            # M1 worker has finished). Empty string if not yet analyzed.
            "ai_description": (ai.get("description") or "").strip() if ai else "",
            "ai_indicators": ", ".join(ai.get("indicators", [])) if ai.get("indicators") else "",
            "locality": _from_description(r.get("description", "")) or "—",
            "coords": coords,
            "lat": lat,
            "lon": lon,
            "has_photo": bool(r.get("image_path")),
        })

    head_extra = (
        '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">'
        '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
        '<style>'
        '.pending-card { border: 1px solid var(--rule); padding: 1rem 1.25rem; margin-bottom: 1rem; }'
        '.pending-grid { display: grid; grid-template-columns: 1fr 280px; '
        ' gap: 1.25rem; margin-top: 0.5rem; align-items: start; }'
        '.pending-text { min-width: 0; }'
        '.pending-visuals { display: flex; flex-direction: column; gap: 0.5rem; }'
        '.pending-thumb { width: 100%; height: 160px; object-fit: cover; '
        ' border: 1px solid var(--rule); cursor: zoom-in; }'
        '.pending-thumb:hover { opacity: 0.92; }'
        '.pending-thumb-empty { width: 100%; height: 90px; border: 1px dashed var(--rule); '
        ' display: flex; align-items: center; justify-content: center; '
        ' color: var(--muted); font-size: 0.85rem; font-style: italic; }'
        '.pending-map { width: 100%; height: 160px; border: 1px solid var(--rule); }'
        '.ai-block { font-size: 0.92rem; background: var(--accent-soft); '
        ' padding: 0.5rem 0.75rem; margin-top: 0.5rem; border-left: 3px solid var(--accent); }'
        '.img-modal { display: none; position: fixed; inset: 0; '
        ' background: rgba(0,0,0,0.88); z-index: 1000; '
        ' align-items: center; justify-content: center; cursor: zoom-out; }'
        '.img-modal img { max-width: 92vw; max-height: 92vh; object-fit: contain; }'
        '.publish-photo-toggle { display: inline-flex; align-items: center; '
        ' gap: 0.4rem; font-size: 0.85rem; padding: 0.25rem 0.55rem; '
        ' border: 1px solid var(--rule); cursor: pointer; user-select: none; }'
        '.publish-photo-toggle input { margin: 0; cursor: pointer; }'
        '.publish-photo-toggle:has(input:checked) { '
        ' background: var(--accent-soft); border-color: var(--accent); }'
        '@media (max-width: 720px) { .pending-grid { grid-template-columns: 1fr; } }'
        '</style>'
    )
    return render(
        PENDING_TEMPLATE,
        title="Pending review",
        active="pending",
        pending=rows,
        head_extra=head_extra,
    )


@app.post("/approve/<report_id>")
@auth_required
def approve(report_id: str):
    # Checkbox "include_photo" only present in the form when the operator
    # explicitly opted to publish the photo. Default = photo stays NAS-only.
    include_photo = request.form.get("include_photo") == "1"
    ok = _call_bot_admin(
        "approve-report",
        {"report_id": report_id, "include_photo": include_photo},
    )
    msg_word = (
        ("Approved+with+photo" if include_photo else "Approved+text-only")
        if ok else "Approve+failed"
    )
    return redirect(url_for("pending_view") + f"?msg={msg_word}+{report_id[:16]}")


@app.post("/reject/<report_id>")
@auth_required
def reject(report_id: str):
    ok = _call_bot_admin("reject-report", {"report_id": report_id})
    msg = "Rejected" if ok else "Reject+failed"
    return redirect(url_for("pending_view") + f"?msg={msg}+{report_id[:16]}")


def _call_bot_admin(action: str, payload: Dict[str, Any]) -> bool:
    """POST to bot /admin/<action> with the X-Admin-Key header."""
    api_key = os.environ.get("AQ_EVOLUTION_KEY", "")
    if not api_key:
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
            api_key = cfg.get("evolution_api", {}).get("api_key", "")
        except Exception:  # noqa: BLE001
            pass
    if not api_key:
        return False
    try:
        r = requests.post(
            f"{BOT_URL}/admin/{action}",
            json=payload,
            headers={"X-Admin-Key": api_key},
            timeout=10,
        )
        return r.ok
    except requests.RequestException:
        return False


REPORTS_TEMPLATE = """
  <h2>Reports</h2>
  <p style="color: var(--muted);">Last {{ reports|length }} reports.
     Click a row to view raw JSON.</p>

  {% if reports %}
  <table>
    <thead>
      <tr>
        <th>When</th>
        <th>ID</th>
        <th>Locality</th>
        <th>Category</th>
        <th>Severity</th>
        <th>Lat,Lon</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {% for r in reports %}
      <tr>
        <td class="mono">{{ r.ts }}</td>
        <td class="mono"><a href="{{ url_for('report_detail', report_id=r.id) }}">{{ r.id[:24] }}</a></td>
        <td>{{ r.locality }}</td>
        <td>{{ r.category or '—' }}</td>
        <td>{{ r.severity or '—' }}</td>
        <td class="mono">{{ r.coords }}</td>
        <td>{{ r.status }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
    <p class="empty">No reports yet.</p>
  {% endif %}
"""


@app.get("/reports")
@auth_required
def reports_view():
    raw = load_reports(limit=100)
    rows = []
    for r in raw:
        loc = r.get("location") or {}
        lat = loc.get("lat") if isinstance(loc, dict) else None
        lon = loc.get("lon") if isinstance(loc, dict) else None
        coords = f"{lat:.4f}, {lon:.4f}" if (lat is not None and lon is not None) else "—"
        rows.append({
            "id": r.get("id", "?"),
            "ts": _short_ts(r.get("timestamp", "")),
            "locality": _from_description(r.get("description", "")),
            "category": (r.get("ai_analysis") or {}).get("category") or r.get("category"),
            "severity": (r.get("ai_analysis") or {}).get("severity"),
            "coords": coords,
            "status": r.get("status", "—"),
        })
    return render(REPORTS_TEMPLATE, title="Reports", active="reports", reports=rows)


@app.get("/reports/<report_id>")
@auth_required
def report_detail(report_id: str):
    p = DATA_DIR / f"{report_id}.json"
    if not p.exists():
        abort(404)
    body = """
      <h2 class="mono">{{ report_id }}</h2>
      <p><a href="{{ url_for('reports_view') }}">← Back to reports</a></p>
      <pre style="background:#f6f6f6; padding:1rem; overflow:auto;">{{ raw }}</pre>
    """
    return render(body, title="Report", active="reports", report_id=report_id,
                  raw=p.read_text())


@app.get("/image/<report_id>")
@auth_required
def report_image(report_id: str):
    """Serve the photo attached to a report.

    The image path stored in the report JSON is treated as untrusted —
    we resolve it and confirm it lives inside our images dir before
    serving, so a malformed report can't leak arbitrary files.
    """
    p = DATA_DIR / f"{report_id}.json"
    if not p.exists():
        abort(404)
    try:
        r = json.loads(p.read_text())
    except json.JSONDecodeError:
        abort(404)
    image_path = r.get("image_path")
    if not image_path:
        abort(404)
    safe_dir = (ROOT / "images").resolve()
    try:
        target = Path(image_path).resolve()
        target.relative_to(safe_dir)  # raises if outside safe_dir
    except (ValueError, OSError):
        abort(404)
    if not target.exists():
        abort(404)
    ext = target.suffix.lower().lstrip(".")
    mime = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "png": "image/png", "gif": "image/gif", "webp": "image/webp",
    }.get(ext, "application/octet-stream")
    # Cache aggressively — images are immutable per report_id
    return Response(
        target.read_bytes(),
        mimetype=mime,
        headers={"Cache-Control": "private, max-age=3600"},
    )


MAP_TEMPLATE = """
  <h2>Reports map</h2>
  <p style="color: var(--muted);">{{ profiles|length }} profiles with coordinates.</p>

  <div style="margin-bottom: 0.5rem; display:flex; align-items:center; gap:0.4rem;">
    <button id="mode-markers" type="button"
            style="font-size:0.85rem; padding:0.2rem 0.7rem; background:var(--accent); border:0;">Markers</button>
    <button id="mode-heatmap" type="button"
            class="contrast outline"
            style="font-size:0.85rem; padding:0.2rem 0.7rem;">Heatmap</button>
    <span id="mode-hint" style="color: var(--muted); font-size: 0.85rem; margin-left: 0.5rem;">
      Showing individual reports
    </span>
  </div>

  <div id="map"></div>
  <script>
    const profiles = {{ profiles_json|safe }};
    const center = {{ center|safe }};
    const map = L.map('map').setView(center, 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '© OpenStreetMap'
    }).addTo(map);

    // Category colors — must stay in sync with messages.CATEGORY_EMOJI.
    const colors = {
      burning: '#c4392b', trash: '#e08a2e', water: '#3a7ab8',
      vehicle: '#5b8def', construction: '#a37e3e', industrial: '#7a3a8c',
      dust: '#9b9b9b', other: '#666', none: '#28a745'
    };

    // Marker layer
    const markerLayer = L.layerGroup();
    profiles.forEach(p => {
      if (!p.lat || !p.lon) return;
      const color = colors[p.category] || '#666';
      L.circleMarker([p.lat, p.lon], {
        radius: 7, color: color, fillColor: color, fillOpacity: 0.7, weight: 2
      }).bindPopup(
        `<strong>${p.name}</strong><br>` +
        `<span style="color:#666">${p.ts}</span><br>` +
        `${p.description || ''}<br>` +
        `<em>Severity: ${p.severity}</em>`
      ).addTo(markerLayer);
    });
    markerLayer.addTo(map);

    // Heatmap layer (built but not added by default)
    const heatPoints = profiles
      .filter(p => p.lat && p.lon)
      .map(p => [p.lat, p.lon, 0.7]);
    const heatLayer = L.heatLayer(heatPoints, {
      radius: 35, blur: 25, maxZoom: 17, minOpacity: 0.4
    });

    const btnMarkers = document.getElementById('mode-markers');
    const btnHeat = document.getElementById('mode-heatmap');
    const hint = document.getElementById('mode-hint');

    function setActive(active) {
      // Swap button styles to indicate which mode is on.
      [btnMarkers, btnHeat].forEach(b => {
        b.classList.add('contrast', 'outline');
        b.style.background = '';
        b.style.border = '';
      });
      active.classList.remove('outline');
      active.style.background = 'var(--accent)';
      active.style.border = '0';
    }

    btnMarkers.addEventListener('click', () => {
      map.removeLayer(heatLayer);
      if (!map.hasLayer(markerLayer)) markerLayer.addTo(map);
      hint.textContent = 'Showing individual reports';
      setActive(btnMarkers);
    });

    btnHeat.addEventListener('click', () => {
      if (map.hasLayer(markerLayer)) map.removeLayer(markerLayer);
      heatLayer.addTo(map);
      hint.textContent = profiles.length < 20
        ? `Heatmap mode — sparse (${profiles.length} reports). Will resolve clusters as more reports come in.`
        : `Heatmap mode — density of ${profiles.length} reports.`;
      setActive(btnHeat);
    });
  </script>
"""


@app.get("/map")
@auth_required
def map_view():
    cfg = load_config()
    profiles = load_profiles(limit=500)
    points = [
        {
            "lat": p.get("latitude"),
            "lon": p.get("longitude"),
            "name": p.get("name", ""),
            "ts": _short_ts(p.get("date_added", "")),
            "category": p.get("pollution_category", "other"),
            "severity": (p.get("ai_analysis") or {}).get("severity", "?"),
            "description": (p.get("description") or "")[:200],
        }
        for p in profiles
        if p.get("latitude") and p.get("longitude")
    ]

    # Derive map center from points (or fall back to Bukit). For
    # Barcelona's deployment this auto-centers on incoming Barcelona data.
    if points:
        lats = [pt["lat"] for pt in points]
        lons = [pt["lon"] for pt in points]
        center = [sum(lats) / len(lats), sum(lons) / len(lons)]
    else:
        # Default per-node fallback — Bukit center
        center = [-8.82, 115.15]

    head_extra = (
        '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">'
        '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
        '<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>'
    )
    return render(
        MAP_TEMPLATE,
        title="Map",
        active="map",
        profiles=points,
        profiles_json=json.dumps(points),
        center=json.dumps(center),
        head_extra=head_extra,
    )


CONSENT_TEMPLATE = """
  <h2>Consent</h2>
  <p style="color: var(--muted);">
    {{ granted|length }} senders have granted consent ·
    {{ optout|length }} have opted out
  </p>
  <p style="color: var(--muted); font-size: 0.85rem;">
    Phone numbers are stored as one-way SHA-256 hashes (truncated to 16
    chars). The bot never persists raw phone numbers in reports.
  </p>

  {% if granted %}
  <h3 style="margin-top:2rem;">Granted</h3>
  <table>
    <thead><tr><th>Hash</th><th>Reports</th><th></th></tr></thead>
    <tbody>
      {% for h, count in granted %}
      <tr>
        <td class="mono">{{ h }}</td>
        <td>{{ count }}</td>
        <td style="text-align:right;">
          <a class="btn-danger" href="{{ url_for('consent_revoke', hash=h) }}"
             onclick="return confirm('Revoke consent for this sender?');">revoke</a>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}

  {% if optout %}
  <h3 style="margin-top:2rem;">Opted out</h3>
  <table>
    <thead><tr><th>Hash</th></tr></thead>
    <tbody>
      {% for h in optout %}
      <tr><td class="mono">{{ h }}</td></tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}

  {% if not granted and not optout %}
    <p class="empty">No consent records yet.</p>
  {% endif %}
"""


@app.get("/consent")
@auth_required
def consent_view():
    state = load_consent()
    reports = load_reports(limit=10000)
    # Count reports per sender hash
    counts: Dict[str, int] = {}
    for r in reports:
        h = r.get("sender_hash")
        if h:
            counts[h] = counts.get(h, 0) + 1
    granted = sorted(
        [(h, counts.get(h, 0)) for h, v in state.items() if v == "granted"],
        key=lambda x: -x[1],
    )
    optout = sorted([h for h, v in state.items() if v == "optout"])
    return render(
        CONSENT_TEMPLATE,
        title="Consent",
        active="consent",
        granted=granted,
        optout=optout,
    )


@app.get("/consent/revoke/<hash>")
@auth_required
def consent_revoke(hash: str):
    state = load_consent()
    if hash in state:
        state[hash] = "optout"
        save_consent(state)
    return redirect(url_for("consent_view") + f"?msg=Revoked+{hash[:8]}...")


# --- WhatsApp pairing -----------------------------------------------------

WHATSAPP_STATUS_TEMPLATE = """
  <h2>WhatsApp pairing</h2>
  <p style="color: var(--muted);">
    Manage the WhatsApp number this bot uses to receive and send messages.
    Pairing requires scanning a QR code with the WhatsApp app on the phone
    that will be the bot's identity.
  </p>

  <div class="stat" style="margin: 1.5rem 0; padding: 1.25rem 1.5rem;">
    <p class="label">Current state</p>
    <p class="value" style="margin-bottom: 0.5rem;">
      {% if state == 'open' %}
        <span class="pill ok">connected</span>
      {% elif state == 'connecting' %}
        <span class="pill warn">awaiting scan</span>
      {% elif state == 'close' %}
        <span class="pill down">disconnected</span>
      {% elif state == 'none' %}
        <span class="pill neutral">no instance</span>
      {% else %}
        <span class="pill down">{{ state }}</span>
      {% endif %}
    </p>
    <p style="color: var(--muted); font-size: 0.85rem; margin: 0;">
      Instance name: <span class="mono">{{ instance }}</span>
    </p>
  </div>

  {% if state == 'open' %}
    <p>The bot is currently connected and receiving messages.
       To replace this pair with a different phone — for example, switching
       from a personal number to a dedicated bot number — click below.</p>
    <p style="color: var(--muted); margin-top: 0.5rem;">
      <strong>Warning:</strong> This disconnects the current pair. The bot
      will stop receiving messages until the new phone scans the QR.
    </p>
    <form method="post" action="{{ url_for('whatsapp_start_pair') }}" style="margin-top: 1rem;"
          onsubmit="return confirm('This will disconnect the current WhatsApp pair. Continue?');">
      <button type="submit" class="contrast">Pair a different number</button>
    </form>

  {% elif state == 'connecting' %}
    <p>An instance exists but no phone has scanned a QR yet.</p>
    <div style="display:flex; gap:0.75rem; margin-top: 1rem;">
      <a href="{{ url_for('whatsapp_pair_view') }}" role="button">Show QR</a>
      <form method="post" action="{{ url_for('whatsapp_start_pair') }}" style="display:inline;">
        <button type="submit" class="outline">Reset &amp; start fresh</button>
      </form>
    </div>

  {% else %}
    <p>No active WhatsApp pair. Start a new pairing:</p>
    <form method="post" action="{{ url_for('whatsapp_start_pair') }}" style="margin-top: 1rem;">
      <button type="submit">Start pairing</button>
    </form>
  {% endif %}

  <details style="margin-top: 3rem;">
    <summary style="cursor: pointer; user-select: none;">How pairing works</summary>
    <ol style="margin: 1rem 0 0 1.5rem; line-height: 1.7;">
      <li>Click <strong>Start pairing</strong> (or <strong>Pair a different number</strong>) above —
          this resets the bot's Evolution API instance and generates a new QR code.</li>
      <li>On the phone you want to use as the bot's identity, open WhatsApp →
          <em>Settings</em> → <em>Linked Devices</em> → <em>Link a Device</em>.</li>
      <li>Scan the QR code shown in the dashboard.</li>
      <li>Wait ~5 seconds. The status above flips to <strong>connected</strong>.</li>
    </ol>
    <p style="margin: 1rem 0 0; color: var(--muted); font-size: 0.9rem;">
      WhatsApp QRs expire after ~60 seconds. The dashboard auto-refreshes the
      QR every 25 seconds while you're on the pairing page.
    </p>
    <p style="margin: 0.5rem 0 0; color: var(--muted); font-size: 0.9rem;">
      If pairing fails repeatedly, Meta may have rate-limited your phone
      number. Wait 30–60 minutes and try again.
    </p>
  </details>
"""

PAIR_TEMPLATE = """
  <h2>Scan to pair</h2>
  <p style="color: var(--muted);">
    Open WhatsApp on the phone that will be the bot's identity →
    <em>Settings</em> → <em>Linked Devices</em> → <em>Link a Device</em> →
    scan the code below.
  </p>

  <div style="margin: 2rem 0; text-align: center;">
    <img id="qr-img" src="{{ url_for('whatsapp_qr_png') }}?t={{ now }}"
         alt="WhatsApp pairing QR"
         style="width: 320px; height: 320px; border: 1px solid var(--rule); padding: 1rem; background: white;">
    <p id="state-line" style="margin: 1.5rem 0 1rem;">
      <span id="state-pill" class="pill warn">awaiting scan</span>
      <span id="state-detail" style="color: var(--muted); margin-left: 0.5rem;"></span>
    </p>
    <div style="display: flex; gap: 0.75rem; justify-content: center;">
      <form method="post" action="{{ url_for('whatsapp_start_pair') }}" style="display: inline;">
        <button type="submit" class="outline">Refresh QR</button>
      </form>
      <a href="{{ url_for('whatsapp_status') }}" role="button" class="contrast outline">Cancel</a>
    </div>
  </div>

  <script>
    (function() {
      const stateEl = document.getElementById('state-pill');
      const detailEl = document.getElementById('state-detail');
      const imgEl = document.getElementById('qr-img');
      let qrRefreshAt = Date.now() + 25000;

      async function check() {
        try {
          const r = await fetch('/api/whatsapp/state');
          const data = await r.json();
          const state = data.state || 'unknown';
          if (state === 'open') {
            stateEl.className = 'pill ok';
            stateEl.textContent = 'connected!';
            detailEl.textContent = 'Redirecting...';
            imgEl.style.opacity = '0.15';
            setTimeout(() => { location.href = '/whatsapp?msg=Paired+successfully'; }, 1500);
            return false; // stop polling
          } else if (state === 'connecting') {
            stateEl.className = 'pill warn';
            stateEl.textContent = 'awaiting scan';
            const secs = Math.max(0, Math.round((qrRefreshAt - Date.now()) / 1000));
            detailEl.textContent = 'QR refreshes in ' + secs + 's';
          } else {
            stateEl.className = 'pill down';
            stateEl.textContent = state;
            detailEl.textContent = '';
          }
        } catch (e) {
          detailEl.textContent = 'check failed';
        }
        return true;
      }

      function refreshQr() {
        imgEl.src = '/whatsapp/qr.png?t=' + Date.now();
        qrRefreshAt = Date.now() + 25000;
      }

      let pollHandle = setInterval(async () => {
        const keepGoing = await check();
        if (!keepGoing) clearInterval(pollHandle);
      }, 2000);

      setInterval(refreshQr, 25000);
      check();
    })();
  </script>
"""


@app.get("/whatsapp")
@auth_required
def whatsapp_status():
    state = evolution_state_normalized()
    return render(
        WHATSAPP_STATUS_TEMPLATE,
        title="WhatsApp",
        active="whatsapp",
        state=state,
        instance=EVOLUTION_INSTANCE,
    )


@app.post("/whatsapp/start-pair")
@auth_required
def whatsapp_start_pair():
    """
    Reset Evolution instance and prepare a fresh QR.

    Evolution API v2 needs each step to settle before the next — logout
    must complete before delete, delete must complete before create.
    We add small sleeps + a retry if 'already exists' bites.
    """
    import time

    # Step 1: logout if there's an active WhatsApp session (transitions
    # state from 'open' to 'close')
    state = evolution_state_normalized()
    if state == "open":
        evolution_logout()
        time.sleep(2)

    # Step 2: delete the instance entirely
    if state != "none":
        evolution_delete()
        time.sleep(2)

    # Step 3: create fresh
    result = evolution_create()

    # If create says "already exists" (403 from Evolution v2), the previous
    # delete didn't fully take effect — retry the whole cleanup once.
    err = str(result.get("error", "")).lower()
    if "error" in result and (
        "already" in err or "exist" in err or "403" in err or "forbidden" in err
    ):
        print("[whatsapp] create returned 'already exists' — retrying cleanup",
              file=sys.stderr)
        evolution_logout()
        time.sleep(2)
        evolution_delete()
        time.sleep(3)
        result = evolution_create()

    if "error" in result:
        return redirect(
            url_for("whatsapp_status")
            + f"?msg=Create+failed:+{result['error'][:80]}"
        )
    return redirect(url_for("whatsapp_pair_view"))


@app.get("/whatsapp/pair")
@auth_required
def whatsapp_pair_view():
    return render(
        PAIR_TEMPLATE,
        title="Pair WhatsApp",
        active="whatsapp",
        now=int(datetime.now().timestamp()),
    )


@app.get("/whatsapp/qr.png")
@auth_required
def whatsapp_qr_png():
    png = evolution_qr_bytes()
    if not png:
        # Tiny 1x1 transparent fallback so <img> doesn't show broken icon
        png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\rIDATx\x9cc\xfc\xcf\xc0P\x0f\x00\x05"
            b"\x01\x02\xa0\xe6\xab\x82\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
    return Response(
        png,
        mimetype="image/png",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )


@app.get("/api/whatsapp/state")
@auth_required
def whatsapp_state_api():
    return jsonify(state=evolution_state_normalized())


# --- Helpers ---------------------------------------------------------------

def _short_ts(iso: str) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        return iso[:16]


def _from_description(desc: str) -> str:
    """Best-effort locality from text. Same logic the adapter uses."""
    if not desc:
        return "—"
    d = desc.lower()
    for k, name in [
        ("padang padang", "Padang Padang"),
        ("nusa dua", "Nusa Dua"),
        ("uluwatu", "Uluwatu"),
        ("pecatu", "Pecatu"),
        ("ungasan", "Ungasan"),
        ("balangan", "Balangan"),
        ("bingin", "Bingin"),
        ("jimbaran", "Jimbaran"),
        ("kutuh", "Kutuh"),
        ("benoa", "Benoa"),
        ("bukit", "Bukit"),
        ("canggu", "Canggu"),
        ("seminyak", "Seminyak"),
        ("ubud", "Ubud"),
        ("denpasar", "Denpasar"),
    ]:
        if k in d:
            return name
    return "—"


@app.get("/health")
def health():
    """Unauthenticated health probe for container healthcheck."""
    return jsonify(ok=True, time=datetime.now(timezone.utc).isoformat())


# --- Main ------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("DASHBOARD_PORT", "5056"))
    print(f"Dashboard listening on :{port}", file=sys.stderr)
    app.run(host="0.0.0.0", port=port)

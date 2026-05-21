#!/usr/bin/env python3
"""
Murmurations Protocol Adapter for Planet AI Bali Node
Converts AQ Reporter data to Murmurations-compatible profiles.

This adapter:
1. Generates Murmurations-compliant JSON profiles (sanitized — no PII)
2. Writes profiles to a local publish queue (rsync target)
3. Integrates with Murmurations Index API
4. Maintains federated data compatibility

Publish flow:
    save()        →  profiles/AQ_*.json  (local publish queue)
    cron rsync    →  planetai.fab.city/bali/profiles/AQ_*.json  (public)
    auto_index    →  Murmurations Index node registration (optional)

The local `reports/` directory (canonical, includes sender + raw image
paths) is NEVER published. Only sanitized profiles leave the NAS.

Alignment: Planet AI Community-tier (64-d) node
Schema: environmental_observation-v1.0.0
"""

import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Murmurations Index endpoints
MURMURATIONS_INDEX_URL = "https://index.murmurations.network/v2"
MURMURATIONS_TEST_INDEX = "https://test-index.murmurations.network/v2"

# Where published profiles live publicly
PROFILE_BASE_URL = "https://planetai.fab.city/bali/profiles"

# Local publish queue — rsync source. Anything written here is a
# candidate for federation. Treat as public-facing.
LOCAL_PROFILE_DIR = Path(__file__).parent / "profiles"
LOCAL_PROFILE_DIR.mkdir(exist_ok=True)


@dataclass
class MurmurationsConfig:
    """Configuration for Murmurations integration"""
    node_id: str = "bali.fab.city"
    bioregion: str = "indo_pacific_coral_triangle"
    primary_url: str = "https://planetai.fab.city/bali"
    use_test_index: bool = True  # Set to False for production
    auto_index: bool = False  # Auto-post to index on profile creation


class MurmurationsProfile:
    """
    Represents a Murmurations profile for environmental observations.
    
    Combines existing Murmurations fields with Planet AI custom fields
    to create federated, interoperable environmental data.
    """
    
    # Schema version for this profile
    SCHEMA_VERSION = "environmental_observation-v1.0.0"
    
    def __init__(self, config: MurmurationsConfig = None):
        self.config = config or MurmurationsConfig()
        self.profile_data = {}
        
    def from_aq_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert an AQ Reporter report to Murmurations profile format.

        The returned profile is the *public* federation view — sanitized,
        no sender info, no local file paths. The canonical local report
        (with sender, raw image path, etc.) stays in reports/ and is
        never published.

        Args:
            report: AQ report dict from the bot

        Returns:
            Murmurations-compliant profile JSON
        """
        report_id = report.get("id", self._generate_id())
        profile_url = f"{self.config.primary_url}/profiles/{report_id}.json"

        # Location can arrive in two shapes from the bot:
        #   report["location"] = {"lat": ..., "lon": ...}
        # or as a standalone location report with top-level lat/lon.
        location = report.get("location") or {}
        lat = location.get("lat") if isinstance(location, dict) else None
        lon = location.get("lon") if isinstance(location, dict) else None
        if lat is None and "latitude" in report:
            lat = report.get("latitude")
        if lon is None and "longitude" in report:
            lon = report.get("longitude")

        ai_analysis = report.get("ai_analysis") or {}

        # If the bot already published a public image URL we include it;
        # never include a local filesystem path in the federated profile.
        image_url = report.get("image_url")

        # Category and severity must validate against the schema enums.
        category = self._normalize_category(report.get("category"))
        severity = self._normalize_severity(ai_analysis.get("severity"))

        profile = {
            # --- Required Murmurations fields ---
            "linked_schemas": [self.SCHEMA_VERSION],
            "name": self._build_name(category, report),
            "description": report.get("description", ""),
            "primary_url": profile_url,
            "latitude": lat,
            "longitude": lon,
            "geolocation": {"lat": lat, "lon": lon} if lat and lon else None,
            "locality": self._extract_locality(report),
            "region": "Bali",
            "country_name": "Indonesia",
            "country_iso_3166": "ID",
            "tags": self._generate_tags(report, category, severity),
            "image": image_url,
            "status": "active",
            "date_added": report.get("timestamp", datetime.now().isoformat()),

            # --- Planet AI custom fields (per schema) ---
            "observation_type": self._normalize_observation_type(report.get("type")),
            "pollution_category": category,
            "ai_analysis": {
                "detected": bool(ai_analysis.get("detected", False)),
                "confidence": float(ai_analysis.get("confidence", 0) or 0),
                "indicators": ai_analysis.get("indicators", []),
                "description": ai_analysis.get("description", ""),
                "severity": severity,
                "model_version": ai_analysis.get("model_version", "unknown"),
            } if ai_analysis else None,
            # photo_path is set when the operator opts to publish the
            # photo (per-report toggle in admin /pending). Optional —
            # only present in the public profile when explicitly opted-in.
            # The path is relative to the public data/reports/ tree so
            # the dashboard resolves it as `${reportsBaseUrl}/${photo_path}`.
            "photo_path": report.get("photo_path") if report.get("photo_path") else None,
            "data_source": report.get("source", "whatsapp"),
            "planet_ai_node": self.config.node_id,
            "bioregion": self.config.bioregion,
            "action_cycle": {
                "observation_timestamp": report.get("timestamp"),
                "reported_timestamp": report.get("timestamp"),
                "response_status": self._map_status(report.get("status")),
            },
        }

        # Sensor data (Smart Citizen, OpenAQ) when present
        if "sensor_data" in report:
            profile["sensor_data"] = report["sensor_data"]

        # Drop None values so the public profile stays tidy
        profile = {k: v for k, v in profile.items() if v is not None}

        self.profile_data = profile
        return profile

    def _normalize_category(self, category: Optional[str]) -> str:
        """Map free-form bot categories onto schema-valid enum values."""
        if not category:
            return "other"
        c = category.lower().strip()
        valid = {
            "burning", "trash", "industrial", "vehicle", "construction",
            "dust", "chemical", "water", "noise", "radiation",
            "deforestation", "other", "none",
        }
        if c in valid:
            return c
        # Common aliases coming from vision models
        aliases = {
            "vehicle_exhaust": "vehicle",
            "traffic": "vehicle",
            "exhaust": "vehicle",
            "smoke": "burning",
            "fire": "burning",
            "open_burning": "burning",
            "waste": "trash",
            "garbage": "trash",
            "dumping": "trash",
            "factory": "industrial",
            "smokestack": "industrial",
            "demolition": "construction",
            "excavation": "construction",
            "unknown": "other",
        }
        return aliases.get(c, "other")

    def _normalize_severity(self, severity: Optional[str]) -> str:
        """Schema allows low/medium/high/critical."""
        if not severity:
            return "low"
        s = severity.lower().strip()
        if s in {"low", "medium", "high", "critical"}:
            return s
        return "low"

    def _normalize_observation_type(self, obs_type: Optional[str]) -> str:
        """Schema enum: photo, video, drone_aerial, satellite,
        sensor_reading, eyewitness, eyewitness_audio, other."""
        if not obs_type:
            return "other"
        t = obs_type.lower().strip()
        valid = {
            "photo", "video", "drone_aerial", "satellite",
            "sensor_reading", "eyewitness", "eyewitness_audio", "other",
        }
        if t in valid:
            return t
        aliases = {
            "text": "eyewitness",
            "voice": "eyewitness_audio",
            "audio": "eyewitness_audio",
            "image": "photo",
            "location": "other",
        }
        return aliases.get(t, "other")

    def _build_name(self, category: str, report: Dict[str, Any]) -> str:
        """Human-readable name for the profile — shown in the index."""
        locality = self._extract_locality(report)
        cat = category.replace("_", " ").title()
        return f"{cat} observation — {locality}, Bali"
    
    def _generate_id(self) -> str:
        """Generate unique profile ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"AQ_{timestamp}"
    
    def _hash_sender(self, sender: str) -> str:
        """Anonymize sender identifier"""
        if not sender:
            return ""
        return hashlib.sha256(sender.encode()).hexdigest()[:16]
    
    # Bukit (south Bali peninsula) bounding box — used for fast
    # locality assignment when we only have GPS. Tight enough to be
    # meaningful, loose enough to cover the whole peninsula south
    # of Jimbaran roundabout.
    BUKIT_BBOX = {
        "lat_min": -8.86,
        "lat_max": -8.74,
        "lon_min": 115.08,
        "lon_max": 115.24,
    }

    # Ordered: longer / more specific names first so "Nusa Dua" matches
    # before "Nusa", "Padang Padang" before "Padang", etc.
    BALI_LOCALITIES = [
        # --- Bukit (pilot area) ---
        ("padang padang", "Padang Padang"),
        ("nusa dua", "Nusa Dua"),
        ("uluwatu", "Uluwatu"),
        ("pecatu", "Pecatu"),
        ("ungasan", "Ungasan"),
        ("balangan", "Balangan"),
        ("bingin", "Bingin"),
        ("jimbaran", "Jimbaran"),
        ("benoa", "Benoa"),
        ("kutuh", "Kutuh"),
        ("bukit", "Bukit"),
        # --- Rest of Bali (for future / overflow reports) ---
        ("canggu", "Canggu"),
        ("seminyak", "Seminyak"),
        ("kerobokan", "Kerobokan"),
        ("kuta", "Kuta"),
        ("legian", "Legian"),
        ("ubud", "Ubud"),
        ("denpasar", "Denpasar"),
        ("sanur", "Sanur"),
        ("tabanan", "Tabanan"),
        ("gianyar", "Gianyar"),
        ("klungkung", "Klungkung"),
        ("amed", "Amed"),
        ("lovina", "Lovina"),
        ("singaraja", "Singaraja"),
    ]

    def _extract_locality(self, report: Dict) -> str:
        """
        Resolve locality with this precedence:
        1. Explicit `locality` field on the report (trusted, e.g. from
           reverse geocoding done elsewhere).
        2. GPS-in-Bukit-bbox → "Bukit" if no finer match is in description.
        3. Keyword match against BALI_LOCALITIES in the description.
        4. Fall back to "Bali".
        """
        # 1. Explicit locality wins
        explicit = report.get("locality")
        if explicit and isinstance(explicit, str):
            return explicit.strip()

        description = (report.get("description") or "").lower()

        # 3. Description keyword match (most specific)
        for key, name in self.BALI_LOCALITIES:
            if key in description:
                return name

        # 2. GPS-based fallback for the Bukit peninsula
        location = report.get("location") or {}
        lat = location.get("lat") if isinstance(location, dict) else None
        lon = location.get("lon") if isinstance(location, dict) else None
        if lat is None:
            lat = report.get("latitude")
        if lon is None:
            lon = report.get("longitude")
        if lat is not None and lon is not None:
            b = self.BUKIT_BBOX
            if b["lat_min"] <= lat <= b["lat_max"] and b["lon_min"] <= lon <= b["lon_max"]:
                return "Bukit"

        # 4. Default
        return "Bali"
    
    def _generate_tags(
        self,
        report: Dict,
        category: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[str]:
        """
        Tags drive Murmurations Index discovery — keep them lowercase,
        short, snake_case. Tomas/other nodes will query against these.
        """
        tags = ["air_quality", "environment", "community_report", "planet_ai"]

        # Category — already normalized by caller
        if category and category not in ("other", "none"):
            tags.append(category)

        # Source channel (whatsapp, telegram, smart_citizen, ...)
        source = report.get("source")
        if source:
            tags.append(f"source:{source}")

        # Severity for action-priority queries
        if severity:
            tags.append(f"severity:{severity}")

        # Bioregion tag for cross-node aggregation
        if self.config.bioregion:
            tags.append(f"bioregion:{self.config.bioregion}")

        # Pilot tag — lets us distinguish pilot-phase Bukit data from
        # later production. Strip later by moving to production node id.
        tags.append("bukit_pilot")

        # Dedupe while preserving order
        seen = set()
        return [t for t in tags if not (t in seen or seen.add(t))]
    
    def _map_status(self, status: Optional[str]) -> str:
        """
        Map the bot's internal report status to a schema-valid
        action_cycle.response_status value.

        Schema enum: observed, reported, under_review, verified,
                     in_response, escalated, resolved, archived
        """
        if not status:
            return "observed"
        mapping = {
            "pending": "observed",       # bot received, awaiting location
            "complete": "reported",      # report has all fields
            "under_review": "under_review",
            "verified": "verified",
            "in_response": "in_response",
            "escalated": "escalated",
            "resolved": "resolved",
            "archived": "archived",
        }
        return mapping.get(status, "observed")
    
    def save(self, filename: str = None, report_id: str = None) -> Path:
        """
        Save the federated profile to the local publish queue.

        Files in LOCAL_PROFILE_DIR are rsynced to planetai.fab.city by
        a cron job, making them publicly accessible at the URL declared
        in profile["primary_url"].

        Args:
            filename: override output filename (defaults to <report_id>.json)
            report_id: explicit report id, used when profile_data doesn't
                       carry it (we strip internal underscore fields).

        Returns:
            Path to saved file in the publish queue.
        """
        if not self.profile_data:
            raise ValueError("No profile data. Call from_aq_report() first.")

        if filename is None:
            # Prefer explicit, then derive from primary_url, then generate
            rid = report_id
            if not rid:
                primary = self.profile_data.get("primary_url", "")
                rid = Path(primary).stem if primary else self._generate_id()
            filename = f"{rid}.json"

        filepath = LOCAL_PROFILE_DIR / filename
        with open(filepath, "w") as f:
            json.dump(self.profile_data, f, indent=2, ensure_ascii=False)
        return filepath

    @staticmethod
    def list_publish_queue() -> List[Path]:
        """Return all profiles currently in the publish queue."""
        return sorted(LOCAL_PROFILE_DIR.glob("AQ_*.json"))
    
    def to_json(self) -> str:
        """Return profile as JSON string"""
        return json.dumps(self.profile_data, indent=2)


class MurmurationsIndexClient:
    """
    Client for interacting with Murmurations Index API.
    Handles posting, updating, and searching profiles.
    """
    
    def __init__(self, config: MurmurationsConfig = None):
        self.config = config or MurmurationsConfig()
        self.base_url = (
            MURMURATIONS_TEST_INDEX if self.config.use_test_index 
            else MURMURATIONS_INDEX_URL
        )
    
    def post_profile(self, profile_url: str) -> Dict[str, Any]:
        """
        Post a profile to the Murmurations Index.
        
        Args:
            profile_url: Publicly accessible URL to profile JSON
            
        Returns:
            Index response with node_id, status, etc.
        """
        endpoint = f"{self.base_url}/nodes"
        
        payload = {"profile_url": profile_url}
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "failed",
                "profile_url": profile_url
            }
    
    def update_profile(self, profile_url: str) -> Dict[str, Any]:
        """
        Update an existing profile in the index.
        (Same as post - index handles updates automatically)
        """
        return self.post_profile(profile_url)
    
    def search(
        self,
        tags: List[str] = None,
        locality: str = None,
        country: str = None,
        schema: str = None,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Search the Murmurations Index for profiles.
        
        Args:
            tags: List of tags to filter by
            locality: City/area name
            country: Country name
            schema: Schema name
            **filters: Additional query parameters
            
        Returns:
            List of matching profiles
        """
        endpoint = f"{self.base_url}/nodes"
        
        params = {}
        if tags:
            params["tags"] = ",".join(tags)
        if locality:
            params["locality"] = locality
        if country:
            params["country"] = country
        if schema:
            params["schema"] = schema
        
        # Add any additional filters
        params.update(filters)
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get("data", [])
        
        except requests.exceptions.RequestException as e:
            return [{"error": str(e)}]
    
    def get_node(self, node_id: str) -> Dict[str, Any]:
        """Get a specific node by ID"""
        endpoint = f"{self.base_url}/nodes/{node_id}"
        
        try:
            response = requests.get(endpoint, timeout=30)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node from the index.
        Note: This requires the node to have been posted with a valid signature.
        """
        endpoint = f"{self.base_url}/nodes/{node_id}"
        
        try:
            response = requests.delete(endpoint, timeout=30)
            return response.status_code == 200
        
        except requests.exceptions.RequestException:
            return False


class PlanetAINode:
    """
    High-level interface for Planet AI Bali node operations.
    Combines profile generation with index management.
    """
    
    def __init__(self, config: MurmurationsConfig = None):
        self.config = config or MurmurationsConfig()
        self.profile_gen = MurmurationsProfile(self.config)
        self.index_client = MurmurationsIndexClient(self.config)
    
    def process_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an AQ report through the full Murmurations pipeline:
        1. Convert to Murmurations profile (sanitized — no PII)
        2. Save to local publish queue (rsync target)
        3. Optionally post to the Murmurations Index

        Returns:
            Dict with profile, file path, and index response (if any).
        """
        profile = self.profile_gen.from_aq_report(report)

        # Use the canonical report id from the local report so the
        # published filename matches its primary_url and stays stable
        # across re-publishes (e.g., when vision results land later).
        report_id = report.get("id")
        profile_path = self.profile_gen.save(report_id=report_id)

        result = {
            "profile": profile,
            "local_path": str(profile_path),
            "profile_url": profile.get("primary_url"),
            "indexed": False,
            "index_response": None,
        }

        # Only post to the index when (a) auto-indexing is on,
        # (b) the URL points to a public host, and (c) the profile is
        # complete enough to be useful (has lat/lon + category).
        if (
            self.config.auto_index
            and self._is_public_url(profile.get("primary_url"))
            and profile.get("latitude") is not None
            and profile.get("longitude") is not None
        ):
            index_response = self.index_client.post_profile(profile.get("primary_url"))
            result["index_response"] = index_response
            result["indexed"] = index_response.get("status") == "posted"

        return result
    
    def _is_public_url(self, url: str) -> bool:
        """Check if URL is publicly accessible (not localhost)"""
        if not url:
            return False
        return not any(x in url for x in ["localhost", "127.0.0.1", "::1", "file://"])
    
    def get_federated_reports(
        self,
        locality: str = None,
        tags: List[str] = None,
        bioregion: str = None
    ) -> List[Dict[str, Any]]:
        """
        Query federated reports from across the Murmurations network.
        
        This is where Planet AI's power emerges - querying not just
        Bali data, but any node using the environmental_observation schema.
        """
        search_tags = tags or []
        search_tags.append("planet_ai")
        
        results = self.index_client.search(
            tags=search_tags,
            locality=locality,
            schema=self.profile_gen.SCHEMA_VERSION
        )
        
        # Filter by bioregion if specified
        if bioregion:
            results = [
                r for r in results 
                if r.get("bioregion") == bioregion
            ]
        
        return results
    
    def sync_with_bioregion(self) -> Dict[str, Any]:
        """
        Sync this node's data with bioregional aggregation.
        Called periodically to update regional dashboards.
        """
        # Get all reports from this bioregion
        reports = self.get_federated_reports(bioregion=self.config.bioregion)
        
        return {
            "node_id": self.config.node_id,
            "bioregion": self.config.bioregion,
            "total_reports": len(reports),
            "localities": list(set(r.get("locality") for r in reports if r.get("locality"))),
            "categories": self._count_categories(reports),
            "reports": reports[:10]  # Last 10 for preview
        }
    
    def _count_categories(self, reports: List[Dict]) -> Dict[str, int]:
        """Count reports by pollution category"""
        counts = {}
        for report in reports:
            cat = report.get("pollution_category", "unknown")
            counts[cat] = counts.get(cat, 0) + 1
        return counts


# Example usage / smoke test
if __name__ == "__main__":
    print("Planet AI Bali — Murmurations Adapter smoke test\n")

    # Sample AQ report, Bukit area (Uluwatu cliff zone)
    # Note: sender is set but MUST NOT appear in the federated profile.
    sample_report = {
        "id": "AQ_20260511_120000",
        "timestamp": "2026-05-11T12:00:00+08:00",
        "source": "whatsapp",
        "sender": "+6281234567890",
        "type": "photo",
        "description": "Trash being burned near Pecatu, thick black smoke drifting toward Uluwatu temple road",
        "location": {"lat": -8.8290, "lon": 115.0850},
        "category": "burning",
        "ai_analysis": {
            "detected": True,
            "confidence": 0.87,
            "indicators": ["thick smoke plume", "open flame", "mixed waste"],
            "description": "Open burning of mixed waste, visible flames and dark smoke",
            "severity": "high",
            "model_version": "phi-3.5-vision-mlx-0.1",
        },
        "status": "complete",
    }

    config = MurmurationsConfig(
        node_id="bali.fab.city",
        bioregion="indo_pacific_coral_triangle",
        primary_url="https://planetai.fab.city/bali",
        use_test_index=True,
        auto_index=False,  # Don't hit the index from a smoke test
    )

    node = PlanetAINode(config)

    print("Processing sample report...")
    result = node.process_report(sample_report)

    print(f"  Profile saved: {result['local_path']}")
    print(f"  Profile URL:   {result['profile_url']}")
    print(f"  Indexed:       {result['indexed']}")

    # Sanity check: no sender info should be in the profile
    profile = result["profile"]
    pii_keys = [k for k in profile if k.startswith("_") or k in ("sender",)]
    assert not pii_keys, f"PII leak in profile: {pii_keys}"
    print(f"  PII check:     OK (no sender fields in profile)")

    print("\nGenerated Murmurations profile:\n")
    print(json.dumps(profile, indent=2, ensure_ascii=False))

    print("\nPublish queue:")
    for p in MurmurationsProfile.list_publish_queue()[-5:]:
        print(f"  {p.name}")

    print("\nDone. Next step: cron rsync profiles/ → planetai.fab.city/bali/profiles/")
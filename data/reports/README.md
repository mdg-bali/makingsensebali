**English** · [Bahasa Indonesia](README.id.md) · [Español](README.es.md)

# `data/reports/` — approved citizen-report profiles

This directory holds the sanitized Murmurations profiles of citizen
reports that have been approved by the campaign operator. Files here
are public artifacts — the home page (`index.html`) and the dashboard
(`dashboard/index.html`) fetch them via `data.js`'s `fetchReports()`
and render them on the map alongside sensor pins.

## Files

- **`index.json`** — manifest listing all approved profile filenames.
  Updated automatically by `reports/sync_profiles.sh` after each
  approval cycle.
- **`AQ_<timestamp_id>.json`** — one file per approved report. Format
  is the Murmurations [`environmental_observation-v1.0.0`](../../reports/schemas/environmental_observation-v1.0.0.json)
  schema. Already PII-stripped by the Sense Making adapter.

## How profiles arrive here

1. A resident sends a WhatsApp report to the bot
2. The bot saves it locally as `pending_review`
3. The operator reviews the report in the local dashboard and clicks
   **Approve**
4. The bot writes a sanitized Murmurations profile to its local
   `profiles/` directory
5. `reports/sync_profiles.sh` (run by cron on the NAS) copies new
   profiles into this `data/reports/` directory, regenerates
   `index.json`, commits, and pushes to GitHub
6. GitHub Pages rebuilds; the map shows the new report

Nothing here should ever be edited by hand except for emergency
removal (e.g., a report approved in error). To remove a profile,
delete its file and remove the filename from `index.json`, then
commit and push.

## Privacy guarantees

- These profiles have already been stripped of sender phone numbers,
  sender hashes, local image paths, and Evolution API media keys
  by `reports/murmurations_adapter.py` before being written.
- The reporter's identity is never recoverable from anything in this
  directory.
- For details, see `reports/README.md` and the privacy section of
  `../../REPLICATION.md`.

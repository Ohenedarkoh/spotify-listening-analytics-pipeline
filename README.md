# Spotify Listening Analytics Pipeline (2026)

This project builds a production-style analytics pipeline for personal Spotify listening data. Each phase will explain what i build and why it matters in real-world data engineering.

## Architecture (Logical Flow)
Spotify Web API
-> Ingestion service (Python)
-> Raw JSON in GCS (date-partitioned)
-> BigQuery raw layer
-> dbt transformations
-> Analytics star schema
-> Dashboard (Metabase/Looker Studio)

## Why This Architecture
- Separate raw storage from curated models to preserve source truth and allow reprocessing.
- Use a warehouse for fast analytics and governance.
- Use dbt for transparent, testable transformations.
- Orchestrate with Kestra to make the pipeline repeatable and reliable.

## Project Phases
- Phase 0: Repo structure + architecture (no code yet)
- Phase 1: Ingestion foundation (OAuth + API extraction)
- Phase 2: Data lake + raw warehouse
- Phase 3: Incremental loading + deduplication
- Phase 4: dbt star schema + tests
- Phase 5: Orchestration + IaC + CI/CD
- Phase 6: Backfill enhancement (Spotify export)

## Constraints
- Spotify API provides limited history; daily ingestion builds history over time.
- Full history requires optional account data export backfill.

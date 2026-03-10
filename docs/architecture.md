# Architecture Notes (Systems and Logic)

## System Goal
Turn raw personal listening events into reliable, analyzable tables that answer questions like:
- What do I listen to most over time?
- Which artists/albums are trending in my behavior?
- How do my listening patterns shift by day/week/month?

## Core Design Principles
- **Separation of concerns**: ingestion, storage, transformation, and analytics are independent layers.
- **Immutability at the edge**: raw data is stored exactly as received for traceability and replay.
- **Incremental processing**: new data is appended; re-runs must not create duplicates.
- **Data quality visibility**: tests make assumptions explicit and measurable.

## Logical Data Flow
1) **Ingestion (Source Boundary)**
   - Spotify API provides personal listening events within its access limits.
   - Ingestion converts API responses into raw JSON files.

2) **Data Lake (Raw Persistence)**
   - Raw files are stored by ingestion date.
   - This is the long-term “source of truth” for replay and audit.

3) **Warehouse Raw Layer**
   - Raw JSON is loaded into BigQuery tables.
   - Tables are partitioned by ingestion date to keep queries efficient.

4) **Transformation Layer (dbt)**
   - Raw tables are cleaned, deduplicated, and modeled.
   - Dimensions (artist/album/track/time) describe entities.
   - Fact table (listening events) captures behavior at a clear grain.

5) **Analytics Layer**
   - Curated star schema supports dashboards and metrics.

## Why This Works in Real Systems
- It isolates failures and makes debugging possible (raw data never changes).
- It supports both small and growing datasets.
- It mirrors patterns used in production analytics teams.

## Data Limitations and Backfill Strategy
- Spotify API does not provide full lifetime listening history.
- Daily ingestion grows the dataset forward.
- Optional account data export can be used to backfill history.

## Orchestration and Reliability
- A scheduler (Kestra) coordinates steps to ensure consistent daily runs.
- Retries and idempotency are required because APIs fail and jobs rerun.

## Security and Access
- OAuth tokens are required to access personal data.
- Secrets are stored outside code (env vars or secret managers).

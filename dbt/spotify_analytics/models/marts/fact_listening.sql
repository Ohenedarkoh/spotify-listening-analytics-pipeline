{{
  config(
    materialized='table',
    partition_by={
      "field": "played_at_ts",
      "data_type": "timestamp",
      "granularity": "day"
    },
    cluster_by=["track_id", "artist_id"]
  )
}}

-- Fact table at listening event grain.
-- Partition by day for time-window queries and cluster by common filter/group keys.
select
  played_at_ts,
  track_id,
  album_id,
  artist_id
from {{ ref('stg_listening_history') }}
where played_at_ts is not null

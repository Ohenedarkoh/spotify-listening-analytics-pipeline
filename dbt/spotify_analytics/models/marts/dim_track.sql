-- One row per track_id (aggregate)
select
  track_id,
  any_value(track_name) as track_name,
  any_value(album_id) as album_id,
  max(duration_ms) as duration_ms,
  max(track_popularity) as track_popularity
from {{ ref('stg_listening_history') }}
where track_id is not null
group by track_id

-- Fact table at listening event grain
select
  played_at_ts,
  track_id,
  album_id,
  artist_id
from {{ ref('stg_listening_history') }}
where played_at_ts is not null

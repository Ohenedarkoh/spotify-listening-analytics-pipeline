-- Flatten raw listening events into a clean staging view
select
  timestamp(played_at) as played_at_ts,
  played_at as played_at_raw,
  track.id as track_id,
  track.name as track_name,
  track.duration_ms as duration_ms,
  track.popularity as track_popularity,
  track.album.id as album_id,
  track.album.name as album_name,
  track.artists[SAFE_OFFSET(0)].id as artist_id,
  track.artists[SAFE_OFFSET(0)].name as artist_name
from {{ source('spotify_raw', 'listening_history_raw') }}

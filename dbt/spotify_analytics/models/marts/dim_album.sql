-- Unique albums from staging
select distinct
  album_id,
  album_name,
  artist_id
from {{ ref('stg_listening_history') }}
where album_id is not null

-- Unique artists from staging
select distinct
  artist_id,
  artist_name
from {{ ref('stg_listening_history') }}
where artist_id is not null

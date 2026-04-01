-- Time dimension from play timestamps
select distinct
  played_at_ts as ts,
  date(played_at_ts) as date,
  extract(year from played_at_ts) as year,
  extract(month from played_at_ts) as month,
  extract(day from played_at_ts) as day,
  extract(hour from played_at_ts) as hour
from {{ ref('stg_listening_history') }}
where played_at_ts is not null

SELECT
  id AS gameweek_id,
  name,
  deadline_time,
FROM
  `leverageai-sandbox.source.ext_fpl_api_bootstrap_static_events`
WHERE
  source_date=(SELECT MAX(source_date) FROM `leverageai-sandbox.source.ext_fpl_api_bootstrap_static_events`)
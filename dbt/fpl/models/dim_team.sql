SELECT
  id AS team_id,
  name AS team_name,
  short_name,
FROM
  `leverageai-sandbox.source.ext_fpl_api_bootstrap_static_teams`
WHERE
  source_date=(SELECT MAX(source_date) FROM `leverageai-sandbox.source.ext_fpl_api_bootstrap_static_teams`)
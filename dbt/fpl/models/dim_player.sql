SELECT
  id AS player_id,
  first_name,
  second_name AS last_name,
FROM
  `leverageai-sandbox.source.ext_fpl_api_bootstrap_static_elements`
WHERE
  source_date=(SELECT MAX(source_date) FROM `leverageai-sandbox.source.ext_fpl_api_bootstrap_static_elements`)
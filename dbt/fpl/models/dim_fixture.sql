SELECT
  id AS fixture_id,
  event AS gameweek_id,
  team_h AS home_team_id,
  team_a AS away_team_id,
  kickoff_time,
FROM
  `leverageai-sandbox.source.ext_fpl_api_fixtures`
WHERE
  source_date=(SELECT MAX(source_date) FROM `leverageai-sandbox.source.ext_fpl_api_fixtures`)
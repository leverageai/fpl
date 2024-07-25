{{
  config(
    materialized='table'
  )
}}

WITH
events AS 
(
  SELECT
    id AS fixture_id,
    event AS gameweek_id,
    team_h AS home_team_id,
    team_a AS away_team_id,
    team_h_difficulty AS home_team_difficulty,
    team_a_difficulty AS away_team_difficulty,
    team_h_score AS home_team_score,
    team_a_score AS away_team_score,
    stats
  FROM
    `leverageai-sandbox.source.ext_fpl_api_fixtures`
  WHERE
    source_date=(SELECT MAX(source_date) FROM `leverageai-sandbox.source.ext_fpl_api_fixtures`)
),
home_stats AS (
SELECT
  fixture_id,
  gameweek_id,
  home_team_id AS team_id,
  home_team_id,
  away_team_id,
  home_team_difficulty,
  away_team_difficulty,
  home_team_score,
  away_team_score,
  flattened_stats.identifier,
  flattened_stats_h.element AS player_id,
  flattened_stats_h.value,
FROM
  events
CROSS JOIN 
  UNNEST(events.stats) AS flattened_stats
CROSS JOIN 
  UNNEST(flattened_stats.h) AS flattened_stats_h
),
away_stats AS (
SELECT
  fixture_id,
  gameweek_id,
  away_team_id AS team_id,
  home_team_id,
  away_team_id,
  home_team_difficulty,
  away_team_difficulty,
  home_team_score,
  away_team_score,
  flattened_stats.identifier,
  flattened_stats_a.element AS player_id,
  flattened_stats_a.value,
FROM
  events
CROSS JOIN 
  UNNEST(events.stats) AS flattened_stats
CROSS JOIN 
  UNNEST(flattened_stats.a) AS flattened_stats_a
),
all_stats AS (
  SELECT * FROM home_stats
  UNION ALL
  SELECT * FROM away_stats
),
events_stats AS (
  SELECT
    player_id,
    team_id,
    fixture_id,
    gameweek_id,
    home_team_id,
    away_team_id,
    home_team_difficulty,
    away_team_difficulty,
    home_team_score,
    away_team_score,
    IFNULL(goals_scored,0) AS goals_scored,
    IFNULL(assists,0) AS assists,
    IFNULL(clean_sheets,0) AS clean_sheets,
    IFNULL(goals_conceded,0) AS goals_conceded,
    IFNULL(own_goals,0) AS own_goals,
    IFNULL(penalties_saved,0) AS penalties_saved,
    IFNULL(penalties_missed,0) AS penalties_missed,
    IFNULL(yellow_cards,0) AS yellow_cards,
    IFNULL(red_cards,0) AS red_cards,
    IFNULL(saves,0) AS saves,
    IFNULL(bonus,0) AS bonus,
    IFNULL(bps,0) AS bonus_points_system,
  FROM
    all_stats
  PIVOT(
    SUM(value) FOR identifier IN (
      'goals_scored',
      'assists',
      'clean_sheets',
      'goals_conceded',
      'own_goals',
      'penalties_saved',
      'penalties_missed',
      'yellow_cards',
      'red_cards',
      'saves',
      'bonus',
      'bps'
    )
  )
),
player_stats AS (
  SELECT
    id AS player_id,
    event_id AS gameweek_id,
    minutes,
    starts,
    expected_goals,
    expected_assists,
    expected_goal_involvements,
    expected_goals_conceded,
  FROM
    `leverageai-sandbox.source.ext_fpl_api_event_stats`
  WHERE
    source_date=(SELECT MAX(source_date) FROM `leverageai-sandbox.source.ext_fpl_api_event_stats`)
)
SELECT
  events_stats.player_id,
  events_stats.team_id,
  events_stats.fixture_id,
  events_stats.gameweek_id,
  events_stats.home_team_id,
  events_stats.away_team_id,
  home_team_difficulty,
  away_team_difficulty,
  home_team_score,
  away_team_score,
  IFNULL(minutes,0) AS minutes,
  IFNULL(goals_scored,0) AS goals_scored,
  IFNULL(assists,0) AS assists,
  IFNULL(clean_sheets,0) AS clean_sheets,
  IFNULL(goals_conceded,0) AS goals_conceded,
  IFNULL(own_goals,0) AS own_goals,
  IFNULL(penalties_saved,0) AS penalties_saved,
  IFNULL(penalties_missed,0) AS penalties_missed,
  IFNULL(yellow_cards,0) AS yellow_cards,
  IFNULL(red_cards,0) AS red_cards,
  IFNULL(saves,0) AS saves,
  IFNULL(bonus,0) AS bonus,
  IFNULL(bonus_points_system,0) AS bonus_points_system,
  IFNULL(starts,0) AS starts,
  IFNULL(expected_goals,0) AS expected_goals,
  IFNULL(expected_assists,0) AS expected_assists,
  IFNULL(expected_goal_involvements,0) AS expected_goal_involvements,
  IFNULL(expected_goals_conceded,0) AS expected_goals_conceded,
FROM
  events_stats
LEFT OUTER JOIN
  player_stats
  ON events_stats.player_id=player_stats.player_id
  AND events_stats.gameweek_id=player_stats.gameweek_id
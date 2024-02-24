/*
 * Create external table from FPL API bootstrap static total players
 */
CREATE EXTERNAL TABLE IF NOT EXISTS `source.ext_fpl_api_bootstrap_static_total_players`
(
  `total_players` INT64
)
WITH PARTITION COLUMNS
OPTIONS (
  format="CSV",
  uris=["gs://leverageai-sandbox-data/staging/source_name=fpl_api_bootstrap_static/element=total_players/*.jsonl"],
  hive_partition_uri_prefix="gs://leverageai-sandbox-data/staging/source_name=fpl_api_bootstrap_static/element=total_players/"
)
;
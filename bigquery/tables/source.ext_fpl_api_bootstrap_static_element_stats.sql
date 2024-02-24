/*
 * Create external table from FPL API bootstrap static element stats
 */
CREATE EXTERNAL TABLE IF NOT EXISTS `source.ext_fpl_api_bootstrap_static_element_stats`
WITH PARTITION COLUMNS
OPTIONS (
  format="JSON",
  uris=["gs://leverageai-sandbox-data/staging/source_name=fpl_api_bootstrap_static/element=element_stats/*.jsonl"],
  hive_partition_uri_prefix="gs://leverageai-sandbox-data/staging/source_name=fpl_api_bootstrap_static/element=element_stats/"
)
;
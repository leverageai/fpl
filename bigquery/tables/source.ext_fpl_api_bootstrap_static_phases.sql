/*
 * Create external table from FPL API bootstrap static phases
 */
CREATE EXTERNAL TABLE IF NOT EXISTS `source.ext_fpl_api_bootstrap_static_phases`
WITH PARTITION COLUMNS
OPTIONS (
  format="JSON",
  uris=["gs://leverageai-sandbox-data/staging/source_name=fpl_api_bootstrap_static/element=phases/*.jsonl"],
  hive_partition_uri_prefix="gs://leverageai-sandbox-data/staging/source_name=fpl_api_bootstrap_static/element=phases/"
)
;
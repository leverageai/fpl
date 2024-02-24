/*
 * Create external table from FPL API bootstrap static elements
 */
CREATE EXTERNAL TABLE IF NOT EXISTS `source.ext_fpl_api_bootstrap_static_elements`
WITH PARTITION COLUMNS
OPTIONS (
  format="JSON",
  uris=["gs://leverageai-sandbox-data/staging/source_name=fpl_api_bootstrap_static/element=elements/*.jsonl"],
  hive_partition_uri_prefix="gs://leverageai-sandbox-data/staging/source_name=fpl_api_bootstrap_static/element=elements/"
)
;
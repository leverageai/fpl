/*
 * Create external table from FPL API fixtures
 */
CREATE EXTERNAL TABLE IF NOT EXISTS `source.ext_fpl_api_fixtures`
WITH PARTITION COLUMNS
OPTIONS (
  format="JSON",
  uris=["gs://leverageai-sandbox-data/staging/source_name=fpl_api_fixtures/*.jsonl"],
  hive_partition_uri_prefix="gs://leverageai-sandbox-data/staging/source_name=fpl_api_fixtures/"
)
;
/*
 * Create external table from FPL API event explain
 */
CREATE EXTERNAL TABLE IF NOT EXISTS `source.ext_fpl_api_event_explain`
WITH PARTITION COLUMNS
OPTIONS (
  format="CSV",
  uris=["gs://leverageai-sandbox-data/staging/source_name=fpl_api_event/element=explain/*.csv"],
  hive_partition_uri_prefix="gs://leverageai-sandbox-data/staging/source_name=fpl_api_event/element=explain/"
)
;
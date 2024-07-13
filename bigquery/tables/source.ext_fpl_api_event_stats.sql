/*
 * Create external table from FPL API event stats
 */
CREATE EXTERNAL TABLE IF NOT EXISTS `source.ext_fpl_api_event_stats`
WITH PARTITION COLUMNS
OPTIONS (
  format="CSV",
  uris=["gs://leverageai-sandbox-data/staging/source_name=fpl_api_event/element=stats/*.csv"],
  hive_partition_uri_prefix="gs://leverageai-sandbox-data/staging/source_name=fpl_api_event/element=stats/"
)
;
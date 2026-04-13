## 1. Extend Exporter

- [x] 1.1 Add `get_rogues()` method to UnleashedClient that POSTs `<rogue/>` query and parses each `<rogue>` element including its `<detection>` children
- [x] 1.2 Define new Prometheus gauges: `unleashed_rogue_rssi_dbm` (with full label set), `unleashed_rogue_count`, `unleashed_rogue_malicious_count`, `unleashed_rogue_count_by_band`, `unleashed_rogue_count_by_channel`
- [x] 1.3 Add `update_rogue_metrics()` that processes the parsed rogues, sets per-rogue-per-detector RSSI gauges, computes summary aggregations, and cleans up stale rogue metrics
- [x] 1.4 Call `get_rogues()` in main poll loop alongside existing client/AP queries
- [x] 1.5 Map rogue-type to is_malicious boolean label (malicious if string contains "malicious")

## 2. Tests

- [x] 2.1 Create mock fixture `tests/mock/fixtures/rogue_response.py` with realistic rogue XML (one regular AP, one malicious same-network, one multi-detector)
- [x] 2.2 Write `tests/mock/test_rogue_metrics.py` with tests for: XML parsing, RSSI value extraction, malicious classification, summary aggregations (count, malicious_count, by_band, by_channel), stale cleanup
- [x] 2.3 Run all mock tests and verify all pass

## 3. Verify Against Live AP

- [x] 3.1 Rebuild and restart unleashed-exporter container
- [x] 3.2 Verify `/metrics` endpoint returns rogue metrics with real data from live AP
- [x] 3.3 Confirm Prometheus successfully scrapes new metrics

## 4. Documentation

- [x] 4.1 Update METRICS.md with rogue metrics section
- [x] 4.2 Update README.md available metrics list

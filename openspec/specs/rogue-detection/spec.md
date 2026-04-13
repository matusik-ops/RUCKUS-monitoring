## ADDED Requirements

### Requirement: Exporter polls rogue AP data via _cmdstat.jsp
The system SHALL extend the Unleashed exporter to POST `<ajax-request action='getstat' comp='stamgr' enable-gzip='0'><rogue/></ajax-request>` to `_cmdstat.jsp` each poll cycle and parse the XML response for `<rogue>` elements (each containing one or more `<detection>` child elements).

#### Scenario: Successful rogue poll
- **WHEN** the exporter's poll interval elapses
- **THEN** the exporter queries client stats, AP stats, and rogue stats — all in the same poll cycle

#### Scenario: Rogue query fails
- **WHEN** the rogue query returns an error or empty response
- **THEN** the exporter logs an error and increments the error counter; client and AP metrics are unaffected

### Requirement: Per-rogue detection metrics are exposed
The system SHALL expose a gauge `unleashed_rogue_rssi_dbm` (negative dBm value, derived from the `rssi` attribute as `-rssi`) per rogue+detector pair. Labels: `rogue_mac`, `rogue_ssid`, `rogue_channel`, `rogue_band` (2.4g/5g), `rogue_type`, `is_malicious` (true/false), `detector_ap` (sys-name of detecting AP).

#### Scenario: Rogue seen by multiple APs
- **WHEN** a rogue MAC is detected by 3 different APs
- **THEN** 3 separate metric samples are exposed, one per detector with its own RSSI value

#### Scenario: Malicious rogue
- **WHEN** the rogue-type field is "malicious AP (Same-Network)"
- **THEN** the metric sample has `is_malicious="true"`

### Requirement: Rogue summary metrics are exposed
The system SHALL expose summary gauges derived from the rogue list:
- `unleashed_rogue_count` — total unique rogue MACs detected
- `unleashed_rogue_malicious_count` — total rogues classified as malicious
- `unleashed_rogue_count_by_band{radio_band}` — rogue count per 2.4g/5g
- `unleashed_rogue_count_by_channel{channel, radio_band}` — rogue count per channel

#### Scenario: 20 rogues across both bands
- **WHEN** 12 rogues are on 2.4GHz and 8 on 5GHz, with 2 marked malicious
- **THEN** `unleashed_rogue_count = 20`, `unleashed_rogue_malicious_count = 2`, `unleashed_rogue_count_by_band{radio_band="2.4g"} = 12`, `unleashed_rogue_count_by_band{radio_band="5g"} = 8`

### Requirement: Stale rogue metrics are cleaned up
The system SHALL remove metric samples for rogue+detector pairs that no longer appear in the latest poll response, so Prometheus does not retain stale rogue data.

#### Scenario: Rogue disappears
- **WHEN** a rogue MAC that was previously detected no longer appears in the rogue XML response
- **THEN** all metric samples for that rogue MAC are removed from the exporter's `/metrics` output

### Requirement: Rogue collection is independently testable
The system SHALL include mock test fixtures with sample rogue XML responses (representative of real data observed: regular APs, malicious same-network APs, multi-detector rogues) and unit tests covering: parsing, label assignment, malicious flag, summary aggregations, and stale cleanup.

#### Scenario: Mock test for malicious classification
- **WHEN** a mock rogue XML contains a "malicious AP (Same-Network)" entry
- **THEN** the test verifies the metric sample has `is_malicious="true"` and is included in `unleashed_rogue_malicious_count`

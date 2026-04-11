## ADDED Requirements

### Requirement: Exporter collects per-AP, per-radio stats from _cmdstat.jsp
The system SHALL extend the Unleashed exporter to also POST `<ajax-request action='getstat' comp='stamgr' enable-gzip='0'><ap LEVEL='1'/></ajax-request>` to _cmdstat.jsp each poll cycle, parsing the XML response for per-AP and per-radio `<radio>` child elements.

#### Scenario: Successful AP stats poll
- **WHEN** the exporter's poll interval elapses
- **THEN** the exporter queries both client stats and AP stats, parsing radio elements from each connected AP

#### Scenario: AP stats query fails
- **WHEN** the AP stats query returns an error or empty response
- **THEN** the exporter logs an error and increments the error counter; client metrics are unaffected

### Requirement: Per-radio airtime metrics are exposed
The system SHALL expose per-radio airtime as Prometheus gauges: `unleashed_radio_airtime_total`, `unleashed_radio_airtime_busy`, `unleashed_radio_airtime_rx`, `unleashed_radio_airtime_tx`. Labeled by `ap_name`, `radio_band` (2.4g/5g), `channel`.

#### Scenario: Radio with moderate airtime
- **WHEN** AP05 5GHz radio reports airtime-total=51, airtime-busy=0, airtime-rx=32, airtime-tx=19
- **THEN** the exporter exposes four gauge metrics with those values

### Requirement: Per-radio client count and avg RSSI are exposed
The system SHALL expose `unleashed_radio_num_sta` (client count per radio) and `unleashed_radio_avg_rssi` (average client RSSI per radio). Labeled by `ap_name`, `radio_band`, `channel`.

#### Scenario: Radio with clients
- **WHEN** AP05 2.4GHz radio has num-sta=4 and avg-rssi=50
- **THEN** the exporter exposes gauge metrics with those values

### Requirement: Per-radio traffic counters are exposed
The system SHALL expose `unleashed_radio_tx_bytes_total`, `unleashed_radio_rx_bytes_total`, `unleashed_radio_tx_pkts_total`, `unleashed_radio_rx_pkts_total`. Labeled by `ap_name`, `radio_band`, `channel`.

#### Scenario: Active radio
- **WHEN** a radio has non-zero traffic counters
- **THEN** the exporter exposes gauge metrics for all four counters

### Requirement: Per-radio Tx quality metrics are exposed
The system SHALL expose `unleashed_radio_tx_fail_total`, `unleashed_radio_retries_total`, `unleashed_radio_rx_decrypt_error_total`, `unleashed_radio_fcs_error_total`. Labeled by `ap_name`, `radio_band`, `channel`.

#### Scenario: Radio with retries
- **WHEN** AP05 5GHz radio has radio-total-retries=23778 and radio-total-tx-fail=58
- **THEN** the exporter exposes gauge metrics with those values

### Requirement: Per-radio auth/assoc counters are exposed
The system SHALL expose `unleashed_radio_auth_fail`, `unleashed_radio_auth_success`, `unleashed_radio_assoc_fail`, `unleashed_radio_assoc_success`. Labeled by `ap_name`, `radio_band`, `channel`.

#### Scenario: Radio with auth failures
- **WHEN** AP06 5GHz radio has mgmt-auth-fail=2508
- **THEN** the exporter exposes a gauge metric with that value

### Requirement: Per-radio config info is exposed
The system SHALL expose `unleashed_radio_channel`, `unleashed_radio_tx_power`, `unleashed_radio_channelization` as gauges. Labeled by `ap_name`, `radio_band`.

#### Scenario: Radio config visible
- **WHEN** AP05 5GHz radio is on channel 149 with channelization 40
- **THEN** the exporter exposes gauge metrics for channel=149 and channelization=40

### Requirement: Disconnected AP radios are excluded
The system SHALL only expose radio metrics for APs with state=1 (connected). Disconnected APs (state=0) SHALL be excluded, and stale metrics for disconnected APs SHALL be removed.

#### Scenario: AP disconnects
- **WHEN** an AP that was previously connected changes to state=0
- **THEN** the exporter removes all radio metrics for that AP

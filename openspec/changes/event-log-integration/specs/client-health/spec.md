## MODIFIED Requirements

### Requirement: Per-client RSSI and noise floor metrics are collected
The system SHALL expose per-client signal metrics: received-signal-strength (dBm) as `unleashed_client_rssi_dbm`, rssi (AP-reported SNR-like value) as `unleashed_client_snr_db`, and noise-floor (dBm) as `unleashed_client_noise_floor_dbm`. Labeled by client MAC, AP name, SSID, radio band, and hostname.

Additionally, the Client Health dashboard SHALL display per-client auth failure count from `unleashed_auth_fail_total` alongside signal metrics, enabling correlation of auth failures with signal quality.

#### Scenario: Client with good signal
- **WHEN** a client has received-signal-strength of -54 dBm, rssi of 42, and noise-floor of -96 dBm
- **THEN** the exporter exposes gauge metrics with those values and labels including hostname

#### Scenario: Client with poor signal
- **WHEN** a client has received-signal-strength of -73 dBm
- **THEN** the exporter exposes the value, enabling alerting and dashboard visualization

#### Scenario: Client with auth failures
- **WHEN** a client has accumulated auth failures
- **THEN** the Client Health dashboard shows the auth failure count alongside signal metrics for that client

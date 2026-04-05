# client-health Specification

## Purpose
TBD - created by archiving change ruckus-r720-monitoring-dashboard. Update Purpose after archive.
## Requirements
### Requirement: Custom Prometheus exporter collects per-client metrics from Unleashed web API
The system SHALL include a Python-based Prometheus exporter that authenticates to the Ruckus Unleashed _cmdstat.jsp XML/AJAX interface (login via GET /admin/login.jsp with credentials, then fetch CSRF token from /admin/_csrfTokenVar.jsp) and polls per-client station data with interval stats via POST to /admin/_cmdstat.jsp with XML payload `<client INTERVAL-STATS='yes' .../>`, exposing metrics in Prometheus format on a /metrics HTTP endpoint. Interval stats provide additional per-client fields (tx-rate, total-rx-bytes, total-tx-bytes) not available in the base client list.

#### Scenario: Successful API poll
- **WHEN** the exporter's poll interval elapses
- **THEN** the exporter authenticates (if needed), posts a client list XML request with INTERVAL-STATS to _cmdstat.jsp, parses the XML response including interval-stats child elements, and updates Prometheus metrics

#### Scenario: API authentication failure
- **WHEN** login.jsp does not set a session cookie (wrong credentials)
- **THEN** the exporter logs an error and exposes an error counter metric; it retries authentication on the next poll cycle

#### Scenario: Session expired
- **WHEN** _cmdstat.jsp redirects to login.jsp (session expired)
- **THEN** the exporter re-authenticates, re-fetches CSRF token, and retries the request

#### Scenario: API unreachable
- **WHEN** the Unleashed AP does not respond to HTTPS requests
- **THEN** the exporter logs an error and exposes an error counter metric; previously collected metrics remain until the next successful poll

### Requirement: Per-client RSSI and noise floor metrics are collected
The system SHALL expose per-client signal metrics: received-signal-strength (dBm) as `unleashed_client_rssi_dbm`, rssi (AP-reported SNR-like value) as `unleashed_client_snr_db`, and noise-floor (dBm) as `unleashed_client_noise_floor_dbm`. Labeled by client MAC, AP name, SSID, radio band, and hostname.

#### Scenario: Client with good signal
- **WHEN** a client has received-signal-strength of -54 dBm, rssi of 42, and noise-floor of -96 dBm
- **THEN** the exporter exposes gauge metrics with those values and labels including hostname

#### Scenario: Client with poor signal
- **WHEN** a client has received-signal-strength of -73 dBm
- **THEN** the exporter exposes the value, enabling alerting and dashboard visualization

### Requirement: Per-client data rate metric is collected
The system SHALL expose per-client Tx data rate as `unleashed_client_tx_rate_kbps` (in Kbps, e.g., 135000 = 135 Mbps), sourced from the `tx-rate` field in the interval-stats child element. Labeled by client MAC, AP name, SSID, radio band, and hostname.

#### Scenario: Client connected at high data rate
- **WHEN** a client has tx-rate of 135000.0 on 5GHz
- **THEN** the exporter exposes a gauge metric with value 135000

### Requirement: Per-client traffic metrics are collected
The system SHALL expose per-client total Rx/Tx bytes as `unleashed_client_rx_bytes_total` and `unleashed_client_tx_bytes_total`, sourced from `total-rx-bytes` and `total-tx-bytes` in the XML response. Labeled by client MAC, AP name, SSID, radio band, and hostname.

#### Scenario: Active client
- **WHEN** a client has total-rx-bytes of 999638 and total-tx-bytes of 2277824
- **THEN** the exporter exposes gauge metrics with those values

### Requirement: Per-client association time is collected
The system SHALL expose per-client association start time as `unleashed_client_assoc_time_seconds` (unix timestamp), sourced from the `first-assoc` field. Labeled by client MAC, AP name, SSID, radio band, and hostname.

#### Scenario: Client associated since a known time
- **WHEN** a client has first-assoc of 1775364286
- **THEN** the exporter exposes a gauge metric with that unix timestamp value

### Requirement: Per-client channel metric is collected
The system SHALL expose the wireless channel each client is connected to as `unleashed_client_channel`, labeled by client MAC, AP name, SSID, radio band, and hostname.

#### Scenario: Clients on different channels
- **WHEN** clients are connected on channels 6, 44, and 153
- **THEN** the exporter exposes channel gauge metrics for each client

### Requirement: Client count per SSID and per AP are derived
The system SHALL expose `unleashed_clients_per_ssid` (labeled by SSID) and `unleashed_clients_per_ap` (labeled by AP name), derived from the client station list, plus `unleashed_client_count` as total count.

#### Scenario: Multiple SSIDs and APs active
- **WHEN** clients are connected across 2 SSIDs and 3 APs
- **THEN** the exporter exposes count gauges for each SSID and each AP

### Requirement: Exporter credentials are configurable via environment variables
The system SHALL read UNLEASHED_API_URL, UNLEASHED_USERNAME, and UNLEASHED_PASSWORD from environment variables so that credentials are not hardcoded.

#### Scenario: Configuring credentials
- **WHEN** an operator sets the environment variables in the .env file
- **THEN** the exporter uses those values to authenticate with the Unleashed web API

### Requirement: Exporter poll interval is configurable
The system SHALL allow the poll interval to be configured via UNLEASHED_POLL_INTERVAL, with a default of 60 seconds.

#### Scenario: Default poll interval
- **WHEN** no custom poll interval is set
- **THEN** the exporter polls every 60 seconds

### Requirement: Client disconnection is reflected in metrics
The system SHALL remove metrics for clients that are no longer in the station list, so that stale client data does not persist. Stale SSID and AP count entries SHALL also be removed.

#### Scenario: Client disconnects
- **WHEN** a client that was previously connected no longer appears in the XML response
- **THEN** the exporter removes that client's metrics from the /metrics output


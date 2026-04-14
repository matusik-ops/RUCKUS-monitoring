## ADDED Requirements

### Requirement: Extend exporter with additional per-client fields
The system SHALL extend the Unleashed web API exporter to collect and expose the following per-client fields currently present in the XML response but not yet exported:
- Identity: IP address (`ip`), VLAN (`vlan`), device type (`dvctype`), OS/model (`model`), encryption method (`encryption`), authentication method (`auth-method`)
- Quality: per-client total retries (`total-retries`), retry bytes (`total-retry-bytes`), Rx/Tx packet counts (`total-rx-pkts`, `total-tx-pkts`)
- Signal history: min/max received-signal-strength from interval-stats child element

These SHALL be exposed as a new `unleashed_client_info` gauge (with textual labels) and numeric metrics `unleashed_client_retries_total`, `unleashed_client_retry_bytes_total`, `unleashed_client_rx_pkts_total`, `unleashed_client_tx_pkts_total`, `unleashed_client_min_rssi_dbm`, `unleashed_client_max_rssi_dbm`.

#### Scenario: Client inventory data collected
- **WHEN** the exporter polls and receives a client with ip=10.91.2.133, vlan=2, dvctype=Laptop, model="Windows 10/11"
- **THEN** `unleashed_client_info` exposes a sample with those values as labels

#### Scenario: Per-client retries collected
- **WHEN** a client has 127 total-retries and 12345 total-tx-pkts
- **THEN** `unleashed_client_retries_total` and `unleashed_client_tx_pkts_total` expose those values, enabling retry-rate queries

### Requirement: Clients Overview dashboard
The system SHALL provide a Grafana dashboard "Clients Overview" with a large sortable table showing all connected clients with columns: Hostname, MAC, OS, IP, VLAN, AP, SSID, Band, Channel, Encryption, Auth Method, RSSI (dBm), SNR, Noise, Link Speed (Mbps), Current Rx Mbps, Current Tx Mbps, Total Rx, Total Tx, Retries, Connected Since, Association Duration.

#### Scenario: Finding a client
- **WHEN** an operator views Clients Overview
- **THEN** they can see all connected clients with their full profile and sort by any column

#### Scenario: Filtering clients
- **WHEN** an operator uses template variable filters (AP, SSID, Band)
- **THEN** the table updates to show only matching clients

### Requirement: Client Health dashboard
The system SHALL provide a Grafana dashboard "Client Health" focused on per-client quality:
- Fleet KPIs: Total clients, Clients with Good Signal %, Average RSSI, Weak-signal client count, High-retry client count
- Per-client retry rate panel (retry % as WiFi packet-loss proxy)
- Time-series: RSSI, SNR, Link Speed per client with template variables
- Problem tables: Weak signal clients (RSSI < -70), High retry clients (>10%), Low link rate clients (<30 Mbps)
- Documentation panel explaining retry rate as packet-loss proxy and noting latency/jitter require external probes

#### Scenario: Quality at a glance
- **WHEN** operator views Client Health
- **THEN** they immediately see how many clients are struggling (weak signal, high retries, low rate)

#### Scenario: Drilling into a specific client
- **WHEN** operator selects a client MAC from template variable
- **THEN** RSSI/SNR/link speed time-series filter to that client

### Requirement: Retry rate computed as packet-loss proxy
The Client Health dashboard SHALL compute per-client retry rate as `rate(retries[5m]) / rate(tx_pkts[5m]) * 100` and display it with thresholds: green <2%, yellow 2-10%, red >10%. A text panel SHALL explain that this is the MAC-layer equivalent of packet loss and that true ICMP latency/jitter/packet-loss requires a separate probe collector.

#### Scenario: Client with high retry rate
- **WHEN** a client has retry rate 25%
- **THEN** the metric displays in red and the client appears in the "High retry clients" table

### Requirement: Old Client Health dashboard replaced
The existing `grafana/dashboards/client-health.json` SHALL be replaced by the two new dashboards. The UID `ruckus-client-health` SHALL be reused for the new Client Health dashboard to preserve existing bookmarks/links. A new UID `ruckus-clients-overview` SHALL be assigned to the inventory dashboard.

#### Scenario: Existing bookmark still works
- **WHEN** a user opens `/d/ruckus-client-health`
- **THEN** they see the new Client Health dashboard at the expected URL

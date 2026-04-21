# Grafana Dashboard Guide

This guide explains every panel across all four dashboards.

---

## 1. Ruckus Network Overview

High-level view of the entire wireless network. Use this as your starting point.

### Network Status (top row)

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Active Issues** | Count of: weak-signal clients (RSSI < -70) + APs with auth fail rate > 5% + radios with airtime > 40% | Red = multiple issues need attention |
| **Total Throughput** | Combined Tx+Rx bandwidth across all APs (from SNMP) | Dropping suddenly = problem |
| **APs with Clients** | How many APs have at least one client connected vs total APs | If fewer than total, some APs may be unused or down |
| **Weak-Signal Clients** | Count of clients with RSSI worse than -70 dBm | These clients have slow, unreliable connections |
| **APs Online** | Number of APs currently reporting to the master (from SNMP) | Should match expected AP count |
| **Total Clients** | Total connected clients across all APs and bands | Baseline for your network load |
| **Master CPU** | CPU usage on the master AP | Above 80% = master is overloaded |
| **Master Memory** | Memory usage on the master AP | Above 80% = risk of instability |
| **Exporter** | Whether the unleashed-exporter can reach the AP API | DOWN = no data collection |
| **Internet** | ICMP ping to 8.8.8.8 / 1.1.1.1 via blackbox_exporter | DOWN = internet outage |
| **SNMP** | Whether the SNMP exporter can reach the AP | DOWN = no SNMP metrics |
| **Master Uptime** | How long since the master AP last rebooted | Short uptime = recent reboot/crash |
| **Auth'd / All Clients** | Authenticated clients vs total associated (from SNMP) | Big difference = auth problems |
| **Registered / Online APs** | Registered APs vs actually online | Difference = AP is down |
| **Exporter Polls/Errors** | How often the exporter polls and any errors | Errors = API connection issues |

### Per-AP Health

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Throughput per AP** | Combined Tx+Rx data rate per AP (bps) | Uneven distribution = some APs overloaded |
| **Clients per AP** | Number of connected clients per AP | Above 30-40 = overloaded, risk of disconnects |
| **Packets/s per AP** | Combined Tx+Rx packet rate per AP | Above 20,000 p/s = heavy load |
| **Radio Off/On Events (DFS)** | Counter of DFS-triggered radio off/on events over time | Any increase = DFS event happened, clients disconnected |
| **DFS / Radio Event History** | Table of all historical Radio Off and Radio On events from the AP alarm log, with AP name, band, and timestamp | Shows when DFS events happened in the past |
| **Airtime Busy % (2.4GHz)** | Current percentage of airtime used on each AP's 2.4GHz radio. Raw value, not averaged. | Above 40% = congested, clients compete for airtime |
| **Airtime Busy % (5GHz)** | Same for 5GHz radio | Above 40% = congested |
| **Auth Fail Rate % 2.4GHz** | Cumulative authentication failure rate per AP on 2.4GHz (total fails / total attempts since AP reboot) | Above 5% = something is wrong with client auth |
| **Auth Fail Rate % 5GHz** | Same for 5GHz | Above 5% = check client compatibility, 802.11r, PMF settings |

### Problem Clients

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Weak Signal (RSSI < -70 dBm)** | Table of clients with poor signal. Shows AP, MAC, hostname, band, SSID, RSSI | These clients are too far from the AP or have obstructions |
| **Lowest Data Rates** | Bottom 10 clients by Tx link speed (Mbps) | 0-6 Mbps = nearly unusable, 6-24 Mbps = very slow |

### Trends

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Total Clients** | Client count over time | Sudden drops = mass disconnect event |
| **WLAN Error Rates /s** | System-wide error rates from SNMP: retries, failures, Tx/Rx errors, dropped packets, association failures per second | Spikes correlate with connectivity problems |
| **Wireless Throughput** | Total Tx and Rx throughput over time (from SNMP) | Drops correlate with outages |
| **Auth Failures per AP (2.4GHz)** | Auth failure count per AP over time on 2.4GHz. Shows hourly increase. | Spikes = something is actively failing to authenticate |
| **Auth Failures per AP (5GHz)** | Same for 5GHz | Constant failures = check device compatibility |

### Distribution

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Clients per SSID** | Pie chart of client distribution across SSIDs | Should match expected usage |
| **Clients per AP** | Pie chart of client distribution across APs | Very uneven = poor AP placement or band steering issues |
| **Clients per Band** | Pie chart of 2.4GHz vs 5GHz clients | Ideally 60%+ on 5GHz if band steering is enabled |

---

## 2. Ruckus Network Health

Detailed RF health, per-radio diagnostics, rogue detection, and AP inventory.

### Overview

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Clients with Good Signal %** | Percentage of clients above -65 dBm | Below 80% = too many weak clients |
| **APs Online** | Online AP count | Should match expected |
| **Total Clients** | Total client count | Baseline |
| **Avg Client RSSI** | Average signal strength across all clients | Below -65 dBm = overall weak coverage |
| **Active Alerts** | Combined count of: weak clients + congested radios + high auth fail APs + malicious rogues | Higher = more problems |
| **Max Clients (in range)** | Peak client count within the selected time range | Shows maximum load |
| **Weak Signal Clients** | Clients below -75 dBm (stricter than overview's -70) | These need immediate attention |
| **Congested Radios** | Radios with airtime busy > 50% | These radios are overloaded |
| **Malicious Rogues** | Same-network rogue APs detected | Security concern |
| **Master AP** | Whether a master AP role is detected | Should always be 1 |

### RF Environment — Radio Tables

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **2.4 GHz Radios** | Table per AP: channel, width, clients, avg RSSI, airtime busy %, Rx/Tx Mbps, Tx retries, auth/assoc failure rate | High retries or auth failures on specific APs |
| **5 GHz Radios** | Same for 5GHz radios | Same concerns |

### Airtime & Throughput History

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Airtime Busy % per Channel (2.4GHz/5GHz)** | Airtime utilization over time grouped by channel | Sustained high airtime = interference or overload |
| **Total Throughput over time** | Aggregate network throughput | Baseline for capacity planning |
| **Throughput per AP over time** | Per-AP throughput trends | Identify overloaded APs |
| **Airtime Busy % per AP over time** | Per-AP airtime trend | Correlate with client issues |
| **Rx/Tx Throughput per AP/Band** | Detailed per-radio throughput | Identify asymmetric traffic |

### Channel History

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Channel over time** | Which channel each AP radio is on over time | Changes = DFS event or auto-channel switch |
| **Tx Power over time** | Transmit power level per radio over time | Changes = AP adjusting power (normal for auto-power) |

### Rogue Devices

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Total Rogues** | Total rogue APs detected | High count = noisy RF environment |
| **Malicious Rogues** | Same-network rogues (spoofing your SSID) | Any = security concern |
| **Strongest Rogue** | Strongest rogue signal in dBm | Above -50 = very close, high interference |
| **Rogues 2.4GHz / 5GHz** | Rogue count per band | Which band has more rogues |
| **Rogues by Channel** | Which channels have the most rogues | Avoid these channels if possible |
| **All Rogue APs** | Full table of detected rogues with MAC, SSID, channel, band, type, signal | Identify and locate rogue devices |

### Access Points

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **AP Inventory** | Table of all APs: name, model, IP, MAC, serial, firmware, PoE, role | Verify all APs are present and on same firmware |
| **AP Live Stats** | Detailed per-AP metrics: state, CPU, memory, uptime, connected time, wired Rx/Tx, reboot counts, kernel panics | High CPU, low memory, kernel panics = hardware issues |

### SSIDs & Network Events

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Per-SSID Stats** | Table per SSID: state, clients, Rx/Tx bytes/pkts, auth/assoc success/fail | High failure rate on specific SSID |
| **AP Disconnect/Reconnect Events** | How many times each AP's state changed in the last hour | Frequent changes = AP is flapping (unstable) |
| **Channel Changes per AP** | How many channel changes per AP per hour | Frequent = DFS events or auto-channel instability |

### WAN / Internet

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Internet** | UP/DOWN status via ICMP to 8.8.8.8/1.1.1.1 | DOWN = internet outage |
| **Gateway** | UP/DOWN status of default gateway | DOWN = local network problem |
| **DNS Resolution** | Whether DNS queries succeed | DOWN = DNS failure |
| **Gateway/Internet/DNS Latency** | Response time in milliseconds | Spikes = network congestion or routing issues |
| **WAN Latency History** | Latency to gateway, Google DNS, Cloudflare over time | Correlate latency spikes with WiFi issues |

---

## 3. Ruckus Clients Overview

Detailed view of all connected clients with filtering.

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Total Clients** | Connected client count | Baseline |
| **Clients per Band** | Pie chart: 2.4GHz vs 5GHz | Ideally majority on 5GHz |
| **Clients per SSID** | Pie chart by SSID | Should match expected usage |
| **Clients per AP** | Pie chart by AP | Uneven = load imbalance |
| **Client Live Stats** | Full table per client: hostname, device, RSSI, SNR, noise, channel, link speed, Rx/Tx Mbps, total bytes, packets, retries, connected time | Main diagnostic table — find problem clients here |
| **Client Inventory** | Identity table: AP, device group, auth method, encryption, MAC, hostname, IP, VLAN, band, SSID, type, OS | Find specific devices and their properties |
| **Top Talkers** | Top 10 clients by total traffic (Rx + Tx bytes) | Identify bandwidth hogs |
| **Device Types** | Pie chart by device type (Laptop, Smartphone, etc.) | Understand your client mix |
| **Band Distribution** | Pie chart of band usage | Same as Clients per Band |
| **Client OS** | Pie chart by operating system | Identify problematic OS types |
| **5GHz Client %** | Percentage of clients on 5GHz over time | Should be stable, drops = band steering failing |

---

## 4. Ruckus Client Health

Per-client signal quality, retries, and throughput diagnostics.

### Fleet Signal Health

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Total Clients** | Connected count | Baseline |
| **Clients with Good Signal %** | Percentage above -65 dBm | Below 80% = coverage issues |
| **Avg RSSI** | Average signal across all clients | Below -65 = weak overall |
| **Weak Signal Clients** | Count below -70 dBm | These need attention |
| **High Retry Clients** | Clients with retry rate > 10% | These have unreliable connections |

### Problem Clients

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Weak Signal (RSSI < -70 dBm)** | Table of clients with poor signal | Move these closer to an AP or add coverage |
| **High Retry Rate (>10%)** | Table of clients with excessive retransmissions | Usually caused by weak signal or interference |
| **Low Link Rate (<30 Mbps)** | Bottom 10 clients by negotiated link speed | Low rate = far from AP, old hardware, or interference |

### Per-Client Time Series

Use the hostname/MAC filters at the top to select a specific client, then these panels show its history:

| Panel | What it shows | When to worry |
|-------|--------------|---------------|
| **Client RSSI** | Signal strength over time (with min/max range) | Fluctuating = client is moving or intermittent obstruction |
| **Client SNR** | Signal-to-noise ratio over time | Below 15 dB = unreliable, below 25 = degraded |
| **Client Link Speed** | Negotiated Tx rate over time (Mbps) | Dropping = signal degradation |
| **Client Retry Rate %** | Percentage of packets that needed retransmission | Above 10% = connection problems |
| **Client Throughput** | Actual data throughput (Rx + Tx bps) | Should match expected usage |

---

## Quick Reference: What to Check When...

### Clients are disconnecting
1. Check **Active Issues** and **Auth Fail Rate 5GHz** — auth failures?
2. Check **Clients per AP** — any AP above 30-40 clients?
3. Check **Airtime Busy %** — any radio above 40%?
4. Check **DFS / Radio Event History** — Radio Off events?
5. Check **Total Clients** trend — sudden drops?

### WiFi is slow
1. Check **Airtime Busy %** — congested?
2. Check **Lowest Data Rates** — clients stuck at low speeds?
3. Check **WLAN Error Rates** — high retries or failures?
4. Check **Throughput per AP** — is one AP saturated?

### Specific client has issues
1. Go to **Client Health** dashboard
2. Select the client by hostname or MAC
3. Check **Client RSSI** — weak signal?
4. Check **Client Retry Rate** — high retries?
5. Check **Client Link Speed** — dropping?

### AP seems problematic
1. Check **AP Live Stats** in Network Health — CPU, memory, reboots
2. Check radio tables — airtime, retries, auth failures for that AP
3. Check **Channel Changes per AP** — DFS instability?
4. Check **AP Disconnect/Reconnect Events** — AP flapping?

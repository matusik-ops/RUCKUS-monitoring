# Ruckus Unleashed API Reference

Undocumented `_cmdstat.jsp` XML/AJAX API. Discovered by reverse-engineering the Unleashed web UI.

## Authentication

1. GET `/admin/login.jsp?username=USER&password=PASS&ok=Log+In`
2. GET `/admin/_csrfTokenVar.jsp` → extract CSRF token
3. POST `/admin/_cmdstat.jsp` with XML payload and `X-CSRF-Token` header

## API Endpoints

### Clients: `comp="stamgr"`, `<client/>`

```xml
<ajax-request action="getstat" comp="stamgr" enable-gzip="0">
  <client INTERVAL-STATS="yes" INTERVAL-START="START_UNIX" INTERVAL-STOP="STOP_UNIX" />
</ajax-request>
```

**Client attributes:**
| Field | Description | Example |
|-------|-------------|---------|
| mac | Client MAC address | aa:bb:cc:dd:ee:01 |
| ap-name | Connected AP name | AP01 |
| ssid | Connected SSID | Corp-WiFi |
| radio-band | Band (2.4g or 5g) | 5g |
| hostname | Client hostname | Laptop-01 |
| ip | Client IP address | 10.91.2.100 |
| vlan | VLAN ID | 2 |
| channel | WiFi channel | 44 |
| received-signal-strength | RSSI in dBm | -54 |
| rssi | SNR-like value from AP | 42 |
| noise-floor | Noise floor in dBm | -96 |
| tx-rate | Tx rate in Kbps (from interval-stats) | 135000.0 |
| total-rx-bytes | Total received bytes | 1000000 |
| total-tx-bytes | Total transmitted bytes | 2000000 |
| total-rx-pkts | Total received packets | 10000 |
| total-tx-pkts | Total transmitted packets | 15000 |
| total-retries | Total retry count | 50 |
| total-retry-bytes | Total retried bytes | 500000 |
| first-assoc | Association start time (unix timestamp) | 1775364286 |
| auth-method | Authentication method | Open |
| encryption | Encryption type | WPA2 |
| radio-type | Radio standard | 11ac |
| status | Connection status | 1 |
| dvctype | Device type | Laptop |
| model | Device model/OS | Windows 10/11 |
| min-received-signal-strength | Min RSSI seen | -57 |
| max-received-signal-strength | Max RSSI seen | -52 |

**Note:** `first-assoc` resets on WPA2 re-keying (~every 15 min). The exporter caches the earliest value.

---

### AP Stats: `comp="stamgr"`, `<ap LEVEL="1"/>`

```xml
<ajax-request action="getstat" comp="stamgr" enable-gzip="0">
  <ap LEVEL="1"/>
</ajax-request>
```

**AP attributes:**
| Field | Description | Example |
|-------|-------------|---------|
| mac | AP MAC address | ec:58:ea:10:f3:f0 |
| devname | AP name | AP01 |
| model | AP model | R720 |
| ip | AP IP address | 10.91.1.101 |
| serial-number | Serial number | 171803010596 |
| firmware-version | Firmware version | 200.15.6.212.27 |
| role | AP role | master / member |
| uptime | AP uptime in seconds | 534377 |
| num-sta | Total clients connected | 18 |
| num-vap | Active VAPs (SSIDs broadcasting) | 3 |
| cpu-util | CPU utilization percentage | 4 |
| mem-total | Total memory in KB | 1734004 |
| mem-avail | Available memory in KB | 1230480 |
| temperature | Temperature (-999 if unavailable) | -999 |
| application-reboot-counter | App reboot count | 0 |
| kernel-panic-reboot-counter | Kernel panic count | 0 |
| powercycle-reboot-counter | Power-cycle reboot count | 0 |
| total-boot-counter | Total boot count | 9 |
| amount-connected-time | Cumulative connected time (seconds) | 534444 |
| ap-join-counter | Rejoin counter | 1 |
| ap-crashfile-flag | Has saved crashfile (1=yes, 0=no) | 1 |
| lan_stats_rx_byte | Wired Ethernet Rx bytes | 3623109794 |
| lan_stats_tx_byte | Wired Ethernet Tx bytes | 3143491298 |
| lan_stats_rx_pkt_succ | Wired Ethernet Rx packets | 332367709 |
| lan_stats_tx_pkt | Wired Ethernet Tx packets | 274428002 |
| lan_stats_dropped | Wired Ethernet dropped packets | 2 |
| poe-mode | PoE mode | 802.3bt5 Switch/Injector |
| last-reboot-reason | Last reboot reason | application reboot |
| last-rejoin-reason | Last rejoin reason | AP Restart |

**Per-radio attributes (nested `<radio>` elements):**
| Field | Description | Example |
|-------|-------------|---------|
| radio-band | Band | 2.4g / 5g |
| channel | Current channel | 6 |
| channelization | Channel width | 20 / 40 / 80 |
| tx-power | Transmit power setting | 3 |
| num-sta | Clients on this radio | 18 |
| avg-rssi | Average client RSSI (SNR-like) | 33 |
| noisefloor | Noise floor in dBm | -106 |
| phyerr | PHY errors count | 1164 |
| rf-samples | Number of RF measurement samples | 9 |
| airtime-total | Airtime total (sum of busy+rx+tx) | 28 |
| airtime-busy | Airtime busy (interference/other) | 10 |
| airtime-rx | Airtime receiving | 9 |
| airtime-tx | Airtime transmitting | 9 |
| radio-total-tx-bytes | Radio Tx bytes | 15457070774 |
| radio-total-rx-bytes | Radio Rx bytes | 12783569108 |
| radio-total-tx-pkts | Radio Tx packets | 71611778 |
| radio-total-rx-pkts | Radio Rx packets | 42599073 |
| radio-total-tx-fail | Radio Tx failures | 7 |
| radio-total-retries | Radio retries | 2575 |
| total-fcs-err | FCS errors | 0 |
| mgmt-auth-success | Auth successes | 1404 |
| mgmt-auth-fail | Auth failures | 6 |
| mgmt-assoc-success | Association successes | 1330 |
| mgmt-assoc-fail | Association failures | 3 |
| enabled | Radio enabled (1/0) | 1 |
| radio-type | Radio standard | 11ng / 11ac |
| avail-chan | Available channels | 1,6,11 |
| block-chan | Blocked channels | 2,3,4,5,7,8,9,10 |
| bgscan | Background scan status | Enabled |

**Note on airtime values:** These are raw counter values from the AP's RF sampling. `airtime-total` = `airtime-busy` + `airtime-rx` + `airtime-tx`. Values are NOT percentages. Use for relative comparison between APs. The `rf-samples` field shows the number of measurement intervals. Actual utilization percentage cannot be reliably calculated.

**Note on R850:** `radio-total-tx-bytes` and `radio-total-rx-bytes` are always 0 on R850 firmware. Packet counters work fine. This is a firmware bug.

---

### WLANs: `comp="stamgr"`, `<wlan LEVEL="1"/>`

```xml
<ajax-request action="getstat" comp="stamgr">
  <wlan LEVEL="1"/>
</ajax-request>
```

**WLAN attributes:**
| Field | Description | Example |
|-------|-------------|---------|
| ssid | SSID name | Corp-WiFi |
| state | WLAN state | enabled |
| vlan-id | VLAN ID | 2 |
| num-sta | Connected clients | 45 |
| num-vap | Active VAPs | 7 |
| rx-bytes | Total Rx bytes | 1000000000 |
| tx-bytes | Total Tx bytes | 2000000000 |
| rx-pkts | Total Rx packets | 5000000 |
| tx-pkts | Total Tx packets | 8000000 |
| mgmt-auth-success | Auth successes | 36430 |
| mgmt-auth-fail | Auth failures | 0 |
| mgmt-assoc-success | Association successes | 36000 |
| mgmt-assoc-fail | Association failures | 0 |
| total-auth | Total auth attempts | 36430 |
| total-assoc | Total assoc attempts | 36000 |

---

### Rogues: `comp="stamgr"`, `<rogue/>`

```xml
<ajax-request action="getstat" comp="stamgr" enable-gzip="0">
  <rogue/>
</ajax-request>
```

Returns rogue AP detections with nested `<detection>` elements per detecting AP.

---

### Alarms: `comp="eventd"`, `<alarm/>`

```xml
<ajax-request action="getstat" comp="eventd" enable-gzip="0">
  <alarm/>
</ajax-request>
```

**Alarm types:**
| name | Description |
|------|-------------|
| AP Has Joined | AP joined/rebooted with reason |
| AP Radio On | Radio turned on (DFS recovery) |
| AP Radio Off | Radio turned off (DFS radar detected) |
| Same-Network Rogue AP Detected | Rogue on same network |

**Alarm attributes:**
| Field | Description |
|-------|-------------|
| name | Event type name |
| msg | Message ID |
| severity | Severity level |
| time | Unix timestamp |
| ap-name | AP name |
| radioindex | Radio band (5G / 2.4G) — for radio events |
| reason | Reason text — for join events |
| lmsg | Human-readable message |
| id | Event ID |

---

### Events: `comp="eventd"`, `<xevent/>`

```xml
<ajax-request action="getstat" comp="eventd" enable-gzip="0">
  <xevent/>
</ajax-request>
```

**Xevent types:**
| msg | Description |
|-----|-------------|
| MSG_AP_warm_reboot | AP warm reboot |
| MSG_AP_joined_with_reason | AP joined with reason |
| MSG_same_network_spoofing_AP_detected | Rogue detected |
| MSG_AP_RADIO_ON / MSG_AP_RADIO_OFF | Radio state change |
| MSG_system_failure_recovered | System recovery |
| UN_Upgrade_System_upgraded_success | Firmware upgrade |

---

## Discovery Method

The API was discovered by:
1. Opening the AP web UI in a browser
2. Inspecting `/assets/js/dashboard.js` for API calls
3. Searching for `getstat`, `comp=`, and `ajax-request` patterns
4. Testing payloads against the live AP

## Known Firmware Issues

| Model | Firmware | Issue |
|-------|----------|-------|
| R850 | 200.15.x | `radio-total-tx-bytes` and `radio-total-rx-bytes` always 0 |
| R850 | 200.15.x | `client tx-rate` always 0 |
| R850 | 200.15.x | `temperature` returns -999 |
| All | 200.15.x | `first-assoc` resets on WPA2 re-keying |

# API Fields Audit — What We Collect vs What's Available

Total API fields: ~330+
Currently collected by exporter: ~80 fields
Shown in Grafana dashboards: ~65 fields

## Legend

- ✅ = Collected by exporter AND shown in Grafana
- 📦 = Collected by exporter but NOT shown in Grafana
- ❌ = NOT collected — available in API but we don't use it

---

## 1. CLIENT FIELDS (52 total from API)

### Collected and in Grafana (15)
| API Field | Prometheus Metric | Grafana |
|-----------|------------------|---------|
| ✅ mac | label: client_mac | All client panels |
| ✅ ap-name | label: ap_name | All client panels |
| ✅ ssid | label: ssid | All client panels |
| ✅ radio-band | label: radio_band | All client panels |
| ✅ hostname | label: hostname | All client panels |
| ✅ received-signal-strength | unleashed_client_rssi_dbm | Client Live Stats, Weak Signal |
| ✅ rssi | unleashed_client_snr_db | Client Live Stats |
| ✅ noise-floor | unleashed_client_noise_floor_dbm | Client Live Stats |
| ✅ channel | unleashed_client_channel | Client Live Stats |
| ✅ total-rx-bytes | unleashed_client_rx_bytes_total | Client Live Stats |
| ✅ total-tx-bytes | unleashed_client_tx_bytes_total | Client Live Stats |
| ✅ total-rx-pkts | unleashed_client_rx_pkts_total | Client Live Stats |
| ✅ total-tx-pkts | unleashed_client_tx_pkts_total | Client Live Stats |
| ✅ total-retries | unleashed_client_retries_total | Client Live Stats |
| ✅ first-assoc | unleashed_client_assoc_time_seconds | Connected For |

### Collected but not prominently in Grafana (8)
| API Field | Prometheus Metric | Notes |
|-----------|------------------|-------|
| 📦 ip | label on client_info | In Client Inventory table |
| 📦 vlan | label on client_info | In Client Inventory table |
| 📦 auth-method | label on client_info | In Client Inventory table |
| 📦 encryption | label on client_info | In Client Inventory table |
| 📦 dvctype | label on client_info | In Client Inventory table |
| 📦 model | label on client_info (as model_os) | In Client Inventory table |
| 📦 tx-rate (interval-stats) | unleashed_client_tx_rate_kbps | In Client Live Stats |
| 📦 total-retry-bytes | unleashed_client_retry_bytes_total | Not in any panel |
| 📦 min-received-signal-strength | unleashed_client_min_rssi_dbm | Client Health RSSI graph |
| 📦 max-received-signal-strength | unleashed_client_max_rssi_dbm | Client Health RSSI graph |

### NOT collected — available but unused (29)
| API Field | Value Example | Useful? |
|-----------|--------------|---------|
| ❌ display-health-level | "Good" | ⭐ Yes — AP's assessment of client health |
| ❌ health-level | "MN_Excellent" | ⭐ Yes — machine-readable health |
| ❌ rssi-level | "excellent" | Low — redundant with RSSI value |
| ❌ avg-rssi | 46 | Medium — average RSSI from AP side |
| ❌ total-usage-bytes | 167136357 | Low — just rx+tx combined |
| ❌ total-rx-crc-errs | 0 | ⭐ Yes — CRC errors indicate bad signal |
| ❌ total-rx-dup | 0 | Medium — duplicate packets |
| ❌ tx-drop-data | 0 | ⭐ Yes — dropped data frames |
| ❌ tx-drop-mgmt | 0 | ⭐ Yes — dropped management frames |
| ❌ total-tx-reassoc | 0 | Medium — reassociation count |
| ❌ total-rx-management | 0 | Low |
| ❌ total-tx-management | 0 | Low |
| ❌ channelization | 20 | Medium — client channel width |
| ❌ ieee80211-radio-type | g/n | Low — redundant with radio-type |
| ❌ radio-type | 11ng | Low — already have radio-band |
| ❌ radio-type-text | 11ng | Low — duplicate |
| ❌ status | 1 | Low — always 1 for connected |
| ❌ ext-status | 0 | Low |
| ❌ blocked | 0 | Medium — is client blocked |
| ❌ favourite | 0 | Low |
| ❌ iot | 0 | Medium — IoT device flag |
| ❌ acct-session-id | 6a2112b8-15a4 | Low — accounting |
| ❌ acct-multi-session-id | ec58ea... | Low — accounting |
| ❌ dpsk-id | 0 | Low — dynamic PSK |
| ❌ role-id | 0 | Low |
| ❌ group-id | 1 | Low |
| ❌ wlan-id | 3 | Low — redundant with ssid |
| ❌ oldname | d4:01:c3:6f:ba:5a | Low — previous hostname |
| ❌ description | | Low |
| ❌ user | | Low |
| ❌ ipv6 | | Low |
| ❌ location | | Low |
| ❌ vap-mac | ec:58:ea:10:b4:f8 | Low |
| ❌ wpa-passphrase | encoded | Never collect — security |
| ❌ called-station-id-type | 0 | Low |
| ❌ num-interval-stats | 0 | Low |
| ❌ dvcinfo | | Low |
| ❌ dvcinfo-group | 11 | Low |

---

## 2. AP FIELDS (120 total from API)

### Collected and in Grafana (18)
| API Field | Prometheus Metric | Grafana |
|-----------|------------------|---------|
| ✅ devname | label: ap_name | All AP panels |
| ✅ cpu_util | unleashed_ap_cpu_util | AP Live Stats |
| ✅ mem_avail | unleashed_ap_mem_avail | Used for mem_used_pct |
| ✅ mem_total | unleashed_ap_mem_total | Used for mem_used_pct |
| ✅ uptime | unleashed_ap_uptime_seconds | AP Live Stats |
| ✅ num-sta | unleashed_ap_num_sta | AP Live Stats |
| ✅ num-vap | unleashed_ap_num_vap | AP Live Stats |
| ✅ state | unleashed_ap_state | AP Live Stats |
| ✅ amount-connected-time | unleashed_ap_connected_time_seconds | AP Live Stats |
| ✅ ap-join-counter | unleashed_ap_join_counter | AP Live Stats |
| ✅ application-reboot-counter | unleashed_ap_app_reboots_total | AP Live Stats |
| ✅ kernel-panic-reboot-counter | unleashed_ap_kernel_panics_total | AP Live Stats |
| ✅ powercycle-reboot-counter | unleashed_ap_powercycle_reboots_total | AP Live Stats |
| ✅ total-boot-counter | unleashed_ap_total_reboots | AP Live Stats |
| ✅ ap-crashfile-flag | unleashed_ap_crashfile_flag | AP Live Stats |
| ✅ lan_stats_rx_byte | unleashed_ap_lan_rx_bytes_total | AP Live Stats |
| ✅ lan_stats_tx_byte | unleashed_ap_lan_tx_bytes_total | AP Live Stats |
| ✅ lan_stats_dropped | unleashed_ap_lan_dropped_total | AP Live Stats |

### Collected as info labels (10)
| API Field | On Metric | Grafana |
|-----------|----------|---------|
| 📦 model | unleashed_ap_info | AP Inventory |
| 📦 ip / external-ip | unleashed_ap_info | AP Inventory |
| 📦 mac | unleashed_ap_info | AP Inventory |
| 📦 serial-number | unleashed_ap_info | AP Inventory |
| 📦 firmware-version | unleashed_ap_info | AP Inventory |
| 📦 poe-mode-str | unleashed_ap_info | AP Inventory |
| 📦 role | unleashed_ap_info | AP Inventory |
| 📦 last-reboot-reason | unleashed_ap_info | AP Inventory |
| 📦 last-rejoin-reason | unleashed_ap_info | AP Inventory |
| 📦 current-temperature | unleashed_ap_temperature | AP Live Stats (-999 on R850) |

### NOT collected — useful (20)
| API Field | Value Example | Useful? |
|-----------|--------------|---------|
| ❌ max-client | 100 | ⭐⭐ Yes — max client limit per AP! |
| ❌ sta_rx_byte | 68322123 | ⭐ Yes — wireless station traffic |
| ❌ sta_tx_byte | 208485212 | ⭐ Yes — wireless station traffic |
| ❌ wlan_tx_drop_frame | 0 | ⭐ Yes — WLAN dropped frames |
| ❌ wlan_tx_error_frame | 0 | ⭐ Yes — WLAN error frames |
| ❌ lan_stats_rx_pkt_succ | 325532173 | 📦 Collected but not in panel |
| ❌ lan_stats_tx_pkt | 232448320 | 📦 Collected but not in panel |
| ❌ lan_stats_rx_pkt_err | 0 | ⭐ Yes — wired Rx errors |
| ❌ last-seen | 1779040485 | Medium — last seen timestamp |
| ❌ gateway | 10.91.1.254 | Medium — AP gateway |
| ❌ netmask | 255.255.255.0 | Low |
| ❌ dns1 | 10.91.1.254 | Low |
| ❌ hardware-version | 30.0.0 | Medium |
| ❌ support-11ac | true | Low — capability flag |
| ❌ support-11ax | false | Low — capability flag |
| ❌ support-dedicated-master | false | Medium |
| ❌ mesh-enabled | false | Low |
| ❌ lacp-state | 255 | Medium — link aggregation |
| ❌ led-off | false | Low |
| ❌ usb-installed | true | Low |

### NOT collected — low value (90+)
Configuration fields, coordinates, mesh settings, IPv6, cable modem fields, bonjour settings, etc. Not useful for monitoring.

---

## 3. RADIO FIELDS (72 per radio from API)

### Collected and in Grafana (20)
| API Field | Prometheus Metric | Grafana |
|-----------|------------------|---------|
| ✅ radio-band | label | All radio panels |
| ✅ channel | unleashed_radio_channel | Radio tables, Channel History |
| ✅ channelization | unleashed_radio_channelization | Radio tables |
| ✅ tx-power | unleashed_radio_tx_power | Tx Power History |
| ✅ num-sta | unleashed_radio_num_sta | Clients per AP |
| ✅ avg-rssi | unleashed_radio_avg_rssi | Radio tables |
| ✅ noisefloor | unleashed_radio_noise_floor_dbm | Radio tables |
| ✅ phyerr | unleashed_radio_phy_err | Radio tables |
| ✅ airtime-total | unleashed_radio_airtime_total | Airtime Breakdown |
| ✅ airtime-busy | unleashed_radio_airtime_busy | Airtime Breakdown |
| ✅ airtime-rx | unleashed_radio_airtime_rx | Airtime Breakdown |
| ✅ airtime-tx | unleashed_radio_airtime_tx | Airtime Breakdown |
| ✅ radio-total-tx-bytes | unleashed_radio_tx_bytes_total | Throughput per AP |
| ✅ radio-total-rx-bytes | unleashed_radio_rx_bytes_total | Throughput per AP |
| ✅ radio-total-tx-pkts | unleashed_radio_tx_pkts_total | Packets/s per AP |
| ✅ radio-total-rx-pkts | unleashed_radio_rx_pkts_total | Packets/s per AP |
| ✅ radio-total-tx-fail | unleashed_radio_tx_fail_total | Tx Failures per AP |
| ✅ radio-total-retries | unleashed_radio_retries_total | Retries per AP |
| ✅ mgmt-auth-fail | unleashed_radio_auth_fail | Auth Fail Rate |
| ✅ mgmt-auth-success | unleashed_radio_auth_success | Auth Fail Rate |

### Collected but not in dedicated panel (4)
| API Field | Prometheus Metric | Notes |
|-----------|------------------|-------|
| 📦 total-fcs-err | unleashed_radio_fcs_error_total | In radio tables |
| 📦 mgmt-assoc-fail | unleashed_radio_assoc_fail | In radio tables |
| 📦 mgmt-assoc-success | unleashed_radio_assoc_success | In radio tables |

### NOT collected — useful (15)
| API Field | Value Example | Useful? |
|-----------|--------------|---------|
| ❌ rf-samples | 13 | ⭐ Yes — needed for airtime % calculation |
| ❌ radio-total-rx-decrypt-error | 0 | ⭐ Yes — decryption errors |
| ❌ mgmt-reassoc-req | 59 | ⭐ Yes — reassociation count (roaming) |
| ❌ mgmt-reassoc-resp | 59 | Medium |
| ❌ mgmt-disassoc-abnormal | 0 | ⭐ Yes — abnormal disconnects |
| ❌ mgmt-disassoc-capacity | 0 | ⭐ Yes — disconnects due to capacity |
| ❌ mgmt-disassoc-leave | 0 | ⭐ Yes — client left normally |
| ❌ mgmt-disassoc-misc | 0 | Medium |
| ❌ mgmt-auth-req | 1410 | Medium — total auth requests |
| ❌ mgmt-assoc-req | 1274 | Medium — total assoc requests |
| ❌ radio-total-rx-mcast | 2880 | Low — multicast traffic |
| ❌ radio-total-tx-mcast | 0 | Low |
| ❌ avail-chan | 1,6,11 | Medium — available channels |
| ❌ block-chan | 2,3,4,5... | Medium — blocked channels (DFS) |
| ❌ dfs-channel-11na | 60 | Medium — DFS channel for 5GHz |

### NOT collected — low value (33)
Beacon period, RTS threshold, frag threshold, protection mode, WLAN group IDs, per-type packet counts (bcast/mcast/ucast), duplicate fields, etc.

---

## 4. WLAN/SSID FIELDS (48 total from API)

### Collected and in Grafana (14)
| API Field | Prometheus Metric | Grafana |
|-----------|------------------|---------|
| ✅ ssid | label | Per-SSID Stats |
| ✅ state | label | Per-SSID Stats |
| ✅ vlan-id | label | Per-SSID Stats |
| ✅ num-sta | unleashed_wlan_num_sta | Per-SSID Stats |
| ✅ num-vap | unleashed_wlan_num_vap | Per-SSID Stats |
| ✅ rx-bytes | unleashed_wlan_rx_bytes_total | Per-SSID Stats |
| ✅ tx-bytes | unleashed_wlan_tx_bytes_total | Per-SSID Stats |
| ✅ rx-pkts | unleashed_wlan_rx_pkts_total | Not in panel |
| ✅ tx-pkts | unleashed_wlan_tx_pkts_total | Not in panel |
| ✅ mgmt-auth-success | unleashed_wlan_auth_success_total | Not in panel |
| ✅ mgmt-auth-fail | unleashed_wlan_auth_fail_total | Not in panel |
| ✅ mgmt-assoc-success | unleashed_wlan_assoc_success_total | Not in panel |
| ✅ mgmt-assoc-fail | unleashed_wlan_assoc_fail_total | Not in panel |
| ✅ total-assoc / total-auth | unleashed_wlan_total_assoc/auth | Not in panel |

### NOT collected — useful (10)
| API Field | Value Example | Useful? |
|-----------|--------------|---------|
| ❌ fast-bss | enabled | ⭐⭐ Yes — 802.11r status! Shows if Fast Roaming is on |
| ❌ down_drop_frame | 2332033024 | ⭐ Yes — downstream dropped frames |
| ❌ down_retx_frame | 0 | ⭐ Yes — downstream retransmissions |
| ❌ down_total_frame | 342538935 | Medium — total downstream frames |
| ❌ up_drop_frame | 0 | ⭐ Yes — upstream dropped frames |
| ❌ up_retx_frame | 0 | ⭐ Yes — upstream retransmissions |
| ❌ up_total_frame | 288605742 | Medium — total upstream frames |
| ❌ encryption | wpa2 | Medium — encryption type |
| ❌ authentication | open | Medium — auth type |
| ❌ client-isolation | disabled | Medium |

### NOT collected — low value (24)
Passphrase, WEP keys, bind settings, DPSK, cipher, description, etc.

---

## 5. ALARM TYPES (from eventd API)

### Collected (4 types)
| ✅ AP Has Joined | AP join/reboot event |
| ✅ AP Radio On | Radio turned on (DFS recovery) |
| ✅ AP Radio Off | Radio turned off (DFS) |
| ✅ Same-Network Rogue AP Detected | Rogue on same network |

### NOT collected (1 type found)
| ❌ AP Lost Contact | ⭐⭐ Yes — AP went offline! |

---

## 6. XEVENT TYPES (from eventd API)

### Collected (2 types)
| ✅ MSG_AP_warm_reboot | AP warm reboot |
| ✅ MSG_AP_joined_with_reason | AP joined with reason |

### NOT collected (5 types found)
| Type | Useful? |
|------|---------|
| ❌ MSG_client_repeat_auth_fail | ⭐⭐⭐ Yes — shows WHICH CLIENT MAC fails auth! |
| ❌ MSG_AP_lost_heartbeat | ⭐⭐ Yes — AP losing heartbeat |
| ❌ MSG_AP_lost | ⭐⭐ Yes — AP went offline |
| ❌ MSG_admin_warm_restarted | Medium — system restart |
| ❌ MSG_AP_RADIO_ON/OFF | ✅ Already collected via alarm |

---

## TOP PRIORITY — Fields to Add

### Must Have (would solve real problems)
1. **MSG_client_repeat_auth_fail** — gives the client MAC causing auth failures. Currently we can only see auth fail count per AP, not which device.
2. **max-client** — the configured max client limit per AP. Needed to know if AP is at capacity.
3. **fast-bss** — shows if 802.11r is enabled per SSID. Would have caught the SCTN01 problem instantly.
4. **MSG_AP_lost / MSG_AP_lost_heartbeat** — AP went offline events.

### Should Have (improves diagnostics)
5. **rf-samples** — needed for proper airtime utilization calculation
6. **mgmt-disassoc-abnormal/capacity/leave** — why clients disconnect
7. **mgmt-reassoc-req** — roaming frequency indicator
8. **down_drop_frame / up_drop_frame** — WLAN dropped frames
9. **total-rx-crc-errs** — client CRC errors (bad signal indicator)
10. **tx-drop-data** — client dropped data frames
11. **radio-total-rx-decrypt-error** — decryption errors
12. **lan_stats_rx_pkt_err** — wired interface errors

### Nice to Have
13. **sta_rx_byte / sta_tx_byte** — per-AP wireless station traffic
14. **wlan_tx_drop_frame / wlan_tx_error_frame** — AP-level WLAN errors
15. **display-health-level** — AP's own assessment of client health
16. **avail-chan / block-chan** — channel availability info

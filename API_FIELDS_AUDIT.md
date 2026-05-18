# API Fields Audit — What We Collect vs What's Available

**Verified against live AP (10.6.66.101) on 2026-05-18, firmware 200.15.6.212.27**

Total API fields: 308
Currently collected by exporter: 68 fields (22%)
Not collected: 240 fields

## Legend

- ✅ = Collected by exporter
- ❌ = NOT collected — available in API but we don't use it

---

## 1. AP FIELDS (166 total from API, 30 collected)

### Collected (30)
| API Field | Prometheus Metric |
|-----------|------------------|
| ✅ ap-name | label: ap_name |
| ✅ amount-connected-time | unleashed_ap_connected_time_seconds |
| ✅ ap-crashfile-flag | unleashed_ap_crashfile_flag |
| ✅ ap-join-counter | unleashed_ap_join_counter |
| ✅ application-reboot-counter | unleashed_ap_app_reboots_total |
| ✅ cpu_util | unleashed_ap_cpu_util |
| ✅ current-temperature | unleashed_ap_temperature |
| ✅ display-model | label on unleashed_ap_info |
| ✅ firmware-version | label on unleashed_ap_info |
| ✅ id | internal |
| ✅ ip | label on unleashed_ap_info |
| ✅ kernel-panic-reboot-counter | unleashed_ap_kernel_panics_total |
| ✅ lan_stats_dropped | unleashed_ap_lan_dropped_total |
| ✅ lan_stats_rx_byte | unleashed_ap_lan_rx_bytes_total |
| ✅ lan_stats_rx_pkt_succ | unleashed_ap_lan_rx_pkts_total |
| ✅ lan_stats_tx_byte | unleashed_ap_lan_tx_bytes_total |
| ✅ lan_stats_tx_pkt | unleashed_ap_lan_tx_pkts_total |
| ✅ last-reboot-reason | label on unleashed_ap_info |
| ✅ last-rejoin-reason | label on unleashed_ap_info |
| ✅ mac | label on unleashed_ap_info |
| ✅ mem_avail | unleashed_ap_mem_avail |
| ✅ mem_total | unleashed_ap_mem_total |
| ✅ model | label on unleashed_ap_info |
| ✅ name | internal (AP MAC) |
| ✅ num-sta | unleashed_ap_num_sta |
| ✅ num-vap | unleashed_ap_num_vap |
| ✅ poe-mode-str | label on unleashed_ap_info |
| ✅ powercycle-reboot-counter | unleashed_ap_powercycle_reboots_total |
| ✅ role | label on unleashed_ap_info |
| ✅ serial-number | label on unleashed_ap_info |
| ✅ state | unleashed_ap_state |
| ✅ total-boot-counter | unleashed_ap_total_reboots |
| ✅ uptime | unleashed_ap_uptime_seconds |

### NOT collected — useful (15)
| API Field | Value Example | Priority |
|-----------|--------------|----------|
| ❌ max-client | 100 | ⭐⭐ Max client limit per AP |
| ❌ sta_rx_byte | 68322123 | ⭐ Wireless station Rx bytes |
| ❌ sta_tx_byte | 208485212 | ⭐ Wireless station Tx bytes |
| ❌ wlan_tx_drop_frame | 0 | ⭐ WLAN dropped frames |
| ❌ wlan_tx_error_frame | 0 | ⭐ WLAN error frames |
| ❌ lan_stats_rx_pkt_err | 0 | ⭐ Wired Rx errors |
| ❌ lan_stats_rx_pkt_bcast | 0 | Low — broadcast packets |
| ❌ lan_stats_rx_pkt_mcast | 0 | Low — multicast packets |
| ❌ hardware-version | 30.0.0 | Medium |
| ❌ gateway | 10.91.1.254 | Medium |
| ❌ last-seen | 1779040485 | Medium — last seen timestamp |
| ❌ support-dedicated-master | false | Medium |
| ❌ lacp-state | 255 | Medium — link aggregation |
| ❌ firstAssoc | 1778132570 | Medium — when AP first joined |
| ❌ nonrun-reboot-counter | 0 | Medium |

### NOT collected — low value (121)
Configuration fields (auth-mode, bonjour, coordinates, mesh, IPv6, cable modem, dns, tunnel, USB, etc.)

---

## 2. RADIO FIELDS (79 per radio from API, 24 collected)

### Collected (24)
| API Field | Prometheus Metric |
|-----------|------------------|
| ✅ radio-band | label |
| ✅ channel | unleashed_radio_channel |
| ✅ channelization | unleashed_radio_channelization |
| ✅ tx-power | unleashed_radio_tx_power |
| ✅ num-sta | unleashed_radio_num_sta |
| ✅ avg-rssi | unleashed_radio_avg_rssi |
| ✅ noisefloor | unleashed_radio_noise_floor_dbm |
| ✅ phyerr | unleashed_radio_phy_err |
| ✅ airtime-total | unleashed_radio_airtime_total |
| ✅ airtime-busy | unleashed_radio_airtime_busy |
| ✅ airtime-rx | unleashed_radio_airtime_rx |
| ✅ airtime-tx | unleashed_radio_airtime_tx |
| ✅ radio-total-tx-bytes | unleashed_radio_tx_bytes_total |
| ✅ radio-total-rx-bytes | unleashed_radio_rx_bytes_total |
| ✅ radio-total-tx-pkts | unleashed_radio_tx_pkts_total |
| ✅ radio-total-rx-pkts | unleashed_radio_rx_pkts_total |
| ✅ radio-total-tx-fail | unleashed_radio_tx_fail_total |
| ✅ radio-total-retries | unleashed_radio_retries_total |
| ✅ total-fcs-err | unleashed_radio_fcs_error_total |
| ✅ mgmt-auth-fail | unleashed_radio_auth_fail |
| ✅ mgmt-auth-success | unleashed_radio_auth_success |
| ✅ mgmt-assoc-fail | unleashed_radio_assoc_fail |
| ✅ mgmt-assoc-success | unleashed_radio_assoc_success |
| ✅ total-rx-bytes / total-tx-bytes / total-rx-pkts / total-tx-pkts | internal |

### NOT collected — useful (16)
| API Field | Value Example | Priority |
|-----------|--------------|----------|
| ❌ rf-samples | 4-13 | ⭐⭐ Needed for real airtime % calculation |
| ❌ radio-total-rx-decrypt-error | 0 | ⭐ Decryption errors |
| ❌ mgmt-reassoc-req | 59 | ⭐ Reassociation count (roaming indicator) |
| ❌ mgmt-reassoc-resp | 59 | Medium |
| ❌ mgmt-disassoc-abnormal | 0 | ⭐ Abnormal disconnects |
| ❌ mgmt-disassoc-capacity | 0 | ⭐ Disconnects due to capacity |
| ❌ mgmt-disassoc-leave | 0 | ⭐ Client left normally |
| ❌ mgmt-disassoc-misc | 0 | Medium |
| ❌ mgmt-auth-req | 1410 | Medium — total auth requests |
| ❌ mgmt-assoc-req | 1274 | Medium — total assoc requests |
| ❌ avail-chan | 1,6,11 | Medium — available channels |
| ❌ block-chan | 2,3,4,5... | Medium — blocked channels (DFS) |
| ❌ dfs-channel-11na | 60 | Medium — DFS channel for 5GHz |
| ❌ enabled | 1 | Medium — radio enabled/disabled |
| ❌ radio-total-rx-mcast | 2880 | Low — multicast traffic |
| ❌ radio-total-tx-mcast | 0 | Low |

### NOT collected — low value (39)
Beacon period, RTS/frag thresholds, protection mode, WLAN group IDs, per-type packet counts (bcast/mcast/ucast), settings fields (*-setting), ieee80211 type, wmm, etc.

---

## 3. CLIENT FIELDS (52 total from API, 25 collected)

Note: Client count confirmed from other sites. Test AP had 0 clients at time of audit.

### Collected (25)
| API Field | Prometheus Metric |
|-----------|------------------|
| ✅ mac | label: client_mac |
| ✅ ap-name | label: ap_name |
| ✅ ssid | label: ssid |
| ✅ radio-band | label: radio_band |
| ✅ hostname | label: hostname |
| ✅ ip | label on client_info |
| ✅ vlan | label on client_info |
| ✅ auth-method | label on client_info |
| ✅ encryption | label on client_info |
| ✅ dvctype | label on client_info |
| ✅ model | label on client_info (as model_os) |
| ✅ received-signal-strength | unleashed_client_rssi_dbm |
| ✅ rssi | unleashed_client_snr_db |
| ✅ noise-floor | unleashed_client_noise_floor_dbm |
| ✅ channel | unleashed_client_channel |
| ✅ tx-rate (interval-stats) | unleashed_client_tx_rate_kbps |
| ✅ total-rx-bytes | unleashed_client_rx_bytes_total |
| ✅ total-tx-bytes | unleashed_client_tx_bytes_total |
| ✅ total-rx-pkts | unleashed_client_rx_pkts_total |
| ✅ total-tx-pkts | unleashed_client_tx_pkts_total |
| ✅ total-retries | unleashed_client_retries_total |
| ✅ total-retry-bytes | unleashed_client_retry_bytes_total |
| ✅ first-assoc | unleashed_client_assoc_time_seconds |
| ✅ min-received-signal-strength | unleashed_client_min_rssi_dbm |
| ✅ max-received-signal-strength | unleashed_client_max_rssi_dbm |

### NOT collected — useful (10)
| API Field | Value Example | Priority |
|-----------|--------------|----------|
| ❌ display-health-level | "Good" | ⭐ AP's assessment of client health |
| ❌ health-level | "MN_Excellent" | ⭐ Machine-readable health |
| ❌ total-rx-crc-errs | 0 | ⭐ CRC errors (bad signal indicator) |
| ❌ tx-drop-data | 0 | ⭐ Dropped data frames |
| ❌ tx-drop-mgmt | 0 | ⭐ Dropped management frames |
| ❌ total-rx-dup | 0 | Medium — duplicate packets |
| ❌ total-tx-reassoc | 0 | Medium — reassociation count |
| ❌ channelization | 20 | Medium — client channel width |
| ❌ blocked | 0 | Medium — is client blocked |
| ❌ avg-rssi | 46 | Medium — average RSSI |

### NOT collected — low value (17)
Status, ext-status, radio-type variants, accounting IDs, DPSK, role-id, group-id, wlan-id, oldname, description, user, ipv6, location, vap-mac, wpa-passphrase, dvcinfo, etc.

---

## 4. WLAN/SSID FIELDS (63 total from API, 16 collected)

### Collected (16)
| API Field | Prometheus Metric |
|-----------|------------------|
| ✅ ssid | label |
| ✅ name | internal |
| ✅ state | label |
| ✅ vlan-id | label |
| ✅ id | internal |
| ✅ encryption | internal |
| ✅ num-sta | unleashed_wlan_num_sta |
| ✅ num-vap | unleashed_wlan_num_vap |
| ✅ rx-bytes | unleashed_wlan_rx_bytes_total |
| ✅ tx-bytes | unleashed_wlan_tx_bytes_total |
| ✅ rx-pkts | unleashed_wlan_rx_pkts_total |
| ✅ tx-pkts | unleashed_wlan_tx_pkts_total |
| ✅ mgmt-auth-success | unleashed_wlan_auth_success_total |
| ✅ mgmt-auth-fail | unleashed_wlan_auth_fail_total |
| ✅ mgmt-assoc-success | unleashed_wlan_assoc_success_total |
| ✅ mgmt-assoc-fail | unleashed_wlan_assoc_fail_total |
| ✅ total-assoc | unleashed_wlan_total_assoc |
| ✅ total-auth | unleashed_wlan_total_auth |

### NOT collected — useful (12)
| API Field | Value Example | Priority |
|-----------|--------------|----------|
| ❌ fast-bss | enabled | ⭐⭐ 802.11r status! |
| ❌ down_drop_frame | 2332033024 | ⭐ Downstream dropped frames |
| ❌ down_retx_frame | 0 | ⭐ Downstream retransmissions |
| ❌ down_total_frame | 342538935 | Medium — total downstream |
| ❌ down_error_frame | 0 | ⭐ Downstream errors |
| ❌ up_drop_frame | 0 | ⭐ Upstream dropped frames |
| ❌ up_retx_frame | 0 | ⭐ Upstream retransmissions |
| ❌ up_total_frame | 288605742 | Medium — total upstream |
| ❌ total-auth-success | 6149 | Medium |
| ❌ authentication | open | Medium — auth type |
| ❌ client-isolation | disabled | Medium |
| ❌ rx_data_frame_lan | 287888948 | Low |

### NOT collected — low value (35)
Passphrase, WEP keys, bind settings, DPSK, cipher, description, bgscan, ofdm, balance, close-system, usage, wifi6, assoc-stas, mgmt detail counters, etc.

---

## 5. ALARM TYPES (from eventd API)

### Collected (4 types)
| ✅ AP Has Joined | AP join/reboot event |
| ✅ AP Radio On | Radio turned on (DFS recovery) |
| ✅ AP Radio Off | Radio turned off (DFS) |
| ✅ Same-Network Rogue AP Detected | Rogue on same network |

### NOT collected (1 type found)
| ❌ AP Lost Contact | ⭐⭐ AP went offline! |

---

## 6. XEVENT TYPES (from eventd API)

### Collected (2 types)
| ✅ MSG_AP_warm_reboot | AP warm reboot |
| ✅ MSG_AP_joined_with_reason | AP joined with reason |

### NOT collected (5 types found)
| Type | Priority |
|------|----------|
| ❌ MSG_client_repeat_auth_fail | ⭐⭐⭐ Shows WHICH CLIENT MAC fails auth! |
| ❌ MSG_AP_lost_heartbeat | ⭐⭐ AP losing heartbeat |
| ❌ MSG_AP_lost | ⭐⭐ AP went offline |
| ❌ MSG_admin_warm_restarted | Medium — system restart |
| ❌ MSG_AP_RADIO_ON/OFF | ✅ Already collected via alarm |

---

## TOP PRIORITY — Fields to Add

### Must Have (would solve real problems)
1. **rf-samples** — needed for real airtime % calculation (currently can't calculate true utilization)
2. **MSG_client_repeat_auth_fail** — gives the client MAC causing auth failures
3. **max-client** — the configured max client limit per AP
4. **fast-bss** — shows if 802.11r is enabled per SSID
5. **MSG_AP_lost / MSG_AP_lost_heartbeat** — AP went offline events

### Should Have (improves diagnostics)
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

---

## Airtime Values Explained

The AP reports airtime as raw counters per poll:
- `airtime-tx` — time spent transmitting
- `airtime-rx` — time spent receiving
- `airtime-busy` — time channel busy (interference)
- `airtime-total` — always equals tx + rx + busy
- `rf-samples` — number of measurement intervals

**To calculate real utilization %:**
```
Usage % = airtime-total / (rf-samples * 100) * 100
IDLE % = 100 - Usage %
```

Example: rf-samples=5, total=179 → Usage = 179/500 = 35.8%, IDLE = 64.2%

**Note:** rf-samples varies between polls (4, 5, 9, 13...). Without it, we can only show raw values or ratios — not real percentages.

---

## Known Firmware Bugs (200.15.x)

| Model | Issue |
|-------|-------|
| R850 | `radio-total-tx-bytes` and `radio-total-rx-bytes` always 0 |
| R850 | `client tx-rate` always 0 |
| R850 | `temperature` returns -999 (unavailable) |
| All | `first-assoc` resets on WPA2 re-keying (~every 15 min) |

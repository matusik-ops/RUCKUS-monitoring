# Future Work

## Client Latency via blackbox_exporter
- Add `blackbox_exporter` container to Docker Compose
- Dynamically generate ping targets from `unleashed_client_info` metric (client IPs)
- Configure Prometheus to probe each client IP via ICMP
- Add per-client latency (RTT) and packet loss (ICMP) panels to Client Health dashboard
- **Challenges**: VLAN routing (clients on different subnets may not be pingable), mobile clients come/go, some clients block ICMP
- **Also useful for**: WAN/uplink monitoring (ping 8.8.8.8, gateway, DNS servers)

## WAN / Uplink Monitoring
- Same blackbox_exporter can probe internet targets (8.8.8.8, 1.1.1.1, gateway)
- Add dashboard panels: WAN UP/DOWN, internet latency, DNS response time, packet loss
- See detailed instructions in Network Health dashboard → SSIDs & Network Events → WAN panel

## Event Log Integration
- [x] Research `_cmdstat.jsp` event log query format — **DONE**: uses `comp="eventd"` (not `comp="system"`)
  - `<alarm/>` returns: AP joins, rogue detections, radio on/off (structured XML with `alarmdef-id`, `name`, `msg`, `severity`, `time`, `ap-name`, `lmsg`)
  - `<xevent/>` returns: firmware upgrades, AP reboots, rogue detections (structured XML with `msg`, `severity`, `time`, `ap-name`, `lmsg`)
  - **Available event types**: AP Has Joined, AP Radio On/Off, Same-Network Rogue AP Detected, AP warm reboot, System failure recovered, Firmware upgrade
  - **No explicit DFS radar event** — DFS can be inferred from 5GHz Radio Off → Radio On pairs in quick succession
  - **Client connect/disconnect events are NOT available** as discrete events — must be derived by diffing the client list between polls
- [ ] Implement event collection in exporter (`get_events()` method using `comp="eventd"`)
- [ ] Expose event counters as Prometheus metrics
- [ ] Track connect/disconnect by diffing client list between polls
- [ ] Track auth failure events with client MAC (identify WHICH device causes AP06/AP08 auth failures)
- [ ] Track DFS radar events (infer from 5GHz Radio Off/On pairs)
- [ ] Track roaming events (client X moved from AP01 to AP05)
- [ ] Add event panels to Grafana dashboards
- Full change proposal at: `openspec/changes/event-log-integration/`

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
- Research `_cmdstat.jsp` event log query format
- Track connect/disconnect events with client MAC + timestamp
- Track auth failure events with client MAC (identify WHICH device causes AP06/AP08 auth failures)
- Track DFS radar events (when 5GHz channels change due to radar detection)
- Track roaming events (client X moved from AP01 to AP05)

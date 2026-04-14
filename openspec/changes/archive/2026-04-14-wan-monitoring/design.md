## Context

The Network Health dashboard has a placeholder text panel explaining WAN monitoring needs blackbox_exporter. The TODO.md documents this as deferred work. Now implementing it.

The gateway IP is 10.91.1.254 (from AP config data we've seen). External targets: 8.8.8.8 (Google DNS), 1.1.1.1 (Cloudflare).

## Goals / Non-Goals

**Goals:**
- Detect internet outages within 30 seconds
- Measure latency to gateway and internet
- Detect DNS resolution failures
- Show WAN status on both Network Overview and Network Health dashboards

**Non-Goals:**
- Bandwidth/throughput testing (would need iperf, too heavy for continuous monitoring)
- Per-client latency (different problem, needs pinging each client IP)
- ISP SLA monitoring (that's a business-level concern)

## Decisions

### 1. blackbox_exporter with ICMP module

Standard Prometheus probe exporter. ICMP ping is the lightest, most reliable WAN health check. No authentication needed, works through any firewall that allows ping.

Targets:
- `10.91.1.254` — gateway/router (tests local wired path)
- `8.8.8.8` — Google DNS (tests full internet path)
- `1.1.1.1` — Cloudflare DNS (redundant internet check)

### 2. DNS module for resolution testing

Separate probe that sends a DNS query for `google.com` to the configured DNS server. Tests if name resolution works independently of ICMP reachability.

### 3. Scrape interval 15s for probes

Faster than the 30s WiFi polling — WAN issues need faster detection. Ping is lightweight so 15s is fine.

### 4. Dashboard placement

- **Network Overview**: add one "Internet" stat panel (UP/DOWN) in the status bar
- **Network Health → SSIDs & Network Events**: replace WAN placeholder with 5 real panels (UP/DOWN, gateway latency, internet latency, packet loss, DNS time)

## Risks / Trade-offs

- **False positives** — if the monitoring host itself loses network, all probes fail. Mitigation: compare gateway (local) vs internet (remote) — if both fail, it's the monitoring host, not the WAN.
- **ICMP blocked** — some networks block outbound ICMP. Mitigation: DNS and HTTP probes as fallback.
- **Gateway IP hardcoded** — 10.91.1.254 in config. Mitigation: configurable via .env variable.

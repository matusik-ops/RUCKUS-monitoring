## 1. Refine Dashboard JSON

- [x] 1.1 Update status bar thresholds: APs Online (green ≥7, yellow ≥5, red <5), adjust stat panel sizes for wall-mount readability
- [x] 1.2 Add drill-down links from per-AP health bar gauges to AP Detail and Radio Health dashboards (using ap_name variable)
- [x] 1.3 Tune color thresholds for airtime busy (green <20%, yellow <40%, red ≥40%), auth failures (green <50, yellow <200, red ≥200), client data rate (green >70K, yellow >30K, red ≤30K)
- [x] 1.4 Sort weak-signal client table by RSSI ascending (worst first), data rate table by rate ascending (slowest first)

## 2. Set as Grafana Home Dashboard

- [x] 2.1 Update Grafana provisioning to set network-overview as the default home dashboard (grafana.ini or environment variable GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH)

## 3. Verify

- [x] 3.1 Restart Grafana, confirm dashboard loads as home page, all panels show data, drill-down links work
- [x] 3.2 Verify weak-signal and data-rate tables are populated correctly (or empty if no problem clients)

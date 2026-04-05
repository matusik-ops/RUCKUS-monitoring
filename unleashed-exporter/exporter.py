"""Prometheus exporter for Ruckus Unleashed per-client metrics.

Uses the _cmdstat.jsp XML/AJAX interface (firmware 200.15+).
Authentication: login.jsp + CSRF token from _csrfTokenVar.jsp.
"""

import logging
import os
import re
import signal
import sys
import time
import xml.etree.ElementTree as ET

import requests
from prometheus_client import CollectorRegistry, Gauge, Counter, start_http_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("unleashed-exporter")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_URL = os.environ.get("UNLEASHED_API_URL", "https://10.91.1.109")
USERNAME = os.environ.get("UNLEASHED_USERNAME", "admin")
PASSWORD = os.environ.get("UNLEASHED_PASSWORD", "")
POLL_INTERVAL = int(os.environ.get("UNLEASHED_POLL_INTERVAL", "60"))
VERIFY_SSL = os.environ.get("UNLEASHED_VERIFY_SSL", "false").lower() == "true"
EXPORTER_PORT = int(os.environ.get("EXPORTER_PORT", "9191"))

# ---------------------------------------------------------------------------
# Prometheus metrics
# ---------------------------------------------------------------------------
registry = CollectorRegistry()

CLIENT_LABELS = ["client_mac", "ap_name", "ssid", "radio_band", "hostname"]

client_rssi = Gauge(
    "unleashed_client_rssi_dbm",
    "Client received signal strength in dBm",
    CLIENT_LABELS,
    registry=registry,
)
client_noise_floor = Gauge(
    "unleashed_client_noise_floor_dbm",
    "Client noise floor in dBm",
    CLIENT_LABELS,
    registry=registry,
)
client_snr = Gauge(
    "unleashed_client_snr_db",
    "Client signal-to-noise ratio in dB (rssi value from AP)",
    CLIENT_LABELS,
    registry=registry,
)
client_channel = Gauge(
    "unleashed_client_channel",
    "Client wireless channel",
    CLIENT_LABELS,
    registry=registry,
)
client_tx_rate = Gauge(
    "unleashed_client_tx_rate_kbps",
    "Client Tx data rate in Kbps",
    CLIENT_LABELS,
    registry=registry,
)
client_rx_bytes = Gauge(
    "unleashed_client_rx_bytes_total",
    "Client total received bytes",
    CLIENT_LABELS,
    registry=registry,
)
client_tx_bytes = Gauge(
    "unleashed_client_tx_bytes_total",
    "Client total transmitted bytes",
    CLIENT_LABELS,
    registry=registry,
)
client_assoc_time = Gauge(
    "unleashed_client_assoc_time_seconds",
    "Client association start time (unix timestamp)",
    CLIENT_LABELS,
    registry=registry,
)
clients_per_ssid = Gauge(
    "unleashed_clients_per_ssid",
    "Number of connected clients per SSID",
    ["ssid"],
    registry=registry,
)
clients_per_ap = Gauge(
    "unleashed_clients_per_ap",
    "Number of connected clients per AP",
    ["ap_name"],
    registry=registry,
)
poll_errors = Counter(
    "unleashed_exporter_errors_total",
    "Total number of poll errors",
    ["type"],
    registry=registry,
)
poll_success = Counter(
    "unleashed_exporter_polls_total",
    "Total number of successful polls",
    registry=registry,
)
client_count = Gauge(
    "unleashed_client_count",
    "Total number of connected clients",
    registry=registry,
)

_CLIENT_GAUGES = [
    client_rssi,
    client_noise_floor,
    client_snr,
    client_channel,
    client_tx_rate,
    client_rx_bytes,
    client_tx_bytes,
    client_assoc_time,
]


# ---------------------------------------------------------------------------
# Unleashed _cmdstat.jsp client
# ---------------------------------------------------------------------------
class UnleashedClient:
    """Client for the Unleashed _cmdstat.jsp XML/AJAX interface."""

    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.csrf_token = None
        self._authenticated = False

    def login(self) -> bool:
        """Authenticate via login.jsp and fetch CSRF token."""
        try:
            # Step 1: Login via GET with credentials in query params
            resp = self.session.get(
                f"{self.base_url}/admin/login.jsp",
                params={
                    "username": self.username,
                    "password": self.password,
                    "ok": "Log In",
                },
                allow_redirects=True,
                timeout=15,
            )
            # 302 redirect = success, 200 with login page = failure
            # After following redirects we should have a session cookie
            if "-ejs-session-" not in str(self.session.cookies):
                log.error("Login failed: no session cookie received")
                poll_errors.labels(type="auth_failure").inc()
                self._authenticated = False
                return False

            # Step 2: Get CSRF token
            csrf_resp = self.session.get(
                f"{self.base_url}/admin/_csrfTokenVar.jsp",
                timeout=10,
            )
            match = re.search(r"var csfrToken = '([^']+)'", csrf_resp.text)
            if not match:
                # Try alternate format
                match = re.search(r"var defined_csrf = '([^']+)'", csrf_resp.text)
            if match:
                self.csrf_token = match.group(1)
                self._authenticated = True
                log.info("Authenticated (CSRF: %s...)", self.csrf_token[:4])
                return True
            else:
                log.error("Login succeeded but CSRF token not found: %s", csrf_resp.text[:200])
                poll_errors.labels(type="csrf_failure").inc()
                self._authenticated = False
                return False

        except requests.RequestException as exc:
            log.error("Login request failed: %s", exc)
            poll_errors.labels(type="connection_error").inc()
            self._authenticated = False
            return False

    def _cmdstat(self, xml_payload: str) -> str | None:
        """POST to _cmdstat.jsp and return the response text."""
        if not self._authenticated:
            if not self.login():
                return None
        try:
            resp = self.session.post(
                f"{self.base_url}/admin/_cmdstat.jsp",
                data=xml_payload,
                headers={
                    "Content-Type": "text/xml",
                    "X-CSRF-Token": self.csrf_token or "",
                },
                timeout=30,
            )
            # Check for redirect to login (session expired)
            if "login.jsp" in resp.url or resp.status_code == 302:
                log.warning("Session expired, re-authenticating")
                self._authenticated = False
                if not self.login():
                    return None
                resp = self.session.post(
                    f"{self.base_url}/admin/_cmdstat.jsp",
                    data=xml_payload,
                    headers={
                        "Content-Type": "text/xml",
                        "X-CSRF-Token": self.csrf_token or "",
                    },
                    timeout=30,
                )
            if resp.status_code == 200 and len(resp.text) > 1:
                return resp.text
            log.error("cmdstat failed: HTTP %s, body length %d", resp.status_code, len(resp.text))
            poll_errors.labels(type="api_error").inc()
            return None
        except requests.RequestException as exc:
            log.error("cmdstat request failed: %s", exc)
            poll_errors.labels(type="connection_error").inc()
            return None

    def get_stations(self) -> list[dict] | None:
        """Fetch per-client station list with interval stats via _cmdstat.jsp."""
        now = int(time.time())
        start = now - 300  # 5-minute window for interval stats
        xml = self._cmdstat(
            f"<ajax-request action='getstat' comp='stamgr' enable-gzip='0'>"
            f"<client INTERVAL-STATS='yes' INTERVAL-START='{start}' INTERVAL-STOP='{now}' />"
            f"</ajax-request>"
        )
        if xml is None:
            return None
        try:
            root = ET.fromstring(xml)
            clients = []
            for client_el in root.iter("client"):
                attrs = dict(client_el.attrib)
                # Merge interval-stats child element attributes (tx-rate, rx/tx bytes, etc.)
                for child in client_el:
                    if child.tag == "interval-stats":
                        for k, v in child.attrib.items():
                            if k not in attrs:
                                attrs[k] = v
                clients.append(attrs)
            return clients
        except ET.ParseError as exc:
            log.error("XML parse error: %s", exc)
            poll_errors.labels(type="parse_error").inc()
            return None


# ---------------------------------------------------------------------------
# Metric update logic
# ---------------------------------------------------------------------------
def _clear_client_metrics(known_labels: set[tuple]):
    """Remove metrics for clients no longer present."""
    for gauge in _CLIENT_GAUGES:
        stale = set(gauge._metrics.keys()) - known_labels
        for key in stale:
            gauge.remove(*key)


def update_metrics(stations: list[dict]):
    """Update all Prometheus metrics from the station list."""
    current_labels: set[tuple] = set()
    ssid_counts: dict[str, int] = {}
    ap_counts: dict[str, int] = {}

    for sta in stations:
        mac = sta.get("mac", "unknown")
        ap = sta.get("ap-name", "unknown")
        ssid = sta.get("ssid", "unknown")
        band = sta.get("radio-band", "unknown")
        hostname = sta.get("hostname", sta.get("oldname", mac))
        labels = (mac, ap, ssid, band, hostname)
        current_labels.add(labels)

        # received-signal-strength is the dBm value (e.g., -54)
        rss = sta.get("received-signal-strength")
        if rss is not None:
            client_rssi.labels(*labels).set(float(rss))

        # rssi is the SNR-like value from the AP (e.g., 42)
        snr = sta.get("rssi")
        if snr is not None:
            client_snr.labels(*labels).set(float(snr))

        nf = sta.get("noise-floor")
        if nf is not None:
            client_noise_floor.labels(*labels).set(float(nf))

        ch = sta.get("channel")
        if ch is not None:
            client_channel.labels(*labels).set(float(ch))

        # tx-rate is in Kbps (e.g., 135000.0 = 135 Mbps) — from interval stats
        tx_rate = sta.get("tx-rate")
        if tx_rate is not None:
            client_tx_rate.labels(*labels).set(float(tx_rate))

        rx = sta.get("total-rx-bytes")
        if rx is not None:
            client_rx_bytes.labels(*labels).set(float(rx))

        tx = sta.get("total-tx-bytes")
        if tx is not None:
            client_tx_bytes.labels(*labels).set(float(tx))

        assoc = sta.get("first-assoc")
        if assoc is not None:
            client_assoc_time.labels(*labels).set(float(assoc))

        ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1
        ap_counts[ap] = ap_counts.get(ap, 0) + 1

    # Remove stale clients
    _clear_client_metrics(current_labels)

    # Per-SSID counts
    stale_ssids = set(clients_per_ssid._metrics.keys()) - {(s,) for s in ssid_counts}
    for key in stale_ssids:
        clients_per_ssid.remove(*key)
    for ssid, count in ssid_counts.items():
        clients_per_ssid.labels(ssid=ssid).set(count)

    # Per-AP counts
    stale_aps = set(clients_per_ap._metrics.keys()) - {(a,) for a in ap_counts}
    for key in stale_aps:
        clients_per_ap.remove(*key)
    for ap, count in ap_counts.items():
        clients_per_ap.labels(ap_name=ap).set(count)

    client_count.set(len(stations))
    poll_success.inc()
    log.info("Updated metrics for %d clients across %d SSIDs, %d APs",
             len(stations), len(ssid_counts), len(ap_counts))


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def main():
    if not PASSWORD:
        log.error("UNLEASHED_PASSWORD not set")
        sys.exit(1)

    if not VERIFY_SSL:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    client = UnleashedClient(API_URL, USERNAME, PASSWORD, VERIFY_SSL)

    log.info("Starting unleashed-exporter on :%d (poll interval: %ds)", EXPORTER_PORT, POLL_INTERVAL)
    start_http_server(EXPORTER_PORT, registry=registry)

    running = True

    def _shutdown(signum, frame):
        nonlocal running
        log.info("Shutting down")
        running = False

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    while running:
        stations = client.get_stations()
        if stations is not None:
            update_metrics(stations)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

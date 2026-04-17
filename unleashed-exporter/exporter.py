"""Prometheus exporter for Ruckus Unleashed per-client and per-radio metrics.

Uses the _cmdstat.jsp XML/AJAX interface (firmware 200.15+).
Authentication: login.jsp + CSRF token from _csrfTokenVar.jsp.
Collects three data sets per poll cycle:
  1. Per-client stats via <client INTERVAL-STATS='yes'/>
  2. Per-AP, per-radio stats via <ap LEVEL='1'/>
  3. Rogue AP detections via <rogue/>
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

client_retries = Gauge(
    "unleashed_client_retries_total",
    "Client total Tx retries",
    CLIENT_LABELS,
    registry=registry,
)
client_retry_bytes = Gauge(
    "unleashed_client_retry_bytes_total",
    "Client total retry bytes",
    CLIENT_LABELS,
    registry=registry,
)
client_rx_pkts = Gauge(
    "unleashed_client_rx_pkts_total",
    "Client total received packets",
    CLIENT_LABELS,
    registry=registry,
)
client_tx_pkts = Gauge(
    "unleashed_client_tx_pkts_total",
    "Client total transmitted packets",
    CLIENT_LABELS,
    registry=registry,
)
client_min_rssi = Gauge(
    "unleashed_client_min_rssi_dbm",
    "Client min RSSI over interval-stats window (dBm)",
    CLIENT_LABELS,
    registry=registry,
)
client_max_rssi = Gauge(
    "unleashed_client_max_rssi_dbm",
    "Client max RSSI over interval-stats window (dBm)",
    CLIENT_LABELS,
    registry=registry,
)

# Info gauge with textual labels (IP, VLAN, OS, etc.)
CLIENT_INFO_LABELS = [
    "client_mac", "apz_device", "hostname", "ip", "vlan", "ap_name", "ssid",
    "radio_band", "auth_method", "encryption", "dvctype", "model_os"
]
client_info = Gauge(
    "unleashed_client_info",
    "Client inventory info (always 1); labels contain identity/config",
    CLIENT_INFO_LABELS,
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
    client_retries,
    client_retry_bytes,
    client_rx_pkts,
    client_tx_pkts,
    client_min_rssi,
    client_max_rssi,
]

# ---------------------------------------------------------------------------
# Per-radio metrics (from <ap LEVEL='1'/> query)
# ---------------------------------------------------------------------------
RADIO_LABELS = ["ap_name", "radio_band", "channel"]

radio_airtime_total = Gauge("unleashed_radio_airtime_total", "Radio airtime total", RADIO_LABELS, registry=registry)
radio_airtime_busy = Gauge("unleashed_radio_airtime_busy", "Radio airtime busy (interference/other)", RADIO_LABELS, registry=registry)
radio_airtime_rx = Gauge("unleashed_radio_airtime_rx", "Radio airtime Rx", RADIO_LABELS, registry=registry)
radio_airtime_tx = Gauge("unleashed_radio_airtime_tx", "Radio airtime Tx", RADIO_LABELS, registry=registry)
radio_num_sta = Gauge("unleashed_radio_num_sta", "Clients per radio", RADIO_LABELS, registry=registry)
radio_avg_rssi = Gauge("unleashed_radio_avg_rssi", "Average client RSSI per radio", RADIO_LABELS, registry=registry)
radio_tx_bytes = Gauge("unleashed_radio_tx_bytes_total", "Radio total Tx bytes", RADIO_LABELS, registry=registry)
radio_rx_bytes = Gauge("unleashed_radio_rx_bytes_total", "Radio total Rx bytes", RADIO_LABELS, registry=registry)
radio_tx_pkts = Gauge("unleashed_radio_tx_pkts_total", "Radio total Tx packets", RADIO_LABELS, registry=registry)
radio_rx_pkts = Gauge("unleashed_radio_rx_pkts_total", "Radio total Rx packets", RADIO_LABELS, registry=registry)
radio_tx_fail = Gauge("unleashed_radio_tx_fail_total", "Radio total Tx failures", RADIO_LABELS, registry=registry)
radio_retries = Gauge("unleashed_radio_retries_total", "Radio total Tx retries", RADIO_LABELS, registry=registry)
radio_fcs_err = Gauge("unleashed_radio_fcs_error_total", "Radio total FCS errors", RADIO_LABELS, registry=registry)
radio_auth_fail = Gauge("unleashed_radio_auth_fail", "Radio auth failures", RADIO_LABELS, registry=registry)
radio_auth_success = Gauge("unleashed_radio_auth_success", "Radio auth successes", RADIO_LABELS, registry=registry)
radio_assoc_fail = Gauge("unleashed_radio_assoc_fail", "Radio assoc failures", RADIO_LABELS, registry=registry)
radio_assoc_success = Gauge("unleashed_radio_assoc_success", "Radio assoc successes", RADIO_LABELS, registry=registry)
radio_channel_g = Gauge("unleashed_radio_channel", "Radio channel number", ["ap_name", "radio_band"], registry=registry)
radio_tx_power = Gauge("unleashed_radio_tx_power", "Radio Tx power setting", ["ap_name", "radio_band"], registry=registry)
radio_channelization = Gauge("unleashed_radio_channelization", "Radio channel width (MHz)", ["ap_name", "radio_band"], registry=registry)
radio_noise_floor = Gauge("unleashed_radio_noise_floor_dbm", "Radio noise floor in dBm", RADIO_LABELS, registry=registry)
radio_phy_err = Gauge("unleashed_radio_phy_err", "Radio PHY-layer errors (cumulative)", RADIO_LABELS, registry=registry)

# ---------------------------------------------------------------------------
# Per-AP metrics (numeric stats)
# ---------------------------------------------------------------------------
AP_NUMERIC_LABELS = ["ap_name"]
ap_cpu = Gauge("unleashed_ap_cpu_util", "AP CPU utilization (%)", AP_NUMERIC_LABELS, registry=registry)
ap_mem_total = Gauge("unleashed_ap_mem_total", "AP total memory (KB)", AP_NUMERIC_LABELS, registry=registry)
ap_mem_avail = Gauge("unleashed_ap_mem_avail", "AP available memory (KB)", AP_NUMERIC_LABELS, registry=registry)
ap_mem_used_pct = Gauge("unleashed_ap_mem_used_pct", "AP memory used percentage", AP_NUMERIC_LABELS, registry=registry)
ap_uptime = Gauge("unleashed_ap_uptime_seconds", "AP uptime in seconds", AP_NUMERIC_LABELS, registry=registry)
ap_num_sta = Gauge("unleashed_ap_num_sta", "AP total clients", AP_NUMERIC_LABELS, registry=registry)
ap_num_vap = Gauge("unleashed_ap_num_vap", "AP active VAPs (SSIDs broadcasting)", AP_NUMERIC_LABELS, registry=registry)
ap_temperature = Gauge("unleashed_ap_temperature", "AP temperature (or -999 if unavailable)", AP_NUMERIC_LABELS, registry=registry)
ap_app_reboots = Gauge("unleashed_ap_app_reboots_total", "AP application reboot counter", AP_NUMERIC_LABELS, registry=registry)
ap_kernel_panics = Gauge("unleashed_ap_kernel_panics_total", "AP kernel panic counter", AP_NUMERIC_LABELS, registry=registry)
ap_powercycle_reboots = Gauge("unleashed_ap_powercycle_reboots_total", "AP power-cycle reboot counter", AP_NUMERIC_LABELS, registry=registry)
ap_total_reboots = Gauge("unleashed_ap_total_reboots", "AP total boot counter", AP_NUMERIC_LABELS, registry=registry)
ap_connected_time = Gauge("unleashed_ap_connected_time_seconds", "AP cumulative connected time (seconds)", AP_NUMERIC_LABELS, registry=registry)
ap_join_counter = Gauge("unleashed_ap_join_counter", "AP rejoin counter (how many times AP has rejoined)", AP_NUMERIC_LABELS, registry=registry)
ap_crashfile = Gauge("unleashed_ap_crashfile_flag", "AP has saved crashfile (1=yes, 0=no)", AP_NUMERIC_LABELS, registry=registry)
ap_lan_rx_bytes = Gauge("unleashed_ap_lan_rx_bytes_total", "AP wired Ethernet Rx bytes", AP_NUMERIC_LABELS, registry=registry)
ap_lan_tx_bytes = Gauge("unleashed_ap_lan_tx_bytes_total", "AP wired Ethernet Tx bytes", AP_NUMERIC_LABELS, registry=registry)
ap_lan_rx_pkts = Gauge("unleashed_ap_lan_rx_pkts_total", "AP wired Ethernet Rx packets", AP_NUMERIC_LABELS, registry=registry)
ap_lan_tx_pkts = Gauge("unleashed_ap_lan_tx_pkts_total", "AP wired Ethernet Tx packets", AP_NUMERIC_LABELS, registry=registry)
ap_lan_dropped = Gauge("unleashed_ap_lan_dropped_total", "AP wired Ethernet dropped packets", AP_NUMERIC_LABELS, registry=registry)

# AP info — uses labels for textual fields (IP, MAC, model, firmware, etc.)
AP_INFO_LABELS = ["ap_name", "ip", "mac", "model", "serial_number",
                  "firmware_version", "poe_mode", "last_reboot_reason",
                  "last_rejoin_reason", "role"]
ap_info = Gauge("unleashed_ap_info", "AP inventory info (always 1)", AP_INFO_LABELS, registry=registry)

ap_state = Gauge("unleashed_ap_state", "AP state (1=connected, 0=disconnected)", AP_NUMERIC_LABELS, registry=registry)

_AP_NUMERIC_GAUGES = [
    ap_cpu, ap_mem_total, ap_mem_avail, ap_mem_used_pct,
    ap_uptime, ap_num_sta, ap_num_vap, ap_temperature,
    ap_app_reboots, ap_kernel_panics, ap_powercycle_reboots, ap_total_reboots,
    ap_state, ap_connected_time, ap_join_counter, ap_crashfile,
    ap_lan_rx_bytes, ap_lan_tx_bytes, ap_lan_rx_pkts, ap_lan_tx_pkts, ap_lan_dropped,
]

# ---------------------------------------------------------------------------
# Per-WLAN (SSID) metrics — from <wlan LEVEL='1'/>
# ---------------------------------------------------------------------------
WLAN_LABELS = ["ssid", "vlan_id", "state"]

wlan_num_sta = Gauge("unleashed_wlan_num_sta", "Clients on this WLAN/SSID", WLAN_LABELS, registry=registry)
wlan_num_vap = Gauge("unleashed_wlan_num_vap", "Number of VAP instances for this SSID", WLAN_LABELS, registry=registry)
wlan_rx_bytes = Gauge("unleashed_wlan_rx_bytes_total", "WLAN total Rx bytes", WLAN_LABELS, registry=registry)
wlan_tx_bytes = Gauge("unleashed_wlan_tx_bytes_total", "WLAN total Tx bytes", WLAN_LABELS, registry=registry)
wlan_rx_pkts = Gauge("unleashed_wlan_rx_pkts_total", "WLAN total Rx packets", WLAN_LABELS, registry=registry)
wlan_tx_pkts = Gauge("unleashed_wlan_tx_pkts_total", "WLAN total Tx packets", WLAN_LABELS, registry=registry)
wlan_auth_success = Gauge("unleashed_wlan_auth_success_total", "WLAN total auth successes", WLAN_LABELS, registry=registry)
wlan_auth_fail = Gauge("unleashed_wlan_auth_fail_total", "WLAN total auth failures", WLAN_LABELS, registry=registry)
wlan_assoc_success = Gauge("unleashed_wlan_assoc_success_total", "WLAN total assoc successes", WLAN_LABELS, registry=registry)
wlan_assoc_fail = Gauge("unleashed_wlan_assoc_fail_total", "WLAN total assoc failures", WLAN_LABELS, registry=registry)
wlan_total_auth = Gauge("unleashed_wlan_total_auth", "WLAN total auth attempts", WLAN_LABELS, registry=registry)
wlan_total_assoc = Gauge("unleashed_wlan_total_assoc", "WLAN total assoc attempts", WLAN_LABELS, registry=registry)

_WLAN_GAUGES = [
    wlan_num_sta, wlan_num_vap, wlan_rx_bytes, wlan_tx_bytes, wlan_rx_pkts, wlan_tx_pkts,
    wlan_auth_success, wlan_auth_fail, wlan_assoc_success, wlan_assoc_fail,
    wlan_total_auth, wlan_total_assoc,
]

_RADIO_GAUGES = [
    radio_airtime_total, radio_airtime_busy, radio_airtime_rx, radio_airtime_tx,
    radio_num_sta, radio_avg_rssi, radio_tx_bytes, radio_rx_bytes,
    radio_tx_pkts, radio_rx_pkts, radio_tx_fail, radio_retries, radio_fcs_err,
    radio_auth_fail, radio_auth_success, radio_assoc_fail, radio_assoc_success,
    radio_noise_floor, radio_phy_err,
]
_RADIO_CONFIG_GAUGES = [radio_channel_g, radio_tx_power, radio_channelization]

# ---------------------------------------------------------------------------
# Rogue AP metrics (from <rogue/> query)
# ---------------------------------------------------------------------------
ROGUE_LABELS = ["rogue_mac", "rogue_ssid", "rogue_channel", "rogue_band",
                "rogue_type", "is_malicious", "detector_ap"]

rogue_rssi = Gauge(
    "unleashed_rogue_rssi_dbm",
    "Rogue AP signal strength in dBm as detected by one of our APs",
    ROGUE_LABELS,
    registry=registry,
)
rogue_count = Gauge(
    "unleashed_rogue_count",
    "Total number of unique rogue APs detected",
    registry=registry,
)
rogue_malicious_count = Gauge(
    "unleashed_rogue_malicious_count",
    "Total number of malicious (same-network) rogue APs detected",
    registry=registry,
)
rogue_count_by_band = Gauge(
    "unleashed_rogue_count_by_band",
    "Number of rogues per radio band",
    ["radio_band"],
    registry=registry,
)
rogue_count_by_channel = Gauge(
    "unleashed_rogue_count_by_channel",
    "Number of rogues per channel",
    ["channel", "radio_band"],
    registry=registry,
)


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


    def get_wlans(self) -> list[dict] | None:
        """Fetch per-SSID/WLAN stats via _cmdstat.jsp."""
        xml = self._cmdstat(
            "<ajax-request action='getstat' comp='stamgr'>"
            "<wlan LEVEL='1'/>"
            "</ajax-request>"
        )
        if xml is None:
            return None
        try:
            root = ET.fromstring(xml)
            wlans = []
            for wlan_el in root.iter("wlan"):
                wlans.append(dict(wlan_el.attrib))
            return wlans
        except ET.ParseError as exc:
            log.error("WLAN XML parse error: %s", exc)
            poll_errors.labels(type="parse_error").inc()
            return None

    def get_rogues(self) -> list[dict] | None:
        """Fetch rogue AP detections via _cmdstat.jsp.

        Returns a list of dicts, each representing one rogue+detector pair.
        Each rogue can be detected by multiple of our APs, producing one entry per detector.
        """
        xml = self._cmdstat(
            "<ajax-request action='getstat' comp='stamgr' enable-gzip='0'>"
            "<rogue/>"
            "</ajax-request>"
        )
        if xml is None:
            return None
        try:
            root = ET.fromstring(xml)
            entries = []
            for rogue_el in root.iter("rogue"):
                rogue_attrs = dict(rogue_el.attrib)
                detections = list(rogue_el.iter("detection"))
                if not detections:
                    # Rogue with no detection child — still record with empty detector
                    entries.append({"rogue": rogue_attrs, "detection": {}})
                else:
                    for det in detections:
                        entries.append({"rogue": rogue_attrs, "detection": dict(det.attrib)})
            return entries
        except ET.ParseError as exc:
            log.error("Rogue XML parse error: %s", exc)
            poll_errors.labels(type="parse_error").inc()
            return None

    def get_ap_stats(self) -> list[dict] | None:
        """Fetch per-AP, per-radio stats via _cmdstat.jsp."""
        xml = self._cmdstat(
            "<ajax-request action='getstat' comp='stamgr' enable-gzip='0'>"
            "<ap LEVEL='1'/>"
            "</ajax-request>"
        )
        if xml is None:
            return None
        try:
            root = ET.fromstring(xml)
            aps = []
            for ap_el in root.iter("ap"):
                ap_data = {"attrs": dict(ap_el.attrib), "radios": []}
                for radio_el in ap_el.iter("radio"):
                    ap_data["radios"].append(dict(radio_el.attrib))
                aps.append(ap_data)
            return aps
        except ET.ParseError as exc:
            log.error("AP stats XML parse error: %s", exc)
            poll_errors.labels(type="parse_error").inc()
            return None


# ---------------------------------------------------------------------------
# Metric update logic
# ---------------------------------------------------------------------------
def _detect_device_groups(stations: list[dict]) -> dict[str, str]:
    """Detect dual-radio devices by finding sequential MAC addresses.

    If two clients share the same MAC prefix (first 5 octets) and differ
    only in the last octet by 1-2, they're likely the same physical device
    with two WiFi NICs.

    Returns: dict mapping MAC → apz_device (hostname of the "best" NIC).
    """
    mac_to_prefix: dict[str, tuple] = {}
    for sta in stations:
        mac = sta.get("mac", "")
        if len(mac) == 17:
            prefix = mac[:14]  # first 5 octets "aa:bb:cc:dd:ee"
            last_byte = int(mac[15:17], 16)
            mac_to_prefix[mac] = (prefix, last_byte)

    # Group MACs by prefix
    from collections import defaultdict
    by_prefix: dict[str, list] = defaultdict(list)
    for mac, (prefix, last_byte) in mac_to_prefix.items():
        by_prefix[prefix].append((mac, last_byte))

    # Find groups where MACs differ by 1-2 in last byte
    mac_to_device: dict[str, str] = {}
    for prefix, members in by_prefix.items():
        if len(members) < 2:
            continue
        members.sort(key=lambda x: x[1])
        # Check if consecutive MACs are within 2 of each other
        group = [members[0]]
        for i in range(1, len(members)):
            if members[i][1] - members[i-1][1] <= 2:
                group.append(members[i])

        if len(group) >= 2:
            # Find the best hostname for this device group
            group_macs = {m[0] for m in group}
            best_hostname = ""
            for sta in stations:
                if sta.get("mac") in group_macs:
                    h = sta.get("hostname", "")
                    # Prefer a real hostname over MAC-as-hostname
                    if h and ":" not in h and (not best_hostname or ":" in best_hostname):
                        best_hostname = h
                    elif not best_hostname:
                        best_hostname = h
            if not best_hostname:
                best_hostname = group[0][0]

            for mac, _ in group:
                mac_to_device[mac] = best_hostname

    return mac_to_device


_client_earliest_assoc: dict[str, float] = {}


def _clear_client_metrics(known_labels: set[tuple]):
    """Remove metrics for clients no longer present."""
    known_macs = {lbl[0] for lbl in known_labels}
    for mac in list(_client_earliest_assoc):
        if mac not in known_macs:
            del _client_earliest_assoc[mac]
    for gauge in _CLIENT_GAUGES:
        stale = set(gauge._metrics.keys()) - known_labels
        for key in stale:
            gauge.remove(*key)


def update_metrics(stations: list[dict]):
    """Update all Prometheus metrics from the station list."""
    current_labels: set[tuple] = set()
    ssid_counts: dict[str, int] = {}
    ap_counts: dict[str, int] = {}

    current_info_labels: set[tuple] = set()
    mac_to_device = _detect_device_groups(stations)

    for sta in stations:
        mac = sta.get("mac", "unknown")
        ap = sta.get("ap-name", "unknown")
        ssid = sta.get("ssid", "unknown")
        band = sta.get("radio-band", "unknown")
        hostname = sta.get("hostname", sta.get("oldname", mac))
        labels = (mac, ap, ssid, band, hostname)
        current_labels.add(labels)

        # Info gauge with all textual/identity labels
        apz_device = mac_to_device.get(mac, "")  # empty = single-NIC device
        info_labels = (
            mac,
            apz_device,
            hostname,
            sta.get("ip", ""),
            sta.get("vlan", ""),
            ap,
            ssid,
            band,
            sta.get("auth-method", ""),
            sta.get("encryption", ""),
            sta.get("dvctype", ""),
            sta.get("model", ""),
        )
        current_info_labels.add(info_labels)
        client_info.labels(*info_labels).set(1)

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
            assoc_val = float(assoc)
            prev = _client_earliest_assoc.get(mac)
            if prev is None or assoc_val < prev:
                _client_earliest_assoc[mac] = assoc_val
            client_assoc_time.labels(*labels).set(_client_earliest_assoc[mac])

        retries = sta.get("total-retries")
        if retries is not None:
            client_retries.labels(*labels).set(float(retries))

        retry_bytes = sta.get("total-retry-bytes")
        if retry_bytes is not None:
            client_retry_bytes.labels(*labels).set(float(retry_bytes))

        rx_pkts = sta.get("total-rx-pkts")
        if rx_pkts is not None:
            client_rx_pkts.labels(*labels).set(float(rx_pkts))

        tx_pkts = sta.get("total-tx-pkts")
        if tx_pkts is not None:
            client_tx_pkts.labels(*labels).set(float(tx_pkts))

        min_rssi = sta.get("min-received-signal-strength")
        if min_rssi is not None:
            try:
                client_min_rssi.labels(*labels).set(float(min_rssi))
            except (ValueError, TypeError):
                pass

        max_rssi = sta.get("max-received-signal-strength")
        if max_rssi is not None:
            try:
                client_max_rssi.labels(*labels).set(float(max_rssi))
            except (ValueError, TypeError):
                pass

        ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1
        ap_counts[ap] = ap_counts.get(ap, 0) + 1

    # Remove stale clients
    _clear_client_metrics(current_labels)

    # Cleanup client_info gauge
    stale_info = set(client_info._metrics.keys()) - current_info_labels
    for key in stale_info:
        client_info.remove(*key)

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


def _clear_radio_metrics(known_labels: set[tuple]):
    """Remove radio metrics for APs/radios no longer present."""
    for gauge in _RADIO_GAUGES:
        stale = set(gauge._metrics.keys()) - known_labels
        for key in stale:
            gauge.remove(*key)
    # Config gauges use 2 labels (ap_name, radio_band)
    known_config = {(l[0], l[1]) for l in known_labels}
    for gauge in _RADIO_CONFIG_GAUGES:
        stale = set(gauge._metrics.keys()) - known_config
        for key in stale:
            gauge.remove(*key)


def _set_radio_gauge(gauge, labels, value):
    """Set a gauge if value is not None and non-empty."""
    if value is not None and value != "":
        try:
            gauge.labels(*labels).set(float(value))
        except (ValueError, TypeError):
            pass


def update_ap_info_metrics(aps: list[dict]):
    """Update per-AP inventory + numeric metrics from AP stats."""
    current_ap_names: set[str] = set()
    current_info_labels: set[tuple] = set()

    for ap_data in aps:
        attrs = ap_data["attrs"]
        ap_name = attrs.get("ap-name", "")
        if not ap_name:
            continue

        current_ap_names.add(ap_name)
        labels = (ap_name,)

        # State
        try:
            ap_state.labels(*labels).set(1 if attrs.get("state") == "1" else 0)
        except (ValueError, TypeError):
            pass

        # Numeric metrics — only set if value is meaningful
        _set_radio_gauge(ap_cpu, labels, attrs.get("cpu_util"))
        _set_radio_gauge(ap_mem_total, labels, attrs.get("mem_total"))
        _set_radio_gauge(ap_mem_avail, labels, attrs.get("mem_avail"))

        try:
            mt = float(attrs.get("mem_total") or 0)
            ma = float(attrs.get("mem_avail") or 0)
            if mt > 0:
                used_pct = (mt - ma) / mt * 100
                ap_mem_used_pct.labels(*labels).set(used_pct)
        except (ValueError, TypeError):
            pass

        _set_radio_gauge(ap_uptime, labels, attrs.get("uptime"))
        _set_radio_gauge(ap_num_sta, labels, attrs.get("num-sta"))
        _set_radio_gauge(ap_num_vap, labels, attrs.get("num-vap"))
        _set_radio_gauge(ap_app_reboots, labels, attrs.get("application-reboot-counter"))
        _set_radio_gauge(ap_kernel_panics, labels, attrs.get("kernel-panic-reboot-counter"))
        _set_radio_gauge(ap_powercycle_reboots, labels, attrs.get("powercycle-reboot-counter"))
        _set_radio_gauge(ap_total_reboots, labels, attrs.get("total-boot-counter"))
        _set_radio_gauge(ap_connected_time, labels, attrs.get("amount-connected-time"))
        _set_radio_gauge(ap_join_counter, labels, attrs.get("ap-join-counter"))
        _set_radio_gauge(ap_crashfile, labels, attrs.get("ap-crashfile-flag"))
        _set_radio_gauge(ap_lan_rx_bytes, labels, attrs.get("lan_stats_rx_byte"))
        _set_radio_gauge(ap_lan_tx_bytes, labels, attrs.get("lan_stats_tx_byte"))
        _set_radio_gauge(ap_lan_rx_pkts, labels, attrs.get("lan_stats_rx_pkt_succ"))
        _set_radio_gauge(ap_lan_tx_pkts, labels, attrs.get("lan_stats_tx_pkt"))
        _set_radio_gauge(ap_lan_dropped, labels, attrs.get("lan_stats_dropped"))

        # Temperature
        temp = attrs.get("current-temperature")
        if temp and temp != "unavailable":
            try:
                ap_temperature.labels(*labels).set(float(temp))
            except (ValueError, TypeError):
                ap_temperature.labels(*labels).set(-999)
        else:
            ap_temperature.labels(*labels).set(-999)

        # Info gauge with text labels
        info_labels = (
            ap_name,
            attrs.get("ip", ""),
            attrs.get("mac", ""),
            attrs.get("display-model", attrs.get("model", "")),
            attrs.get("serial-number", ""),
            attrs.get("firmware-version", ""),
            attrs.get("poe-mode-str", ""),
            attrs.get("last-reboot-reason", ""),
            attrs.get("last-rejoin-reason", ""),
            attrs.get("role", ""),
        )
        current_info_labels.add(info_labels)
        ap_info.labels(*info_labels).set(1)

    # Cleanup numeric gauges for APs that disappeared
    for gauge in _AP_NUMERIC_GAUGES:
        stale = set(gauge._metrics.keys()) - {(n,) for n in current_ap_names}
        for key in stale:
            gauge.remove(*key)

    # Cleanup info gauge
    stale_info = set(ap_info._metrics.keys()) - current_info_labels
    for key in stale_info:
        ap_info.remove(*key)


def update_radio_metrics(aps: list[dict]):
    """Update per-radio Prometheus metrics from AP stats."""
    current_labels: set[tuple] = set()
    radio_count = 0

    for ap_data in aps:
        attrs = ap_data["attrs"]
        state = attrs.get("state", "0")
        if state != "1":
            continue  # Skip disconnected APs

        ap_name = attrs.get("ap-name", "unknown")

        for radio in ap_data["radios"]:
            band = radio.get("radio-band", "unknown")
            ch = radio.get("channel", "0")
            labels = (ap_name, band, ch)
            current_labels.add(labels)
            radio_count += 1

            _set_radio_gauge(radio_airtime_total, labels, radio.get("airtime-total"))
            _set_radio_gauge(radio_airtime_busy, labels, radio.get("airtime-busy"))
            _set_radio_gauge(radio_airtime_rx, labels, radio.get("airtime-rx"))
            _set_radio_gauge(radio_airtime_tx, labels, radio.get("airtime-tx"))
            _set_radio_gauge(radio_num_sta, labels, radio.get("num-sta"))
            _set_radio_gauge(radio_avg_rssi, labels, radio.get("avg-rssi"))
            _set_radio_gauge(radio_tx_bytes, labels, radio.get("radio-total-tx-bytes"))
            _set_radio_gauge(radio_rx_bytes, labels, radio.get("radio-total-rx-bytes"))
            _set_radio_gauge(radio_tx_pkts, labels, radio.get("radio-total-tx-pkts"))
            _set_radio_gauge(radio_rx_pkts, labels, radio.get("radio-total-rx-pkts"))
            _set_radio_gauge(radio_tx_fail, labels, radio.get("radio-total-tx-fail"))
            _set_radio_gauge(radio_retries, labels, radio.get("radio-total-retries"))
            _set_radio_gauge(radio_fcs_err, labels, radio.get("total-fcs-err"))
            _set_radio_gauge(radio_auth_fail, labels, radio.get("mgmt-auth-fail"))
            _set_radio_gauge(radio_auth_success, labels, radio.get("mgmt-auth-success"))
            _set_radio_gauge(radio_assoc_fail, labels, radio.get("mgmt-assoc-fail"))
            _set_radio_gauge(radio_assoc_success, labels, radio.get("mgmt-assoc-success"))
            _set_radio_gauge(radio_noise_floor, labels, radio.get("noisefloor"))
            _set_radio_gauge(radio_phy_err, labels, radio.get("phyerr"))

            config_labels = (ap_name, band)
            _set_radio_gauge(radio_channel_g, config_labels, ch)
            _set_radio_gauge(radio_tx_power, config_labels, radio.get("tx-power"))
            _set_radio_gauge(radio_channelization, config_labels, radio.get("channelization"))

    _clear_radio_metrics(current_labels)
    log.info("Updated radio metrics for %d radios", radio_count)


def update_wlan_metrics(wlans: list[dict]):
    """Update per-WLAN (SSID) Prometheus metrics."""
    current_labels: set[tuple] = set()

    for w in wlans:
        ssid = w.get("ssid", "unknown")
        vlan_id = w.get("vlan-id", "")
        state = w.get("state", "")
        labels = (ssid, vlan_id, state)
        current_labels.add(labels)

        _set_radio_gauge(wlan_num_sta, labels, w.get("num-sta"))
        _set_radio_gauge(wlan_num_vap, labels, w.get("num-vap"))
        _set_radio_gauge(wlan_rx_bytes, labels, w.get("rx-bytes"))
        _set_radio_gauge(wlan_tx_bytes, labels, w.get("tx-bytes"))
        _set_radio_gauge(wlan_rx_pkts, labels, w.get("rx-pkts"))
        _set_radio_gauge(wlan_tx_pkts, labels, w.get("tx-pkts"))
        _set_radio_gauge(wlan_auth_success, labels, w.get("mgmt-auth-success"))
        _set_radio_gauge(wlan_auth_fail, labels, w.get("mgmt-auth-fail"))
        _set_radio_gauge(wlan_assoc_success, labels, w.get("mgmt-assoc-success"))
        _set_radio_gauge(wlan_assoc_fail, labels, w.get("mgmt-assoc-fail"))
        _set_radio_gauge(wlan_total_auth, labels, w.get("total-auth"))
        _set_radio_gauge(wlan_total_assoc, labels, w.get("total-assoc"))

    # Cleanup stale
    for gauge in _WLAN_GAUGES:
        stale = set(gauge._metrics.keys()) - current_labels
        for key in stale:
            gauge.remove(*key)

    log.info("Updated WLAN metrics for %d SSIDs", len(wlans))


def update_rogue_metrics(entries: list[dict]):
    """Update per-rogue Prometheus metrics from rogue detections.

    `entries` is a list of {"rogue": {...}, "detection": {...}} dicts,
    one per rogue+detector pair.
    """
    current_labels: set[tuple] = set()
    unique_rogues: set[str] = set()
    malicious_rogues: set[str] = set()
    band_counts: dict[str, set] = {}  # band -> set of rogue MACs
    channel_counts: dict[tuple, set] = {}  # (channel, band) -> set of rogue MACs

    for entry in entries:
        rogue = entry["rogue"]
        detection = entry["detection"]

        mac = rogue.get("mac", "unknown")
        ssid = rogue.get("ssid", "")
        channel = rogue.get("channel", "0")
        band = rogue.get("radio-band", "unknown")
        rogue_type = rogue.get("rogue-type", "unknown")
        is_malicious = "true" if "malicious" in rogue_type.lower() else "false"
        detector = detection.get("sys-name", "unknown")
        rssi_raw = detection.get("rssi")

        labels = (mac, ssid, channel, band, rogue_type, is_malicious, detector)
        current_labels.add(labels)

        # RSSI is a scaled value (0-100, same as client rssi field)
        # Convert to approximate dBm: dBm ≈ rssi - 96
        if rssi_raw is not None:
            try:
                rssi_dbm = float(rssi_raw) - 96
                rogue_rssi.labels(*labels).set(rssi_dbm)
            except (ValueError, TypeError):
                pass

        # Aggregations (count unique rogues, not detector pairs)
        unique_rogues.add(mac)
        if is_malicious == "true":
            malicious_rogues.add(mac)
        band_counts.setdefault(band, set()).add(mac)
        channel_counts.setdefault((channel, band), set()).add(mac)

    # Remove stale rogue+detector samples
    stale = set(rogue_rssi._metrics.keys()) - current_labels
    for key in stale:
        rogue_rssi.remove(*key)

    # Update summary gauges
    rogue_count.set(len(unique_rogues))
    rogue_malicious_count.set(len(malicious_rogues))

    stale_bands = set(rogue_count_by_band._metrics.keys()) - {(b,) for b in band_counts}
    for key in stale_bands:
        rogue_count_by_band.remove(*key)
    for band, macs in band_counts.items():
        rogue_count_by_band.labels(radio_band=band).set(len(macs))

    stale_channels = set(rogue_count_by_channel._metrics.keys()) - {(c, b) for (c, b) in channel_counts}
    for key in stale_channels:
        rogue_count_by_channel.remove(*key)
    for (channel, band), macs in channel_counts.items():
        rogue_count_by_channel.labels(channel=channel, radio_band=band).set(len(macs))

    log.info("Updated rogue metrics: %d rogues (%d malicious) across %d bands",
             len(unique_rogues), len(malicious_rogues), len(band_counts))


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

        ap_stats = client.get_ap_stats()
        if ap_stats is not None:
            update_radio_metrics(ap_stats)
            update_ap_info_metrics(ap_stats)

        rogues = client.get_rogues()
        if rogues is not None:
            update_rogue_metrics(rogues)

        wlans = client.get_wlans()
        if wlans is not None:
            update_wlan_metrics(wlans)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

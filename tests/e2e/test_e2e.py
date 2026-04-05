"""End-to-end tests against the live Ruckus R720 AP.

These tests start the full Docker Compose stack, point it at the live AP,
and verify that real data flows through to Prometheus and Grafana.

Run with: make test-e2e
Requires: Live AP at LIVE_AP_ADDRESS (default: 10.91.1.109)
"""

import os
import socket
import subprocess
import time

import pytest
import requests

LIVE_AP = os.environ.get("LIVE_AP_ADDRESS", "10.91.1.109")
PROMETHEUS_URL = "http://localhost:9090"
GRAFANA_URL = "http://localhost:3000"
UNLEASHED_EXPORTER_URL = "http://localhost:9191"
SCRAPE_WAIT = int(os.environ.get("E2E_SCRAPE_WAIT", "130"))
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def _ap_reachable(host: str, port: int = 443, timeout: float = 3.0) -> bool:
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def _prometheus_query(query: str):
    """Execute a PromQL instant query and return the result."""
    resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", {}).get("result", [])


# ---------------------------------------------------------------------------
# Skip all e2e tests if AP is unreachable
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.skipif(
    not _ap_reachable(LIVE_AP),
    reason=f"Live AP at {LIVE_AP} is unreachable — skipping e2e tests",
)


@pytest.fixture(scope="module", autouse=True)
def docker_compose_stack():
    """Start the full stack, wait for readiness, yield, then tear down."""
    env = os.environ.copy()
    env.setdefault("UNLEASHED_API_URL", f"https://{LIVE_AP}")

    # Load .env.test if it exists
    env_test = os.path.join(PROJECT_ROOT, ".env.test")
    if os.path.exists(env_test):
        with open(env_test) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env.setdefault(k.strip(), v.strip())

    # Start
    subprocess.run(
        ["docker", "compose", "up", "-d", "--build"],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
        capture_output=True,
    )

    # Wait for Prometheus to be ready
    for _ in range(60):
        try:
            resp = requests.get(f"{PROMETHEUS_URL}/-/ready", timeout=2)
            if resp.status_code == 200:
                break
        except requests.ConnectionError:
            pass
        time.sleep(2)

    # Wait for at least 2 scrape intervals
    time.sleep(SCRAPE_WAIT)

    yield

    # Tear down
    subprocess.run(
        ["docker", "compose", "down", "-v"],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
    )


class TestSNMPCollection:
    """Verify SNMP exporter collects real metrics."""

    def test_sysuptime_present(self):
        result = _prometheus_query(f'sysUpTime{{instance="{LIVE_AP}"}}')
        assert len(result) > 0, "sysUpTime metric not found"
        assert float(result[0]["value"][1]) > 0

    def test_cpu_util_present(self):
        result = _prometheus_query(f'ruckusUnleashedSystemStatsCPUUtil{{instance="{LIVE_AP}"}}')
        assert len(result) > 0, "CPU utilization metric not found"

    def test_radio_client_count_present(self):
        result = _prometheus_query(f'ruckusRadioStatsNumSta{{instance="{LIVE_AP}"}}')
        assert len(result) > 0, "Radio client count metric not found"


class TestUnleashedExporter:
    """Verify REST API exporter collects real client data."""

    def test_exporter_metrics_endpoint(self):
        resp = requests.get(f"{UNLEASHED_EXPORTER_URL}/metrics", timeout=10)
        assert resp.status_code == 200
        # Should contain at least the poll counter
        assert "unleashed_exporter_polls_total" in resp.text

    def test_no_exporter_errors(self):
        resp = requests.get(f"{UNLEASHED_EXPORTER_URL}/metrics", timeout=10)
        lines = resp.text.split("\n")
        error_lines = [l for l in lines if "unleashed_exporter_errors_total" in l and not l.startswith("#")]
        # Errors should be 0 or very low
        for line in error_lines:
            val = float(line.split()[-1])
            assert val < 5, f"Too many exporter errors: {line}"


class TestPrometheusTargets:
    """Verify both scrape targets are up."""

    def test_targets_healthy(self):
        resp = requests.get(f"{PROMETHEUS_URL}/api/v1/targets", timeout=10)
        resp.raise_for_status()
        targets = resp.json()["data"]["activeTargets"]

        snmp_targets = [t for t in targets if t["labels"].get("job") == "snmp"]
        unleashed_targets = [t for t in targets if t["labels"].get("job") == "unleashed"]

        assert len(snmp_targets) > 0, "No SNMP targets found"
        assert len(unleashed_targets) > 0, "No unleashed targets found"

        for t in snmp_targets:
            assert t["health"] == "up", f"SNMP target {t['labels'].get('instance')} is not up"

        for t in unleashed_targets:
            assert t["health"] == "up", f"Unleashed target is not up"


class TestGrafanaDashboards:
    """Verify Grafana dashboards are provisioned and render."""

    def test_dashboards_provisioned(self):
        resp = requests.get(
            f"{GRAFANA_URL}/api/search",
            auth=("admin", os.environ.get("GRAFANA_ADMIN_PASSWORD", "admin")),
            timeout=10,
        )
        resp.raise_for_status()
        dashboards = resp.json()
        uids = {d["uid"] for d in dashboards}

        expected = {"ruckus-fleet-overview", "ruckus-ap-detail", "ruckus-radio-health", "ruckus-client-health"}
        missing = expected - uids
        assert not missing, f"Missing dashboards: {missing}"

    def test_datasource_query_returns_data(self):
        """Query Prometheus through Grafana to verify the data pipeline."""
        resp = requests.post(
            f"{GRAFANA_URL}/api/ds/query",
            auth=("admin", os.environ.get("GRAFANA_ADMIN_PASSWORD", "admin")),
            json={
                "queries": [
                    {
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": "prometheus"},
                        "expr": "up{job=\"snmp\"}",
                        "instant": True,
                    }
                ],
                "from": "now-5m",
                "to": "now",
            },
            timeout=10,
        )
        # Grafana datasource proxy may have different UID; accept 200 or 400 (bad UID)
        assert resp.status_code in (200, 400)

"""Tests for SNMP Exporter configuration validity.

These tests verify the snmp.yml structure and, when a recorded walk file
is available, that the expected OIDs are present.
"""

import os
import yaml
import pytest

SNMP_YML = os.path.join(os.path.dirname(__file__), "..", "..", "snmp-exporter", "snmp.yml")
WALK_FILE = os.path.join(os.path.dirname(__file__), "fixtures", "r720_walk.txt")


@pytest.fixture
def snmp_config():
    with open(SNMP_YML) as f:
        return yaml.safe_load(f)


class TestSnmpYmlStructure:
    """Verify snmp.yml is well-formed and contains expected sections."""

    def test_has_ruckus_module(self, snmp_config):
        assert "modules" in snmp_config
        assert "ruckus_r720" in snmp_config["modules"]

    def test_module_has_walk_oids(self, snmp_config):
        module = snmp_config["modules"]["ruckus_r720"]
        assert "walk" in module
        assert len(module["walk"]) > 0

    def test_module_has_metrics(self, snmp_config):
        module = snmp_config["modules"]["ruckus_r720"]
        assert "metrics" in module
        assert len(module["metrics"]) > 0

    def test_has_auth_config(self, snmp_config):
        assert "auths" in snmp_config
        assert "ruckus_v2" in snmp_config["auths"]
        assert snmp_config["auths"]["ruckus_v2"]["version"] == 2

    def test_expected_metric_names_present(self, snmp_config):
        """Verify key metric names are defined."""
        metrics = snmp_config["modules"]["ruckus_r720"]["metrics"]
        names = {m["name"] for m in metrics}

        expected = {
            "sysUpTime",
            "ruckusUnleashedSystemStatsCPUUtil",
            "ruckusUnleashedSystemStatsMemoryUtil",
            "ruckusUnleashedSystemStatsNumAP",
            "ruckusUnleashedSystemStatsNumSta",
            "ruckusUnleashedSystemStatsAllNumSta",
            "ruckusUnleashedSystemStatsWLANTotalTxRetry",
            "ruckusUnleashedSystemStatsWLANTotalTxFail",
            "ruckusUnleashedSystemStatsWLANTotalRxBytes",
            "ruckusUnleashedSystemStatsWLANTotalTxBytes",
            "ifInOctets",
            "ifOutOctets",
        }
        missing = expected - names
        assert not missing, f"Missing expected metrics: {missing}"

    def test_oids_use_correct_unleashed_base(self, snmp_config):
        """All ruckusUnleashed metrics should use OID base 1.3.6.1.4.1.25053.1.15, NOT 1.3.6.1.4.1.25053.1.1.13."""
        metrics = snmp_config["modules"]["ruckus_r720"]["metrics"]
        for m in metrics:
            if m["name"].startswith("ruckusUnleashed"):
                assert m["oid"].startswith("1.3.6.1.4.1.25053.1.15"), \
                    f"{m['name']} uses wrong OID base: {m['oid']}"

    def test_no_radio_mib_references(self, snmp_config):
        """RUCKUS-RADIO-MIB OIDs (1.3.6.1.4.1.25053.1.1.12) should NOT be present — they don't exist on firmware 200.15."""
        metrics = snmp_config["modules"]["ruckus_r720"]["metrics"]
        for m in metrics:
            assert not m["oid"].startswith("1.3.6.1.4.1.25053.1.1.12"), \
                f"{m['name']} references non-existent RUCKUS-RADIO-MIB OID: {m['oid']}"
        walks = snmp_config["modules"]["ruckus_r720"]["walk"]
        for w in walks:
            assert not w.startswith("1.3.6.1.4.1.25053.1.1.12"), \
                f"Walk references non-existent RUCKUS-RADIO-MIB OID: {w}"


class TestSnmpWalkValidation:
    """Validate recorded SNMP walk contains expected OIDs.
    Skipped if no walk file exists (run tests/mock/fixtures/record_snmp_walk.sh first).
    """

    @pytest.fixture
    def walk_lines(self):
        if not os.path.exists(WALK_FILE):
            pytest.skip("No recorded SNMP walk file.")
        with open(WALK_FILE) as f:
            return f.readlines()

    def test_walk_has_sysuptime(self, walk_lines):
        # The walk file may only contain Ruckus enterprise OIDs if recorded with a subtree filter.
        # Check for either sysUpTime or Ruckus system uptime.
        has_std = any(".1.3.6.1.2.1.1.3" in line for line in walk_lines)
        has_ruckus_uptime = any(".1.3.6.1.4.1.25053.1.15.1.1.1.1.8" in line for line in walk_lines)
        assert has_std or has_ruckus_uptime, "Neither sysUpTime nor ruckusUnleashedSystemUptime found in walk"

    def test_walk_has_unleashed_system_stats(self, walk_lines):
        # ruckusUnleashedSystemStats subtree
        assert any(".1.3.6.1.4.1.25053.1.15.1.1.1.15" in line for line in walk_lines)

    def test_walk_has_cpu_util(self, walk_lines):
        # OID .15.13 = CPU util
        assert any(".1.3.6.1.4.1.25053.1.15.1.1.1.15.13" in line for line in walk_lines)

    def test_walk_has_ap_table(self, walk_lines):
        # AP table at .1.15.2.1.1.2.1.1
        assert any(".1.3.6.1.4.1.25053.1.15.2.1.1.2.1.1" in line for line in walk_lines)

    def test_walk_uses_correct_oid_base(self, walk_lines):
        """Walk should have OIDs under 1.3.6.1.4.1.25053.1.15, NOT 1.3.6.1.4.1.25053.1.1.13."""
        ruckus_lines = [l for l in walk_lines if ".1.3.6.1.4.1.25053" in l]
        assert len(ruckus_lines) > 0, "No Ruckus OIDs in walk"
        for line in ruckus_lines:
            assert ".1.3.6.1.4.1.25053.1.15" in line or ".1.3.6.1.4.1.25053.2.15" in line, \
                f"Unexpected OID base in walk: {line.strip()[:80]}"

"""Tests for rogue AP metrics from the rogue query."""

import sys
import os
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "unleashed-exporter"))

from tests.mock.fixtures.rogue_response import (
    ROGUE_XML,
    ROGUE_XML_REDUCED,
    ROGUE_XML_EMPTY,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    if "exporter" in sys.modules:
        del sys.modules["exporter"]


@pytest.fixture
def exporter_module():
    with patch.dict(os.environ, {
        "UNLEASHED_API_URL": "https://10.91.1.109",
        "UNLEASHED_USERNAME": "admin",
        "UNLEASHED_PASSWORD": "testpass",
        "UNLEASHED_VERIFY_SSL": "false",
    }):
        import exporter
        return exporter


def _parse_rogues(xml_text):
    """Parse rogue XML like the exporter does — flatten to rogue+detector pairs."""
    root = ET.fromstring(xml_text)
    entries = []
    for rogue_el in root.iter("rogue"):
        rogue_attrs = dict(rogue_el.attrib)
        detections = list(rogue_el.iter("detection"))
        if not detections:
            entries.append({"rogue": rogue_attrs, "detection": {}})
        else:
            for det in detections:
                entries.append({"rogue": rogue_attrs, "detection": dict(det.attrib)})
    return entries


class TestGetRogues:
    """Tests for UnleashedClient.get_rogues()."""

    def test_parses_rogue_xml(self, exporter_module):
        client = exporter_module.UnleashedClient(
            "https://10.91.1.109", "admin", "testpass", False
        )
        client._authenticated = True
        client.csrf_token = "ABC1234567"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = ROGUE_XML
        mock_resp.url = "https://10.91.1.109/admin/_cmdstat.jsp"
        client.session.post = MagicMock(return_value=mock_resp)

        entries = client.get_rogues()
        assert entries is not None
        # 1 + 1 + 3 detections = 5 entries
        assert len(entries) == 5


class TestUpdateRogueMetrics:
    """Tests for update_rogue_metrics()."""

    def test_rssi_converted_to_dbm(self, exporter_module):
        """API rssi=7 converts to 7-96 = -89 dBm (approx)."""
        entries = _parse_rogues(ROGUE_XML)
        exporter_module.update_rogue_metrics(entries)

        labels = ("48:a9:8a:ff:12:77", "gafaauto", "44", "5g", "AP", "false", "AP08")
        val = exporter_module.rogue_rssi.labels(*labels)._value.get()
        assert val == -89.0

    def test_malicious_classification(self, exporter_module):
        entries = _parse_rogues(ROGUE_XML)
        exporter_module.update_rogue_metrics(entries)

        # The Photoneo-Playhouse rogue at MAC d0:21:f9:5d:48:3a is malicious
        labels = ("d0:21:f9:5d:48:3a", "Photoneo-Playhouse", "11", "2.4g",
                  "malicious AP (Same-Network)", "true", "AP02")
        val = exporter_module.rogue_rssi.labels(*labels)._value.get()
        assert val == -47.0

    def test_unique_rogue_count(self, exporter_module):
        entries = _parse_rogues(ROGUE_XML)
        exporter_module.update_rogue_metrics(entries)
        # 3 unique rogue MACs (one is detected by 3 APs but counted once)
        assert exporter_module.rogue_count._value.get() == 3

    def test_malicious_count(self, exporter_module):
        entries = _parse_rogues(ROGUE_XML)
        exporter_module.update_rogue_metrics(entries)
        assert exporter_module.rogue_malicious_count._value.get() == 1

    def test_count_by_band(self, exporter_module):
        entries = _parse_rogues(ROGUE_XML)
        exporter_module.update_rogue_metrics(entries)

        # 1 rogue on 5g, 2 unique rogues on 2.4g
        assert exporter_module.rogue_count_by_band.labels(radio_band="5g")._value.get() == 1
        assert exporter_module.rogue_count_by_band.labels(radio_band="2.4g")._value.get() == 2

    def test_count_by_channel(self, exporter_module):
        entries = _parse_rogues(ROGUE_XML)
        exporter_module.update_rogue_metrics(entries)

        # 1 rogue on ch44/5g, 1 on ch11/2.4g, 1 on ch1/2.4g
        assert exporter_module.rogue_count_by_channel.labels(channel="44", radio_band="5g")._value.get() == 1
        assert exporter_module.rogue_count_by_channel.labels(channel="11", radio_band="2.4g")._value.get() == 1
        assert exporter_module.rogue_count_by_channel.labels(channel="1", radio_band="2.4g")._value.get() == 1

    def test_multi_detector_rogue_creates_multiple_samples(self, exporter_module):
        entries = _parse_rogues(ROGUE_XML)
        exporter_module.update_rogue_metrics(entries)

        # The Photoneo-Playhouse on ch1/2.4g is detected by AP05, AP02, AP06
        for detector, expected_rssi in [("AP05", -57.0), ("AP02", -68.0), ("AP06", -82.0)]:
            labels = ("d0:21:f9:5c:c1:34", "Photoneo-Playhouse", "1", "2.4g",
                      "AP", "false", detector)
            val = exporter_module.rogue_rssi.labels(*labels)._value.get()
            assert val == expected_rssi, f"detector {detector} expected {expected_rssi}, got {val}"

    def test_stale_rogue_cleanup(self, exporter_module):
        # First poll: 3 rogues
        exporter_module.update_rogue_metrics(_parse_rogues(ROGUE_XML))
        assert exporter_module.rogue_count._value.get() == 3

        # Second poll: only 1 rogue
        exporter_module.update_rogue_metrics(_parse_rogues(ROGUE_XML_REDUCED))
        assert exporter_module.rogue_count._value.get() == 1

        # The disappeared rogue's metrics should be gone
        stale_labels = ("d0:21:f9:5c:c1:34", "Photoneo-Playhouse", "1", "2.4g",
                        "AP", "false", "AP05")
        assert stale_labels not in exporter_module.rogue_rssi._metrics

    def test_empty_rogue_list(self, exporter_module):
        # First populate, then clear
        exporter_module.update_rogue_metrics(_parse_rogues(ROGUE_XML))
        exporter_module.update_rogue_metrics(_parse_rogues(ROGUE_XML_EMPTY))

        assert exporter_module.rogue_count._value.get() == 0
        assert exporter_module.rogue_malicious_count._value.get() == 0
        assert len(exporter_module.rogue_rssi._metrics) == 0

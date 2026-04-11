"""Tests for per-radio metrics from the AP stats query."""

import sys
import os
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "unleashed-exporter"))

from tests.mock.fixtures.ap_stats_response import (
    AP_STATS_XML,
    AP_STATS_ALL_DISCONNECTED_XML,
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


def _parse_ap_stats(xml_text):
    """Parse AP stats XML like the exporter does."""
    root = ET.fromstring(xml_text)
    aps = []
    for ap_el in root.iter("ap"):
        ap_data = {"attrs": dict(ap_el.attrib), "radios": []}
        for radio_el in ap_el.iter("radio"):
            ap_data["radios"].append(dict(radio_el.attrib))
        aps.append(ap_data)
    return aps


class TestGetApStats:
    """Tests for UnleashedClient.get_ap_stats()."""

    def test_parses_ap_stats_xml(self, exporter_module):
        client = exporter_module.UnleashedClient(
            "https://10.91.1.109", "admin", "testpass", False
        )
        client._authenticated = True
        client.csrf_token = "ABC1234567"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = AP_STATS_XML
        mock_resp.url = "https://10.91.1.109/admin/_cmdstat.jsp"
        client.session.post = MagicMock(return_value=mock_resp)

        aps = client.get_ap_stats()
        assert aps is not None
        assert len(aps) == 2
        assert aps[0]["attrs"]["ap-name"] == "AP05"
        assert len(aps[0]["radios"]) == 2


class TestUpdateRadioMetrics:
    """Tests for update_radio_metrics()."""

    def test_airtime_metrics(self, exporter_module):
        aps = _parse_ap_stats(AP_STATS_XML)
        exporter_module.update_radio_metrics(aps)

        labels_24 = ("AP05", "2.4g", "11")
        assert exporter_module.radio_airtime_total.labels(*labels_24)._value.get() == 106.0
        assert exporter_module.radio_airtime_busy.labels(*labels_24)._value.get() == 5.0
        assert exporter_module.radio_airtime_rx.labels(*labels_24)._value.get() == 94.0
        assert exporter_module.radio_airtime_tx.labels(*labels_24)._value.get() == 7.0

    def test_5ghz_airtime(self, exporter_module):
        aps = _parse_ap_stats(AP_STATS_XML)
        exporter_module.update_radio_metrics(aps)

        labels_5g = ("AP05", "5g", "149")
        assert exporter_module.radio_airtime_total.labels(*labels_5g)._value.get() == 51.0
        assert exporter_module.radio_airtime_busy.labels(*labels_5g)._value.get() == 0.0

    def test_client_count_per_radio(self, exporter_module):
        aps = _parse_ap_stats(AP_STATS_XML)
        exporter_module.update_radio_metrics(aps)

        assert exporter_module.radio_num_sta.labels("AP05", "2.4g", "11")._value.get() == 4.0
        assert exporter_module.radio_num_sta.labels("AP05", "5g", "149")._value.get() == 6.0

    def test_auth_fail_per_radio(self, exporter_module):
        aps = _parse_ap_stats(AP_STATS_XML)
        exporter_module.update_radio_metrics(aps)

        assert exporter_module.radio_auth_fail.labels("AP05", "2.4g", "11")._value.get() == 5.0
        assert exporter_module.radio_auth_fail.labels("AP05", "5g", "149")._value.get() == 24.0

    def test_tx_retries_per_radio(self, exporter_module):
        aps = _parse_ap_stats(AP_STATS_XML)
        exporter_module.update_radio_metrics(aps)

        assert exporter_module.radio_retries.labels("AP05", "5g", "149")._value.get() == 23778.0

    def test_disconnected_ap_excluded(self, exporter_module):
        aps = _parse_ap_stats(AP_STATS_XML)
        exporter_module.update_radio_metrics(aps)

        # AP07 is state=0 (disconnected) — should not have metrics
        assert ("AP07", "2.4g", "0") not in exporter_module.radio_airtime_total._metrics

    def test_stale_ap_cleanup(self, exporter_module):
        # First update with AP05 connected
        aps = _parse_ap_stats(AP_STATS_XML)
        exporter_module.update_radio_metrics(aps)
        assert ("AP05", "2.4g", "11") in exporter_module.radio_airtime_total._metrics

        # Second update with only disconnected APs
        aps2 = _parse_ap_stats(AP_STATS_ALL_DISCONNECTED_XML)
        exporter_module.update_radio_metrics(aps2)
        assert ("AP05", "2.4g", "11") not in exporter_module.radio_airtime_total._metrics

    def test_radio_config_metrics(self, exporter_module):
        aps = _parse_ap_stats(AP_STATS_XML)
        exporter_module.update_radio_metrics(aps)

        assert exporter_module.radio_channel_g.labels("AP05", "5g")._value.get() == 149.0
        assert exporter_module.radio_channelization.labels("AP05", "5g")._value.get() == 40.0

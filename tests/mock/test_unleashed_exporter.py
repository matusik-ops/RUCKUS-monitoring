"""Tests for the Unleashed _cmdstat.jsp Prometheus exporter."""

import sys
import os
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "unleashed-exporter"))

from tests.mock.fixtures.api_responses import (
    CSRF_TOKEN_RESPONSE,
    STATIONS_3_CLIENTS_XML,
    STATIONS_2_CLIENTS_XML,
    STATIONS_EMPTY_XML,
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


def _parse_stations(xml_text):
    """Helper: parse XML to list of dicts like the exporter does."""
    root = ET.fromstring(xml_text)
    return [dict(el.attrib) for el in root.iter("client")]


class TestUnleashedClient:
    """Tests for the UnleashedClient _cmdstat.jsp wrapper."""

    def test_login_success(self, exporter_module):
        client = exporter_module.UnleashedClient(
            "https://10.91.1.109", "admin", "testpass", False
        )
        # Mock login.jsp response with session cookie
        login_resp = MagicMock()
        login_resp.status_code = 200
        client.session.get = MagicMock(side_effect=[login_resp])
        client.session.cookies = MagicMock()
        client.session.cookies.__str__ = MagicMock(return_value="-ejs-session-=abc123")

        # Mock CSRF response
        csrf_resp = MagicMock()
        csrf_resp.text = CSRF_TOKEN_RESPONSE
        client.session.get = MagicMock(side_effect=[login_resp, csrf_resp])

        assert client.login() is True
        assert client.csrf_token == "ABC1234567"
        assert client._authenticated is True

    def test_login_failure_no_cookie(self, exporter_module):
        client = exporter_module.UnleashedClient(
            "https://10.91.1.109", "admin", "wrong", False
        )
        login_resp = MagicMock()
        login_resp.status_code = 200
        client.session.get = MagicMock(return_value=login_resp)
        client.session.cookies = MagicMock()
        client.session.cookies.__str__ = MagicMock(return_value="")

        assert client.login() is False
        assert client._authenticated is False

    def test_login_connection_error(self, exporter_module):
        import requests
        client = exporter_module.UnleashedClient(
            "https://10.91.1.109", "admin", "testpass", False
        )
        client.session.get = MagicMock(
            side_effect=requests.ConnectionError("Connection refused")
        )

        assert client.login() is False

    def test_get_stations_success(self, exporter_module):
        client = exporter_module.UnleashedClient(
            "https://10.91.1.109", "admin", "testpass", False
        )
        client._authenticated = True
        client.csrf_token = "ABC1234567"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = STATIONS_3_CLIENTS_XML
        mock_resp.url = "https://10.91.1.109/admin/_cmdstat.jsp"
        client.session.post = MagicMock(return_value=mock_resp)

        stations = client.get_stations()
        assert stations is not None
        assert len(stations) == 3
        assert stations[0]["mac"] == "aa:bb:cc:dd:ee:01"
        assert stations[0]["received-signal-strength"] == "-54"

    def test_get_stations_connection_error(self, exporter_module):
        import requests
        client = exporter_module.UnleashedClient(
            "https://10.91.1.109", "admin", "testpass", False
        )
        client._authenticated = True
        client.csrf_token = "ABC1234567"
        client.session.post = MagicMock(
            side_effect=requests.ConnectionError("timeout")
        )

        stations = client.get_stations()
        assert stations is None


class TestUpdateMetrics:
    """Tests for the metric update logic."""

    def test_successful_collection_3_clients(self, exporter_module):
        stations = _parse_stations(STATIONS_3_CLIENTS_XML)
        exporter_module.update_metrics(stations)

        labels = ("aa:bb:cc:dd:ee:01", "AP01", "Corp-WiFi", "5g", "Seabiscuit")
        val = exporter_module.client_rssi.labels(*labels)._value.get()
        assert val == -54.0

        labels2 = ("aa:bb:cc:dd:ee:02", "AP01", "Guest-WiFi", "2.4g", "Galaxy-Tab")
        val2 = exporter_module.client_rssi.labels(*labels2)._value.get()
        assert val2 == -72.0

    def test_noise_floor_collected(self, exporter_module):
        stations = _parse_stations(STATIONS_3_CLIENTS_XML)
        exporter_module.update_metrics(stations)

        labels = ("aa:bb:cc:dd:ee:01", "AP01", "Corp-WiFi", "5g", "Seabiscuit")
        val = exporter_module.client_noise_floor.labels(*labels)._value.get()
        assert val == -96.0

    def test_snr_collected(self, exporter_module):
        stations = _parse_stations(STATIONS_3_CLIENTS_XML)
        exporter_module.update_metrics(stations)

        labels = ("aa:bb:cc:dd:ee:01", "AP01", "Corp-WiFi", "5g", "Seabiscuit")
        val = exporter_module.client_snr.labels(*labels)._value.get()
        assert val == 42.0

    def test_channel_collected(self, exporter_module):
        stations = _parse_stations(STATIONS_3_CLIENTS_XML)
        exporter_module.update_metrics(stations)

        labels = ("aa:bb:cc:dd:ee:01", "AP01", "Corp-WiFi", "5g", "Seabiscuit")
        val = exporter_module.client_channel.labels(*labels)._value.get()
        assert val == 44.0

    def test_per_ssid_client_count(self, exporter_module):
        stations = _parse_stations(STATIONS_3_CLIENTS_XML)
        exporter_module.update_metrics(stations)

        corp = exporter_module.clients_per_ssid.labels(ssid="Corp-WiFi")._value.get()
        guest = exporter_module.clients_per_ssid.labels(ssid="Guest-WiFi")._value.get()
        assert corp == 2
        assert guest == 1

    def test_per_ap_client_count(self, exporter_module):
        stations = _parse_stations(STATIONS_3_CLIENTS_XML)
        exporter_module.update_metrics(stations)

        ap01 = exporter_module.clients_per_ap.labels(ap_name="AP01")._value.get()
        ap02 = exporter_module.clients_per_ap.labels(ap_name="AP02")._value.get()
        assert ap01 == 2
        assert ap02 == 1

    def test_total_client_count(self, exporter_module):
        stations = _parse_stations(STATIONS_3_CLIENTS_XML)
        exporter_module.update_metrics(stations)
        assert exporter_module.client_count._value.get() == 3

    def test_client_disconnection_cleanup(self, exporter_module):
        stations_3 = _parse_stations(STATIONS_3_CLIENTS_XML)
        exporter_module.update_metrics(stations_3)
        labels_03 = ("aa:bb:cc:dd:ee:03", "AP02", "Corp-WiFi", "5g", "Alonso")
        assert labels_03 in exporter_module.client_rssi._metrics

        stations_2 = _parse_stations(STATIONS_2_CLIENTS_XML)
        exporter_module.update_metrics(stations_2)
        assert labels_03 not in exporter_module.client_rssi._metrics

    def test_empty_station_list(self, exporter_module):
        stations_3 = _parse_stations(STATIONS_3_CLIENTS_XML)
        exporter_module.update_metrics(stations_3)

        stations_empty = _parse_stations(STATIONS_EMPTY_XML)
        exporter_module.update_metrics(stations_empty)

        assert len(exporter_module.client_rssi._metrics) == 0
        assert exporter_module.client_count._value.get() == 0

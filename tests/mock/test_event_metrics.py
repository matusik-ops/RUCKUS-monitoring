"""Tests for event log metrics from the eventd query."""

import sys
import os
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "unleashed-exporter"))

from tests.mock.fixtures.event_responses import (
    ALARMS_XML,
    XEVENTS_XML,
    ALARMS_EMPTY_XML,
    XEVENTS_EMPTY_XML,
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
    }):
        if "exporter" in sys.modules:
            del sys.modules["exporter"]
        import exporter
        # Reset dedup timestamps
        exporter._last_alarm_time = 0.0
        exporter._last_xevent_time = 0.0
        yield exporter


def _parse_alarms(xml_text):
    root = ET.fromstring(xml_text)
    return [dict(el.attrib) for el in root.iter("alarm")]


def _parse_xevents(xml_text):
    root = ET.fromstring(xml_text)
    return [dict(el.attrib) for el in root.iter("xevent")]


def _counter_value(counter, labels):
    """Get the current value of a Counter with given labels."""
    return counter.labels(**labels)._value.get()


class TestAlarmMetrics:
    def test_radio_off_counted(self, exporter_module):
        alarms = _parse_alarms(ALARMS_XML)
        exporter_module.update_alarm_metrics(alarms)
        val = _counter_value(exporter_module.ap_radio_off_total,
                             {"ap_name": "AP02", "radio_band": "5g"})
        assert val == 1.0

    def test_radio_on_counted(self, exporter_module):
        alarms = _parse_alarms(ALARMS_XML)
        exporter_module.update_alarm_metrics(alarms)
        val = _counter_value(exporter_module.ap_radio_on_total,
                             {"ap_name": "AP08", "radio_band": "5g"})
        assert val == 1.0

    def test_radio_on_24g(self, exporter_module):
        alarms = _parse_alarms(ALARMS_XML)
        exporter_module.update_alarm_metrics(alarms)
        val = _counter_value(exporter_module.ap_radio_on_total,
                             {"ap_name": "AP02", "radio_band": "2.4g"})
        assert val == 1.0

    def test_ap_join_counted(self, exporter_module):
        alarms = _parse_alarms(ALARMS_XML)
        exporter_module.update_alarm_metrics(alarms)
        val = _counter_value(exporter_module.ap_join_event_total,
                             {"ap_name": "AP08"})
        assert val == 1.0

    def test_rogue_detected_counted(self, exporter_module):
        alarms = _parse_alarms(ALARMS_XML)
        exporter_module.update_alarm_metrics(alarms)
        val = _counter_value(exporter_module.rogue_detected_event_total,
                             {"ap_name": "AP08"})
        assert val == 1.0

    def test_dedup_prevents_double_count(self, exporter_module):
        alarms = _parse_alarms(ALARMS_XML)
        exporter_module.update_alarm_metrics(alarms)
        # Second call with same data should not increment
        exporter_module.update_alarm_metrics(alarms)
        val = _counter_value(exporter_module.ap_radio_off_total,
                             {"ap_name": "AP02", "radio_band": "5g"})
        assert val == 1.0

    def test_empty_alarms(self, exporter_module):
        alarms = _parse_alarms(ALARMS_EMPTY_XML)
        exporter_module.update_alarm_metrics(alarms)
        # No errors, no metrics created


class TestXeventMetrics:
    def test_warm_reboot_counted(self, exporter_module):
        xevents = _parse_xevents(XEVENTS_XML)
        exporter_module.update_xevent_metrics(xevents)
        val = _counter_value(exporter_module.ap_reboot_event_total,
                             {"ap_name": "AP08"})
        assert val == 1.0

    def test_dedup_prevents_double_count(self, exporter_module):
        xevents = _parse_xevents(XEVENTS_XML)
        exporter_module.update_xevent_metrics(xevents)
        exporter_module.update_xevent_metrics(xevents)
        val = _counter_value(exporter_module.ap_reboot_event_total,
                             {"ap_name": "AP08"})
        assert val == 1.0

    def test_empty_xevents(self, exporter_module):
        xevents = _parse_xevents(XEVENTS_EMPTY_XML)
        exporter_module.update_xevent_metrics(xevents)
        # No errors, no metrics created

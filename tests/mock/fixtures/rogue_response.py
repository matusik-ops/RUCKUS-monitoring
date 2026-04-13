"""Mock rogue AP XML responses from _cmdstat.jsp <rogue/>."""

# Real-world sample: 1 regular rogue, 1 malicious same-network, 1 multi-detector
ROGUE_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<apstamgr-stat>
<rogue mac="48:a9:8a:ff:12:77" ieee80211-radio-type="a/n/ac" num-detection="1"
       rogue-type="AP" radio-type="802.11a/n/ac" radio-band="5g" channel="44"
       ssid="gafaauto" is-open="Encrypted" last-seen="1776060370">
  <detection ap="ec:58:ea:10:f3:f0" sys-name="AP08" location="" rssi="7" last-seen="1776060370" />
</rogue>
<rogue mac="d0:21:f9:5d:48:3a" ieee80211-radio-type="g/n" num-detection="1"
       rogue-type="malicious AP (Same-Network)" radio-type="802.11g/n" radio-band="2.4g"
       channel="11" ssid="Photoneo-Playhouse" is-open="Encrypted" last-seen="1776063948">
  <detection ap="ec:58:ea:10:b4:f0" sys-name="AP02" location="" rssi="49" last-seen="1776063948" />
</rogue>
<rogue mac="d0:21:f9:5c:c1:34" ieee80211-radio-type="g/n" num-detection="3"
       rogue-type="AP" radio-type="802.11g/n" radio-band="2.4g" channel="1"
       ssid="Photoneo-Playhouse" is-open="Encrypted" last-seen="1776065749">
  <detection ap="e8:1d:a8:2a:cb:90" sys-name="AP05" location="" rssi="39" last-seen="1776064826" />
  <detection ap="ec:58:ea:10:b4:f0" sys-name="AP02" location="" rssi="28" last-seen="1776065749" />
  <detection ap="ec:58:ea:11:bc:40" sys-name="AP06" location="" rssi="14" last-seen="1776064821" />
</rogue>
</apstamgr-stat>
</response>
</ajax-response>"""

# After the multi-detector rogue disappears
ROGUE_XML_REDUCED = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<apstamgr-stat>
<rogue mac="48:a9:8a:ff:12:77" ieee80211-radio-type="a/n/ac" num-detection="1"
       rogue-type="AP" radio-type="802.11a/n/ac" radio-band="5g" channel="44"
       ssid="gafaauto" is-open="Encrypted" last-seen="1776060370">
  <detection ap="ec:58:ea:10:f3:f0" sys-name="AP08" location="" rssi="7" last-seen="1776060370" />
</rogue>
</apstamgr-stat>
</response>
</ajax-response>"""

ROGUE_XML_EMPTY = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<apstamgr-stat>
</apstamgr-stat>
</response>
</ajax-response>"""

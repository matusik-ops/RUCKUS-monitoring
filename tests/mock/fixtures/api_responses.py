"""Mock Unleashed _cmdstat.jsp XML responses for testing."""

# CSRF token response from _csrfTokenVar.jsp
CSRF_TOKEN_RESPONSE = "<script>\nvar csfrToken = 'ABC1234567';\n</script>"

# Successful XML client list response from _cmdstat.jsp
# Includes all fields the exporter reads: identity, signal, traffic, retries, interval-stats
STATIONS_3_CLIENTS_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<apstamgr-stat>
<client mac="aa:bb:cc:dd:ee:01" ap-name="AP01" ssid="Corp-WiFi" radio-band="5g"
  rssi="42" received-signal-strength="-54" noise-floor="-96" channel="44"
  hostname="Seabiscuit" radio-type="11ac" status="1"
  ip="10.91.2.100" vlan="2" dvctype="Laptop" model="Windows 10/11"
  auth-method="Open" encryption="WPA2" first-assoc="1775364286"
  total-rx-bytes="1000000" total-tx-bytes="2000000"
  total-rx-pkts="10000" total-tx-pkts="15000"
  total-retries="50" total-retry-bytes="500000"
  min-received-signal-strength="-57" max-received-signal-strength="-52">
  <interval-stats tx-rate="135000.0" rx-bytes="500000" tx-bytes="1000000"/>
</client>
<client mac="aa:bb:cc:dd:ee:02" ap-name="AP01" ssid="Guest-WiFi" radio-band="2.4g"
  rssi="18" received-signal-strength="-72" noise-floor="-96" channel="6"
  hostname="Galaxy-Tab" radio-type="11ng" status="1"
  ip="10.91.4.50" vlan="4" dvctype="Smartphone" model="Android 10.0.0"
  auth-method="Open FT" encryption="WPA2" first-assoc="1775364300"
  total-rx-bytes="500000" total-tx-bytes="1000000"
  total-rx-pkts="5000" total-tx-pkts="8000"
  total-retries="1500" total-retry-bytes="2000000"
  min-received-signal-strength="-78" max-received-signal-strength="-68">
  <interval-stats tx-rate="72000.0" rx-bytes="250000" tx-bytes="500000"/>
</client>
<client mac="aa:bb:cc:dd:ee:03" ap-name="AP02" ssid="Corp-WiFi" radio-band="5g"
  rssi="10" received-signal-strength="-80" noise-floor="-96" channel="153"
  hostname="Alonso" radio-type="11ac" status="1"
  ip="10.91.2.55" vlan="2" dvctype="" model=""
  auth-method="Open" encryption="WPA2" first-assoc="1775364400"
  total-rx-bytes="100000" total-tx-bytes="200000"
  total-rx-pkts="1000" total-tx-pkts="1500"
  total-retries="10" total-retry-bytes="50000"
  min-received-signal-strength="-85" max-received-signal-strength="-77">
  <interval-stats tx-rate="54000.0" rx-bytes="50000" tx-bytes="100000"/>
</client>
</apstamgr-stat>
</response>
</ajax-response>"""

# After client 03 disconnects
STATIONS_2_CLIENTS_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<apstamgr-stat>
<client mac="aa:bb:cc:dd:ee:01" ap-name="AP01" ssid="Corp-WiFi" radio-band="5g"
  rssi="42" received-signal-strength="-54" noise-floor="-96" channel="44"
  hostname="Seabiscuit" radio-type="11ac" status="1"
  ip="10.91.2.100" vlan="2" dvctype="Laptop" model="Windows 10/11"
  auth-method="Open" encryption="WPA2" first-assoc="1775364286"
  total-rx-bytes="1000000" total-tx-bytes="2000000"
  total-rx-pkts="10000" total-tx-pkts="15000"
  total-retries="50" total-retry-bytes="500000">
  <interval-stats tx-rate="135000.0" rx-bytes="500000" tx-bytes="1000000"/>
</client>
<client mac="aa:bb:cc:dd:ee:02" ap-name="AP01" ssid="Guest-WiFi" radio-band="2.4g"
  rssi="18" received-signal-strength="-72" noise-floor="-96" channel="6"
  hostname="Galaxy-Tab" radio-type="11ng" status="1"
  ip="10.91.4.50" vlan="4" dvctype="Smartphone" model="Android 10.0.0"
  auth-method="Open FT" encryption="WPA2" first-assoc="1775364300"
  total-rx-bytes="500000" total-tx-bytes="1000000"
  total-rx-pkts="5000" total-tx-pkts="8000"
  total-retries="1500" total-retry-bytes="2000000">
  <interval-stats tx-rate="72000.0" rx-bytes="250000" tx-bytes="500000"/>
</client>
</apstamgr-stat>
</response>
</ajax-response>"""

STATIONS_EMPTY_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<apstamgr-stat>
</apstamgr-stat>
</response>
</ajax-response>"""

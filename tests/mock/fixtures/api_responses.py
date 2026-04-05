"""Mock Unleashed _cmdstat.jsp XML responses for testing."""

# CSRF token response from _csrfTokenVar.jsp
CSRF_TOKEN_RESPONSE = "<script>\nvar csfrToken = 'ABC1234567';\n</script>"

# Successful XML client list response from _cmdstat.jsp
STATIONS_3_CLIENTS_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<apstamgr-stat>
<client mac="aa:bb:cc:dd:ee:01" ap-name="AP01" ssid="Corp-WiFi" radio-band="5g"
  rssi="42" received-signal-strength="-54" noise-floor="-96" channel="44"
  hostname="Seabiscuit" radio-type="11ac" status="1" />
<client mac="aa:bb:cc:dd:ee:02" ap-name="AP01" ssid="Guest-WiFi" radio-band="2.4g"
  rssi="18" received-signal-strength="-72" noise-floor="-96" channel="6"
  hostname="Galaxy-Tab" radio-type="11ng" status="1" />
<client mac="aa:bb:cc:dd:ee:03" ap-name="AP02" ssid="Corp-WiFi" radio-band="5g"
  rssi="10" received-signal-strength="-80" noise-floor="-96" channel="153"
  hostname="Alonso" radio-type="11ac" status="1" />
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
  hostname="Seabiscuit" radio-type="11ac" status="1" />
<client mac="aa:bb:cc:dd:ee:02" ap-name="AP01" ssid="Guest-WiFi" radio-band="2.4g"
  rssi="18" received-signal-strength="-72" noise-floor="-96" channel="6"
  hostname="Galaxy-Tab" radio-type="11ng" status="1" />
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

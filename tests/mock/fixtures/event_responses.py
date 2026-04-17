"""Mock Unleashed eventd XML responses for testing."""

ALARMS_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<response>
<alarm alarmdef-id="54" name="AP Has Joined" msg="MSG_AP_joined_with_reason"
  severity="1" time="1775150390" c="system" ap="ec:58:ea:10:f3:f0"
  ap-name="AP08" uptime="153" reason="AP Restart : application reboot"
  lmsg="AP[AP08] joins with uptime [153] s" occurs="1" id="1" />
<alarm alarmdef-id="9" name="Same-Network Rogue AP Detected"
  msg="MSG_same_network_spoofing_AP_detected" severity="1" time="1775150415"
  c="system" rogue="d0:21:f9:5d:48:3a" ssid="Evil-WiFi"
  ap="ec:58:ea:10:f3:f0" ap-name="AP08"
  lmsg="A new Same-Network Rogue detected by AP[AP08]" occurs="1" id="2" />
<alarm alarmdef-id="55" name="AP Radio On" msg="MSG_AP_RADIO_ON"
  severity="1" time="1775150460" c="system" ap="ec:58:ea:10:f3:f0"
  radioindex="5G" ap-name="AP08"
  lmsg="Radio [5G] of AP[AP08] is ON" occurs="1" id="3" />
<alarm alarmdef-id="55" name="AP Radio Off" msg="MSG_AP_RADIO_OFF"
  severity="1" time="1775150500" c="system" ap="ec:58:ea:10:b4:f0"
  radioindex="5G" ap-name="AP02"
  lmsg="Radio [5G] of AP[AP02] is OFF" occurs="1" id="4" />
<alarm alarmdef-id="55" name="AP Radio On" msg="MSG_AP_RADIO_ON"
  severity="1" time="1775150550" c="system" ap="ec:58:ea:10:b4:f0"
  radioindex="2.4G" ap-name="AP02"
  lmsg="Radio [2.4G] of AP[AP02] is ON" occurs="1" id="5" />
</response>
</response>
</ajax-response>"""

XEVENTS_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<response>
<xevent msg="MSG_AP_warm_reboot" severity="1" time="1775150392"
  c="system" ap="ec:58:ea:10:f3:f0" ap-name="AP08"
  reason="application reboot"
  lmsg="AP[AP08] warm boot successfully" />
<xevent msg="MSG_AP_joined_with_reason" severity="1" time="1775150394"
  c="system" ap="ec:58:ea:10:f8:b0" ap-name="AP09-sales"
  uptime="159" reason="AP Restart : application reboot"
  lmsg="AP[AP09-sales] joins with uptime [159] s" />
<xevent msg="UN_Upgrade_System_upgraded_success" severity="1" time="1775150388"
  c="system" new-version="200.15.6.212.27" old-version="200.7.10.202.145"
  lmsg="Unleashed image has been upgraded" />
</response>
</response>
</ajax-response>"""

ALARMS_EMPTY_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<response />
</response>
</ajax-response>"""

XEVENTS_EMPTY_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<response />
</response>
</ajax-response>"""

"""Mock AP stats XML response from _cmdstat.jsp <ap LEVEL='1'/>."""

AP_STATS_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<apstamgr-stat>
<ap mac="e8:1d:a8:2a:cb:90" state="1" ap-name="AP05" model="R720">
  <radio radio-band="2.4g" channel="11" channelization="20" tx-power="3"
    airtime-total="106" airtime-busy="5" airtime-rx="94" airtime-tx="7"
    num-sta="4" avg-rssi="50"
    radio-total-tx-bytes="500000" radio-total-rx-bytes="300000"
    radio-total-tx-pkts="5000" radio-total-rx-pkts="3000"
    radio-total-tx-fail="20" radio-total-retries="7290"
    radio-total-rx-decrypt-error="0" total-fcs-err="0"
    mgmt-auth-req="100" mgmt-auth-success="95" mgmt-auth-fail="5"
    mgmt-assoc-req="90" mgmt-assoc-success="85" mgmt-assoc-fail="5"
    radio-type="11ng" />
  <radio radio-band="5g" channel="149" channelization="40" tx-power="5"
    airtime-total="51" airtime-busy="0" airtime-rx="32" airtime-tx="19"
    num-sta="6" avg-rssi="40"
    radio-total-tx-bytes="2000000" radio-total-rx-bytes="1000000"
    radio-total-tx-pkts="20000" radio-total-rx-pkts="10000"
    radio-total-tx-fail="58" radio-total-retries="23778"
    radio-total-rx-decrypt-error="0" total-fcs-err="0"
    mgmt-auth-req="200" mgmt-auth-success="176" mgmt-auth-fail="24"
    mgmt-assoc-req="180" mgmt-assoc-success="178" mgmt-assoc-fail="2"
    radio-type="11ac" />
</ap>
<ap mac="44:1e:98:15:6c:50" state="0" ap-name="AP07" model="R720">
  <radio radio-band="2.4g" channel="0" num-sta="0" avg-rssi="0"
    airtime-total="0" airtime-busy="0" airtime-rx="0" airtime-tx="0"
    radio-total-tx-bytes="0" radio-total-rx-bytes="0"
    radio-total-tx-pkts="0" radio-total-rx-pkts="0"
    radio-total-tx-fail="0" radio-total-retries="0"
    radio-total-rx-decrypt-error="0" total-fcs-err="0"
    mgmt-auth-fail="0" mgmt-auth-success="0"
    mgmt-assoc-fail="0" mgmt-assoc-success="0"
    radio-type="11ng" />
  <radio radio-band="5g" channel="0" num-sta="0" avg-rssi="0"
    airtime-total="0" airtime-busy="0" airtime-rx="0" airtime-tx="0"
    radio-total-tx-bytes="0" radio-total-rx-bytes="0"
    radio-total-tx-pkts="0" radio-total-rx-pkts="0"
    radio-total-tx-fail="0" radio-total-retries="0"
    radio-total-rx-decrypt-error="0" total-fcs-err="0"
    mgmt-auth-fail="0" mgmt-auth-success="0"
    mgmt-assoc-fail="0" mgmt-assoc-success="0"
    radio-type="11ac" />
</ap>
</apstamgr-stat>
</response>
</ajax-response>"""

# After AP05 disconnects — only disconnected AP07 remains
AP_STATS_ALL_DISCONNECTED_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ajax-response>
<ajax-response>
<response type="object" id="DEH">
<apstamgr-stat>
<ap mac="44:1e:98:15:6c:50" state="0" ap-name="AP07" model="R720">
  <radio radio-band="2.4g" channel="0" num-sta="0" avg-rssi="0"
    airtime-total="0" airtime-busy="0" airtime-rx="0" airtime-tx="0"
    radio-total-tx-bytes="0" radio-total-rx-bytes="0"
    radio-total-tx-pkts="0" radio-total-rx-pkts="0"
    radio-total-tx-fail="0" radio-total-retries="0"
    radio-total-rx-decrypt-error="0" total-fcs-err="0"
    mgmt-auth-fail="0" mgmt-auth-success="0"
    mgmt-assoc-fail="0" mgmt-assoc-success="0"
    radio-type="11ng" />
</ap>
</apstamgr-stat>
</response>
</ajax-response>"""

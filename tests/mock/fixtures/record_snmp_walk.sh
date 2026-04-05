#!/bin/bash
# Record an SNMP walk from the live R720 for offline testing.
# Run this once with the AP reachable to generate the walk file.
#
# Prerequisites: snmpwalk (from net-snmp)
# Usage: ./record_snmp_walk.sh [AP_ADDRESS] [COMMUNITY]

AP_ADDRESS="${1:-10.91.1.109}"
COMMUNITY="${2:-public}"
OUTPUT_DIR="$(dirname "$0")"
OUTPUT_FILE="$OUTPUT_DIR/r720_walk.txt"

echo "Recording SNMP walk from $AP_ADDRESS (community: $COMMUNITY)..."
snmpwalk -v2c -c "$COMMUNITY" -On "$AP_ADDRESS" .1 > "$OUTPUT_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "Walk saved to $OUTPUT_FILE ($(wc -l < "$OUTPUT_FILE") OIDs)"
else
    echo "ERROR: SNMP walk failed. Is the AP reachable?"
    exit 1
fi

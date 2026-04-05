# Ruckus MIB Files

This directory should contain the Ruckus MIB files needed by the SNMP Exporter generator.

## Required MIBs

- `RUCKUS-ROOT-MIB` (dependency)
- `RUCKUS-TC-MIB` (dependency)
- `RUCKUS-PRODUCTS-MIB` (dependency)
- `RUCKUS-RADIO-MIB` (per-radio stats)
- `RUCKUS-UNLEASHED-SYSTEM-MIB` (AP system stats)
- `RUCKUS-HWINFO-MIB` (hardware identity)

## Where to Get Them

### Option 1: LibreNMS GitHub (recommended, publicly available)

```bash
BASE_URL="https://raw.githubusercontent.com/librenms/librenms/master/mibs/ruckus"
for mib in RUCKUS-ROOT-MIB RUCKUS-TC-MIB RUCKUS-PRODUCTS-MIB RUCKUS-RADIO-MIB RUCKUS-UNLEASHED-SYSTEM-MIB RUCKUS-HWINFO-MIB; do
    curl -sL "$BASE_URL/$mib" -o "$mib"
done
```

### Option 2: CommScope/Ruckus Support Portal

1. Go to https://support.ruckuswireless.com/
2. Navigate to Software Downloads > MIB files
3. Download the MIB bundle for Unleashed firmware
4. Extract the required MIB files into this directory

## Regenerating snmp.yml

If you need to regenerate the SNMP Exporter config from MIBs:

```bash
# Install the generator
go install github.com/prometheus/snmp_exporter/generator@latest

# Generate
cd mibs/
generator generate
```

Note: The provided `snmp-exporter/snmp.yml` was manually crafted with specific OIDs
and should work without regeneration.

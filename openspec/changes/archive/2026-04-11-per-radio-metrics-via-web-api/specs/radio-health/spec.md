## MODIFIED Requirements

### Requirement: Radio health dashboard uses real per-radio airtime data
The radio health dashboard SHALL display per-radio airtime utilization computed as `airtime_busy / airtime_total * 100` from the web API, replacing the previous system-level aggregate proxy. Panels SHALL show airtime-busy, airtime-rx, airtime-tx per AP per radio band.

#### Scenario: Comparing airtime across APs
- **WHEN** a user views the radio health dashboard
- **THEN** the dashboard shows airtime utilization per radio for each AP, enabling comparison of RF load across the fleet

#### Scenario: High airtime on specific AP
- **WHEN** AP06 2.4GHz radio has airtime-busy=29 out of airtime-total=169
- **THEN** the dashboard shows ~17% busy airtime, highlighted if above threshold

### Requirement: Radio health dashboard shows per-radio auth/assoc failure rates
The dashboard SHALL display per-radio auth and assoc failure counts from the web API, replacing the previous "not available" limitation.

#### Scenario: Auth failure spike on one radio
- **WHEN** AP06 5GHz radio has mgmt-auth-fail=2508
- **THEN** the dashboard highlights this AP/radio as having an auth issue

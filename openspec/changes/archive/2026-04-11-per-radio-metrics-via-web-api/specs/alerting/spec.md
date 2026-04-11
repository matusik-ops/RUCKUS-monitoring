## ADDED Requirements

### Requirement: Alert on high airtime busy
The system SHALL raise an alert when per-radio airtime-busy exceeds a configurable percentage of airtime-total for a sustained period.

#### Scenario: Congested radio
- **WHEN** a radio's airtime-busy / airtime-total exceeds 50% for 5 minutes
- **THEN** Prometheus fires a HighAirtimeBusy alert for that AP and radio band

### Requirement: Alert on per-radio auth failure spike
The system SHALL raise an alert when per-radio mgmt-auth-fail rate exceeds a configurable threshold.

#### Scenario: Auth failures on specific radio
- **WHEN** a radio's auth-fail count increases by more than 100 in 5 minutes
- **THEN** Prometheus fires a RadioAuthFailureSpike alert for that AP and radio band

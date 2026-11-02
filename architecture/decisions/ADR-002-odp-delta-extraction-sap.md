# ADR-002: Utilization of SAP Operational Data Provisioning (ODP) & CDS Views
## Context
Meridian Manufacturing operates SAP S/4HANA 2023 FPS02 on SAP HANA 2.0. Legacy table-level pooling (e.g. `SELECT * FROM BSEG`) causes massive database locking and is strictly vetoed by SAP Basis Administrator Priya Deshmukh. Furthermore, extracting large volumes must not interfere with the nightly batch job `RGGBS000` (01:00-04:30 IST) or exhaust the 50-connection RFC pool.

## Decision
We mandate the use of **SAP Operational Data Provisioning (ODP)** backed by custom Core Data Services (CDS) Views (e.g., `ZZ_CDS_ACDOCA_DELTA`). Delta capture utilizes SAP HANA's native Change Data Capture (CDC) mechanism with delta tokens.

## Consequences
- **Positive:** Zero table locks on `ACDOCA` or `BKPF`; delta queue manages cursor state natively in SAP; extraction footprint is reduced to small incremental packets every 30 minutes; complies with SAP recommended best practices.
- **Negative:** Requires initial transport deployment of CDS Views and ODP subscriptions in SAP PRD; requires SAP Basis transport sign-off.
- **Status:** APPROVED by Priya Deshmukh.

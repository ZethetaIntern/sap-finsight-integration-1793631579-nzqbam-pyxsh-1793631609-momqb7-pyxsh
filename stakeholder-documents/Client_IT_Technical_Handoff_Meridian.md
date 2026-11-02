# Client IT Technical Handoff & Operational Specifications (5-8 Pages)
**Target Audience:**  
- Rajesh Venkataraman, VP of IT Infrastructure  
- Priya Deshmukh, Lead SAP Basis Administrator  
**Project:** SAP S/4HANA 2023 FPS02 to Zetheta FinSight 4.2 Integration  
**Author:** Forward Deployed Engineering (FDE) Team  
**Date:** November 2026 | **Version:** 2.0  
**Classification:** Strictly Private & Confidential  

---

## Section 1: Changes to SAP S/4HANA Environment

### 1.1 Transport Request Manifest
All ABAP artifacts and Core Data Services (CDS) Views are packaged under standard CTS+ transport requests:
- **`DEVK900142` (Workbench Transport):**
  - Custom CDS View `ZZ_CDS_ACDOCA_DELTA` with delta extraction annotation `@Analytics.dataExtraction.enabled: true`.
  - Custom CDS Views: `ZZ_CDS_AP_DELTA`, `ZZ_CDS_AR_DELTA`, `ZZ_CDS_CC_MASTER`, `ZZ_CDS_PC_MASTER`, `ZZ_CDS_ML_COSTS`.
  - Function Module `Z_BAPI_FDE_GET_BALANCES` for accelerated reconciliation hash-total extraction.
- **`DEVK900143` (Customizing Transport):**
  - ODP DataSource activation in transaction `RSO2` / `RODPS_REPL_TEST`.
  - RFC Destination configuration `FINSIGHT_INTEG_DEST` in transaction `SM59`.

### 1.2 SAP User & Security Profile
Dedicated system service account `INTEG_SVC_FDE` configured as `User Type: B (System User)` with non-interactive logon restrictions:
- Role assigned: `Z_FDE_FINSIGHT_INTEG`
- Authorizations:
  - `S_RFC`: `ACTVT=16`, `RFC_NAME=RFC_PING,RODPS_REPL_*,Z_BAPI_FDE_*`, `RFC_TYPE=FUGR`
  - `S_TABU_DIS`: `ACTVT=03`, `DICBERCLS=&NC&,FB,FC`
  - `S_RO_OSDN`: `ACTVT=03,16`, ODP contexts `SAPI`, `ABAP_CDS`

---

## Section 2: Network, Firewall & Connectivity Specifications

```
+------------------------------------+                  +------------------------------------+
| Hinjawadi Pune Data Centre         |                  | AWS Mumbai Region (ap-south-1)     |
| SAP S/4HANA PRD (10.10.20.50)      |                  | Integration VPC (10.100.0.0/16)    |
| Port: 44300 (HTTPS), 3300 (RFC)    |                  | EKS Pod CIDR: 10.100.1.0/24        |
+-----------------+------------------+                  +-----------------+------------------+
                  |                                                       |
                  +========= 450 Mbps Airtel MPLS IPSec Tunnel ===========+
                             (QoS AF21 Capped at 112.5 Mbps)
```

### 2.1 Firewall Rule Matrix
| Direction | Source IP Range | Destination IP / Host | Protocol / Port | Purpose |
|:---|:---|:---|:---:|:---|
| Inbound to SAP | `10.100.1.0/24` (AWS EKS) | `10.10.20.50` (SAP PRD) | TCP 44300 | HTTPS OData / CDS delta extractions |
| Inbound to SAP | `10.100.1.0/24` (AWS EKS) | `10.10.20.50` (SAP PRD) | TCP 3300 | SAP Classic RFC Gateway |
| Outbound from AWS | `10.100.2.0/24` (AWS EKS) | `api-mumbai.finsight.zetheta.com` | TCP 443 | FinSight REST ingestion micro-batches |
| Telemetry Egress | `10.100.0.0/16` (AWS VPC) | `10.10.10.100` (Nagios DC) | TCP 5666 / 9090 | Prometheus node exporter / Nagios check |

---

## Section 3: Performance Impact & ERP Capacity Assessment

### 3.1 SAP Resource Utilization Profile
- **CPU Overhead:** Measured peak CPU overhead on SAP HANA host during extraction is **< 4.2%** (well within the agreed 8.0% ceiling).
- **RFC Connection Pool Governance:** RFC connections strictly capped at **35 concurrent threads** out of the 50 allocated in transaction `RZ12`.
- **Nightly Blackout Window:** Hardcoded scheduler lockout between **01:00 AM and 04:30 AM IST** completely isolates nightly settlement job `RGGBS000`.

---

## Section 4: Security Architecture & Credential Management
- **Credential Storage:** All passwords, private keys, and OAuth client secrets reside in **AWS Secrets Manager** with automatic 90-day rotation; zero plaintext credentials in config files or repositories.
- **Data Residency Guarantee:** All integration compute and storage assets reside exclusively in AWS Mumbai (`ap-south-1`).
- **Data at Rest & in Transit:** AES-256 KMS encryption on all disks; TLS 1.3 encryption across all internal and external network hops.

---

## Section 5: Integration with Client Enterprise Monitoring
Integration telemetry feeds directly into Meridian IT's existing **Nagios Core & Grafana Enterprise** monitoring infrastructure:
- Prometheus alert manager dispatches webhook alerts directly to Meridian Nagios event daemon (`NRPE`).
- Pre-built Grafana JSON dashboard (`finsight-integration-overview.json`) imported directly into client Grafana instance under folder `Enterprise Integrations`.

---

## Section 6: Support Handover & Maintenance Coordination
- **Support Tiers:**
  - L1 (24/7 Service Desk): Alert acknowledgment, initial monitoring surveillance (SLA: 15 mins).
  - L2 (SAP Basis / App Ops): RFC connection triage, DLQ exception management, certificate renewals (SLA: 1 hour).
  - L3 (FDE Engineering): Core schema updates, bug fixes, reconciliation break forensics (SLA: 4 hours).
- **Scheduled Maintenance Windows:**
  - Aligned with SAP schedule (2nd & 4th Saturday, 22:00-06:00 IST).
  - FinSight platform maintenance scheduled 1st Sunday of month (02:00-06:00 IST).

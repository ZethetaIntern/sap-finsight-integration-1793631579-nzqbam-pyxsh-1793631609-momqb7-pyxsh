# Network and Security Architecture Specification
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

## 1. Network Architecture & Traffic Flow
The integration spans a secure hybrid cloud infrastructure connecting the client's on-premise data centre with AWS Mumbai.

```
+------------------------------------+         +-------------------------------------+
| On-Premise Data Centre (Pune, MH)  |         | AWS Mumbai Region (ap-south-1)      |
| SAP S/4HANA PRD (Client 100)       |         | Integration VPC (10.100.0.0/16)     |
| IP: 10.10.20.50                    |         |                                     |
| Port: 44300 (HTTPS), 3300 (RFC)    |         | Private Subnet A (10.100.1.0/24)    |
|                                    |         | - Extractor & Transformer Pods      |
| Cisco SD-WAN Edge Router           |         | - Kafka Broker 1                    |
+-----------------+------------------+         |                                     |
                  |                            | Private Subnet B (10.100.2.0/24)    |
         450 Mbps | Airtel MPLS Link           | - FinSight Loaders & Recon Engine   |
        Encrypted | IPSec Tunnel               | - Kafka Broker 2                    |
                  | (Max 25% = 112.5 Mbps)     | - PostgreSQL Primary (RDS Multi-AZ) |
                  v                            |                                     |
+-----------------+------------------+         | Private Subnet C (10.100.3.0/24)    |
| AWS Direct Connect / TGW           |-------->| - Kafka Broker 3                    |
| Virtual Private Gateway            |         | - PostgreSQL Standby                |
+------------------------------------+         +------------------+------------------+
                                                                  |
                                                                  | HTTPS / TLS 1.3
                                                                  | OAuth 2.0 Bearer
                                                                  v
                                               +------------------+------------------+
                                               | Zetheta FinSight 4.2 Cloud          |
                                               | Public / Private API Endpoint       |
                                               | Ingestion Gateway (Port 443)        |
                                               +-------------------------------------+
```

### 1.1 Network Port and Firewall Matrix
| Source | Destination | Protocol / Port | Purpose | Encryption Standard |
|:---|:---|:---|:---|:---|
| Extractor Pods (`10.100.1.x`) | SAP PRD (`10.10.20.50`) | TCP 44300 | SAP ODP / CDS HTTPS OData Calls | TLS 1.3 (Internal CA) |
| Extractor Pods (`10.100.1.x`) | SAP PRD (`10.10.20.50`) | TCP 3300 | SAP Classic RFC Gateway | SNC (Secure Network Communications) |
| Integration Pods | Kafka Brokers (`10.100.x.x`) | TCP 9094 | Kafka Client Ingestion & Consumption | TLS with mTLS |
| Integration Pods | PostgreSQL (`10.100.2.50`) | TCP 5432 | Audit & Recon Metadata Queries | TLS 1.3 / SSL Enforced |
| FinSight Loader | FinSight Gateway | TCP 443 | REST API Batch Ingestion | TLS 1.3 (DigiCert CA) |
| Prometheus | Integration Pods | TCP 9090 / 9100 | Telemetry Metrics Scraping | HTTP over VPC Peering |

---

## 2. Security & Compliance Governance

### 2.1 SAP Authorisation Object Profile
The dedicated SAP service user `INTEG_SVC_FDE` is assigned role `Z_FDE_FINSIGHT_INTEG` containing the following least-privilege authorizations:
- **`S_RFC`:**
  - `ACTVT`: 16 (Execute)
  - `RFC_NAME`: `RFC_PING`, `BAPI_ACC_GET_BALANCES`, `RODPS_REPL_*`, `RFC_READ_TABLE`
  - `RFC_TYPE`: `FUGR` (Function Group)
- **`S_TABU_DIS`:**
  - `ACTVT`: 03 (Display only)
  - `DICBERCLS`: `&NC&`, `FB`, `FC` (Financial and Controlling tables)
- **`S_RO_OSDN`:**
  - `ACTVT`: 03 (Display), 16 (Execute extraction)
  - Authorized for ODP extraction contexts `SAPI`, `ABAP_CDS`
- **Password & Authentication Policy:** Technical system user with certificate-based X.509 logon; interactive SAP GUI login strictly disabled (`User Type: System`).

### 2.2 Data Residency & RBI Compliance
1. **Zero Egress Outside India:** Strict AWS Service Control Policy (SCP) permanently disables compute and storage provisioning in any region outside `ap-south-1` (Mumbai).
2. **Encrypted Key Management:** AWS KMS Customer Managed Keys (CMK) configured with annual rotation; keys are generated within Indian hardware security modules (HSM).
3. **Retention & Disposal:** Transactional audit logs are retained in PostgreSQL for 90 days, then moved to encrypted Snowflake S3 cold storage for 7 years per Indian Companies Act 2013 rules.

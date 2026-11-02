import os

def create_architecture_docs():
    os.makedirs(r'architecture/decisions', exist_ok=True)
    os.makedirs(r'architecture/risk-register', exist_ok=True)

    # Technology Selection
    tech_selection = """# Technology Stack Selection and Architectural Evaluation
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

## 1. Evaluation Methodology
The selection of architectural components balances enterprise reliability, low operational footprint, high throughput, zero data loss, and ease of auditability under Indian regulatory standards.

| Architectural Layer | Selected Technology | Evaluated Alternatives | Technical Justification for Selection | Rejection Rationale for Alternatives |
|:---|:---|:---|:---|:---|
| **Integration Runtime** | **Node.js 22 LTS + TypeScript 5.x** | Java Spring Boot 3, Python FastAPI, Go | Non-blocking event-driven I/O model is ideal for I/O-heavy API routing and Kafka streaming; strong TypeScript typing guarantees JSON schema contract safety; lightweight container footprint (under 120MB vs ~450MB JVM). | Spring Boot incurs higher cold-start and memory overhead in containerized clusters; Python GIL limits raw multi-threaded JSON parsing throughput at 500k-record scale. |
| **Message Broker** | **Apache Kafka 3.6 (Strimzi / Amazon MSK)** | RabbitMQ, AWS SQS/SNS, Apache Pulsar | Distributed log architecture provides true event replayability (crucial for financial auditing and reconciliation); partitioned topics enable horizontal consumer scaling; durable persistence guarantees zero message loss (RPO=0). | RabbitMQ queue-based model destroys messages upon consumption, preventing audit re-reads; SQS lacks multi-AZ message ordering guarantees across high-throughput partition keys. |
| **Audit & Reconciliation Database** | **PostgreSQL 16 (Amazon RDS Multi-AZ)** | MongoDB, DynamoDB, Redis, SQLite | ACID compliance is mandatory for financial balance ledgers and delta token tracking; robust JSONB support enables flexible storage of raw/transformed payloads; standard SQL facilitates complex reconciliation queries. | MongoDB lacks distributed transaction safety across complex multi-table accounting reconciliations; Redis is purely in-memory with durability risks. |
| **API Gateway & Ingress** | **Traefik / NGINX Ingress Controller** | Kong Gateway, AWS API Gateway, Apigee | Cloud-native, zero-downtime hot reloads; low latency TLS 1.3 termination; built-in rate-limiting, IP whitelisting, and circuit breaker middleware. | Apigee introduces significant cost and vendor lock-in; AWS API Gateway incurs high per-request costs at 500,000 requests/batch. |
| **Observability & Metrics** | **Prometheus + Grafana Enterprise** | Datadog, New Relic, Dynatrace | Open-source, self-hosted inside Indian AWS VPC ensuring zero telemetry data leakage across borders; native PromQL alerting aligns directly with enterprise Nagios/PagerDuty. | Commercial APMs violate strict corporate budget constraints and risk transmitting sensitive metadata outside India. |
| **API Specification Standard** | **OpenAPI 3.0 (YAML)** | RAML, GraphQL, gRPC | Universal enterprise standard; native support for JSON Schema, automated contract linting (Spectral), Postman collection generation, and multi-language client stub generation. | GraphQL adds unnecessary query complexity for standard batch ingestion pipelines; gRPC is not natively supported by FinSight's public REST ingestion ingress. |

---

## 2. Mandatory vs. Optional Prototype Components
- **Mandatory Production Architecture:** Apache Kafka cluster, PostgreSQL Audit Store, ODP RFC Extractor Service, Transformer Workers, Prometheus/Grafana stack, Azure AD OAuth 2.0 integration.
- **Optional Prototype Components:** In-memory mock SAP server, simulated FinSight ingestion receiver, local Docker Compose orchestration harness for rapid local validation without live SAP credentials.
"""

    # ADRs
    adr_001 = """# ADR-001: Adoption of Apache Kafka for Asynchronous Event Decoupling
## Context
The integration pipeline must ingest ~2.1 million monthly transactions from SAP S/4HANA across 7 manufacturing plants and stream them into Zetheta FinSight 4.2. Peak load requires handling 500,000 General Ledger entries within a 2-hour window. Direct synchronous HTTP streaming from SAP to FinSight exposes the pipeline to cascading failures, network jitter, and target API rate limiting.

## Decision
We adopt **Apache Kafka** as the central asynchronous message broker. The architecture deploys three core topics per data domain:
1. `sap.raw.<domain>`: Ephemeral raw extracted envelopes from SAP ODP/RFC.
2. `sap.transformed.<domain>`: Validated, canonical JSON events ready for ingestion.
3. `sap.dlq.<domain>`: Dead Letter Queue for schema failures, validation breaks, or unrecoverable HTTP errors.

## Consequences
- **Positive:** Guarantees durability and RPO=0 via distributed disk persistence (`min.insync.replicas=2`); decouples SAP extraction rate from FinSight ingestion rate; enables point-in-time replay for financial audit and reconciliation.
- **Negative:** Requires managing a 3-node Kafka cluster (or managed Amazon MSK); introduces eventual consistency latency (typically 2-5 seconds).
- **Status:** APPROVED by Rajesh Venkataraman & Marcus Wei.
"""

    adr_002 = """# ADR-002: Utilization of SAP Operational Data Provisioning (ODP) & CDS Views
## Context
Meridian Manufacturing operates SAP S/4HANA 2023 FPS02 on SAP HANA 2.0. Legacy table-level pooling (e.g. `SELECT * FROM BSEG`) causes massive database locking and is strictly vetoed by SAP Basis Administrator Priya Deshmukh. Furthermore, extracting large volumes must not interfere with the nightly batch job `RGGBS000` (01:00-04:30 IST) or exhaust the 50-connection RFC pool.

## Decision
We mandate the use of **SAP Operational Data Provisioning (ODP)** backed by custom Core Data Services (CDS) Views (e.g., `ZZ_CDS_ACDOCA_DELTA`). Delta capture utilizes SAP HANA's native Change Data Capture (CDC) mechanism with delta tokens.

## Consequences
- **Positive:** Zero table locks on `ACDOCA` or `BKPF`; delta queue manages cursor state natively in SAP; extraction footprint is reduced to small incremental packets every 30 minutes; complies with SAP recommended best practices.
- **Negative:** Requires initial transport deployment of CDS Views and ODP subscriptions in SAP PRD; requires SAP Basis transport sign-off.
- **Status:** APPROVED by Priya Deshmukh.
"""

    adr_003 = """# ADR-003: OAuth 2.0 Client Credentials Grant with Automated Pre-Expiry Refresh
## Context
FinSight 4.2 requires secure REST authentication via OAuth 2.0. Ingestion tokens expire every 3,600 seconds (1 hour). If a token expires during a 500,000-entry batch upload, in-flight requests will fail with HTTP 401 Unauthorized, risking pipeline stalls and duplicate re-transmissions.

## Decision
Implement an automated **OAuth 2.0 Token Lifecycle Manager** within the FinSight Loader microservice:
1. Authenticates against Azure AD / FinSight OAuth endpoint using `client_credentials` grant with dedicated scopes (`finsight:gl:write`, `finsight:ap:write`, etc.).
2. Tracks token TTL and triggers preemptive background refresh **120 seconds before expiry**.
3. Employs mutex locking during refresh to prevent multiple concurrent worker threads from issuing duplicate token requests.

## Consequences
- **Positive:** Zero HTTP 401 pipeline interruptions during continuous operations; thread-safe token sharing; strict adherence to least-privilege scope models.
- **Negative:** Requires secure secret storage in AWS Secrets Manager with automatic credential rotation.
- **Status:** APPROVED by Marcus Wei & Rajesh Venkataraman.
"""

    adr_004 = """# ADR-004: PostgreSQL for Metadata, Reconciliation & Audit Checkpointing
## Context
Internal Audit (Dr. Sanjay Kulkarni) requires a complete, immutable audit trail proving that every SAP document matches the visual records in FinSight. In addition, reconciliation engines need high-speed relational queries to perform debit-credit balance comparisons and track DLQ item resolutions.

## Decision
Deploy a multi-AZ **PostgreSQL 16** database as the dedicated Integration Metadata and Reconciliation Store. Tables include:
- `reconciliation_batch_ledger`: Batch run metadata, row counts, hash sums, variance indicators.
- `audit_document_lineage`: Mapping of SAP Document ID + Fiscal Year to FinSight Ingestion UUID, checksum, and timestamp.
- `dlq_exception_store`: Structured log of all failed records, error codes, and replay audit history.

## Consequences
- **Positive:** Full ACID guarantees; high-performance relational joins for financial reconciliations; native JSONB storage for historical payload diffs.
- **Negative:** Additional infrastructure provisioning in AWS Mumbai; requires automated backup and archiving to Snowflake after 90 days.
- **Status:** APPROVED by Dr. Sanjay Kulkarni.
"""

    adr_005 = """# ADR-005: Circuit Breaker Pattern for Downstream Fault Isolation
## Context
If FinSight 4.2 experiences maintenance outages, database degradation, or network timeouts, continuing to flood the target endpoint will trigger cascading failures, exhaust connection pools, and violate rate limits.

## Decision
Implement the **Martin Fowler Circuit Breaker Pattern** in the FinSight Ingestion microservice:
- **States:** `CLOSED` (Normal operations), `OPEN` (Fast-fail mode), `HALF-OPEN` (Canary probing mode).
- **Failure Threshold:** 5 consecutive HTTP 5xx or timeout errors within a 30-second sliding window.
- **Open State Duration:** 60 seconds (no outbound traffic sent; incoming Kafka consumption paused or buffered).
- **Half-Open Probe:** Dispatches a single canary request; if successful, resets to `CLOSED`; if failed, resets to `OPEN` for 120 seconds.

## Consequences
- **Positive:** Protects downstream analytics platform from denial-of-service; prevents integration worker crash loops; triggers immediate PagerDuty P2 operational alerts.
- **Negative:** Requires distributed state synchronization (via Redis or internal cluster state) if running multiple loader instances.
- **Status:** APPROVED by Marcus Wei & Rajesh Venkataraman.
"""

    # Master Document: D1_Integration_Architecture_v2.md
    d1_master = """# D1: Enterprise Integration Architecture Document
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Author:** Forward Deployed Engineering (FDE) Team  
**Version:** 2.0  
**Classification:** Strictly Private & Confidential  

---

## 1. Executive Summary & Architecture Blueprint
This document defines the production integration architecture connecting Meridian Manufacturing Ltd.'s on-premise **SAP S/4HANA 2023 FPS02** enterprise core with **Zetheta FinSight 4.2** in AWS Mumbai (`ap-south-1`). The solution bridges financial data silos across 7 manufacturing facilities and achieves an **83.3% improvement in data freshness (from 24 hours to <= 4 hours)** while adhering to strict Indian regulatory and data localization standards.

### Architectural Principles:
1. **Decoupled Asynchrony:** Zero tight synchronous coupling; Apache Kafka buffers peak loads up to 500,000 records.
2. **Defensive Ingestion:** Strict contract validation against canonical schemas; invalid data is trapped in Dead Letter Queues with zero data loss.
3. **Guaranteed Financial Integrity:** Automated 4-dimension reconciliation (Completeness, Accuracy, Timeliness, Consistency) ensuring zero debit-credit imbalances.
4. **Minimal ERP Overhead:** Delta extraction via SAP ODP and CDS Views respecting the nightly 01:00-04:30 IST batch window and capping RFC pool usage at 35 connections.

---

## 2. C4 Architecture Models

### 2.1 C4 Level 1: System Context Diagram
Refer to `architecture/diagrams/source/DGM_C4_SystemContext.mermaid` and exported visual `architecture/diagrams/exports/DGM_C4_SystemContext.svg`.
The Integration Platform sits at the enterprise boundary, mediating all interactions between Meridian's internal systems (SAP ERP, Salesforce CRM, Siemens Opcenter MES, Snowflake DW, Azure AD IdP) and the Zetheta FinSight analytics cloud.

### 2.2 C4 Level 2: Container Diagram
Refer to `architecture/diagrams/source/DGM_C4_Container.mermaid` and exported visual `architecture/diagrams/exports/DGM_C4_Container.svg`.
The platform comprises eight core containers deployed in AWS Mumbai across Multi-AZ availability zones:
1. **API Ingress Gateway:** Rate limiting, mTLS termination, and perimeter authentication.
2. **Distributed Extraction Scheduler:** Cron-based scheduling respecting blackout periods.
3. **SAP Extraction Engine:** Node.js/TypeScript runtime managing SAP RFC connection pools and ODP delta consumers.
4. **Apache Kafka Cluster:** 3-broker event bus with topic partitions per business domain.
5. **Transformation & Validation Engine:** Worker pool executing 50+ domain mappings, currency normalization, and 28 data quality rules.
6. **FinSight Ingestion Loader:** Resilient client handling OAuth 2.0 token management, circuit breaking, and retry backoff.
7. **Reconciliation & Audit Engine:** Automated cross-system balance comparator and break detector.
8. **PostgreSQL Audit & Checkpoint Store:** Relational ledger for audit lineage and DLQ management.

### 2.3 C4 Level 3: Component Specifications
- **Extraction Engine Component:** Details RFC connection pooling, CDS delta token persistence, cursor pagination, and metadata enrichment.
- **Transformation Engine Component:** Details JSON Schema validation, multi-currency lookup via `TCURR` cache, fiscal-to-calendar period mapping, and 7-level hierarchy flattening.

---

## 3. Network, Security & Infrastructure Architecture

### 3.1 Network Topology & Bandwidth Management
- **Interconnect:** Dedicated 450 Mbps Cisco SD-WAN over Airtel MPLS link connecting Hinjawadi Pune Data Centre with AWS Transit Gateway in Mumbai (`ap-south-1`).
- **QoS Bandwidth Capping:** Integration traffic is classified under DSCP AF21 and strictly throttled to **25% (112.5 Mbps)** during business hours (08:00 to 20:00 IST) to prevent starving MES and voice traffic.
- **Transport Compression:** All payloads over the wire utilize Gzip compression, reducing average payload size by 78%.

### 3.2 Security Architecture
- **In-Transit Encryption:** Mandatory TLS 1.3 for all HTTP communications and TLS with mTLS for Kafka broker-client communication.
- **At-Rest Encryption:** AES-256 encryption across Kafka EBS volumes, PostgreSQL RDS databases, and S3 cold storage archives using AWS KMS customer-managed keys (CMK).
- **Authentication & Authorization:**
  - Ingress to Integration Gateway: Azure Active Directory OAuth 2.0 with RS256 JWT signatures.
  - Egress to FinSight APIs: Dedicated OAuth 2.0 Client Credentials with domain-specific scopes (`finsight:financial:write`).
  - SAP RFC Authorization: Dedicated system user `INTEG_SVC_FDE` restricted to authorization objects `S_RFC`, `S_TABU_DIS`, and `S_RO_OSDN`.
- **Data Residency Compliance:** Strict enforcement that 100% of compute, storage, and networking remains within Indian sovereign territory (`ap-south-1`), fulfilling RBI guidelines and the DPDP Act 2023.

---

## 4. End-to-End Data Flows & Sequencing
The architecture specifies four formal data flows and three sequence traces:
1. **Real-Time ODP Delta Flow:** 30-minute extraction cycle from SAP CDS Views to FinSight ingestion.
2. **Batch Extraction Flow:** High-throughput 500,000-record batch processing with parallel consumer workers.
3. **Error Handling & Retry Flow:** Multi-tiered defense with exponential backoff, jitter, circuit breaker tripping, and DLQ routing.
4. **Reconciliation & Audit Flow:** Automated debit-credit checksum validation and break detection.
"""

    # Risk Register
    risk_reg = """# Enterprise Integration Risk Register
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

## 1. Risk Evaluation Matrix
Risks are evaluated using a standard 5x5 Probability vs. Impact matrix. All identified enterprise risks have documented mitigation strategies, trigger conditions, and assigned risk owners.

| Risk ID | Category | Risk Description | Prob (1-5) | Impact (1-5) | Severity Score | Mitigation Strategy | Contingency Plan | Risk Owner |
|:---|:---|:---|:---:|:---:|:---:|:---|:---|:---|
| **RSK-01** | Infrastructure | **RFC Connection Starvation:** Integration exhausts the 50-connection SAP RFC pool, blocking dialog SAP GUI users. | 3 | 5 | **15 (High)** | Cap integration connection pool at 35 connections (70%); implement connection keep-alive timeout of 30s in Node.js connector. | Drop non-critical master data syncs; alert Priya Deshmukh; throttle extractor concurrency. | Priya Deshmukh / FDE Lead |
| **RSK-02** | Operational | **Batch Blackout Violation:** Extraction runs during nightly `RGGBS000` job (01:00-04:30 IST), causing table locks or batch job aborts. | 2 | 5 | **10 (High)** | Hardcoded Blackout Window Guard in Quartz scheduler pauses extractions at 00:55 IST and resumes at 04:35 IST. | Emergency kill-switch API to immediately sever active RFC extraction threads. | Rajesh Venkataraman |
| **RSK-03** | Performance | **Network Saturation:** Integration bursts exceed 25% (112.5 Mbps) of MPLS link, impacting MES telemetry and plant operations. | 3 | 4 | **12 (High)** | Enforce Gzip compression on all payloads; configure Cisco SD-WAN QoS traffic shaping to clamp integration bandwidth at 110 Mbps. | Pause batch syncs; prioritize real-time ODP delta streams only. | Rajesh Venkataraman |
| **RSK-04** | API / Vendor | **FinSight API Rate Limiting (HTTP 429):** High-volume batches trigger rate limiting on FinSight ingestion ingress. | 4 | 3 | **12 (High)** | Micro-batching (max 500 records/POST); honor `Retry-After` header; implement exponential backoff with full jitter. | Temporarily buffer messages in Kafka topic partitions. | Marcus Wei / FDE Lead |
| **RSK-05** | Security | **OAuth Token Expiry Mid-Batch:** Token expires during a 500k-record batch, triggering mass HTTP 401 failures. | 3 | 4 | **12 (High)** | Preemptive token refresh triggered 120 seconds prior to 3600s TTL expiry; mutex-locked token cache. | Re-authenticate immediately; retry failed chunk without DLQ routing. | Security Lead / FDE Lead |
| **RSK-06** | Data Quality | **Unmapped Legacy Cost Centre:** SAP posts entries with obsolete or newly created cost centres not yet in FinSight master data. | 4 | 3 | **12 (High)** | Referential integrity pre-check against local cached master data; route orphans to DLQ; trigger automated master delta sync. | Route to Business Exception Queue; alert Meridian plant controller. | Dr. Sanjay Kulkarni |
| **RSK-07** | Financial / Audit | **Debit/Credit Imbalance Break:** Incomplete batch load results in unequal debits and credits in FinSight, violating accounting integrity. | 2 | 5 | **10 (High)** | Atomic transaction batching; post-load reconciliation compares sum of debits vs credits; trigger alert if variance > INR 0.00. | Mark batch status as `UNRECONCILED`; suppress executive dashboard update until resolved. | Ananya Krishnan / Dr. Kulkarni |
| **RSK-08** | Regulatory | **Data Residency Violation:** Telemetry or error dumps accidentally route outside AWS Mumbai region to US/EU logging services. | 1 | 5 | **5 (Med)** | VPC endpoint isolation; strict AWS IAM service control policies restricting all resources to `ap-south-1`. | Immediate data purge; alert Meridian Legal and Compliance officers. | Dr. Sanjay Kulkarni |
| **RSK-09** | Application | **Kafka Broker Failure:** One of the three Kafka broker nodes crashes during peak month-end volume. | 2 | 4 | **8 (Med)** | Multi-AZ Kafka cluster (`ap-south-1a`, `1b`, `1c`); topic replication factor = 3; `min.insync.replicas = 2`. | Automatic partition leader failover within 3 seconds; zero message loss. | FDE Lead |
| **RSK-10** | Accounting | **Missing Exchange Rate (`TCURR`):** Foreign currency transaction occurs on bank holiday with missing daily exchange rate. | 3 | 3 | **9 (Med)** | Fallback to nearest previous business day's official rate; tag record with warning flag `STALE_EXCHANGE_RATE`. | Daily automated alert for missing rates in SAP table `TCURR`. | Finance Controller |
| **RSK-11** | Application | **Memory Exhaustion (OOM) in Worker:** Ingesting 500k records causes Node.js heap overflow. | 2 | 4 | **8 (Med)** | Stream-based JSON processing; chunking into 5,000-record sub-streams; container memory limit set to 2GB with Node heap limit 1.5GB. | Kubernetes container restart policy auto-recovers worker; Kafka consumer group rebalances. | FDE Lead |
| **RSK-12** | Human / Change | **SAP CDS View Schema Modification:** SAP Basis updates CDS View structure without notifying integration engineering. | 2 | 4 | **8 (Med)** | Automated schema validation on ingestion; contract testing in CI/CD pipeline; formal SAP change transport governance. | Extractor halts domain gracefully with error `ERR-EXT-003`; alerts integration team. | Priya Deshmukh |
"""

    # Network and Security Architecture
    net_sec = """# Network and Security Architecture Specification
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
"""

    with open(r'architecture/technology-selection.md', 'w', encoding='utf-8') as f:
        f.write(tech_selection)
    with open(r'architecture/decisions/ADR-001-asynchronous-messaging-kafka.md', 'w', encoding='utf-8') as f:
        f.write(adr_001)
    with open(r'architecture/decisions/ADR-002-odp-delta-extraction-sap.md', 'w', encoding='utf-8') as f:
        f.write(adr_002)
    with open(r'architecture/decisions/ADR-003-oauth2-token-management.md', 'w', encoding='utf-8') as f:
        f.write(adr_003)
    with open(r'architecture/decisions/ADR-004-postgresql-reconciliation-store.md', 'w', encoding='utf-8') as f:
        f.write(adr_004)
    with open(r'architecture/decisions/ADR-005-circuit-breaker-resilience.md', 'w', encoding='utf-8') as f:
        f.write(adr_005)
    with open(r'architecture/D1_Integration_Architecture_v2.md', 'w', encoding='utf-8') as f:
        f.write(d1_master)
    with open(r'architecture/risk-register/enterprise-risk-register.md', 'w', encoding='utf-8') as f:
        f.write(risk_reg)
    with open(r'architecture/network-and-security-architecture.md', 'w', encoding='utf-8') as f:
        f.write(net_sec)

    print('Wrote all architecture documents, ADRs, risk register, and network specs!')

if __name__ == '__main__':
    create_architecture_docs()

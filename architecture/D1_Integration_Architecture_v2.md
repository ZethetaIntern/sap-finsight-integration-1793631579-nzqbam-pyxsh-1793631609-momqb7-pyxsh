# D1: Enterprise Integration Architecture Document
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

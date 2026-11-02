# Stakeholder Analysis & Persona Profiles
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.

---

## 1. Stakeholder Matrix Overview
Successful enterprise integration requires active alignment across corporate finance, SAP IT operations, enterprise infrastructure, analytics engineering, and internal regulatory audit. The following six key stakeholder personas govern the project's requirements, architectural approvals, and acceptance criteria:

| Stakeholder Name | Official Role | Department | Key Concern & Focus | Primary Evaluation Criteria | Preferred Communication Channel |
|:---|:---|:---|:---|:---|:---|
| **Ananya Krishnan** | Chief Financial Officer (CFO) | Corporate Finance | Working capital visibility, data freshness, business ROI | 83% freshness gain, zero financial discrepancy, month-end speed | Executive Briefings, High-level KPI Dashboards |
| **Rajesh Venkataraman** | VP of IT Infrastructure | Enterprise IT | Production stability, network load, security compliance | Bandwidth capping (<25%), zero unauthenticated endpoints, ISO 27001 | Architecture Design Reviews, Technical Hand-off |
| **Priya Deshmukh** | Lead SAP Basis Administrator | SAP COE / Basis | RFC connection pool limits, database load, transport stability | RFC connection pooling (<=50), ODP delta frequency (>=30m), no lock escalations | Technical Runbooks, SAP OSS Notes, RFC Audits |
| **Marcus Wei** | Principal Platform Engineer | Zetheta Analytics | API contract integrity, ingestion throughput, schema versioning | OpenAPI 3.0 schema compliance, rate limiting (HTTP 429), token refresh | OpenAPI YAML specs, Swagger Hub, Postman Collections |
| **Dr. Sanjay Kulkarni** | Head of Internal Audit | Compliance & Audit | Statutory compliance, tamper-evident audit trails, data lineage | Source-to-target lineage, Indian RBI data residency, zero undetected breaks | Reconciliation Reports, Checkpoint Verification Logs |
| **Fatima Al-Hassan** | Manufacturing Operations Director | Plant Operations | Standard vs. actual costing variance, scrap rate visibility | Line-item material ledger accuracy, multi-plant visibility (7 plants) | Plant-level operational variance dashboards |

---

## 2. In-Depth Stakeholder Profiles & Engagement Strategy

### 2.1 Ananya Krishnan — Chief Financial Officer (CFO)
* **Perspective:** Ananya views integration not as a technical plumbing exercise, but as a strategic enabler of capital efficiency. Meridian's multi-plant operations suffer from delayed inventory valuation and slow customer collection visibility.
* **Key Demands:**
  - Quantified business ROI: Justification of integration middleware investment.
  - Hard guarantee that financial figures in FinSight reconcile 100% with SAP audited figures.
  - Strict delivery milestones: Go-live prior to Q3 board presentation.
* **Engagement Plan:** Bi-weekly executive dashboards with non-technical milestone tracking, clear financial risk disclosures, and quantified operational gains.

### 2.2 Rajesh Venkataraman — VP of IT Infrastructure
* **Perspective:** Responsible for total infrastructure health. Highly sensitive to external integrations overloading enterprise WAN/MPLS links or creating cybersecurity attack vectors.
* **Key Demands:**
  - Network utilization over shared 450 Mbps MPLS link must never exceed 25% (112.5 Mbps) during business peak hours (08:00 - 20:00 IST).
  - All communication must traverse encrypted TLS 1.3 tunnels with mTLS or strict OAuth 2.0 mutual authentication.
  - Clear disaster recovery (DR) runbooks and failure isolation.
* **Engagement Plan:** Formal Architecture Review Board (ARB) sign-offs, network packet analysis reports, and perimeter firewall specifications.

### 2.3 Priya Deshmukh — Lead SAP Basis Administrator
* **Perspective:** Guardian of SAP S/4HANA production instance (PRD, Client 100). Concerned about unindexed queries, table locks, and memory dumps (short dumps TSV_TNEW_PAGE_ALLOC_FAILED).
* **Key Demands:**
  - Extraction must use SAP standard Operational Data Provisioning (ODP) Framework and Core Data Services (CDS) views.
  - RFC dialog connection pool capped at 50 connections to prevent starving human users.
  - Absolute blackout window: Zero batch extraction between 01:00 AM and 04:30 AM IST during nightly batch job RGGBS000.
  - Transports must follow standard SAP CTS+ procedures via Dev -> QA -> Prod.
* **Engagement Plan:** Detailed ABAP program transport manifest, ODP delta queue extraction testing logs, and Work Process utilization graphs.

### 2.4 Marcus Wei — Principal Platform Engineer (Zetheta FinSight)
* **Perspective:** Owner of the destination ingestion microservices. Protects FinSight from malformed JSON, unbounded batch sizes, and resource-hogging burst payloads.
* **Key Demands:**
  - Strict compliance with Zetheta FinSight 4.2 Ingestion REST API schemas.
  - Client must honor HTTP 429 backoff headers (Retry-After) with jittered exponential backoff.
  - Token refresh cycles must be automated via standard OAuth 2.0 client credentials grant.
  - Payloads must be chunked into deterministic micro-batches (max 500 records per POST request).
* **Engagement Plan:** Direct collaboration via OpenAPI 3.0 YAML contracts, automated Spectral linting validation, and contract testing suites.

### 2.5 Dr. Sanjay Kulkarni — Head of Internal Audit
* **Perspective:** Focuses on regulatory exposure under Indian Companies Act (2013), CARO 2020, and RBI Data Localisation Guidelines.
* **Key Demands:**
  - Immutable audit logs capturing every extracted document ID, extraction timestamp, and transformation hash.
  - Sovereign data residency: Zero transactional financial data stored or processed outside Indian territory (AWS Mumbai p-south-1 only).
  - Daily reconciliation break reports with SLA for manual exception clearance.
* **Engagement Plan:** Weekly audit logs, automated debit-credit balancing checks, and cryptographic hash verification logs.

### 2.6 Fatima Al-Hassan — Manufacturing Operations Director
* **Perspective:** Needs visibility into why plant production costs vary between Pune (automotive engine components) and Chennai (electronic control units).
* **Key Demands:**
  - Accurate allocation of overhead costs from Cost Centre (CO-OM) to Material Ledger actual costing.
  - Timely visibility into Purchase Order price variances (PPV) and goods receipt backlogs.
* **Engagement Plan:** Standardized operational data models ensuring consistent mapping of scrap, bill of materials, and machine hour rates.

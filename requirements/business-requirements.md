# Business Requirements Document (BRD)
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Project Code:** FDE-9B-MERIDIAN-INTEGRATION  
**Author:** Forward Deployed Engineering (FDE) Team  
**Version:** 2.0  
**Classification:** Strictly Private & Confidential  

---

## 1. Executive Context & Problem Statement
Meridian Manufacturing Ltd. is a premier multi-plant precision manufacturer in India operating across automotive, aerospace, and industrial component segments. While core manufacturing and transactional finance operations are hosted on **SAP S/4HANA (Version 2023 FPS02)**, executive financial analytics, management reporting, and variance dashboards are being transitioned to **Zetheta FinSight 4.2**.

Currently, financial data is extracted using manual end-of-day ABAP extractors, batch CSV dumps, and staging ETL jobs that deliver updates on a **24-hour cycle**. Consequently:
1. Executive leadership (CFO, Operations Directors) makes strategic decisions based on day-old figures.
2. Inter-plant production variances and standard-costing variations across 7 manufacturing facilities take up to 36 hours to be detected.
3. Accounts Receivable (AR) dunning and credit risk management lag, increasing Working Capital lock-in.
4. Month-end closing takes 6 business days due to time-consuming manual reconciliation across systems.

### 1.1 Core Business Objective
The primary business objective is to design and deploy an enterprise-grade, automated, resilient integration pipeline between SAP S/4HANA and Zetheta FinSight 4.2 that **reduces financial data latency from 24 hours to a maximum of 4 hours (an 83.3% improvement in data freshness)**, with zero operational degradation to SAP core transaction processing.

---

## 2. In-Scope Business Domains
The integration encompasses 10 core financial and operational accounting domains across all active legal entities and manufacturing facilities:

| Domain ID | Business Domain | SAP Source Artifacts | Target FinSight Entity | Business Impact |
|:---|:---|:---|:---|:---|
| **DOM-01** | General Ledger (GL) | ACDOCA, BKPF, BSEG | journalEntry | Real-time P&L, balance sheet visibility, cash flow tracking |
| **DOM-02** | Accounts Payable (AP) | BSIK, BSAK, LFA1, LFC1 | endorInvoice | Working capital optimization, vendor discount capture |
| **DOM-03** | Accounts Receivable (AR) | BSID, BSAD, KNA1, KNC1 | customerReceivable | DSO reduction, credit limit breach alerts, automated dunning |
| **DOM-04** | Cost Centre Accounting (CO-OM) | CSKS, CSKT, COSP, COSS | costCentrePerformance | Plant overhead tracking, departmental budget control |
| **DOM-05** | Profit Centre Accounting (CO-PCA) | CEPC, CEPCT | profitCentreMargin | Business unit profitability, segment reporting (IND-AS 108) |
| **DOM-06** | Material Ledger (CO-PC) | MBEW, MLCD, CKMLCR | materialValuation | Actual costing variance, inventory revaluation visibility |
| **DOM-07** | Purchase Orders (MM-PUR) | EKKO, EKPO, EKET | purchaseOrderSummary | Procurement spend analytics, GR/IR unbilled liabilities |
| **DOM-08** | Sales Orders (SD-SLS) | VBAK, VBAP, VBEP | salesOrderPipeline | Revenue backlog, unbilled revenue, order fulfillment |
| **DOM-09** | Fixed Assets (FI-AA) | ANLA, ANLZ, ANLP | ixedAssetRegister | Capital expenditure tracking, monthly depreciation runs |
| **DOM-10** | Bank Statements (FI-BL) | FEBKO, FEBEP | ankCashPosition | Intra-day liquidity forecasting, bank clearing reconciliation |

*Additional supporting domains specified for operational completeness include Budget vs. Actuals (COSP/COSS) and Inventory Balances (MARD).*

---

## 3. High-Level Functional Requirements (FR)

| Req ID | Requirement Summary | Description | Mandatory / Optional |
|:---|:---|:---|:---|
| **FR-01** | Automated Near-Real-Time Delta Extraction | Extract incremental transactional data from SAP S/4HANA every 30 minutes via Operational Data Provisioning (ODP) without impacting dialog user sessions. | Mandatory |
| **FR-02** | Master Data Synchronization | Daily synchronized extraction of customer, vendor, cost centre, profit centre, and general ledger master data hierarchies. | Mandatory |
| **FR-03** | Bidirectional Data Validation | Validate incoming SAP records against strict canonical JSON schemas prior to transmission to FinSight; reject malformed records immediately to Dead Letter Queues (DLQ). | Mandatory |
| **FR-04** | Multi-Currency Normalization | Convert foreign currency amounts (USD, EUR, GBP, JPY) to Corporate Group Currency (INR) using daily exchange rate feeds from SAP table TCURR. | Mandatory |
| **FR-05** | Fiscal-to-Calendar Period Mapping | Map SAP fiscal periods (April–March fiscal year, periods 001–016 including audit adjustment periods) into Gregorian calendar quarters and months. | Mandatory |
| **FR-06** | Cost Centre Hierarchy Flattening | Recursively traverse SAP 7-level standard cost centre hierarchy sets (SETNODE, SETLEAF) and flatten into tabular dimensions. | Mandatory |
| **FR-07** | Automated Source-to-Target Reconciliation | Reconcile record counts, debit-credit hash totals, and line item financial amounts at batch completion; enforce zero financial break policy. | Mandatory |
| **FR-08** | Idempotent Loading & Deduplication | Ensure exactly-once processing semantics at the analytics ingest endpoint using composite business keys (CompanyCode-FiscalYear-DocumentNumber-LineItem). | Mandatory |
| **FR-09** | Dead Letter Queue (DLQ) & Reprocessing | Maintain isolated holding storage for failed messages with automated and manual replay capabilities. | Mandatory |
| **FR-10** | Audit Trail & Data Lineage | Retain bidirectional audit logs linking every FinSight visual metric back to source SAP document ID, fiscal year, and extractor token. | Mandatory |

---

## 4. Business Success Metrics & KPIs
1. **Data Freshness Latency:** Reduced from 24h to <= 4h across all 10 domains (target: 30 minutes for ODP delta streams).
2. **Reconciliation Variance:** 0.00% variance for General Ledger debit/credit totals; < 0.01% for inventory moving average revaluations.
3. **Pipeline Availability:** >= 99.9% uptime during operational business hours (06:00 to 22:00 IST).
4. **Processing Throughput:** Capable of processing peak batches of 500,000 GL entries within a 2-hour execution window (target: >= 70 records/second).
5. **Operational Resilience:** Mean Time to Recovery (MTTR) < 15 minutes for transient network/service failures via automated retries and circuit breakers.

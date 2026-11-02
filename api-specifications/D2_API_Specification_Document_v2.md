# D2: API Specification Document (Source & Destination Endpoints)
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Author:** Forward Deployed Engineering (FDE) Team  
**Version:** 2.0  
**Classification:** Strictly Private & Confidential  

---

## 1. Overview and Ingestion Principles
This document specifies the bidirectional interface contracts governing the data pipeline between **SAP S/4HANA 2023 FPS02** and **Zetheta FinSight 4.2**.
- **Source API Paradigm:** SAP Core Data Services (CDS) Views exposed as OData v2/v4 and ODP (Operational Data Provisioning) REST services.
- **Destination API Paradigm:** RESTful micro-batch JSON ingestion endpoints protected by OAuth 2.0 Client Credentials and tenant-isolated namespaces.
- **Idempotency Guarantee:** All destination `POST` endpoints enforce idempotency via the `X-Idempotency-Key` header (UUIDv4) and composite business keys (`CompanyCode-FiscalYear-DocNumber-LineItem`).

---

## 2. SAP Source Endpoint Directory (12 Endpoints)

| Endpoint ID | Domain Name | SAP Source Tables / CDS View | Extraction Pattern | Endpoint URI Path | Delta Mechanism |
|:---|:---|:---|:---|:---|:---|
| **SRC-001** | General Ledger | ACDOCA, BKPF, BSEG (`ZZ_CDS_ACDOCA_DELTA`) | 30-min Delta / Micro-batch | `/ZZ_FIN_GL_CDS/GLItems` | ODP Delta Token (`$skiptoken`) |
| **SRC-002** | Accounts Payable | BSIK, BSAK, LFA1, LFC1 (`ZZ_CDS_AP_DELTA`) | 30-min Delta | `/ZZ_FIN_AP_CDS/VendorInvoices` | ODP Delta Token |
| **SRC-003** | Accounts Receivable | BSID, BSAD, KNA1, KNC1 (`ZZ_CDS_AR_DELTA`) | 30-min Delta | `/ZZ_FIN_AR_CDS/CustomerReceivables` | ODP Delta Token |
| **SRC-004** | Cost Centre | CSKS, CSKT, COSP, COSS (`ZZ_CDS_CC_MASTER`) | Daily Master / Intra-day Actuals | `/ZZ_FIN_CO_CDS/CostCentres` | Timestamp Filter (`AEDAT`) |
| **SRC-005** | Profit Centre | CEPC, CEPCT (`ZZ_CDS_PC_MASTER`) | Daily Master | `/ZZ_FIN_PCA_CDS/ProfitCentres` | Timestamp Filter (`AEDAT`) |
| **SRC-006** | Material Ledger | MBEW, MLCD, CKMLCR (`ZZ_CDS_ML_COSTS`) | Hourly Batch | `/ZZ_FIN_ML_CDS/MaterialValuations` | Period / Valuation Token |
| **SRC-007** | Purchase Orders | EKKO, EKPO, EKET (`ZZ_CDS_MM_PO`) | 30-min Delta | `/ZZ_MM_PO_CDS/PurchaseOrders` | ODP Delta Token |
| **SRC-008** | Sales Orders | VBAK, VBAP, VBEP (`ZZ_CDS_SD_SO`) | 30-min Delta | `/ZZ_SD_SO_CDS/SalesOrders` | ODP Delta Token |
| **SRC-009** | Fixed Assets | ANLA, ANLZ, ANLP (`ZZ_CDS_FI_AA`) | Monthly Batch / Delta | `/ZZ_FI_AA_CDS/FixedAssets` | Asset Capitalization Token |
| **SRC-010** | Bank Statements | FEBKO, FEBEP (`ZZ_CDS_FI_BL`) | Intra-day Delta | `/ZZ_FI_BL_CDS/BankStatements` | Statement ID Token |
| **SRC-011** | Budget vs. Actual | COSP, COSS (`ZZ_CDS_CO_BGT`) | Daily Batch | `/ZZ_CO_BGT_CDS/BudgetActuals` | Fiscal Period Token |
| **SRC-012** | Inventory Balances| MARD, MBEW (`ZZ_CDS_MM_INV`) | Hourly Batch | `/ZZ_MM_INV_CDS/InventoryItems` | Storage Location Token |

---

## 3. FinSight Destination Endpoint Directory (12 Endpoints)
*[Notice: Assumed Contract - Based on Standard Zetheta FinSight 4.2 API Specification]*

| Endpoint ID | FinSight Resource Domain | Ingestion Method & Path | Target Analytics Schema | Expected Batch Size | Ingestion SLA Target |
|:---|:---|:---|:---|:---|:---|
| **DST-001** | General Ledger | `POST /financial/journal-entries/batch` | `CanonicalJournalEntry` | 500 records/payload | < 1.5 seconds P95 |
| **DST-002** | Accounts Payable | `POST /payables/invoices/batch` | `CanonicalVendorInvoice` | 500 records/payload | < 1.5 seconds P95 |
| **DST-003** | Accounts Receivable | `POST /receivables/invoices/batch` | `CanonicalCustomerReceivable` | 500 records/payload | < 1.5 seconds P95 |
| **DST-004** | Cost Centre Performance | `POST /controlling/cost-centres/batch` | `CanonicalCostCentre` | 200 records/payload | < 1.0 seconds P95 |
| **DST-005** | Profit Centre Margins | `POST /controlling/profit-centres/batch` | `CanonicalProfitCentre` | 200 records/payload | < 1.0 seconds P95 |
| **DST-006** | Material Valuation | `POST /inventory/material-costs/batch` | `CanonicalMaterialCost` | 500 records/payload | < 2.0 seconds P95 |
| **DST-007** | Procurement Spend | `POST /procurement/purchase-orders/batch`| `CanonicalPurchaseOrder` | 500 records/payload | < 1.5 seconds P95 |
| **DST-008** | Sales Order Backlog | `POST /sales/orders/batch` | `CanonicalSalesOrder` | 500 records/payload | < 1.5 seconds P95 |
| **DST-009** | Fixed Asset Register | `POST /assets/register/batch` | `CanonicalFixedAsset` | 200 records/payload | < 1.0 seconds P95 |
| **DST-010** | Bank Cash Position | `POST /treasury/cash-positions/batch` | `CanonicalBankStatement` | 100 records/payload | < 0.8 seconds P95 |
| **DST-011** | Budget Performance | `POST /controlling/budget-performance/batch`| `CanonicalBudgetPerformance`| 200 records/payload | < 1.0 seconds P95 |
| **DST-012** | Inventory Balances | `POST /inventory/balances/batch` | `CanonicalInventoryBalance` | 500 records/payload | < 2.0 seconds P95 |

---

## 4. Authentication, Token Lifecycle & Error Contract
- **OAuth 2.0 Flow:** Client Credentials Grant against `https://auth.finsight.zetheta.com/oauth/v2/token`.
- **Token Format:** RS256-signed JWT token containing claims: `iss`, `sub`, `tenant_id`, `exp`, `scope`.
- **Preemptive Refresh:** The integration runtime tracks the 3,600s TTL and executes refresh at T-120 seconds.
- **Standardized Error Responses:** Fully aligned with Appendix B (e.g. `INVALID_REQUEST`, `TOKEN_EXPIRED`, `RATE_LIMITED`, `SERVICE_UNAVAILABLE`).

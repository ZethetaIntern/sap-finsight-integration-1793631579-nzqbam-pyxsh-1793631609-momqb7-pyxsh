# Batch Reconciliation Report: BATCH-GL-20260315-0930
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

### Executive Reconciliation Summary
| Field | Production Value | Verification & Audit Notes |
|:---|:---|:---|
| **Batch ID** | `BATCH-GL-20260315-0930` | Unique deterministic batch execution identifier |
| **Extraction Timestamp** | `2026-03-15T09:30:00+05:30` | Initiated via Quartz ODP Scheduler |
| **Load Completion Timestamp** | `2026-03-15T09:32:45+05:30` | Ingestion acknowledged by FinSight REST API |
| **Data Domain** | General Ledger Journal Entries | Universal Journal line items |
| **Source System** | SAP S/4HANA (PRD, Client 100, Company Code MC01) | Pune Hinjawadi Tier-4 Data Centre |
| **Target System** | Zetheta FinSight (Tenant: `MERIDIAN-PROD`) | AWS Mumbai (`ap-south-1`) Ingestion Cluster |
| **Extraction Method** | ODP Delta via CDS View `ZZ_CDS_ACDOCA_DELTA` | Delta pointer CDC extraction |
| **Delta Token (Previous)** | `20260315_090000_000001` | Committed checkpoint from 09:00 IST cycle |
| **Delta Token (Current)** | `20260315_093000_000001` | Current committed checkpoint |
| **Records Extracted from Source** | **6,247** | Raw extracted rows from SAP S/4HANA |
| **Records Passed Validation** | **6,243** | Passed all 28 canonical Data Quality rules |
| **Records Failed Validation** | **4** | Trapped and routed to Dead Letter Queue |
| **Records Transformed Successfully**| **6,243** | Currency converted and fiscal periods mapped |
| **Records Loaded to Target** | **6,241** | Ingested into FinSight columnar store |
| **Records Skipped (Idempotent)** | **2** | Exact duplicate keys detected; skipped idempotently |
| **Source Checksum (Debit)** | **INR 24,17,89,342.30** | `SUM(HSL)` where `DRCRK = 'S'` |
| **Source Checksum (Credit)** | **INR 24,17,89,342.30** | `SUM(HSL)` where `DRCRK = 'H'` |
| **Target Checksum (Debit)** | **INR 24,17,89,342.30** | `SUM(amountLC)` where `postingType = 'DEBIT'` |
| **Target Checksum (Credit)** | **INR 24,17,89,342.30** | `SUM(amountLC)` where `postingType = 'CREDIT'` |
| **Debit-Credit Balance Variance** | **INR 0.00** | **PERFECT ZERO BREAK (Audited)** |
| **Source-Target Record Count Var**| **4** | Exactly matches 4 DLQ validation failure records |
| **Reconciliation Status** | **RECONCILED** | All loaded records match; 4 in DLQ for steward review |
| **Top Error 1** | `ERR-MAP-003` (Invalid cost centre reference) | 3 records (`KOSTL = '0000009999'`) |
| **Top Error 2** | `ERR-VAL-007` (Future posting date rejected) | 1 record (`BUDAT = '2026-03-29'`) |
| **DLQ Records Routed This Batch** | **4** | Persisted in `dlq_exception_store` |
| **Cumulative DLQ Depth** | **17** | Total unresolved DLQ across all domains |
| **Total Processing Duration** | **2 minutes 45 seconds** | Well within 30-minute extraction SLA |
| - Extraction Duration | 1 minute 12 seconds | Network ODP streaming over MPLS |
| - Transformation Duration | 0 minutes 48 seconds | Multi-threaded worker JSON processing |
| - Loading Duration | 0 minutes 45 seconds | Chunked HTTP/2 micro-batches |
| **Effective Throughput** | **37.8 records/second** | Nominal throughput during regular operations |

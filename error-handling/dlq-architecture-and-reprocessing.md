# Dead Letter Queue (DLQ) Architecture and Reprocessing Specification
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document Ref:** RES-DLQ-01  
**Classification:** Strictly Private & Confidential  

---

## 1. Dead Letter Queue Design
Every malformed, unvalidated, or permanently failing record is preserved in isolated holding infrastructure to ensure **Zero Data Loss (RPO=0)**.

The DLQ infrastructure utilizes a dual storage tier:
1. **Streaming Bus Tier:** Kafka topic `sap.dlq.<domain>` (retained for 30 days, replication factor 3).
2. **Relational Search Tier:** PostgreSQL table `dlq_exception_store` with full-text search and indexing on `documentId`, `errorCode`, and `plantCode`.

---

## 2. DLQ Message Envelope Structure
```json
{
  "dlqMessageId": "DLQ-20260315-000492",
  "originalTopic": "sap.raw.gl",
  "domain": "GENERAL_LEDGER",
  "documentId": "MC01-2026-0100004521-001",
  "errorCode": "ERR-MAP-003",
  "errorCategory": "DATA_QUALITY",
  "errorMessage": "Referenced Cost Centre '0000009999' not found in active master data",
  "failedStage": "TRANSFORMATION_VALIDATION",
  "attemptCount": 3,
  "firstFailureTimestamp": "2026-03-15T09:31:12.450Z",
  "lastFailureTimestamp": "2026-03-15T09:31:45.120Z",
  "sourcePayload": {
    "RBUKRS": "MC01",
    "GJAHR": "2026",
    "BELNR": "0100004521",
    "BUZEI": "001",
    "KOSTL": "0000009999",
    "HSL": 45000.00
  },
  "reprocessingStatus": "PENDING_REVIEW"
}
```

---

## 3. Reprocessing Workflow
1. **Automated Master Data Resync:** If `ERR-MAP-003` occurs, the engine triggers an ad-hoc delta pull for the missing master data entity. Once synced, pending DLQ records are automatically re-evaluated.
2. **Operational Portal Reprocessing:** Meridian financial data stewards access the secure Web Exception Console to review records, apply corrected mappings, and click **Replay Batch**.
3. **Audit Immutability:** Reprocessed records maintain their original DLQ ID and log an audit trail showing the approving user, correction reason, and timestamp.

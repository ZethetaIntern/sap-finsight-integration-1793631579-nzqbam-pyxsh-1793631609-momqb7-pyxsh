# ADR-004: PostgreSQL for Metadata, Reconciliation & Audit Checkpointing
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

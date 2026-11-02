# ADR-001: Adoption of Apache Kafka for Asynchronous Event Decoupling
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

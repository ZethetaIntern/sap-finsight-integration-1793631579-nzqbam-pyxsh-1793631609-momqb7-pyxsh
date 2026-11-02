# Integration Test Scenarios Master Matrix (25 Detailed Scenarios)
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

## Part 1: Functional Test Scenarios (TST-FNC-001 to TST-FNC-010)

### TST-FNC-001: Happy Path General Ledger End-to-End Extraction & Ingestion
- **Category:** Functional
- **Preconditions:** SAP PRD (Client 100) reachable; FinSight staging tenant active; 500 new GL entries posted in SAP.
- **Execution Steps:**
  1. Trigger ODP delta extraction for domain GL via scheduler.
  2. Verify raw message arrival on Kafka topic `sap.raw.gl`.
  3. Inspect transformation worker logs for JSON schema validation and currency conversion.
  4. Query FinSight API endpoint `/financial/journal-entries/batch` to confirm 500 records loaded.
  5. Run batch reconciliation comparing source debit/credit total with FinSight total.
- **Expected Results:** All 500 records ingested with HTTP 201; zero records in DLQ; debit/credit variance = INR 0.00.
- **Pass/Fail Criteria:** PASS if ingested count == 500 and variance == 0.00; FAIL otherwise.

### TST-FNC-002: Accounts Payable Synchronization with Ageing & Multi-Currency Conversion
- **Category:** Functional
- **Preconditions:** Vendor open invoices in `BSIK` with USD, EUR, and INR amounts; active exchange rates in `TCURR`.
- **Execution Steps:**
  1. Extract AP open items for Company Code `MC01`.
  2. Validate transformation logic for `MAP-AP-004` (due date calculation) and `MAP-AP-007` (ageing bucket).
  3. Validate foreign currency conversion to INR group currency.
  4. Verify FinSight payables ingestion.
- **Expected Results:** Invoices correctly categorized into ageing buckets ('CURRENT', '1-30', etc.); all amounts converted to INR at official rate; clearing status = 'OPEN'.
- **Pass/Fail Criteria:** PASS if 100% of currencies match `TCURR` exchange calculations within +/- 0.01 INR rounding.

### TST-FNC-003: Master Data Delta Synchronization (Cost Centre Creation)
- **Category:** Functional
- **Preconditions:** Existing Cost Centre master synchronized between SAP and FinSight.
- **Execution Steps:**
  1. Create new Cost Centre `0000004500` ('Robotics Assembly') in SAP via transaction `KS01`.
  2. Trigger master data delta extraction cycle.
  3. Query FinSight dimension `/controlling/cost-centres/batch`.
- **Expected Results:** New Cost Centre appears in FinSight within one extraction cycle (< 30 minutes) with flattened hierarchy fields populated.
- **Pass/Fail Criteria:** PASS if Cost Centre `4500` is queryable in FinSight with correct parent hierarchy.

### TST-FNC-004: Multi-Company Code Batch & Tenant Isolation Verification
- **Category:** Functional
- **Preconditions:** Test batch containing entries from `MC01` (Maharashtra), `MC02` (Gujarat), and `MC03` (Tamil Nadu).
- **Execution Steps:**
  1. Ingest mixed extraction batch containing all 3 company codes.
  2. Verify tenant routing in API Gateway (`X-Tenant-ID` header and payload company code).
  3. Inspect FinSight multi-tenant data segregation.
- **Expected Results:** Each company code is routed to its respective tenant partition; zero cross-tenant data contamination.
- **Pass/Fail Criteria:** PASS if zero records from `MC01` appear in `MC02` tenant queries.

### TST-FNC-005: Fiscal Period Variant Mapping (Normal & Special Periods)
- **Category:** Functional
- **Preconditions:** Test journal entries with SAP periods `001` through `016`.
- **Execution Steps:**
  1. Process entries spanning April (`001`) through March (`012`), and audit periods (`013` to `016`).
  2. Validate calendar month string output.
- **Expected Results:** Periods 001-012 map to respective calendar months (e.g. 001 -> '2026-04'); periods 013-016 map to '2027-03' with `isSpecialPeriod: true`.
- **Pass/Fail Criteria:** PASS if all 16 periods map accurately per specification `TR-FISC-01`.

### TST-FNC-006: 7-Level Cost Centre Hierarchy Flattening
- **Category:** Functional
- **Preconditions:** SAP standard hierarchy tree in `SETNODE`/`SETLEAF` with 7 nested levels.
- **Execution Steps:**
  1. Run hierarchy flattening extractor on Cost Centre group `MERIDIAN_CORP`.
  2. Inspect generated dimensional records in transformation service.
- **Expected Results:** Tabular structure generated where `Level1` through `Level7` are properly assigned; leaf nodes resolve to specific Cost Centres.
- **Pass/Fail Criteria:** PASS if all 7 levels match the SAP tree hierarchy in transaction `KSH3`.

### TST-FNC-007: Procure-to-Pay (P2P) Document Flow Tracing
- **Category:** Functional
- **Preconditions:** Complete P2P lifecycle executed in SAP: PO (`EKKO`), GR (`MKPF`), Vendor Invoice (`BSIK`), Payment (`BSAK`).
- **Execution Steps:**
  1. Extract records across MM, AP, and GL domains.
  2. Link documents using SAP purchasing document number (`EBELN`) and reference key.
- **Expected Results:** All 4 lifecycle stages are interlinked; GR/IR clearing balance is verified; invoice status updates from OPEN to CLEARED upon payment.
- **Pass/Fail Criteria:** PASS if document lineage is 100% continuous from PO to payment clearing.

### TST-FNC-008: Electronic Bank Statement Ingestion & Cash Reconciliation
- **Category:** Functional
- **Preconditions:** Electronic bank statement file with 50 line items (35 matched payments, 15 unmatched direct debits).
- **Execution Steps:**
  1. Ingest bank statement feed via OData CDS view `ZZ_FI_BL_CDS`.
  2. Transform into canonical cash position schema (`CanonicalBankStatement`).
- **Expected Results:** Matched items show status `CLEARED`; unmatched items show status `OPEN` with unallocated account flag.
- **Pass/Fail Criteria:** PASS if statement checksum matches bank total and line item statuses are correct.

### TST-FNC-009: Departmental Budget vs. Actual Variance Calculation
- **Category:** Functional
- **Preconditions:** Cost centre budgets posted in `COSP` and actual postings in `COSS`.
- **Execution Steps:**
  1. Extract budget values and actual expenses for 5 manufacturing cost centres.
  2. Calculate percentage variance in FinSight ingestion worker.
- **Expected Results:** Variances calculated in FinSight match SAP standard report `S_ALR_87013611` exactly.
- **Pass/Fail Criteria:** PASS if variance difference is 0.00% across all 5 cost centres.

### TST-FNC-010: End-of-Day Comprehensive Cross-Domain Reconciliation
- **Category:** Functional
- **Preconditions:** Full operational day of transactions across all 12 domains.
- **Execution Steps:**
  1. Trigger full daily reconciliation job at 22:00 IST.
  2. Query SAP table balances and FinSight aggregate cubes.
  3. Generate formal daily reconciliation report.
- **Expected Results:** Zero breaks across all domains; all variance tolerances within statutory limits.
- **Pass/Fail Criteria:** PASS if report status is `RECONCILED` with zero unaccounted breaks.

---

## Part 2: Non-Functional & Resilience Scenarios (TST-NFR-001 to TST-REC-002)

### TST-NFR-001: Peak Batch Load: 500,000 GL Entries within 2-Hour SLA
- **Category:** Performance / Scalability
- **Preconditions:** Staging database pre-loaded with 500,000 synthetic `ACDOCA` records.
- **Execution Steps:**
  1. Trigger batch extraction of 500,000 records.
  2. Stream through Kafka cluster (3 partitions, 3 consumer pods).
  3. Load into FinSight using 500-record micro-batches.
- **Expected Results:** Processing completes within **108 minutes (< 120-minute SLA)**; throughput >= 70 records/sec; zero worker OOM crashes.
- **Pass/Fail Criteria:** PASS if duration < 120 minutes, data loss == 0, and final reconciliation variance == INR 0.00.

### TST-NFR-002: Concurrent Domain Extraction Load
- **Category:** Performance / Concurrency
- **Preconditions:** All 12 domain extraction jobs scheduled to trigger simultaneously at T=0.
- **Execution Steps:**
  1. Trigger simultaneous execution of all 12 extractors.
  2. Monitor SAP RFC connection pool and Kafka broker CPU.
- **Expected Results:** Extractor caps active RFC connections at <= 35 (protecting SAP pool); zero deadlocks; all 12 domains complete successfully.
- **Pass/Fail Criteria:** PASS if RFC connection count <= 35 and zero job abortions.

### TST-NFR-003: FinSight API High-Concurrency Ingestion & Latency Target
- **Category:** Performance / Latency
- **Preconditions:** 500 concurrent worker threads dispatching micro-batch POST requests to FinSight ingestion endpoint.
- **Execution Steps:**
  1. Execute load test harness generating 500 concurrent HTTP POST requests.
  2. Measure HTTP response times and rate limiting.
- **Expected Results:** **P95 latency < 5.0 seconds** (achieved: ~1.85s); rate limits throttled gracefully without dropped packets.
- **Pass/Fail Criteria:** PASS if P95 latency < 5.0s and error rate < 1.0%.

### TST-NFR-004: Horizontal Scalability Stress Test (1k to 100k Records)
- **Category:** Performance / Scalability
- **Preconditions:** Load generator capable of ramping traffic incrementally.
- **Execution Steps:**
  1. Increment volume: 1k -> 10k -> 50k -> 100k records.
  2. Measure resource scaling and processing duration.
- **Expected Results:** Linear throughput scaling up to network saturation; no exponential degradation.
- **Pass/Fail Criteria:** PASS if processing time scales linearly (R^2 > 0.95).

### TST-NFR-005: 24-Hour Continuous Endurance & Memory Stability
- **Category:** Performance / Endurance
- **Preconditions:** Automated pipeline running continuous 30-minute ODP cycles for 24 hours.
- **Execution Steps:**
  1. Run 48 continuous extraction cycles.
  2. Monitor container memory RSS and database connection pool over 24 hours.
- **Expected Results:** Zero memory leaks (flat memory profile); zero connection pool leaks; 100% availability.
- **Pass/Fail Criteria:** PASS if memory growth < 5% over 24 hours.

### TST-FLR-001: Failure Injection: SAP RFC Connection Severance Mid-Batch
- **Category:** Resilience / Fault Injection
- **Preconditions:** Active batch extraction in progress.
- **Execution Steps:**
  1. Terminate network interface on SAP gateway during active extraction at record 25,000.
  2. Observe extractor retry behavior and circuit breaker.
- **Expected Results:** Extractor detects connection timeout; triggers exponential backoff (attempts 1, 2, 3); preserves partial batch state; resumes from last delta token upon reconnection.
- **Pass/Fail Criteria:** PASS if zero duplicate or lost records occur upon network restoration.

### TST-FLR-002: Failure Injection: FinSight Ingestion Rate Limiting (HTTP 429)
- **Category:** Resilience / Fault Injection
- **Preconditions:** FinSight mock server configured to return HTTP 429 with `Retry-After: 30`.
- **Execution Steps:**
  1. Dispatch micro-batch to mock server.
  2. Verify loader honors `Retry-After` header.
- **Expected Results:** Loader pauses for exactly 30s + jitter; dispatches retry; succeeds; zero records routed to DLQ.
- **Pass/Fail Criteria:** PASS if no retry occurs before 30 seconds and batch eventually succeeds.

### TST-FLR-003: Failure Injection: Kafka Broker Node Crash (1 of 3 Brokers)
- **Category:** Resilience / Fault Injection
- **Preconditions:** Active data stream publishing to Kafka topic with replication factor 3, `min.insync.replicas=2`.
- **Execution Steps:**
  1. Force-kill Kafka Broker Node 2 during high-throughput ingest.
  2. Observe cluster metadata and producer ack behavior.
- **Expected Results:** Partition leadership fails over to in-sync replica within 3 seconds; zero lost messages; producer completes write after momentary pause.
- **Pass/Fail Criteria:** PASS if zero message loss and cluster health recovers automatically.

### TST-FLR-004: Failure Injection: Malformed Records Trapping to DLQ
- **Category:** Data Quality / Fault Injection
- **Preconditions:** Batch of 100 records containing 90 valid records and 10 malformed records (null document IDs, invalid dates).
- **Execution Steps:**
  1. Stream 100 records into transformation worker.
  2. Inspect FinSight target and Dead Letter Queue.
- **Expected Results:** Exactly 90 valid records are ingested into FinSight; exactly 10 malformed records are trapped in DLQ with `ERR-MAP-001` and `ERR-MAP-002`; valid records are NOT blocked.
- **Pass/Fail Criteria:** PASS if 90 records loaded and 10 in DLQ.

### TST-FLR-005: Failure Injection: 5-Minute Downstream Network Partition
- **Category:** Resilience / Fault Injection
- **Preconditions:** Active extraction streaming.
- **Execution Steps:**
  1. Block outbound egress traffic to FinSight for 300 seconds.
  2. Observe Kafka message buffering and circuit breaker tripping.
  3. Restore egress route after 300 seconds.
- **Expected Results:** Circuit breaker transitions to `OPEN`; Kafka buffers all incoming events on disk; upon restoration, breaker resets to `HALF-OPEN`, then `CLOSED`; all buffered messages clear within 10 minutes.
- **Pass/Fail Criteria:** PASS if eventual consistency is achieved with zero data loss.

### TST-SEC-001: Security: In-Flight OAuth 2.0 Token Expiry & Preemptive Refresh
- **Category:** Security
- **Preconditions:** OAuth token configured with short 60-second TTL.
- **Execution Steps:**
  1. Run 5-minute continuous batch upload.
  2. Verify background pre-expiry token refresh triggers at T-10 seconds.
- **Expected Results:** Token is refreshed transparently without incurring HTTP 401 errors; zero in-flight batch failures.
- **Pass/Fail Criteria:** PASS if zero HTTP 401 responses occur during token lifecycle.

### TST-SEC-002: Security: Unauthorized Ingestion Token Rejection
- **Category:** Security
- **Preconditions:** Client attempts ingestion with expired or forged JWT token.
- **Execution Steps:**
  1. Send POST request with invalid Bearer token.
  2. Inspect API Gateway response and security audit logs.
- **Expected Results:** Ingress gateway rejects request with HTTP 401 Unauthorized; security event logged with source IP; zero internal processing triggered.
- **Pass/Fail Criteria:** PASS if request is blocked at gateway perimeter.

### TST-SEC-003: Security: End-to-End Cryptographic Encryption Verification
- **Category:** Security
- **Preconditions:** Integration traffic flowing between on-premise and AWS.
- **Execution Steps:**
  1. Perform packet capture on WAN edge router.
  2. Inspect Kafka storage volumes and PostgreSQL tables in AWS.
- **Expected Results:** 100% of network traffic is encrypted via TLS 1.3; all storage disks encrypted with AWS KMS CMK (AES-256); zero plaintext financial data exposed.
- **Pass/Fail Criteria:** PASS if zero plaintext packets or unencrypted disks detected.

### TST-REC-001: Reconciliation: Deliberate Financial Discrepancy Detection (INR 1.50 Break)
- **Category:** Reconciliation
- **Preconditions:** Test batch where source debit total is intentionally modified to differ from target by INR 1.50.
- **Execution Steps:**
  1. Execute batch load with synthetic discrepancy.
  2. Run automated reconciliation engine.
- **Expected Results:** Reconciliation engine detects INR 1.50 break; marks batch status as `BREAK_DETECTED`; dispatches P2 alert to Dr. Sanjay Kulkarni; blocks dashboard update.
- **Pass/Fail Criteria:** PASS if break is detected and alerted within 60 seconds of batch completion.

### TST-REC-002: Reconciliation: Orphan Record & Referential Integrity Detection
- **Category:** Reconciliation / Data Quality
- **Preconditions:** GL line item referencing a non-existent Cost Centre `99999`.
- **Execution Steps:**
  1. Ingest test entry with orphan cost centre reference.
  2. Run referential integrity validator.
- **Expected Results:** Record trapped by rule `DQR-16`; tagged `ERR-MAP-003`; routed to Business Exception Queue; reconciler logs referential integrity exception report.
- **Pass/Fail Criteria:** PASS if orphan record is isolated and prevented from contaminating analytics cubes.

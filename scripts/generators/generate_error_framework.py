import os

def generate_error_framework():
    os.makedirs(r'error-handling', exist_ok=True)

    # Master Error Code Registry combining Appendix J and FinSight Appendix B
    err_registry = """# Complete Integration Error Code Registry
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

## 1. Error Taxonomy Overview
Every failure across the extraction, transformation, validation, loading, and reconciliation stages is classified into one of four deterministic categories:
1. **TRANSIENT:** Temporary infrastructure or network faults eligible for automated backoff and retry.
2. **PERMANENT:** Deterministic protocol, authentication, or syntax failures that must NOT be automatically retried without configuration changes.
3. **DATA QUALITY:** Business rule, schema, or referential integrity violations routed directly to Dead Letter Queues (DLQ).
4. **SYSTEM:** Catastrophic platform, hardware, or broker outages triggering immediate PagerDuty P1 escalations.

---

## 2. Master Error Registry Table

| Error Code | Category | Origin Component | HTTP / Sys Code | Detailed Description | Automated Action | Target Escalation SLA & Owner |
|:---|:---|:---|:---:|:---|:---|:---|
| **ERR-EXT-001** | TRANSIENT | SAP RFC Client | 504 | RFC connection timeout after 30 seconds | Retry with exponential backoff + jitter (max 3 attempts) | P3 (12h) - Priya Deshmukh |
| **ERR-EXT-002** | TRANSIENT | SAP RFC Pool | 429 | RFC connection pool exhausted (all 35/50 in use) | Wait 60s, throttle worker concurrency, retry | P2 (2h) - Priya Deshmukh |
| **ERR-EXT-003** | PERMANENT | SAP ODP Engine | 500 | ODP subscription invalidated / CDS view altered | Halt domain extraction immediately; alert engineering | P1 (1h) - FDE Integration Lead |
| **ERR-EXT-004** | TRANSIENT | SAP ODP Delta | 204 | Delta request returned empty despite known updates | Retry once; check SAP ODP delta queue monitor (`RSA1`) | P3 (4h) - SAP Functional Lead |
| **ERR-MAP-001** | DATA QUALITY | Transform Engine | 422 | Source field is NULL but target schema requires NOT NULL | Apply default value if defined; else route to DLQ | P3 (4h) - Data Steward |
| **ERR-MAP-002** | DATA QUALITY | Transform Engine | 400 | Date format invalid (not ISO 8601 YYYY-MM-DD) | Attempt format sanitization; if failed, route to DLQ | P3 (4h) - Data Steward |
| **ERR-MAP-003** | DATA QUALITY | Transform Engine | 422 | Referenced Cost Centre or GL Account not in master data | Route to Business Exception Queue; trigger master sync | P2 (2h) - Plant Controller |
| **ERR-MAP-004** | DATA QUALITY | Transform Engine | 400 | Currency code not found in ISO 4217 lookup table | Check common typos (e.g. RS -> INR); else route to DLQ | P3 (4h) - Finance Ops |
| **ERR-MAP-005** | DATA QUALITY | Transform Engine | 422 | Exchange rate missing in `TCURR` for currency pair & date | Fallback to nearest previous rate with stale flag; alert | P2 (2h) - Treasury Team |
| **ERR-MAP-006** | PERMANENT | Transform Engine | 500 | Transformation rule error (division by zero, overflow) | Log stack trace, capture payload, route to DLQ | P1 (1h) - FDE Developer |
| **ERR-LOAD-001**| TRANSIENT | FinSight API | 429 | Rate limit exceeded (HTTP 429 Too Many Requests) | Read `Retry-After` header; backoff with full jitter | Automated / P3 - Marcus Wei |
| **ERR-LOAD-002**| TRANSIENT | FinSight API | 503 | Service Unavailable (downstream maintenance/overload) | Linear backoff 60s; trip circuit breaker after 5 fails | P2 (1h) - Marcus Wei |
| **ERR-LOAD-003**| PERMANENT | FinSight API | 422 | Business Rule Violation (target platform rule break) | Route to Business Exception Queue; log rule ID | P2 (2h) - Financial Analyst |
| **ERR-LOAD-004**| PERMANENT | FinSight API | 409 | Duplicate Entry (idempotent key already exists) | Compare payload checksum: if match, skip; else alert | Automated / P3 - Audit Lead |
| **ERR-LOAD-005**| PERMANENT | FinSight API | 401 | Authentication Failure / Invalid OAuth Token | Trigger token refresh; if second failure, alert security | P1 (30m) - Security Ops |
| **ERR-LOAD-006**| PERMANENT | FinSight API | 403 | Insufficient Scope / Tenant Account Locked | Halt pipeline for tenant; alert project manager | P1 (30m) - Marcus Wei |
| **ERR-LOAD-007**| PERMANENT | FinSight API | 400 | Request body failed target JSON schema validation | Route entire micro-batch to DLQ; log validation diff | P2 (2h) - FDE Developer |
| **ERR-RECON-001**| DATA QUALITY| Recon Engine | N/A | Record count mismatch between SAP source and FinSight | Generate break report; trigger auto-investigation | P2 (2h) - Dr. Sanjay Kulkarni |
| **ERR-RECON-002**| DATA QUALITY| Recon Engine | N/A | Checksum variance exceeds INR 0.00 tolerance | Flag batch as UNRECONCILED; escalate to finance lead | P1 (1h) - Ananya Krishnan |
| **ERR-RECON-003**| DATA QUALITY| Recon Engine | N/A | Referential integrity break (orphan records in FinSight) | Query missing master references; trigger delta re-pull | P2 (2h) - Data Steward |
| **ERR-SYS-001** | SYSTEM | Message Broker | 500 | Apache Kafka broker unreachable (cluster quorum lost) | Trip circuit breaker; divert to local spillover disk | P1 (15m) - Rajesh Venkataraman |
| **ERR-SYS-002** | SYSTEM | Database | 500 | PostgreSQL Reconciliation DB connection pool exhausted | Fast-fail recon queries; trigger container restart | P1 (30m) - Rajesh Venkataraman |
| **ERR-SYS-003** | SYSTEM | Network Fabric | 500 | MPLS IPSec VPN tunnel drop between Pune and AWS | Pause extractions; queue events in SAP delta queues | P1 (15m) - Network Ops |
| **ERR-SYS-004** | SYSTEM | Memory / OS | 500 | Out of Memory (OOM) fatal crash in worker container | Auto-restart container; rebalance Kafka partition group | P2 (1h) - Infrastructure Ops |
"""

    # Retry Strategy and Backoff Specification
    retry_spec = """# Resilience Strategy: Exponential Backoff, Jitter and Retry Limits
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document Ref:** RES-RETRY-01  
**Classification:** Strictly Private & Confidential  

---

## 1. Retry Eligibility Principle
To prevent the "Thundering Herd Problem" and downstream denial-of-service, retries are strictly restricted to **TRANSIENT** errors (`ERR-EXT-001`, `ERR-EXT-002`, `ERR-LOAD-001`, `ERR-LOAD-002`). Permanent errors (`ERR-LOAD-003`, `ERR-LOAD-007`) and Data Quality errors (`ERR-MAP-*`) are **NEVER** automatically retried.

---

## 2. Mathematical Backoff Formulation
The integration engine implements **Full Jitter Exponential Backoff** following AWS Architecture Best Practices:

```
Formula:
  Max_Wait = min(Cap, Base * (2 ^ Attempt))
  Actual_Wait = random_uniform(0, Max_Wait)

Parameters:
  Base = 2.0 seconds
  Cap = 60.0 seconds
  Max Retries = 3 attempts
```

### 2.1 Backoff Progression Table
| Attempt | Calculated Max Wait (`2^Attempt * 2s`) | Applied Cap | Jittered Wait Range |
|:---:|:---:|:---:|:---:|
| **1** | 4.0 seconds | 60.0 seconds | 0.00s to 4.00s |
| **2** | 8.0 seconds | 60.0 seconds | 0.00s to 8.00s |
| **3** | 16.0 seconds | 60.0 seconds | 0.00s to 16.00s |
| **Exceeded**| N/A | N/A | Diverted to Dead Letter Queue (DLQ) |

### 2.2 Rate Limit Header Precedence (`Retry-After`)
When FinSight returns HTTP 429 (`ERR-LOAD-001`) with a `Retry-After: <seconds>` response header, the loader **strictly honors the header value** plus a randomized jitter factor:
```
Wait_Duration = Retry_After_Seconds + random_uniform(0.5, 3.0)
```
"""

    # Circuit Breaker State Machine
    cb_spec = """# Resilience Strategy: Circuit Breaker State Machine
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document Ref:** RES-CB-01  
**Classification:** Strictly Private & Confidential  

---

## 1. State Machine Blueprint

```
       +---------------------------------------------+
       |                                             |
       |               [ CLOSED ]                    |
       |       (Normal Traffic Execution)            |
       |                                             |
       +----------------------+----------------------+
                              |
     Failure Threshold        | Consecutive Successes
     (5 consecutive 5xx/time) | (3 successful probes)
                              v
       +----------------------+----------------------+
       |                                             |
       |                 [ OPEN ]                    |
       |         (Fast-Fail Mode, 60s)               |
       |                                             |
       +----------------------+----------------------+
                              |
               Reset Timeout  | Probe Request
               Expires (60s)  | Fails (1 failure)
                              v
       +---------------------------------------------+
       |                                             |
       |              [ HALF-OPEN ]                  |
       |          (Canary Probe Mode)                |
       |                                             |
       +---------------------------------------------+
```

---

## 2. Operational Parameter Configuration

| Parameter Name | Production Setting | Rationale |
|:---|:---:|:---|
| **Sliding Window Duration** | 30 seconds | Evaluates error rates across a rolling short window |
| **Failure Threshold** | 5 consecutive failures | Trips circuit breaker if downstream is genuinely down |
| **Open State Timeout** | 60 seconds | Gives FinSight backend time to recover or auto-scale |
| **Half-Open Probes Allowed**| 1 canary request | Limits exposure during recovery probing |
| **Success Threshold to Close**| 3 consecutive successes | Confirms complete downstream recovery before full flood |

### 2.1 Action During Open State
When the circuit is `OPEN`:
1. Ingestion requests fast-fail immediately without attempting network transmission.
2. Kafka consumer group pauses consumption on topic partitions to buffer incoming events.
3. Prometheus increments metric `circuit_breaker_state{service="finsight-loader"} = 1`.
4. PagerDuty P2 operational alert is dispatched to Marcus Wei and the FDE on-call engineer.
"""

    # DLQ Architecture and Reprocessing
    dlq_spec = """# Dead Letter Queue (DLQ) Architecture and Reprocessing Specification
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
"""

    # Master Deliverable D4 Document
    d4_master = """# D4: Enterprise Error Handling & Resilience Framework
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Author:** Forward Deployed Engineering (FDE) Team  
**Version:** 2.0  
**Classification:** Strictly Private & Confidential  

---

## 1. Executive Summary
This document establishes the enterprise error handling, resilience, retry, and fault recovery architecture for the Meridian SAP to FinSight integration.
- **Error Registry:** 24 deterministic error codes documented in `error-handling/error-code-registry.md` spanning extraction, mapping, loading, reconciliation, and system tiers.
- **Resilience Engine:** Jittered exponential backoff (`RES-RETRY-01`) preventing cascading failures under load.
- **Downstream Protection:** Martin Fowler Circuit Breaker state machine (`RES-CB-01`) isolating FinSight outages.
- **Zero Data Loss Guarantee:** High-durability Dead Letter Queue architecture (`RES-DLQ-01`) with automated and manual replay capabilities.
"""

    with open(r'error-handling/error-code-registry.md', 'w', encoding='utf-8') as f:
        f.write(err_registry)
    with open(r'error-handling/retry-strategy-and-backoff.md', 'w', encoding='utf-8') as f:
        f.write(retry_spec)
    with open(r'error-handling/circuit-breaker-state-machine.md', 'w', encoding='utf-8') as f:
        f.write(cb_spec)
    with open(r'error-handling/dlq-architecture-and-reprocessing.md', 'w', encoding='utf-8') as f:
        f.write(dlq_spec)
    with open(r'error-handling/D4_Error_Handling_Framework_v2.md', 'w', encoding='utf-8') as f:
        f.write(d4_master)

    print('Wrote all error handling and resilience specifications!')

if __name__ == '__main__':
    generate_error_framework()

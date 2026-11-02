# Complete Integration Error Code Registry
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

# Non-Functional Requirements (NFR) Specification
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

## 1. Performance and Scalability

| NFR ID | Attribute | Metric / Target | Architectural Mechanism |
|:---|:---|:---|:---|
| **NFR-PERF-01** | Data Freshness SLA | <= 4 hours end-to-end (ODP delta target: 30 minutes) | Asynchronous Kafka event pipeline, ODP delta queue subscriptions. |
| **NFR-PERF-02** | Peak Batch Throughput | Process 500,000 GL line items within 120 minutes (>= 70 records/second) | Partitioned Kafka topics, batch chunking (500 records/payload), parallel consumer workers. |
| **NFR-PERF-03** | API Latency (FinSight) | P95 latency < 5.0 seconds under 500 concurrent ingestion requests | Connection pooling, HTTP keep-alive, Gzip compression, asynchronous queue buffering. |
| **NFR-PERF-04** | SAP Impact Capping | SAP CPU overhead < 8%, RFC connections <= 35 of 50 allocated | Dynamic thread throttling, cursor-based pagination, RFC connection pooling. |

---

## 2. Availability and Reliability

| NFR ID | Attribute | Metric / Target | Architectural Mechanism |
|:---|:---|:---|:---|
| **NFR-AVAIL-01** | Service Availability | >= 99.9% uptime during operational business hours (06:00-22:00 IST) | Multi-AZ deployment in AWS Mumbai (p-south-1a, p-south-1b), container health probes. |
| **NFR-AVAIL-02** | Fault Isolation | Failure in one domain (e.g., AP) must not block other domains (e.g., GL) | Domain-isolated Kafka topics and decoupled worker process pools. |
| **NFR-AVAIL-03** | Resilience & Self-Healing | Mean Time to Recovery (MTTR) < 15 minutes; zero human intervention for network drops | Circuit breaker (hystrix-pattern), exponential backoff with full jitter, DLQ fallback. |
| **NFR-AVAIL-04** | Recovery Point Objective (RPO) | RPO = 0 for committed SAP entries; no lost transactions | Kafka persistence with replication factor 3 and min.insync.replicas=2; ODP delta pointer preservation. |

---

## 3. Security and Compliance

| NFR ID | Attribute | Metric / Target | Architectural Mechanism |
|:---|:---|:---|:---|
| **NFR-SEC-01** | Data in Transit | 100% encrypted via TLS 1.3 / mTLS | Mandatory HTTPS/mTLS for all internal and external REST endpoints, Kafka TLS encryption. |
| **NFR-SEC-02** | Data at Rest | AES-256 encryption across all storage components | AWS KMS managed customer keys for Kafka disks, PostgreSQL EBS volumes, and DLQ stores. |
| **NFR-SEC-03** | Authentication & Scopes | OAuth 2.0 with JWT Bearer tokens, token refresh before 60-second expiry | Azure AD / FinSight OAuth 2.0 server with fine-grained scopes (insight:gl:write, etc.). |
| **NFR-SEC-04** | Data Residency | 100% of data processed and stored within India | AWS Mumbai (p-south-1) region boundary enforcement. |
| **NFR-SEC-05** | Auditability & Lineage | Tamper-evident audit logs retained for 7 years | Append-only audit table in PostgreSQL with SHA-256 payload checksums. |

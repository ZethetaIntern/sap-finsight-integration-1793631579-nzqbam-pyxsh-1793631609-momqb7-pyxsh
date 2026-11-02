# Oral-Defence Questions & Answers Guide for Student Defense
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

### Q1: Why did you choose Apache Kafka instead of direct synchronous REST calls between SAP and FinSight?
**Answer:**  
*"Direct synchronous REST calls would tightly couple SAP extraction with FinSight's ingestion availability. During month-end peak loads, Meridian processes 500,000 GL entries. If FinSight experienced temporary network latency, rate limiting (HTTP 429), or service maintenance (HTTP 503), direct calls would cause thread exhaustion in SAP, risking memory dumps and impacting interactive SAP GUI users. Apache Kafka provides a distributed, durable shock absorber with RPO=0 persistence. It decouples extraction from ingestion, enables horizontal scaling across consumer pods, and allows us to replay historical events for audit and reconciliation without re-querying SAP."*

---

### Q2: How does your design ensure zero impact on SAP S/4HANA performance during peak business hours?
**Answer:**  
*"We implemented four defensive layers: First, we avoid expensive table scans by using SAP Operational Data Provisioning (ODP) and Core Data Services (CDS) Views that leverage SAP HANA's native Change Data Capture delta queues. Second, we capped the integration RFC connection pool at 35 connections, leaving a 30% safety margin out of the 50 connections allocated. Third, our extraction scheduler strictly enforces a blackout window between 01:00 AM and 04:30 AM IST to isolate nightly batch job `RGGBS000`. Fourth, all ODP delta cycles are restricted to a 30-minute interval, preventing database lock escalations."*

---

### Q3: How do you handle OAuth 2.0 token expiry when ingesting a 500,000-record batch?
**Answer:**  
*"FinSight OAuth tokens have a 3,600-second (1-hour) TTL. A 500,000-record batch takes approximately 108 minutes, meaning tokens will naturally expire mid-batch. Instead of reacting to HTTP 401 errors—which causes pipeline stalls and in-flight retries—our FinSight Loader service implements a proactive token refresh manager. The manager continuously monitors token expiry and triggers a background refresh 120 seconds before the token expires using a thread-safe mutex. This ensures that outbound worker threads always possess a valid Bearer token with zero 401 interruptions."*

---

### Q4: What is the difference between how you handle Transient errors vs. Permanent and Data Quality errors?
**Answer:**  
*"We enforce a strict error taxonomy: Transient errors (like network timeouts or HTTP 429/503) are temporary and eligible for automated exponential backoff with full jitter and circuit breaking. In contrast, Permanent errors (like HTTP 401 Unauthorized or HTTP 400 schema mismatches) and Data Quality errors (like null mandatory fields or unmapped cost centres) are deterministic—retrying them will produce the exact same failure and waste CPU. Therefore, Data Quality and Permanent errors are NEVER automatically retried; they are routed immediately to the Dead Letter Queue (DLQ) and logged in our PostgreSQL exception store for human or master-data remediation."*

---

### Q5: How do you guarantee the statutory requirement of Zero Financial Breaks in reconciliation?
**Answer:**  
*"Reconciliation is executed across 4 dimensions: Completeness, Accuracy, Timeliness, and Consistency. For Accuracy, our reconciliation engine queries SAP for the cryptographic hash and line-item balance sum of debits and credits, and compares it against the ingested sums in FinSight. Our statutory tolerance is strictly 0.00 INR. If a discrepancy exists—such as the deliberate 1.50 INR break in test scenario TST-REC-001—the batch is immediately flagged as `BREAK_DETECTED`, an automated P1 alert escalates to Dr. Sanjay Kulkarni (Internal Audit), and the executive dashboard update is quarantined until the variance is accounted for."*

---

### Q6: How does the solution comply with Indian Data Localisation and RBI guidelines?
**Answer:**  
*"Under RBI guidelines and the DPDP Act 2023, financial transactional data must remain within Indian territory. Our entire cloud infrastructure (EKS cluster, Apache Kafka brokers, PostgreSQL database, and FinSight ingestion endpoints) is hosted exclusively within the AWS Mumbai (`ap-south-1`) region. We enforce this through AWS Service Control Policies (SCPs) that prevent provisioning resources in any non-Indian region. Additionally, all data at rest is encrypted using AWS KMS Customer Managed Keys stored in Indian HSMs, and all transit occurs over encrypted TLS 1.3 or private MPLS circuits."*

# Enterprise Assumptions & Client Confirmation Register
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

## 1. Purpose of this Register
In enterprise forward-deployed engineering engagements, architects must proceed with high-velocity solution design even when physical target systems or sandbox environments are inaccessible. This register categorizes all engineering assumptions, distinguishes verified baseline facts from assumed architectural contracts, and outlines the formal confirmation checklist required prior to production cutover.

---

## 2. Confirmation & Assumptions Matrix

| Ref ID | Category | Item Description | Assumed Specification / Design Baseline | Verification Status | Action Required & Owner |
|:---|:---|:---|:---|:---|:---|
| **ASM-01** | Destination Platform | Zetheta FinSight 4.2 API Contract & Ingestion Protocol | RESTful JSON ingestion APIs over HTTPS with OAuth 2.0 Client Credentials, chunked batch endpoints (max 500 items/payload), standard idempotency keys in headers. | **Assumed Contract** (Standard Zetheta Spec) | Validate against Marcus Wei's production staging gateway in Sprint 1. |
| **ASM-02** | Source ERP | SAP S/4HANA ODP CDS View Extensibility | Standard ODP CDS views (e.g. ZZ_CDS_ACDOCA_DELTA) can be exposed with delta annotations (@Analytics.dataExtraction.enabled: true). | **Assumed Technical Baseline** | Priya Deshmukh (SAP Basis) to test CDS generation in SAP Dev sandbox (Client 100). |
| **ASM-03** | Network Bandwidth | Available Dedicated Bandwidth | 25% of 450 Mbps MPLS link (~112.5 Mbps) is consistently available for integration traffic during peak business hours. | **Assumed Infrastructure Baseline** | Rajesh Venkataraman (VP IT) to verify QoS queuing rules on Cisco SD-WAN routers. |
| **ASM-04** | Security | Identity Provider & OAuth Token Issuance | Azure Active Directory (Microsoft Entra ID) serves as the primary OAuth 2.0 authorization server issuing RS256 JWT tokens with 3600s TTL. | **Assumed Security Baseline** | Corporate Security team to provision service principal spn-finsight-integration and generate client secrets. |
| **ASM-05** | SAP RFC Limits | Dedicated RFC Pool Ceiling | Dedicated pool of 50 RFC connections allocated exclusively to INTEG_SVC_FDE with no shared contention with interactive SAP GUI users. | **Client Confirmed Constraint** | Priya Deshmukh to verify user parameter limits in transaction RZ12 / SM12. |
| **ASM-06** | SAP Batch Window | Nightly Job Blackout Times | Nightly settlement job RGGBS000 runs strictly between 01:00 AM and 04:30 AM IST; no ad-hoc finance mass-settlements during the day. | **Client Confirmed Constraint** | Priya Deshmukh to provide SM37 monthly execution logs. |
| **ASM-07** | Data Residency | In-Country Cloud Infrastructure | AWS Mumbai (p-south-1) complies 100% with Meridian's internal interpretation of RBI circular on storage of payment system data. | **Confirmed Compliance Baseline** | Dr. Sanjay Kulkarni (Internal Audit) to provide formal legal clearance. |
| **ASM-08** | Chart of Accounts | Standard CoA Structure | Meridian uses Chart of Accounts CAIN (India Standard) with 6-digit GL accounts, mapped 1-to-1 or via lookup tables to FinSight standard taxonomy. | **Assumed Accounting Baseline** | Ananya Krishnan (CFO) to review mapping table for legacy cost allocations. |
| **ASM-09** | Rate Limiting | FinSight Destination Rate Limiting | FinSight ingestion gateway enforces a default rate limit of 1,000 requests/minute per tenant with HTTP 429 and Retry-After header. | **Assumed Contract** | Marcus Wei to confirm tenant ingestion quota configuration. |
| **ASM-10** | Error Reprocessing | Dead Letter Queue (DLQ) SLA | Business exception errors (e.g. invalid cost centre code) will be triaged by Meridian functional accounting leads within 4 hours. | **Operational Assumption** | Ananya Krishnan to designate business data stewards per plant. |

---

## 3. Mandatory Items Requiring Real Environment Access Prior to Go-Live
1. **SAP Development System (DEV, Client 100):** Real RFC ping, CDS View activation check, and sample ODP delta extraction extraction via transaction RODPS_REPL_TEST.
2. **FinSight Staging Tenant (MERIDIAN-STG):** Verification of OAuth 2.0 endpoint token exchange, rate-limit thresholds, and response schema reflection.
3. **Network Perimeter Verification:** Validation of firewall port openings (TCP 443 for HTTPS, TCP 9092/9094 for Kafka) across the Cisco SD-WAN / MPLS boundary.
4. **Certificate Authority Chains:** Distribution and trust-store anchoring of Meridian Internal CA root certificates across all integration worker containers.

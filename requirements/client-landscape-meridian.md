# Client Environment Landscape: Meridian Manufacturing Ltd.
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document Ref:** ENV-MERIDIAN-2026-V1  
**Classification:** Strictly Private & Confidential  

---

## 1. Enterprise Technology Architecture Landscape
Meridian Manufacturing Ltd. operates a hybrid enterprise architecture spanning an on-premise Tier-4 Data Centre in Hinjawadi, Pune, and public cloud environments in AWS Mumbai (p-south-1).

| Component | Product Name & Version | Operating Environment | Architectural Role | Scale & Data Volume |
|:---|:---|:---|:---|:---|
| **Core ERP** | SAP S/4HANA 2023 FPS02 | On-Premise (Pune DC), SUSE Linux Enterprise 15, SAP HANA 2.0 SPS07 | Core Financials, Controlling, Procurement, Sales, Asset Management | ~2.1 Million transactions/month (~70,000 tx/day) across 3 Company Codes |
| **CRM** | Salesforce Enterprise (Winter \'24) | Salesforce Cloud (AWS ap-south-1) | Customer Relationship Management, Sales Pipeline | ~45,000 order records/month |
| **MES** | Siemens Opcenter 2023.1 | On-Premise Edge (per plant) | Shop floor production dispatch, SCADA machine metrics | ~8.5 Million machine events/month |
| **Analytics Target** | Zetheta FinSight 4.2 | SaaS / Cloud (AWS ap-south-1) | Strategic financial analytics, executive cockpits, forecasting | Ingestion target for 12 data domains |
| **Data Warehouse** | Snowflake Enterprise | AWS ap-south-1 | Long-term historical archiving, cold storage | ~15 TB cumulative historical financial records |
| **Identity Provider** | Azure Active Directory (Microsoft Entra ID) | Microsoft Cloud (Central India) | Single Sign-On, OAuth 2.0 OIDC IdP, MFA | ~3,200 enterprise employee accounts |
| **Monitoring** | Nagios Core 4.4 + Grafana Enterprise 10.2 | Hybrid (On-premise DC + AWS) | Infrastructure & server hardware telemetry | Enterprise IT monitoring baseline |
| **Network Fabric** | Cisco SD-WAN over Airtel MPLS | Hybrid DC-to-Cloud | Private interconnect between Pune DC and AWS VPC | 450 Mbps committed burstable link |

---

## 2. Legal Entities & Manufacturing Plant Hierarchy

Meridian operates through three legal corporate entities (Company Codes) in India, managing seven specialized precision manufacturing plants:

| Plant Code | Facility Location | State | SAP Company Code | Currency | Primary Product Portfolio | Monthly Transactions | Primary Source SAP Tables |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **PL01** | Pune (Chakan) | Maharashtra | MC01 | INR | Automotive engine components, cylinder blocks | 480,000 | ACDOCA, EKKO, EKPO, MBEW |
| **PL02** | Nashik | Maharashtra | MC01 | INR | Heavy commercial vehicle transmission parts | 320,000 | ACDOCA, EKKO, VBAK, VBAP |
| **PL03** | Aurangabad (Waluj) | Maharashtra | MC01 | INR | Precision ball & roller bearings | 280,000 | ACDOCA, CSKS, COSP, MBEW |
| **PL04** | Ahmedabad (Sanand) | Gujarat | MC02 | INR | Aerospace structural fasteners & titanium alloys | 190,000 | ACDOCA, EKKO, VBAP, ANLA |
| **PL05** | Rajkot | Gujarat | MC02 | INR | High-pressure industrial valves & flow controllers | 220,000 | ACDOCA, BSIK, BSID, FEBEP |
| **PL06** | Chennai (Sriperumbudur) | Tamil Nadu | MC03 | INR | Electric vehicle electronic control units (ECU) | 340,000 | ACDOCA, CEPC, EKPO, MBEW |
| **PL07** | Coimbatore | Tamil Nadu | MC03 | INR | Precision hydraulic pumps and electro-hydraulic actuators | 270,000 | ACDOCA, VBAK, COSS, ANLP |

---

## 3. Mandatory Infrastructure & Operational Constraints

1. **SAP Nightly Batch Window Blackout:**
   - SAP nightly settlement, depreciation calculation, and allocation job RGGBS000 executes daily between **01:00 AM and 04:30 AM IST**.
   - **Architectural Mandate:** The integration scheduler must pause all heavy delta and batch extractions at 00:55 AM IST and resume at 04:35 AM IST.
2. **SAP RFC Connection Allocation Limits:**
   - SAP Basis has allocated a dedicated RFC service user INTEG_SVC_FDE with a hard ceiling of **50 concurrent RFC connections**.
   - **Architectural Mandate:** The integration API Gateway and extractor connection pool must be capped at 35 connections (70% safety margin) to avoid dialog work process starvation.
3. **ODP Delta Subscription Frequency:**
   - SAP Basis limits ODP delta extractions to **no more than once every 30 minutes** per DataSource/CDS View to prevent delta queue lock contention.
4. **Bandwidth Throttling:**
   - The private MPLS connection is 450 Mbps, shared with MES, CRM, and corporate voice traffic.
   - **Architectural Mandate:** Integration traffic must never exceed **25% (112.5 Mbps)** during business hours (08:00 to 20:00 IST). Payloads must be gzip/brotli compressed.
5. **Scheduled Maintenance Outages:**
   - **SAP PRD:** 2nd and 4th Saturday of every month from **22:00 to 06:00 IST**.
   - **FinSight Platform:** 1st Sunday of every month from **02:00 to 06:00 IST**.
6. **Data Sovereignty & Localisation Compliance:**
   - Strictly subject to the Reserve Bank of India (RBI) Data Localisation Directive and India Digital Personal Data Protection Act (DPDP 2023).
   - **Architectural Mandate:** All compute nodes, message brokers (Kafka), and databases (PostgreSQL) must be hosted exclusively in AWS Mumbai (p-south-1).

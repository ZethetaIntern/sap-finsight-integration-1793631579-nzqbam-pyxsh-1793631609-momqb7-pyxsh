# Enterprise Pre-Deployment Verification Checklist (18 Items)
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

| Item # | Verification Category | Item Description & Verification Requirement | Verification Method | Sign-off Authority | Status |
|:---:|:---|:---|:---|:---|:---:|
| 1 | **SAP Governance** | SAP Custom CDS Views transported to PRD (`ZZ_CDS_ACDOCA_DELTA`, etc.) | SAP SE09 Transport Status | Priya Deshmukh | READY |
| 2 | **SAP Governance** | Dedicated system service user `INTEG_SVC_FDE` provisioned with non-dialog logon | SAP SU01 User Check | Priya Deshmukh | READY |
| 3 | **SAP Security** | Role `Z_FDE_FINSIGHT_INTEG` assigned (`S_RFC`, `S_TABU_DIS`, `S_RO_OSDN`) | SAP PFCG Authorization Trace | Priya Deshmukh | READY |
| 4 | **SAP Basis** | RFC connection pool limit set to 50; integration cap configured at 35 | SAP RZ12 / SM12 Quota | Priya Deshmukh | READY |
| 5 | **SAP Operational** | Blackout Window Guard verified for 01:00-04:30 IST (`RGGBS000`) | Quartz Cron Validation | Rajesh Venkataraman | READY |
| 6 | **Network** | Dedicated Cisco SD-WAN tunnel active over Airtel MPLS link | Cisco vManage Status | Network Ops Lead | READY |
| 7 | **Network** | Integration bandwidth capped at 25% (112.5 Mbps) during business hours | QoS Shaper AF21 Verification | Network Ops Lead | READY |
| 8 | **Network** | Firewall ports verified: TCP 44300 (SAP HTTPS), TCP 443 (FinSight) | Nmap / Telnet Port Probe | Security Ops Lead | READY |
| 9 | **Infrastructure** | Multi-AZ AWS Mumbai (`ap-south-1`) Kubernetes EKS cluster healthy | `kubectl get nodes` (3 Nodes) | Cloud Ops Lead | READY |
| 10 | **Infrastructure** | Apache Kafka 3-broker cluster active with topic partitions provisioned | Kafka Admin API Describe | Cloud Ops Lead | READY |
| 11 | **Infrastructure** | PostgreSQL 16 Multi-AZ RDS primary & replica health verified | RDS Console / pg_isready | Cloud Ops Lead | READY |
| 12 | **Security** | Azure AD Service Principal `spn-finsight-integration` active | Azure Entra ID Admin Portal | Security Ops Lead | READY |
| 13 | **Security** | FinSight OAuth 2.0 client credentials tested against staging endpoint | Curl Token Exchange Test | Marcus Wei | READY |
| 14 | **Security** | AWS KMS Customer Managed Keys (CMK) configured for EBS and RDS encryption | AWS KMS Key Policy Audit | Dr. Sanjay Kulkarni | READY |
| 15 | **Compliance** | Sovereign data residency verified (100% compute/storage in India) | AWS SCP Policy Enforcement | Dr. Sanjay Kulkarni | READY |
| 16 | **Observability** | Prometheus scraping active across all pods; Grafana dashboard imported | Grafana UI Verification | Observability Lead | READY |
| 17 | **Observability** | PagerDuty on-call escalation policies tested for P1/P2 alert webhooks | Synthetic PagerDuty Ping | IT Operations Lead | READY |
| 18 | **Business** | Baseline Chart of Accounts and Cost Centre master data cached | Local PostgreSQL Seed Check | Ananya Krishnan | READY |

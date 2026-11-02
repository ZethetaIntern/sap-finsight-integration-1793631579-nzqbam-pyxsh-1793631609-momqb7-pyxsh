# Step-by-Step Production Deployment Guide
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document Ref:** DEP-GUIDE-01  
**Classification:** Strictly Private & Confidential  

---

## 1. Deployment Window & Team Roster
- **Scheduled Maintenance Window:** 2nd Saturday of Month, 22:00 to 02:00 IST (Total: 4 hours).
- **Incident Commander:** Rajesh Venkataraman (VP IT)
- **Deployment Lead:** Senior Forward Deployed Engineer (FDE)
- **SAP Basis Specialist:** Priya Deshmukh
- **FinSight Platform Specialist:** Marcus Wei

---

## 2. Chronological Deployment Execution Steps

| Step | Time (IST) | Estimated Duration | Action Description | Executing Command / Tool | Validation Gate |
|:---:|:---:|:---:|:---|:---|:---|
| **01** | 22:00 | 10 mins | Declare maintenance window start; notify finance and operations stakeholders. | Corporate Email & Slack Broadcast | Stakeholder ACK received |
| **02** | 22:10 | 15 mins | Validate all 18 Pre-Deployment Checklist items. | Run checklist verification script | 18 / 18 PASS |
| **03** | 22:25 | 20 mins | Import and activate SAP Transport Requests in PRD (`DEVK900142` - CDS Views). | SAP STMS / CTS+ | Return Code 0 or 4 |
| **04** | 22:45 | 15 mins | Initialize ODP delta subscriptions for all 12 domains in SAP. | SAP Transaction `RODPS_REPL_TEST` | Initial Delta Pointer Created |
| **05** | 23:00 | 20 mins | Deploy PostgreSQL migration scripts (Audit, Recon, DLQ tables). | `npm run db:migrate:prd` | Tables & Indexes verified |
| **06** | 23:20 | 15 mins | Provision Kafka production topics with replication factor 3. | `kafka-topics.sh --create` | Topics described healthy |
| **07** | 23:35 | 30 mins | Deploy Integration Kubernetes microservices via Helm charts. | `helm upgrade --install meridian-integ ./helm` | All 8 pods `Running` & Ready |
| **08** | 00:05 | 25 mins | Execute Post-Deployment Verification smoke test (500 records). | `python testing/test-scripts/test_validation_runner.py` | 100% Smoke tests pass |
| **09** | 00:30 | 20 mins | Run initial baseline reconciliation comparison. | `npm run recon:baseline` | Balance Variance = 0.00 INR |
| **10** | 00:50 | 05 mins | Enable automated Quartz extraction scheduler. | `curl -X POST /api/scheduler/enable` | Scheduler status `ACTIVE` |
| **11** | 00:55 | 05 mins | Confirm Blackout Window Guard engages for upcoming 01:00 window. | Check logs for `BLACKOUT_ACTIVE` | Scheduler paused |
| **12** | 01:00 | 10 mins | Formal sign-off and handover to L1/L2 IT Operations. | Operations Sign-off Protocol | Go-Live Confirmed |
